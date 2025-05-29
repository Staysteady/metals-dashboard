import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { http, HttpResponse } from 'msw'
import App from './App'
import { server } from './test/mocks/server'

// Mock Plotly to avoid rendering issues in tests
vi.mock('react-plotly.js', () => ({
  default: ({ data, layout }: { data: unknown; layout: unknown }) => (
    <div data-testid="plotly-chart">
      <div data-testid="chart-data">{JSON.stringify(data)}</div>
      <div data-testid="chart-layout">{JSON.stringify(layout)}</div>
    </div>
  ),
}));

describe('App', () => {
  it('renders metals dashboard title from Home component', async () => {
    render(<App />)
    
    // Wait for the Home component to load
    await waitFor(() => {
      const titleElement = screen.getByText(/Metals Trading Dashboard/i)
      expect(titleElement).toBeInTheDocument()
    })
  })

  it('displays no error message when API ping is successful', async () => {
    render(<App />)
    
    // Wait for the component to load and ensure no error message is shown
    await waitFor(() => {
      expect(screen.queryByText(/API Error: Could not connect/i)).not.toBeInTheDocument()
    })
  })

  it('displays error message when API call fails', async () => {
    // Override handler for this test
    server.use(
      http.get('http://localhost:8000/ping/', () => {
        return HttpResponse.error()
      })
    )

    render(<App />)
    
    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('API Error: Could not connect')).toBeInTheDocument()
    })
  })
}) 