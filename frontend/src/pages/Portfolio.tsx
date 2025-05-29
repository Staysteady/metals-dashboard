import React from 'react';
import { Briefcase, TrendingUp, DollarSign, PieChart } from 'lucide-react';
import Plot from 'react-plotly.js';

const Portfolio: React.FC = () => {
  // Mock portfolio data
  const portfolioData = [
    { symbol: 'LMCADS03', description: 'LME Copper 3M', quantity: 100, avgPrice: 8450.00, currentPrice: 8500.50 },
    { symbol: 'LMAHDS03', description: 'LME Aluminum 3M', quantity: 200, avgPrice: 2220.00, currentPrice: 2200.75 },
    { symbol: 'XAU=', description: 'Gold Spot', quantity: 10, avgPrice: 2035.00, currentPrice: 2050.00 },
  ];

  const totalValue = portfolioData.reduce((sum, item) => sum + (item.quantity * item.currentPrice), 0);
  const totalGainLoss = portfolioData.reduce((sum, item) => sum + (item.quantity * (item.currentPrice - item.avgPrice)), 0);

  // Portfolio allocation chart data
  const allocationData = {
    values: portfolioData.map(item => item.quantity * item.currentPrice),
    labels: portfolioData.map(item => item.description),
    type: 'pie' as const,
    hole: 0.4,
    marker: {
      colors: ['#3B82F6', '#10B981', '#F59E0B']
    }
  };

  // Performance chart data (mock data)
  const performanceData = {
    x: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    y: [485000, 492000, 478000, 501000, totalValue],
    type: 'scatter' as const,
    mode: 'lines+markers' as const,
    name: 'Portfolio Value',
    line: { color: '#3B82F6', width: 3 }
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Briefcase className="h-8 w-8 text-blue-600" />
          Tickers & Portfolio
        </h1>
        <p className="text-gray-600">Your metals trading portfolio performance and ticker information</p>
      </div>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-gray-900">${totalValue.toLocaleString()}</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Gain/Loss</p>
              <p className={`text-2xl font-bold ${totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalGainLoss >= 0 ? '+' : ''}${totalGainLoss.toLocaleString()}
              </p>
            </div>
            <TrendingUp className={`h-8 w-8 ${totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`} />
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Return %</p>
              <p className={`text-2xl font-bold ${totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {((totalGainLoss / (totalValue - totalGainLoss)) * 100).toFixed(2)}%
              </p>
            </div>
            <PieChart className={`h-8 w-8 ${totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`} />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Portfolio Allocation */}
        <div className="bg-white rounded-lg border p-4">
          <h3 className="text-lg font-semibold mb-4">Portfolio Allocation</h3>
          <Plot
            data={[allocationData]}
            layout={{
              autosize: true,
              margin: { l: 20, r: 20, t: 20, b: 20 },
              showlegend: true,
              legend: { orientation: 'h', y: -0.1 }
            }}
            style={{ width: '100%', height: '300px' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>

        {/* Performance Chart */}
        <div className="bg-white rounded-lg border p-4">
          <h3 className="text-lg font-semibold mb-4">Portfolio Performance</h3>
          <Plot
            data={[performanceData]}
            layout={{
              autosize: true,
              margin: { l: 40, r: 40, t: 20, b: 40 },
              xaxis: { title: { text: 'Month' } },
              yaxis: { title: { text: 'Value (USD)' } },
              showlegend: false
            }}
            style={{ width: '100%', height: '300px' }}
            config={{ responsive: true, displayModeBar: false }}
          />
        </div>
      </div>

      {/* Holdings Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Holdings</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left font-medium text-gray-900">Asset</th>
                <th className="px-6 py-3 text-right font-medium text-gray-900">Quantity</th>
                <th className="px-6 py-3 text-right font-medium text-gray-900">Avg Price</th>
                <th className="px-6 py-3 text-right font-medium text-gray-900">Current Price</th>
                <th className="px-6 py-3 text-right font-medium text-gray-900">Market Value</th>
                <th className="px-6 py-3 text-right font-medium text-gray-900">Gain/Loss</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {portfolioData.map((item) => {
                const marketValue = item.quantity * item.currentPrice;
                const gainLoss = item.quantity * (item.currentPrice - item.avgPrice);
                const gainLossPercent = ((item.currentPrice - item.avgPrice) / item.avgPrice) * 100;

                return (
                  <tr key={item.symbol} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium text-gray-900">{item.description}</div>
                        <div className="text-sm text-gray-500">{item.symbol}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right font-medium">{item.quantity}</td>
                    <td className="px-6 py-4 text-right">${item.avgPrice.toFixed(2)}</td>
                    <td className="px-6 py-4 text-right">${item.currentPrice.toFixed(2)}</td>
                    <td className="px-6 py-4 text-right font-medium">${marketValue.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right">
                      <div className={`${gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        <div className="font-medium">
                          {gainLoss >= 0 ? '+' : ''}${gainLoss.toFixed(2)}
                        </div>
                        <div className="text-sm">
                          ({gainLoss >= 0 ? '+' : ''}{gainLossPercent.toFixed(2)}%)
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Portfolio; 