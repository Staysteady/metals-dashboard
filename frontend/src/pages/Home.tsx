import React, { useEffect, useState, useCallback } from 'react';
import { ArrowUpIcon, ArrowDownIcon, TrendingUp, Activity, BarChart3 } from 'lucide-react';
import Plot from 'react-plotly.js';
import { getLMETickers, getMarketStatus, type Ticker, type MarketStatus } from '../api/client';
import BloombergStatus from '../components/DataSourceToggle';

interface GroupedData {
  [category: string]: Ticker[];
}

const Home: React.FC = () => {
  const [tickerData, setTickerData] = useState<Ticker[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('LMCADS03'); // Default to Copper

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [pricesData, statusData] = await Promise.all([
        getLMETickers(true), // Include live prices
        getMarketStatus()
      ]);
      setTickerData(pricesData);
      setMarketStatus(statusData);
    } catch (err: unknown) {
      console.error('Error fetching data:', err);
      
      if (err && typeof err === 'object' && 'response' in err) {
        const errorWithResponse = err as { response?: { status?: number; data?: { detail?: string } } };
        if (errorWithResponse.response?.status === 500 && errorWithResponse.response?.data?.detail) {
          setError(`API Error: ${errorWithResponse.response.data.detail}`);
        } else {
          setError('Failed to fetch market data');
        }
      } else {
        setError('Failed to fetch market data');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDataSourceChange = useCallback(() => {
    setLoading(true);
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchData();
    
    // Refresh data every 30 seconds if market is open
    const interval = setInterval(() => {
      if (marketStatus?.is_open) {
        fetchData();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [marketStatus?.is_open, fetchData]);

  const groupedData: GroupedData = tickerData.reduce((acc, item) => {
    const category = item.metal || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {} as GroupedData);

  const getCategoryName = (category: string) => {
    return category; // Use the metal name directly
  };

  const formatPrice = (price?: number) => {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatChange = (change?: number, changePct?: number) => {
    if (change === undefined || changePct === undefined) return null;
    
    const isPositive = change >= 0;
    const color = isPositive ? 'text-green-600' : 'text-red-600';
    const Icon = isPositive ? ArrowUpIcon : ArrowDownIcon;
    
    return (
      <div className={`flex items-center gap-1 ${color}`}>
        <Icon className="h-4 w-4" />
        <span>{Math.abs(change).toFixed(2)}</span>
        <span className="text-sm">({Math.abs(changePct).toFixed(2)}%)</span>
      </div>
    );
  };

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatMarketTime = (dateString?: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  // Prepare price distribution chart
  const priceDistributionData = tickerData.length > 0 ? {
    x: tickerData.map(item => item.description || item.ticker),
    y: tickerData.map(item => item.px_last || 0),
    type: 'bar' as const,
    name: 'Current Prices',
    marker: {
      color: tickerData.map(item => {
        const change = item.change || 0;
        return change >= 0 ? '#10B981' : '#EF4444';
      })
    }
  } : null;

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-pulse mx-auto mb-4" />
            <p className="text-gray-600">Loading market data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6">
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Metals Dashboard</h1>
          </div>

          {/* Bloomberg Status */}
          <BloombergStatus onStatusChange={handleDataSourceChange} />
        </div>
      </div>

      {/* Market Status */}
      {marketStatus && (
        <div className={`rounded-lg border p-4 ${
          marketStatus.is_open 
            ? 'border-green-200 bg-green-50' 
            : 'border-red-200 bg-red-50'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full animate-pulse ${
                marketStatus.is_open ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <div>
                <h3 className="font-semibold">{marketStatus.message}</h3>
                <p className="text-sm text-gray-600">{marketStatus.trading_hours}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Current Time</p>
              <p className="font-medium">{formatMarketTime(marketStatus.current_time)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Current Prices Chart */}
      {priceDistributionData && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Current Prices</h2>
          </div>
          <Plot
            data={[priceDistributionData]}
            layout={{
              xaxis: { title: { text: 'Metals' } },
              yaxis: { title: { text: 'Price (USD)' } },
              height: 400,
              margin: { t: 20, r: 20, b: 80, l: 60 },
              plot_bgcolor: 'rgba(0,0,0,0)',
              paper_bgcolor: 'rgba(0,0,0,0)',
              showlegend: false,
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
      )}

      {/* Metals Data Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Live Metals Prices</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metal
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
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(groupedData).map(([category, items]) => (
                <React.Fragment key={category}>
                  <tr className="bg-gray-100">
                    <td colSpan={5} className="px-6 py-2 text-sm font-medium text-gray-700">
                      {getCategoryName(category)}
                    </td>
                  </tr>
                  {items.map((item, index) => (
                    <tr key={`${category}-${index}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className={`w-2 h-2 rounded-full mr-3 ${
                            item.is_live ? 'bg-green-500' : 'bg-gray-400'
                          }`} />
                          <div className="font-medium text-gray-900">{item.metal}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{item.description}</div>
                        <div className="text-sm text-gray-500">{item.bloomberg_symbol}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-lg font-medium">{formatPrice(item.px_last)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        {formatChange(item.change, item.change_pct)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                        {formatTimestamp(item.timestamp)}
                      </td>
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {tickerData.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No market data available</p>
          </div>
        )}
      </div>

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default Home; 