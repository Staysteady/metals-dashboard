import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import Home from './Home';
import { server } from '../test/mocks/server';
import { errorHandlers } from '../test/mocks/handlers';

// Mock Plotly to avoid rendering issues in tests
vi.mock('react-plotly.js', () => ({
  default: ({ data, layout }: { data: unknown; layout: unknown }) => (
    <div data-testid="plotly-chart">
      <div data-testid="chart-data">{JSON.stringify(data)}</div>
      <div data-testid="chart-layout">{JSON.stringify(layout)}</div>
    </div>
  ),
}));

describe('Home', () => {
  it('displays loading state initially', () => {
    render(<Home />);
    expect(screen.getByText(/loading market data/i)).toBeInTheDocument();
  });

  it('displays metal prices and charts after loading', async () => {
    render(<Home />);
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });

    // Check that metals are displayed in the table - use getAllByText to handle duplicates
    const copperTexts = screen.getAllByText('LME Copper 3M');
    expect(copperTexts.length).toBeGreaterThan(0);
    
    const aluminumTexts = screen.getAllByText('LME Aluminum 3M');
    expect(aluminumTexts.length).toBeGreaterThan(0);
    
    const zincTexts = screen.getAllByText('LME Zinc 3M');
    expect(zincTexts.length).toBeGreaterThan(0);
    
    // Check prices are formatted correctly
    expect(screen.getByText('$8,500.50')).toBeInTheDocument();
    expect(screen.getByText('$2,200.75')).toBeInTheDocument();
    expect(screen.getByText('$2,800.00')).toBeInTheDocument();

    // Check that charts are rendered
    const charts = screen.getAllByTestId('plotly-chart');
    expect(charts).toHaveLength(2); // Price history and current prices charts
  });

  it('displays market status with visual indicators', async () => {
    render(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('Market open')).toBeInTheDocument();
    });
    
    // Check for market status indicator - look for the container with green-50 background
    const statusContainer = screen.getByText('Market open').closest('div')?.parentElement?.parentElement;
    expect(statusContainer).toHaveClass('bg-green-50');
    
    // Check for animated pulse indicator
    const pulseIndicator = statusContainer?.querySelector('.animate-pulse');
    expect(pulseIndicator).toBeInTheDocument();
    expect(pulseIndicator).toHaveClass('bg-green-500');
  });

  it('shows precious metals when toggled', async () => {
    const user = userEvent.setup();
    render(<Home />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Initially no precious metals in the table
    const tableElement = screen.getByRole('table');
    expect(within(tableElement).queryByText('Gold Spot')).not.toBeInTheDocument();
    
    // Toggle precious metals
    const checkbox = screen.getByRole('checkbox', { name: /include precious metals/i });
    await user.click(checkbox);
    
    // Wait for precious metals to appear in the table
    await waitFor(() => {
      expect(within(tableElement).getByText('Gold Spot')).toBeInTheDocument();
    });
    
    expect(screen.getByText('$2,050.00')).toBeInTheDocument();
  });

  it('allows switching between different symbols for historical chart', async () => {
    const user = userEvent.setup();
    render(<Home />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Find the symbol selector dropdown
    const symbolSelect = screen.getByDisplayValue('LME Copper 3M');
    expect(symbolSelect).toBeInTheDocument();
    
    // Change to Aluminum
    await user.selectOptions(symbolSelect, 'LMAHDS03');
    
    // Verify the selection changed
    expect(screen.getByDisplayValue('LME Aluminum 3M')).toBeInTheDocument();
  });

  it('displays price changes with correct formatting and colors', async () => {
    render(<Home />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Get the table to search within it specifically
    const tableElement = screen.getByRole('table');
    
    // Check positive change (Copper) - look for the tbody specifically
    const tableBody = tableElement.querySelector('tbody');
    if (!tableBody) throw new Error('Table body not found');
    
    const copperRows = within(tableBody).getAllByText('LME Copper 3M');
    const copperRow = copperRows[0].closest('tr');
    
    if (copperRow) {
      const changeCell = within(copperRow).getByText(/25.30/);
      expect(changeCell.closest('div')).toHaveClass('text-green-600');
      expect(within(copperRow).getByText('(0.30%)')).toBeInTheDocument();
    }
    
    // Check negative change (Aluminum)
    const aluminumRows = within(tableBody).getAllByText('LME Aluminum 3M');
    const aluminumRow = aluminumRows[0].closest('tr');
    
    if (aluminumRow) {
      const changeCell = within(aluminumRow).getByText(/15.25/);
      expect(changeCell.closest('div')).toHaveClass('text-red-600');
      expect(within(aluminumRow).getByText('(0.69%)')).toBeInTheDocument();
    }
  });

  it('groups metals by category in the table', async () => {
    render(<Home />);
    
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
    
    render(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch market data/i)).toBeInTheDocument();
    });
    
    // Check error styling
    const errorDiv = screen.getByText(/failed to fetch market data/i).closest('div');
    expect(errorDiv).toHaveClass('border-red-200', 'bg-red-50');
  });

  it('shows last updated timestamp', async () => {
    render(<Home />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Check for timestamp
    expect(screen.getByText(/last updated:/i)).toBeInTheDocument();
  });

  it('displays chart titles and controls', async () => {
    render(<Home />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Check for chart section headers
    expect(screen.getByText('Price History')).toBeInTheDocument();
    expect(screen.getByText('Current Prices')).toBeInTheDocument();
    
    // Check for chart icons
    expect(screen.getByText('Price History').parentElement?.querySelector('svg')).toBeInTheDocument();
  });

  it('includes data source toggle component', async () => {
    render(<Home />);
    
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Check for data source toggle
    expect(screen.getByText('Data Source')).toBeInTheDocument();
    expect(screen.getByText('Dummy Data')).toBeInTheDocument();
    expect(screen.getByText('Bloomberg')).toBeInTheDocument();
  });

  it('displays dashboard header with icon', async () => {
    render(<Home />);
    
    // Wait for the component to fully load
    await waitFor(() => {
      expect(screen.queryByText(/loading market data/i)).not.toBeInTheDocument();
    });
    
    // Check for main title with icon
    const title = screen.getByText('Metals Trading Dashboard');
    expect(title).toBeInTheDocument();
    expect(title.parentElement?.querySelector('svg')).toBeInTheDocument();
  });
}); 