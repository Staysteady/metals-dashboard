# Metals Dashboard

A streamlined metals trading application with real-time Bloomberg data integration, built with React (frontend) and FastAPI (backend).

## 🚀 Features

- **Live Bloomberg Data** - Real-time metals prices from Bloomberg Terminal
- **Real-time Price Updates** - Automatic data refresh with live market status
- **Bloomberg API Integration** - Direct connection to Bloomberg Terminal for live data
- **Responsive Design** - Clean, modern interface optimized for trading workflows
- **Market Status Monitoring** - Live market open/close status with trading hours

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Bloomberg Terminal** (must be installed and logged in)
- **Git** (for version control)

### Bloomberg Terminal Setup
**CRITICAL:** Bloomberg Terminal must be:
1. ✅ **Installed** on your Windows machine
2. ✅ **Logged in** with valid credentials  
3. ✅ **Running** during application use

The application **requires live Bloomberg data** and will not function without a proper Bloomberg Terminal connection.

## 🛠 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Staysteady/metals-dashboard.git
cd metals-dashboard
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set Bloomberg environment variable (Windows)
set BLPAPI_ROOT=C:\blp\DAPI

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server  
npm run dev
```

### 4. Access Application
- **Application**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏗 Project Structure

```
metals-dashboard/
├── README.md                    # This file
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI application entry
│   │   ├── api/
│   │   │   ├── lme.py          # LME metals endpoints
│   │   │   └── health.py       # Health check endpoints
│   │   ├── services/
│   │   │   └── bloomberg_service.py  # Bloomberg API integration
│   │   ├── models/
│   │   │   └── ticker.py       # Data models
│   │   └── config.py           # Application configuration
│   ├── requirements.txt        # Python dependencies
│   └── tests/                  # Backend tests
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx             # Main application component
│   │   ├── pages/
│   │   │   └── Bloomberg.tsx   # Bloomberg Live page
│   │   ├── components/
│   │   │   ├── Layout.tsx      # Application layout
│   │   │   └── DataSourceToggle.tsx  # Bloomberg status indicator
│   │   ├── api/
│   │   │   └── client.ts       # API client
│   │   └── types/
│   │       └── index.ts        # TypeScript types
│   ├── package.json            # Frontend dependencies
│   └── vite.config.ts          # Vite configuration
└── shared/                     # Shared utilities
    └── types/                  # Shared TypeScript types
```

## 🔧 Configuration

### Environment Variables

Create `.env` files for configuration:

**Backend** (`backend/.env`):
```env
# Bloomberg API Configuration
BLPAPI_ROOT=C:\blp\DAPI

# Application Settings
DEBUG=True
LOG_LEVEL=INFO

# API Configuration
HOST=0.0.0.0
PORT=8000
```

**Frontend** (`frontend/.env`):
```env
# Application
VITE_APP_TITLE=Metals Dashboard
VITE_API_URL=http://localhost:8000

# Development
VITE_APP_ENV=development
```

### Bloomberg Configuration

The application connects to these Bloomberg symbols:
- **LME Copper**: LMCADS03 COMDTY
- **LME Aluminum**: LMAHDS03 COMDTY  
- **LME Zinc**: LMZSDS03 COMDTY
- **LME Lead**: LMPBDS03 COMDTY
- **LME Tin**: LMSNDS03 COMDTY
- **LME Nickel**: LMNIDS03 COMDTY
- **AAPL**: AAPL US Equity (example equity)
- **Index**: CTCTVSQW INDEX (example index)

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests  
```bash
cd frontend
npm test
```

## 📚 API Documentation

### Key Endpoints

- `GET /` - API status and information
- `GET /health/` - Health check with Bloomberg connection status
- `GET /lme/tickers` - Basic ticker information
- `GET /lme/tickers?include_live_prices=true` - Live Bloomberg prices
- `GET /lme/market-status` - Market status and trading hours

### Example API Response
```json
{
  "symbol": "LMCADS03",
  "description": "LME Copper Cash",
  "bloomberg_symbol": "LMCADS03 COMDTY",
  "px_last": 9568.0,
  "change": 45.5,
  "change_pct": 0.48,
  "is_live": true,
  "timestamp": "2024-01-15T14:30:00Z"
}
```

## 🔄 Data Flow

1. **Bloomberg Terminal** provides live market data
2. **Backend** connects to Bloomberg API via `bloomberg_service.py`
3. **API endpoints** serve real-time data to frontend
4. **Frontend** displays live prices with automatic updates
5. **Market status** monitored for trading hours

## 🛡 Production Deployment

### Backend (FastAPI)
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (React)
```bash
# Build for production
npm run build

# Serve static files
npm run preview
```

## 📈 Features in Detail

### Bloomberg Integration
- ✅ Real-time price feeds
- ✅ Market status monitoring  
- ✅ Connection health checks
- ✅ Error handling and fallbacks

### Data Management
- ✅ Live price caching
- ✅ Automatic refresh intervals
- ✅ Market hours awareness
- ✅ Type-safe data models

### User Interface
- ✅ Clean, responsive design
- ✅ Real-time price updates
- ✅ Bloomberg connection status
- ✅ Professional trading interface

## 🐛 Troubleshooting

### Bloomberg Connection Issues
```bash
# Check Bloomberg installation
dir C:\blp\DAPI

# Set environment variable
set BLPAPI_ROOT=C:\blp\DAPI

# Verify Bloomberg login
# Ensure Bloomberg Terminal is running and logged in
```

### Common Issues
1. **"Bloomberg API not found"** - Set `BLPAPI_ROOT` environment variable
2. **"Connection timeout"** - Ensure Bloomberg Terminal is running
3. **"Authentication failed"** - Log into Bloomberg Terminal
4. **"No data returned"** - Check market hours and symbol validity

## 📝 License

This project is licensed under the MIT License.

## 🔗 Links

**🔗 Repository**: https://github.com/Staysteady/metals-dashboard.git 