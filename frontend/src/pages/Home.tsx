import React, { useEffect, useState, useCallback } from 'react';
import { ArrowUpIcon, ArrowDownIcon, TrendingUp, Activity, BarChart3 } from 'lucide-react';
import Plot from 'react-plotly.js';
import { api, type TickerData, type MarketStatus, type HistoricalData } from '../api/client';
import BloombergStatus from '../components/DataSourceToggle';

interface GroupedData {
  [category: string]: TickerData[];
}

const Home: React.FC = () => {
  const [tickerData, setTickerData] = useState<TickerData[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [includePrecious, setIncludePrecious] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('LMCADS03'); // Default to Copper

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [pricesData, statusData] = await Promise.all([
        api.getLatestPrices(includePrecious),
        api.getMarketStatus()
      ]);
      setTickerData(pricesData);
      setMarketStatus(statusData);
      
      // Fetch historical data for the selected symbol
      if (selectedSymbol) {
        const historical = await api.getHistoricalPrices(selectedSymbol);
        setHistoricalData(historical);
      }
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
  }, [includePrecious, selectedSymbol]);

  const handleDataSourceChange = useCallback(() => {
    setLoading(true);
    fetchData();
  }, [fetchData]);

  const handleSymbolChange = useCallback(async (symbol: string) => {
    setSelectedSymbol(symbol);
    try {
      const historical = await api.getHistoricalPrices(symbol);
      setHistoricalData(historical);
    } catch (err) {
      console.error('Error fetching historical data:', err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    
    // Refresh data every 30 seconds if market is open
    const interval = setInterval(() => {
      if (marketStatus?.is_open) {
        fetchData();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [includePrecious, marketStatus?.is_open, fetchData]);

  const groupedData: GroupedData = tickerData.reduce((acc, item) => {
    const category = item.product_category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {} as GroupedData);

  const getCategoryName = (category: string) => {
    const names: { [key: string]: string } = {
      CA: 'Copper',
      AH: 'Aluminum',
      ZN: 'Zinc',
      PB: 'Lead',
      SN: 'Tin',
      NI: 'Nickel',
      PM: 'Precious Metals'
    };
    return names[category] || category;
  };

  const formatPrice = (price: number) => {
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

  // Prepare chart data
  const priceChartData = historicalData ? {
    x: historicalData.data_points.map(point => point.date),
    y: historicalData.data_points.map(point => point.price),
    type: 'scatter' as const,
    mode: 'lines' as const,
    name: `${selectedSymbol} Price History`,
    line: { color: '#3B82F6', width: 2 }
  } : null;

  // Prepare price distribution chart
  const priceDistributionData = tickerData.length > 0 ? {
    x: tickerData.map(item => item.description || item.symbol),
    y: tickerData.map(item => item.px_last),
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
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <TrendingUp className="h-8 w-8 text-blue-600" />
          Metals Trading Dashboard
        </h1>
        
        {/* Market Status Banner */}
        {marketStatus && (
          <div className={`rounded-lg p-3 mb-4 ${
            marketStatus.is_open ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full animate-pulse ${
                  marketStatus.is_open ? 'bg-green-500' : 'bg-gray-400'
                }`} />
                <span className="font-medium">{marketStatus.message}</span>
              </div>
              <div className="text-sm text-gray-600">
                {marketStatus.is_open && marketStatus.next_close && (
                  <span>Closes at {formatMarketTime(marketStatus.next_close)}</span>
                )}
                {!marketStatus.is_open && marketStatus.next_open && (
                  <span>Opens at {formatMarketTime(marketStatus.next_open)}</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Data Source Toggle */}
        <BloombergStatus onDataSourceChange={handleDataSourceChange} />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Historical Price Chart */}
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Price History
            </h3>
            <select
              value={selectedSymbol}
              onChange={(e) => handleSymbolChange(e.target.value)}
              className="px-3 py-1 border rounded-md text-sm"
            >
              {tickerData.map((ticker) => (
                <option key={ticker.symbol} value={ticker.symbol}>
                  {ticker.description || ticker.symbol}
                </option>
              ))}
            </select>
          </div>
          {priceChartData ? (
            <Plot
              data={[priceChartData]}
              layout={{
                autosize: true,
                margin: { l: 40, r: 40, t: 20, b: 40 },
                xaxis: { title: { text: 'Date' } },
                yaxis: { title: { text: 'Price (USD)' } },
                showlegend: false
              }}
              style={{ width: '100%', height: '300px' }}
              config={{ responsive: true, displayModeBar: false }}
            />
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              Loading chart data...
            </div>
          )}
        </div>

        {/* Price Distribution Chart */}
        <div className="bg-white rounded-lg border p-4">
          <h3 className="text-lg font-semibold mb-4">Current Prices</h3>
          {priceDistributionData ? (
            <Plot
              data={[priceDistributionData]}
              layout={{
                autosize: true,
                margin: { l: 40, r: 40, t: 20, b: 80 },
                xaxis: { 
                  title: { text: 'Metals' },
                  tickangle: -45
                },
                yaxis: { title: { text: 'Price (USD)' } },
                showlegend: false
              }}
              style={{ width: '100%', height: '300px' }}
              config={{ responsive: true, displayModeBar: false }}
            />
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              Loading chart data...
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4 mb-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={includePrecious}
            onChange={(e) => setIncludePrecious(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />
          <span>Include Precious Metals</span>
        </label>
        <span className="text-sm text-gray-500">
          Last updated: {formatTimestamp(tickerData[0]?.timestamp)}
        </span>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-900">Metal</th>
                <th className="px-4 py-3 text-right font-medium text-gray-900">Price</th>
                <th className="px-4 py-3 text-right font-medium text-gray-900">Change</th>
                <th className="px-4 py-3 text-right font-medium text-gray-900">Last Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {Object.entries(groupedData).map(([category, items]) => (
                <React.Fragment key={category}>
                  <tr className="bg-gray-25">
                    <td colSpan={4} className="px-4 py-2 font-medium text-gray-700 bg-gray-50">
                      {getCategoryName(category)}
                    </td>
                  </tr>
                  {items.map((item) => (
                    <tr key={item.symbol} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div>
                          <div className="font-medium text-gray-900">
                            {item.description || item.symbol}
                          </div>
                          <div className="text-sm text-gray-500">{item.symbol}</div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right font-medium">
                        {formatPrice(item.px_last)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {formatChange(item.change, item.change_pct)}
                      </td>
                      <td className="px-4 py-3 text-right text-sm text-gray-500">
                        {formatTimestamp(item.timestamp)}
                      </td>
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Home; 