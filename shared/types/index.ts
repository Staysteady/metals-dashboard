export interface MetalPrice {
  metal: string;
  price: number;
  currency: string;
  timestamp: Date;
  change?: number;
  changePercent?: number;
}

export interface HistoricalPrice {
  date: Date;
  price: number;
}

export interface MetalHistoricalData {
  metal: string;
  prices: HistoricalPrice[];
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  timestamp: Date;
}

export type MetalType = 'GOLD' | 'SILVER' | 'PLATINUM' | 'PALLADIUM' | 'COPPER';

export interface DashboardData {
  latestPrices: MetalPrice[];
  lastUpdated: Date;
} 