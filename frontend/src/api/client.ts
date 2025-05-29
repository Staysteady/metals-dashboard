import axios from 'axios';

// Create axios instance with base configuration
const API_BASE = import.meta.env.MODE === 'test' 
  ? 'http://localhost:8000'  // Use absolute URL in tests for MSW
  : '/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface HealthCheckResponse {
  message: string;
  status: string;
  database: {
    status: string;
  };
}

export interface TickerData {
  symbol: string;
  description: string;
  product_category: string;
  px_last: number;
  change: number;
  change_pct: number;
  timestamp: string;
}

export interface HistoricalData {
  symbol: string;
  data_points: Array<{
    date: string;
    price: number;
  }>;
  start_date: string;
  end_date: string;
}

export interface MarketStatus {
  is_open: boolean;
  message: string;
  next_close?: string;
  next_open?: string;
}

export interface SymbolInfo {
  symbol: string;
  description: string;
  category: string;
}

export interface AvailableSymbols {
  base_metals: SymbolInfo[];
  precious_metals: SymbolInfo[];
}

export interface SettingsResponse {
  use_dummy_data: boolean;
  bloomberg_available: boolean;
  bloomberg_connected: boolean;
}

export interface SettingsUpdate {
  use_dummy_data: boolean;
}

export interface DataSourceStatus {
  status: 'dummy' | 'bloomberg' | 'bloomberg_disconnected' | 'no_stream';
  message: string;
  use_dummy_data: boolean;
  bloomberg_available: boolean;
  bloomberg_connected: boolean;
}

// API methods
export const api = {
  // Health check
  async ping(): Promise<HealthCheckResponse> {
    const response = await apiClient.get<HealthCheckResponse>('/ping/');
    return response.data;
  },

  // Get health status
  async health(): Promise<HealthCheckResponse> {
    const response = await apiClient.get<HealthCheckResponse>('/health/');
    return response.data;
  },

  // Get latest prices
  async getLatestPrices(includePrecious: boolean = false, symbols?: string[]): Promise<TickerData[]> {
    const params = new URLSearchParams();
    if (includePrecious) params.append('include_precious', 'true');
    if (symbols && symbols.length > 0) {
      symbols.forEach(symbol => params.append('symbols', symbol));
    }
    
    const response = await apiClient.get<TickerData[]>('/prices/latest', { params });
    return response.data;
  },

  // Get historical prices
  async getHistoricalPrices(symbol: string, days: number = 30): Promise<HistoricalData> {
    const response = await apiClient.get<HistoricalData>(`/prices/historical/${symbol}`, {
      params: { days }
    });
    return response.data;
  },

  // Get market status
  async getMarketStatus(): Promise<MarketStatus> {
    const response = await apiClient.get<MarketStatus>('/prices/market-status');
    return response.data;
  },

  // Get available symbols
  async getAvailableSymbols(): Promise<AvailableSymbols> {
    const response = await apiClient.get<AvailableSymbols>('/prices/symbols');
    return response.data;
  },

  // Settings endpoints
  async getSettings(): Promise<SettingsResponse> {
    const response = await apiClient.get<SettingsResponse>('/settings/');
    return response.data;
  },

  async updateSettings(settings: SettingsUpdate): Promise<SettingsResponse> {
    const response = await apiClient.put<SettingsResponse>('/settings/', settings);
    return response.data;
  },

  async getDataSourceStatus(): Promise<DataSourceStatus> {
    const response = await apiClient.get<DataSourceStatus>('/settings/data-source-status');
    return response.data;
  }
};

export default apiClient; 