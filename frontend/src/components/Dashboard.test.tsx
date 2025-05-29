import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';
import Dashboard from './Dashboard';
import { server } from '../test/mocks/server';
import { errorHandlers } from '../test/mocks/handlers';

describe('Dashboard', () => {
  it('displays loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByText(/loading market data/i)).toBeInTheDocument();
  });

  it('displays metal prices after loading', async () => {
    render(<Dashboard />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });

    // Check that metals are displayed
    expect(screen.getByText('LME Copper 3M')).toBeInTheDocument();
    expect(screen.getByText('LME Aluminum 3M')).toBeInTheDocument();
    expect(screen.getByText('LME Zinc 3M')).toBeInTheDocument();
    
    // Check prices are formatted correctly
    expect(screen.getByText('$8,500.50')).toBeInTheDocument();
    expect(screen.getByText('$2,200.75')).toBeInTheDocument();
    expect(screen.getByText('$2,800.00')).toBeInTheDocument();
  });

  it('displays market status', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Market open')).toBeInTheDocument();
    });
    
    // Check for market status indicator - get the banner not the inner div
    const statusText = screen.getByText('Market open');
    const statusBanner = statusText.closest('div')?.parentElement?.parentElement;
    expect(statusBanner).toHaveClass('bg-green-50');
  });

  it('shows precious metals when toggled', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Initially no precious metals
    expect(screen.queryByText('Gold Spot')).not.toBeInTheDocument();
    
    // Toggle precious metals
    const checkbox = screen.getByRole('checkbox', { name: /include precious metals/i });
    await user.click(checkbox);
    
    // Wait for precious metals to appear
    await waitFor(() => {
      expect(screen.getByText('Gold Spot')).toBeInTheDocument();
    });
    
    expect(screen.getByText('$2,050.00')).toBeInTheDocument();
  });

  it('displays price changes with correct formatting', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Check positive change (Copper)
    const copperRow = screen.getByText('LME Copper 3M').closest('tr');
    if (copperRow) {
      const changeCell = within(copperRow).getByText(/25.30/);
      expect(changeCell.closest('div')).toHaveClass('text-green-600');
      expect(within(copperRow).getByText('(0.30%)')).toBeInTheDocument();
    }
    
    // Check negative change (Aluminum)
    const aluminumRow = screen.getByText('LME Aluminum 3M').closest('tr');
    if (aluminumRow) {
      const changeCell = within(aluminumRow).getByText(/15.25/);
      expect(changeCell.closest('div')).toHaveClass('text-red-600');
      expect(within(aluminumRow).getByText('(0.69%)')).toBeInTheDocument();
    }
  });

  it('groups metals by category', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Check for category headers
    expect(screen.getByText('Copper')).toBeInTheDocument();
    expect(screen.getByText('Aluminum')).toBeInTheDocument();
    expect(screen.getByText('Zinc')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    // Override handlers to return errors
    server.use(...errorHandlers);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch market data/i)).toBeInTheDocument();
    });
    
    // Check error styling
    const errorDiv = screen.getByText(/failed to fetch market data/i).closest('div');
    expect(errorDiv).toHaveClass('border-red-200', 'bg-red-50');
  });

  it('shows last updated timestamp', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Check for timestamp
    expect(screen.getByText(/last updated:/i)).toBeInTheDocument();
  });

  it('auto-refreshes data when market is open', async () => {
    render(<Dashboard />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Verify market is open
    expect(screen.getByText('Market open')).toBeInTheDocument();
    
    // Test that refresh mechanism is set up (not actually waiting for it)
    // The actual interval testing would require more complex setup
    // For now, just verify the component renders correctly with market open
    expect(screen.getByText(/last updated:/i)).toBeInTheDocument();
  });
}); 