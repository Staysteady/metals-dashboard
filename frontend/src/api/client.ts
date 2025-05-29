import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export interface Ticker {
  id: number;
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

export interface MarketStatus {
  is_open: boolean;
  exchange: string;
  current_time: string;
  message: string;
  trading_hours: string;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
  environment: {
    python_version: string;
    platform: string;
  };
  bloomberg: {
    bloomberg_available: boolean;
    is_connected: boolean;
    status: string;
    message: string;
  };
  mode: string;
}

export const getLMETickers = async (includeLivePrices = true): Promise<Ticker[]> => {
  const response = await apiClient.get(`/lme/tickers?include_live_prices=${includeLivePrices}`);
  return response.data;
};

export const getMarketStatus = async (): Promise<MarketStatus> => {
  const response = await apiClient.get('/lme/market-status');
  return response.data;
};

export const getHealthStatus = async (): Promise<HealthStatus> => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const addTicker = async (bloombergSymbol: string, description?: string): Promise<any> => {
  const response = await apiClient.post('/lme/tickers/add', {
    bloomberg_symbol: bloombergSymbol,
    description,
  });
  return response.data;
};

export const deleteTicker = async (tickerId: number): Promise<any> => {
  const response = await apiClient.delete(`/lme/tickers/${tickerId}`);
  return response.data;
};

export default apiClient; 