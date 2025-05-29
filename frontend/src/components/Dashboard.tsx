import React, { useEffect, useState, useCallback } from 'react';
import { ArrowUpIcon, ArrowDownIcon, TrendingUp, Activity } from 'lucide-react';
import { api, type TickerData, type MarketStatus } from '../api/client';
import BloombergStatus from './DataSourceToggle';

interface GroupedData {
  [category: string]: TickerData[];
}

const Dashboard: React.FC = () => {
  const [tickerData, setTickerData] = useState<TickerData[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [includePrecious, setIncludePrecious] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [pricesData, statusData] = await Promise.all([
        api.getLatestPrices(includePrecious),
        api.getMarketStatus()
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
  }, [includePrecious]);

  const handleDataSourceChange = useCallback(() => {
    setLoading(true);
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    fetchData();
    
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
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Metals Trading Dashboard</h1>
        
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

        <BloombergStatus onDataSourceChange={handleDataSourceChange} />

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
      </div>

      <div className="grid gap-6">
        {Object.entries(groupedData).map(([category, items]) => (
          <div key={category} className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6">
              <div className="mb-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  {getCategoryName(category)}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Real-time prices for {getCategoryName(category).toLowerCase()} contracts
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Symbol</th>
                      <th className="text-left py-2">Description</th>
                      <th className="text-right py-2">Price</th>
                      <th className="text-right py-2">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item) => (
                      <tr key={item.symbol} className="border-b hover:bg-gray-50">
                        <td className="py-3 font-mono text-sm">
                          <span className="inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium">
                            {item.symbol}
                          </span>
                        </td>
                        <td className="py-3">{item.description}</td>
                        <td className="py-3 text-right font-medium">
                          {formatPrice(item.px_last)}
                        </td>
                        <td className="py-3 text-right">
                          {formatChange(item.change, item.change_pct)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard; 