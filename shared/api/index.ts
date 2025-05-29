import { MetalPrice, MetalHistoricalData, ApiResponse } from '../types';

const API_BASE_URL = process.env.API_BASE_URL || '/api';

export async function fetchWithErrorHandling<T>(
  url: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json() as T;
    return {
      data,
      timestamp: new Date()
    };
  } catch (error) {
    return {
      data: null as any,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date()
    };
  }
}

export async function getLatestPrices(): Promise<ApiResponse<MetalPrice[]>> {
  return fetchWithErrorHandling<MetalPrice[]>(`${API_BASE_URL}/prices/latest`);
}

export async function getHistoricalPrices(
  metal: string,
  days: number = 30
): Promise<ApiResponse<MetalHistoricalData>> {
  return fetchWithErrorHandling<MetalHistoricalData>(
    `${API_BASE_URL}/prices/${metal}?days=${days}`
  );
}

export async function pingAPI(): Promise<ApiResponse<{ status: string }>> {
  return fetchWithErrorHandling<{ status: string }>(`${API_BASE_URL}/ping`);
} 