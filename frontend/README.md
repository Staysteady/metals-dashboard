# Frontend - Metals Dashboard

React + TypeScript + Vite frontend for the Metals Trading Dashboard with real-time Bloomberg data integration.

## 🚀 Features

- **Single-Page Application** - Streamlined Bloomberg Live data interface
- **Real-time Price Updates** - Live metals prices with automatic refresh
- **Bloomberg Connection Status** - Visual indicator of Bloomberg Terminal connection
- **Professional UI** - Clean, trading-focused interface design
- **Type-Safe** - Full TypeScript implementation with strict type checking

## 🛠 Tech Stack

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type safety and enhanced developer experience
- **Vite** - Lightning-fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library
- **React Router** - Client-side routing

## 📋 Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org/)
- **npm** or **yarn** - Package manager
- **Running Backend** - FastAPI backend must be running on `localhost:8000`

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start development server
npm run dev
```

## 🔧 Environment Variables

Create `.env` file:
```env
# Application
VITE_APP_TITLE=Metals Dashboard
VITE_API_URL=http://localhost:8000

# Development
VITE_APP_ENV=development
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── App.tsx                 # Main application component
│   ├── main.tsx               # Application entry point
│   ├── pages/
│   │   └── Bloomberg.tsx      # Bloomberg Live page (main page)
│   ├── components/
│   │   ├── Layout.tsx         # Application layout wrapper
│   │   └── DataSourceToggle.tsx # Bloomberg status component
│   ├── api/
│   │   └── client.ts          # API client with axios
│   ├── types/
│   │   └── index.ts           # TypeScript type definitions
│   └── styles/
│       └── index.css          # Global styles with Tailwind
├── public/                     # Static assets
├── package.json               # Dependencies and scripts
├── vite.config.ts            # Vite configuration
├── tailwind.config.js        # Tailwind CSS configuration
└── tsconfig.json             # TypeScript configuration
```

## 🎯 Key Components

### Bloomberg.tsx
Main page component displaying:
- **Live Price Data** - Real-time metals prices from Bloomberg
- **Market Status** - Current market open/closed status
- **Price Updates** - Automatic refresh every 30 seconds
- **Error Handling** - Graceful error states and loading indicators

### Layout.tsx
Application shell providing:
- **Navigation** - Clean sidebar with Bloomberg page link
- **Responsive Design** - Mobile-friendly layout
- **Header** - Application title and branding

### DataSourceToggle.tsx
Bloomberg connection indicator showing:
- **Connection Status** - Live/Offline Bloomberg connection
- **Visual Feedback** - Color-coded status indicator
- **Refresh Button** - Manual data refresh capability

## 🔄 Data Flow

1. **API Client** (`client.ts`) makes requests to FastAPI backend
2. **Bloomberg Component** fetches live price data and market status
3. **Type-safe Interfaces** ensure data integrity throughout application
4. **Automatic Updates** refresh data every 30 seconds during market hours
5. **Error Boundaries** handle network failures gracefully

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Test Structure
- **Component Tests** - React Testing Library for UI components
- **API Tests** - Mock service layer testing
- **Type Tests** - TypeScript compilation verification
- **E2E Tests** - End-to-end user workflow testing

## 🎨 Styling

### Tailwind CSS
- **Utility-First** - Rapidly build custom designs
- **Responsive** - Mobile-first responsive design
- **Dark Mode Ready** - Prepared for dark theme implementation
- **Professional Palette** - Trading-appropriate color scheme

### Component Styling
```tsx
// Example: Professional price display
<div className="bg-white rounded-lg shadow-sm border border-gray-200">
  <div className="p-6">
    <h2 className="text-xl font-semibold text-gray-900">
      Live Metals Prices
    </h2>
    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* Price cards */}
    </div>
  </div>
</div>
```

## 📊 Performance

### Optimization Features
- **Code Splitting** - Lazy loading for optimal bundle size
- **Tree Shaking** - Remove unused code automatically
- **Asset Optimization** - Automatic image and asset optimization
- **Caching Strategy** - Intelligent API response caching

### Bundle Analysis
```bash
# Analyze bundle size
npm run build
npm run preview

# Bundle size breakdown
npm run analyze
```

## 🔧 Development

### Available Scripts

```bash
# Development
npm run dev              # Start dev server with hot reload
npm run build            # Production build
npm run preview          # Preview production build

# Testing
npm test                 # Run test suite
npm run test:coverage    # Test with coverage report
npm run test:watch       # Watch mode testing

# Code Quality
npm run lint             # ESLint checking
npm run lint:fix         # Auto-fix linting issues
npm run type-check       # TypeScript type checking

# Formatting
npm run format           # Prettier formatting
npm run format:check     # Check formatting
```

### Development Server
- **Port**: `5173` (default Vite port)
- **Hot Reload** - Instant updates during development
- **Error Overlay** - Clear error messages in browser
- **Network Access** - `--host` flag for network testing

## 🚀 Production Build

```bash
# Create production build
npm run build

# Preview production build locally
npm run preview

# Deploy static files from dist/ folder
```

### Build Output
```
dist/
├── index.html              # Entry HTML file
├── assets/
│   ├── index.css          # Bundled styles
│   └── index.js           # Bundled JavaScript
└── favicon.ico            # Application icon
```

## 🔗 API Integration

### Client Configuration
```typescript
// api/client.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Error Handling
```typescript
// Automatic error handling and retry logic
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors, timeouts, etc.
    return Promise.reject(error);
  }
);
```

## 🐛 Troubleshooting

### Common Issues

#### 1. API Connection Failed
```bash
# Check backend is running
curl http://localhost:8000/health/

# Verify environment variables
cat .env
```

#### 2. Build Fails
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
npm run build -- --force
```

#### 3. Types Not Found
```bash
# Restart TypeScript server in VS Code
# Ctrl+Shift+P > "TypeScript: Restart TS Server"

# Check tsconfig.json paths
npx tsc --noEmit
```

#### 4. Hot Reload Not Working
```bash
# Check if port 5173 is available
netstat -an | findstr 5173

# Restart dev server
npm run dev
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: `< 768px` - Single column layout
- **Tablet**: `768px - 1024px` - Two column layout  
- **Desktop**: `> 1024px` - Full multi-column layout

### Mobile Optimizations
- **Touch Targets** - Minimum 44px touch areas
- **Readable Text** - Minimum 16px font size
- **Navigation** - Collapsible sidebar menu
- **Performance** - Optimized for mobile networks

## 🔒 Security

### Security Features
- **XSS Protection** - React's built-in XSS prevention
- **CSRF Protection** - Token-based API authentication
- **Secure Headers** - Content Security Policy headers
- **Input Validation** - All user inputs validated

## 📈 Browser Support

### Supported Browsers
- **Chrome** 90+ ✅
- **Firefox** 88+ ✅  
- **Safari** 14+ ✅
- **Edge** 90+ ✅

### Polyfills
Vite automatically includes necessary polyfills for:
- **ES2020 Features**
- **CSS Custom Properties**
- **Async/Await**

## 📝 Contributing

### Code Style
- **ESLint** - Airbnb configuration with TypeScript
- **Prettier** - Consistent code formatting
- **Husky** - Pre-commit hooks for quality assurance

### Pull Request Process
1. Create feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

## 🔗 Links

**🔗 Repository**: https://github.com/Staysteady/metals-dashboard.git
**📚 Vite Docs**: https://vitejs.dev/
**⚛️ React Docs**: https://reactjs.org/
**🎨 Tailwind Docs**: https://tailwindcss.com/