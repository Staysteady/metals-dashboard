// Product categories for metals
export enum ProductCategory {
  AH = "AH", // Aluminum
  CA = "CA", // Copper
  ZN = "ZN", // Zinc
  PB = "PB", // Lead
  NI = "NI", // Nickel
  SN = "SN", // Tin
  ALL = "ALL", // All metals
}

// Base ticker interface
export interface Ticker {
  id: number;
  symbol: string;
  description: string;
  product_category: ProductCategory;
  is_custom: boolean;
  created_at: string;
  updated_at?: string;
}

// Price data interface
export interface PriceData {
  ticker_id: number;
  symbol: string;
  date: string;
  px_last: number;
  px_open?: number;
  px_high?: number;
  px_low?: number;
  px_volume?: number;
}

// Price data response
export interface PriceDataResponse {
  ticker: Ticker;
  prices: PriceData[];
  total_records: number;
}

// Latest price data with calculated fields
export interface LatestPrice {
  ticker_id: number;
  symbol: string;
  description: string;
  product_category: ProductCategory;
  px_last?: number;
  date?: string;
  px_open?: number;
  px_high?: number;
  px_low?: number;
  change: number;
  change_pct: number;
}

// Ticker creation/update interfaces
export interface TickerCreate {
  symbol: string;
  description: string;
  product_category: ProductCategory;
  is_custom?: boolean;
}

export interface TickerUpdate {
  description?: string;
  product_category?: ProductCategory;
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Health check response
export interface HealthCheck {
  status: string;
  service: string;
  database: {
    status: string;
    message: string;
    details?: {
      tables: number;
      tickers: number;
      price_records: number;
      database_path: string;
    };
  };
}

// Chart data types
export interface ChartDataPoint {
  x: string | Date;
  y: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
}

export interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  type: 'line' | 'candlestick' | 'bar';
  color?: string;
}

// Settings types
export enum Theme {
  LIGHT = "light",
  DARK = "dark",
}

export interface Settings {
  id: number;
  use_dummy_data: boolean;
  polling_interval_minutes: number;
  theme: Theme;
  database_path: string;
} 