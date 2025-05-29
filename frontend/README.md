# Frontend - Metals Dashboard

React + TypeScript + Vite frontend for the Metals Trading Dashboard with real-time Bloomberg data integration.

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v18 or higher)
- **npm** or **yarn**

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Setup (Optional)
Create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Metals Dashboard
VITE_UPDATE_INTERVAL=30000
```

### 3. Run Development Server
```bash
npm run dev
```

The application will be available at: http://localhost:5173

## 🗂️ Project Structure

```
frontend/
├── src/
│   ├── App.tsx                    # Main application component
│   ├── main.tsx                   # Application entry point
│   ├── pages/                     # Page components
│   │   ├── Home.tsx              # Dashboard with charts and data
│   │   └── Portfolio.tsx         # Portfolio management page
│   ├── components/               # Reusable UI components
│   │   ├── Layout.tsx           # Application layout wrapper
│   │   ├── BloombergStatus.tsx  # Bloomberg connection status
│   │   ├── charts/              # Chart components
│   │   │   ├── PriceHistoryChart.tsx
│   │   │   ├── CurrentPricesChart.tsx
│   │   │   └── PortfolioChart.tsx
│   │   ├── tables/              # Table components
│   │   │   └── MetalsDataTable.tsx
│   │   └── ui/                  # shadcn/ui components
│   ├── services/                # API service layer
│   │   ├── api.ts              # Main API client
│   │   ├── lmeService.ts       # LME data service
│   │   └── types.ts            # API response types
│   ├── types/                  # TypeScript type definitions
│   │   ├── metals.ts           # Metals data types
│   │   └── api.ts              # API types
│   ├── hooks/                  # Custom React hooks
│   │   ├── useMetalsData.ts    # Metals data fetching hook
│   │   └── useMarketStatus.ts  # Market status hook
│   ├── utils/                  # Utility functions
│   │   ├── formatters.ts       # Data formatting utilities
│   │   └── constants.ts        # Application constants
│   └── styles/                 # Global styles
│       └── globals.css         # Tailwind CSS and global styles
├── public/                     # Static assets
├── package.json               # Dependencies and scripts
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── eslint.config.js          # ESLint configuration
└── README.md                 # This file
```

## 🔧 Available Scripts

### Development
```bash
npm run dev          # Start development server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build locally
```

### Testing
```bash
npm test             # Run tests in watch mode
npm run test:coverage # Run tests with coverage report
npm run test:ci      # Run tests once (CI mode)
```

### Code Quality
```bash
npm run lint         # Check for linting errors
npm run lint:fix     # Fix auto-fixable linting errors
npm run format       # Format code with Prettier
npm run format:check # Check if code is properly formatted
npm run type-check   # Run TypeScript type checking
```

## 🎨 Key Components

### Pages

#### Home.tsx
- **Main dashboard** with real-time metals data
- **Interactive charts** using Plotly.js
- **Data table** with sortable columns
- **Market status indicators**
- **Bloomberg connection status**

#### Portfolio.tsx
- **Portfolio overview** with holdings
- **Performance charts**
- **P&L calculations**
- **Asset allocation visualization**

### Components

#### Layout.tsx
- **Navigation wrapper** for all pages
- **Responsive design** for mobile and desktop
- **Common header and footer**

#### BloombergStatus.tsx
- **Bloomberg connection status indicator**
- **Visual indicators** for current connection state
- **Real-time status updates**

#### Charts
- **PriceHistoryChart.tsx** - Historical price trends
- **CurrentPricesChart.tsx** - Current price distribution
- **PortfolioChart.tsx** - Portfolio performance

### Services

#### api.ts
```typescript
// Main API client with axios
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
});
```

#### lmeService.ts
```typescript
// LME-specific API calls
export const getLMETickers = async (includeLivePrices = false) => {
  // Fetch LME tickers with optional live prices
};

export const getMarketStatus = async () => {
  // Get current market status
};
```

## 🔧 Configuration

### Environment Variables
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Metals Dashboard

# Feature Flags
VITE_UPDATE_INTERVAL=30000

# Development
VITE_DEBUG=false
```

### Vite Configuration
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
});
```

## 📊 Data Flow

### Real-time Updates
1. **Initial Load** - Fetch tickers and market status
2. **Polling** - Update data every 30 seconds when market is open
3. **Error Handling** - Graceful fallback to cached data
4. **User Interactions** - Add/remove tickers, view Bloomberg status

### State Management
- **React State** for component-level state
- **Custom hooks** for data fetching and caching
- **Context API** for global state (market status, Bloomberg connection)

## 🎨 Styling

### Tailwind CSS
- **Utility-first** CSS framework
- **Responsive design** with mobile-first approach
- **Custom theme** for metals dashboard colors

### shadcn/ui Components
- **High-quality** pre-built components
- **Accessible** and keyboard navigable
- **Customizable** with CSS variables

## 📈 Charts & Visualization

### Plotly.js Integration
```typescript
import Plot from 'react-plotly.js';

// Price history chart
<Plot
  data={[{
    x: dates,
    y: prices,
    type: 'scatter',
    mode: 'lines',
    name: selectedSymbol
  }]}
  layout={{
    title: 'Price History',
    xaxis: { title: 'Date' },
    yaxis: { title: 'Price (USD)' }
  }}
/>
```

### Chart Types
- **Line Charts** - Price history and trends
- **Bar Charts** - Current price comparison
- **Pie Charts** - Portfolio allocation
- **Scatter Plots** - Price correlation analysis

## 🧪 Testing

### Test Structure
```
src/
├── __tests__/              # Test files
│   ├── components/        # Component tests
│   ├── pages/            # Page tests
│   ├── services/         # Service tests
│   └── utils/            # Utility tests
├── __mocks__/             # Mock implementations
└── test-utils.tsx         # Testing utilities
```

### Testing Libraries
- **Jest** - Test runner and assertions
- **React Testing Library** - Component testing
- **MSW** - API mocking for tests
- **@testing-library/user-event** - User interaction testing

### Example Test
```typescript
import { render, screen } from '@testing-library/react';
import { Home } from '../pages/Home';

test('renders metals dashboard', async () => {
  render(<Home />);
  
  // Check for main elements
  expect(screen.getByText('Metals Dashboard')).toBeInTheDocument();
  expect(screen.getByText('Market Status')).toBeInTheDocument();
  
  // Wait for data to load
  await screen.findByText('Gold');
  expect(screen.getByText('Silver')).toBeInTheDocument();
});
```

## 🔍 Troubleshooting

### Common Issues

#### 1. API Connection Failed
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify environment variables
echo $VITE_API_BASE_URL
```

#### 2. Charts Not Loading
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 3. TypeScript Errors
```bash
# Run type checking
npm run type-check

# Clear TypeScript cache
rm -rf node_modules/.cache
```

#### 4. Hot Reload Not Working
```bash
# Restart development server
npm run dev

# Check for port conflicts
lsof -i :5173  # macOS/Linux
netstat -ano | findstr :5173  # Windows
```

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Preview Build
```bash
npm run preview
```

### Deploy to Static Hosting
```bash
# Build files will be in dist/
# Upload dist/ folder to your hosting provider
```

## 📱 Mobile Responsiveness

### Breakpoints
- **sm**: 640px and up
- **md**: 768px and up  
- **lg**: 1024px and up
- **xl**: 1280px and up

### Mobile Features
- **Touch-friendly** chart interactions
- **Responsive tables** with horizontal scroll
- **Mobile navigation** with collapsible menu
- **Optimized performance** for mobile devices

## 🔧 Development Tips

### Hot Reload
- Changes are reflected immediately
- State is preserved when possible
- Error overlay shows compilation errors

### Debugging
- Use browser DevTools for debugging
- React DevTools extension for component inspection
- Network tab for API request debugging

### Performance
- Charts are memoized to prevent unnecessary re-renders
- API calls are debounced and cached
- Images and assets are optimized

---

**🔗 Repository**: https://github.com/Staysteady/metals-dashboard.git  
**📖 Main README**: [../README.md](../README.md)  
**🚀 Backend**: [../backend/README.md](../backend/README.md)