import { http, HttpResponse } from 'msw';
import type { TickerData, HistoricalData, MarketStatus } from '../../api/client';

// Base URL for API
const API_URL = 'http://localhost:8000';

// Mock data
export const mockTickerData: TickerData[] = [
  {
    symbol: 'LMCADS03',
    description: 'LME Copper 3M',
    product_category: 'CA',
    px_last: 8500.50,
    change: 25.30,
    change_pct: 0.30,
    timestamp: new Date().toISOString()
  },
  {
    symbol: 'LMAHDS03',
    description: 'LME Aluminum 3M',
    product_category: 'AH',
    px_last: 2200.75,
    change: -15.25,
    change_pct: -0.69,
    timestamp: new Date().toISOString()
  },
  {
    symbol: 'LMZSDS03',
    description: 'LME Zinc 3M',
    product_category: 'ZN',
    px_last: 2800.00,
    change: 12.50,
    change_pct: 0.45,
    timestamp: new Date().toISOString()
  }
];

export const mockMarketStatus: MarketStatus = {
  is_open: true,
  message: 'Market open',
  next_close: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString() // 5 hours from now
};

export const mockHistoricalData: HistoricalData = {
  symbol: 'LMCADS03',
  data_points: Array.from({ length: 30 }, (_, i) => ({
    date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    price: 8500 + Math.random() * 200 - 100
  })),
  start_date: new Date(Date.now() - 29 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0]
};

// Define handlers
export const handlers = [
  // Ping endpoint
  http.get(`${API_URL}/ping/`, () => {
    return HttpResponse.json({
      message: 'Hello from FastAPI!',
      status: 'ok'
    });
  }),

  // Health check
  http.get(`${API_URL}/health/`, () => {
    return HttpResponse.json({
      status: 'ok',
      database: { status: 'healthy' }
    });
  }),

  // Latest prices
  http.get(`${API_URL}/prices/latest`, ({ request }) => {
    const url = new URL(request.url);
    const includePrecious = url.searchParams.get('include_precious') === 'true';
    
    const data = [...mockTickerData];
    
    if (includePrecious) {
      data.push({
        symbol: 'XAU=',
        description: 'Gold Spot',
        product_category: 'PM',
        px_last: 2050.00,
        change: 15.00,
        change_pct: 0.74,
        timestamp: new Date().toISOString()
      });
    }
    
    return HttpResponse.json(data);
  }),

  // Market status
  http.get(`${API_URL}/prices/market-status`, () => {
    return HttpResponse.json(mockMarketStatus);
  }),

  // Historical prices
  http.get(`${API_URL}/prices/historical/:symbol`, ({ params }) => {
    const { symbol } = params;
    return HttpResponse.json({
      ...mockHistoricalData,
      symbol: symbol as string
    });
  }),

  // Available symbols
  http.get(`${API_URL}/prices/symbols`, () => {
    return HttpResponse.json({
      base_metals: [
        { symbol: 'LMCADS03', description: 'LME Copper 3M', category: 'CA' },
        { symbol: 'LMAHDS03', description: 'LME Aluminum 3M', category: 'AH' },
        { symbol: 'LMZSDS03', description: 'LME Zinc 3M', category: 'ZN' }
      ],
      precious_metals: [
        { symbol: 'XAU=', description: 'Gold Spot', category: 'PM' },
        { symbol: 'XAG=', description: 'Silver Spot', category: 'PM' }
      ]
    });
  }),

  // Settings - data source status
  http.get(`${API_URL}/settings/data-source-status`, () => {
    return HttpResponse.json({
      use_dummy_data: true,
      bloomberg_available: false,
      data_source: 'dummy_data',
      message: 'Using dummy data for development'
    });
  }),

  // Settings - update settings
  http.put(`${API_URL}/settings/`, () => {
    return HttpResponse.json({
      message: 'Settings updated successfully'
    });
  })
];

// Error handlers for testing error scenarios
export const errorHandlers = [
  http.get(`${API_URL}/prices/latest`, () => {
    return HttpResponse.error();
  }),
  
  http.get(`${API_URL}/prices/market-status`, () => {
    return HttpResponse.error();
  })
]; 