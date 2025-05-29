import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Trash2, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Search
} from 'lucide-react';
import axios from 'axios';

interface LMETickerData {
  id: number;  // Add database ID for deletion
  ticker: string;
  description: string;
  metal: string;
  symbol: string;
  bloomberg_symbol: string;
  px_last?: number;
  change?: number;
  change_pct?: number;
  timestamp?: string;
  is_live: boolean;
}

interface MarketStatus {
  is_open: boolean;
  exchange: string;
  current_time: string;
  message: string;
  trading_hours: string;
}

const Bloomberg: React.FC = () => {
  const [tickers, setTickers] = useState<LMETickerData[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // Add ticker state
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTicker, setNewTicker] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [addingTicker, setAddingTicker] = useState(false);
  const [addResult, setAddResult] = useState<{type: 'success' | 'error', message: string} | null>(null);

  const API_BASE = 'http://localhost:8000';

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      console.log('Bloomberg: Starting to fetch data...');
      setRefreshing(true);
      
      // Fetch tickers and market status in parallel
      console.log('Bloomberg: Fetching from API...');
      const [tickersResponse, statusResponse] = await Promise.all([
        axios.get(`${API_BASE}/lme/tickers?include_live_prices=true`),
        axios.get(`${API_BASE}/lme/market-status`)
      ]);
      
      console.log('Bloomberg: Received responses:', { 
        tickers: tickersResponse.data?.length || 0, 
        status: statusResponse.data 
      });
      
      setTickers(tickersResponse.data || []);
      setMarketStatus(statusResponse.data);
      setError(null);
    } catch (err: any) {
      console.error('Bloomberg: Error fetching data:', err);
      console.error('Bloomberg: Error details:', err.response?.data || err.message);
      setError(`Failed to fetch Bloomberg data: ${err.response?.data?.detail || err.message}. Please ensure your Bloomberg Terminal is running.`);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleAddTicker = async () => {
    if (!newTicker.trim()) return;

    setAddingTicker(true);
    setAddResult(null);

    try {
      const response = await axios.post(`${API_BASE}/lme/tickers/add`, {
        bloomberg_symbol: newTicker.toUpperCase(),
        description: newDescription.trim() || undefined
      });

      setAddResult({
        type: 'success',
        message: `Successfully added ${newTicker.toUpperCase()}: ${response.data.current_price}`
      });

      // Reset form
      setNewTicker('');
      setNewDescription('');
      setShowAddForm(false);

      // Refresh data
      await fetchData();

    } catch (err: any) {
      setAddResult({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to add ticker. Please check if it exists in Bloomberg.'
      });
    } finally {
      setAddingTicker(false);
    }
  };

  const handleDeleteTicker = async (tickerId: string) => {
    if (!confirm('Are you sure you want to remove this ticker?')) return;

    try {
      await axios.delete(`${API_BASE}/lme/tickers/${tickerId}`);
      await fetchData(); // Refresh data
    } catch (err) {
      console.error('Error deleting ticker:', err);
      setError('Failed to delete ticker');
    }
  };

  const formatPrice = (price?: number) => {
    if (price === undefined || price === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatChange = (change?: number, changePercent?: number) => {
    if (change === undefined || change === null || changePercent === undefined || changePercent === null) return null;
    
    const isPositive = change >= 0;
    const Icon = isPositive ? TrendingUp : TrendingDown;
    const colorClass = isPositive ? 'text-green-600' : 'text-red-600';
    
    return (
      <div className={`flex items-center gap-1 ${colorClass}`}>
        <Icon size={16} />
        <span>{isPositive ? '+' : ''}{change.toFixed(2)}</span>
        <span>({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)</span>
      </div>
    );
  };

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return 'No data';
    return new Date(timestamp).toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading Bloomberg data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <DollarSign className="h-8 w-8 text-blue-600" />
          Bloomberg Live Data
        </h1>
        <p className="text-gray-600">Real-time LME metals pricing from Bloomberg Terminal</p>
      </div>

      {/* Market Status */}
      {marketStatus && (
        <div className={`rounded-lg p-4 border ${
          marketStatus.is_open ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                marketStatus.is_open ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
              }`} />
              <span className="font-medium">{marketStatus.message}</span>
              <span className="text-sm text-gray-600">({marketStatus.trading_hours})</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Clock size={16} />
              <span>Last updated: {formatTimestamp(marketStatus.current_time)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={fetchData}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh Data
          </button>
          
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Plus className="h-4 w-4" />
            Add Bloomberg Ticker
          </button>
        </div>

        <div className="text-sm text-gray-600">
          {tickers.length} tickers tracked • 
          {tickers.filter(t => t.is_live).length} live
        </div>
      </div>

      {/* Add Ticker Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg border p-4">
          <h3 className="text-lg font-semibold mb-4">Add New Bloomberg Ticker</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bloomberg Symbol *
              </label>
              <input
                type="text"
                value={newTicker}
                onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                placeholder="e.g., LMAHDS03, XAU="
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (optional)
              </label>
              <input
                type="text"
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="e.g., Gold Spot Price"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-2 mt-4">
            <button
              onClick={handleAddTicker}
              disabled={addingTicker || !newTicker.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {addingTicker ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              {addingTicker ? 'Adding...' : 'Add Ticker'}
            </button>
            
            <button
              onClick={() => {
                setShowAddForm(false);
                setAddResult(null);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>

          {/* Add Result */}
          {addResult && (
            <div className={`mt-4 p-3 rounded-lg flex items-center gap-2 ${
              addResult.type === 'success' ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-700'
            }`}>
              {addResult.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
              <span>{addResult.message}</span>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Tickers Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Live LME Metals Prices</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metal
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Bloomberg Symbol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Price
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Change
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Updated
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tickers.map((ticker, index) => (
                <tr key={ticker.bloomberg_symbol} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        ticker.is_live ? 'bg-green-500' : 'bg-gray-400'
                      }`} />
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        ticker.is_live ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {ticker.is_live ? 'LIVE' : 'OFFLINE'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{ticker.metal}</div>
                    <div className="text-sm text-gray-500">{ticker.symbol}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-mono text-sm">{ticker.bloomberg_symbol}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{ticker.description}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="font-medium text-lg">{formatPrice(ticker.px_last)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    {formatChange(ticker.change, ticker.change_pct)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                    {formatTimestamp(ticker.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <button
                      onClick={() => handleDeleteTicker(ticker.id.toString())}
                      className="text-red-600 hover:text-red-800 p-1"
                      title="Remove ticker"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {tickers.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No tickers found. Add some Bloomberg symbols to get started.</p>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">Bloomberg Terminal Setup</h3>
        <div className="text-sm text-blue-700 space-y-1">
          <p>• Ensure your Bloomberg Terminal is running and logged in</p>
          <p>• The app will automatically validate ticker symbols against Bloomberg</p>
          <p>• Live data requires Bloomberg API permissions</p>
          <p>• Common LME symbols: LMAHDS03 (Aluminum), LMCADS03 (Copper), LMNIDS03 (Nickel)</p>
        </div>
      </div>
    </div>
  );
};

export default Bloomberg; 