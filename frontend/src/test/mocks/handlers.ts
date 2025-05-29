import { http, HttpResponse } from 'msw';

export const handlers = [
  // Health check endpoint
  http.get('/api/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      environment: {
        python_version: '3.12.0',
        platform: 'Windows',
      },
      bloomberg: {
        bloomberg_available: true,
        is_connected: true,
        status: 'connected',
        message: 'Connected to Bloomberg Terminal'
      },
      mode: 'live_bloomberg_only',
    });
  }),

  // LME tickers endpoint
  http.get('/api/lme/tickers', () => {
    return HttpResponse.json([
      {
        id: 1,
        ticker: 'LMCADS03',
        description: 'Copper 3 Month',
        metal: 'Copper',
        symbol: 'CA',
        bloomberg_symbol: 'LMCADS03 COMDTY',
        px_last: 9568.0,
        change: 45.5,
        change_pct: 0.48,
        timestamp: new Date().toISOString(),
        is_live: true,
      },
      {
        id: 2,
        ticker: 'LMAHDS03',
        description: 'Aluminum 3 Month',
        metal: 'Aluminum',
        symbol: 'AH',
        bloomberg_symbol: 'LMAHDS03 COMDTY',
        px_last: 2450.5,
        change: -12.0,
        change_pct: -0.49,
        timestamp: new Date().toISOString(),
        is_live: true,
      },
    ]);
  }),

  // Market status endpoint
  http.get('/api/lme/market-status', () => {
    return HttpResponse.json({
      is_open: true,
      exchange: 'LME',
      current_time: new Date().toISOString(),
      message: 'LME Market Open',
      trading_hours: '01:00-19:00 GMT (Mon-Fri)',
    });
  }),

  // Add ticker endpoint
  http.post('/api/lme/tickers/add', () => {
    return HttpResponse.json({
      status: 'success',
      message: 'Successfully added ticker',
      ticker_id: '3',
    });
  }),

  // Delete ticker endpoint
  http.delete('/api/lme/tickers/:id', () => {
    return HttpResponse.json({
      status: 'success',
      message: 'Ticker deleted successfully',
    });
  }),
]; 