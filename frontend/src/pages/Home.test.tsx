import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { handlers } from '../test/mocks/handlers';
import Home from './Home';

// Setup MSW server
const server = setupServer(...handlers);

// Wrapper component for router context
const RouterWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('Home Page', () => {
  beforeEach(() => {
    server.listen();
  });

  afterEach(() => {
    server.resetHandlers();
    server.close();
  });

  it('renders the main dashboard elements', async () => {
    render(
      <RouterWrapper>
        <Home />
      </RouterWrapper>
    );

    // Check for main heading
    expect(screen.getByText('Metals Dashboard')).toBeInTheDocument();
    
    // Check for Bloomberg status component
    await waitFor(() => {
      expect(screen.getByText(/Bloomberg/)).toBeInTheDocument();
    });
  });

  it('displays market status', async () => {
    render(
      <RouterWrapper>
        <Home />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Market/)).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    render(
      <RouterWrapper>
        <Home />
      </RouterWrapper>
    );

    // Should show some loading indicator
    expect(screen.getByText(/Checking Bloomberg status/)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    server.use(
      http.get('/api/lme/tickers', () => {
        return HttpResponse.error();
      })
    );

    render(
      <RouterWrapper>
        <Home />
      </RouterWrapper>
    );

    await waitFor(() => {
      // Should handle error gracefully without crashing
      expect(screen.getByText('Metals Dashboard')).toBeInTheDocument();
    });
  });

  it('displays ticker data when loaded', async () => {
    render(
      <RouterWrapper>
        <Home />
      </RouterWrapper>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Copper')).toBeInTheDocument();
      expect(screen.getByText('Aluminum')).toBeInTheDocument();
    });
  });
}); 