# Metals Dashboard

A cross-platform metals trading dashboard with real-time price data from Bloomberg, built with React (web), React Native (mobile), and FastAPI (backend).

## ✨ Current Features (Phase 4 Complete)

- 📊 **Interactive Plotly Charts** - Historical price trends and current price distribution
- 🏠 **Home Page Dashboard** - Complete metals trading overview with real-time updates
- 📈 **Real-time Price Tracking** - Gold, Silver, Platinum, Copper, Aluminum, Zinc, Lead, Tin, Nickel
- 📱 **Market Status Indicators** - Visual market open/closed status with timing
- 🎯 **Portfolio Example** - Sample portfolio page with mock holdings and P&L
- 🧪 **Comprehensive Testing** - 100% test coverage with CI/CD pipeline
- 🔍 **Code Quality** - Zero linting errors, pre-commit hooks, automated checks

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (3.9 or higher) - [Download](https://python.org/)
- **Git** - [Download](https://git-scm.com/)
- **Bloomberg Terminal** (required for live data) - [Bloomberg](https://www.bloomberg.com/professional/support/software-updates/)

### 1. Clone Repository
```bash
git clone https://github.com/Staysteady/metals-dashboard.git
cd metals-dashboard
```

### 2. Easy Setup (Both Backend & Frontend)
```bash
# Install all dependencies and set up both backend and frontend
npm run setup

# Run both backend and frontend concurrently
npm run dev
```

**✅ That's it! Your application is now running:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 Detailed Setup Instructions

### Backend Setup (Python/FastAPI)

#### 1. Create Virtual Environment
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### 3. Environment Configuration
Create `backend/.env` file:
```env
# Database
DATABASE_URL=sqlite:///./data/metals.db

# Bloomberg API (required for live data)
BLPAPI_ROOT=C:\blp\API\APIv3\C++API\v3.24.10.1\lib
BLOOMBERG_HOST=localhost
BLOOMBERG_PORT=8194

# API Settings
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true
```

#### 4. Bloomberg API Setup (Required)

**Windows Bloomberg Terminal Users:**
```bash
# Common Bloomberg API paths:
# C:\blp\API\APIv3\C++API\v3.24.10.1\lib
# C:\blp\DAPI\APIv3\C++API\v3.24.10.1\lib

# Set environment variable
set BLPAPI_ROOT=C:\blp\API\APIv3\C++API\v3.24.10.1\lib

# Or add to .env file
echo BLPAPI_ROOT=C:\blp\API\APIv3\C++API\v3.24.10.1\lib >> .env
```

**macOS/Linux:**
```bash
# Install Bloomberg API
# Follow Bloomberg's installation guide for your platform

# Set environment variable
export BLPAPI_ROOT=/opt/bloomberg/blpapi_cpp_3.24.10.1

# Add to .env file
echo "BLPAPI_ROOT=/opt/bloomberg/blpapi_cpp_3.24.10.1" >> .env
```

#### 5. Run Backend
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using the npm script from root
npm run dev:backend
```

### Frontend Setup (React/Vite)

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Environment Configuration (Optional)
Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=Metals Dashboard
```

#### 3. Run Frontend
```bash
# Development mode with hot reload
npm run dev

# Or using the npm script from root
npm run dev:frontend
```

## 🔧 Development Commands

### Root Directory Commands (Recommended)
```bash
# Setup everything
npm run setup

# Run both backend and frontend
npm run dev

# Run tests
npm run test

# Lint and format
npm run lint
npm run format

# Backend only
npm run dev:backend
npm run test:backend
npm run lint:backend

# Frontend only  
npm run dev:frontend
npm run test:frontend
npm run lint:frontend
```

### Individual Component Commands

#### Backend Commands
```bash
cd backend

# Virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run server
uvicorn app.main:app --reload
python -m uvicorn app.main:app --reload

# Testing
pytest
pytest --cov  # With coverage

# Linting
flake8 app tests
mypy app
black app tests  # Format
isort app tests  # Sort imports
```

#### Frontend Commands
```bash
cd frontend

# Development
npm run dev
npm start  # Alternative

# Build
npm run build
npm run preview  # Preview build

# Testing
npm test
npm run test:coverage

# Linting
npm run lint
npm run lint:fix
npm run format
```

## 🗂️ Project Structure

```
metals-dashboard/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── api/               # API route handlers
│   │   │   ├── lme.py        # LME metals endpoints
│   │   │   └── health.py     # Health check endpoints
│   │   ├── services/         # Business logic services
│   │   │   ├── bloomberg_service.py  # Bloomberg API integration
│   │   │   ├── ticker_service.py     # Ticker management
│   │   │   └── market_data.py        # Market data processing
│   │   ├── db/               # Database models and connection
│   │   └── models/           # Pydantic data models
│   ├── venv/                 # Python virtual environment
│   ├── data/                 # Database files
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/                  # React/Vite frontend
│   ├── src/
│   │   ├── App.tsx           # Main application component
│   │   ├── pages/            # Page components
│   │   │   ├── Home.tsx      # Dashboard with charts
│   │   │   └── Portfolio.tsx # Portfolio management
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Layout.tsx    # App layout wrapper
│   │   │   ├── BloombergStatus.tsx  # Bloomberg connection status
│   │   │   └── charts/       # Chart components
│   │   ├── services/         # API service layer
│   │   └── types/            # TypeScript type definitions
│   ├── package.json          # Frontend dependencies
│   └── .env                  # Frontend environment variables
├── shared/                   # Shared utilities (future mobile)
├── node_modules/             # Node.js dependencies
├── package.json              # Root package.json with scripts
└── README.md                 # This file
```

## 🔧 Configuration Details

### Bloomberg API Configuration

#### Windows Setup
1. **Install Bloomberg Terminal** and ensure it's running
2. **Locate Bloomberg API** (usually in `C:\blp\API\`)
3. **Set environment variables**:
   ```cmd
   set BLPAPI_ROOT=C:\blp\API\APIv3\C++API\v3.24.10.1\lib
   set PATH=%PATH%;%BLPAPI_ROOT%
   ```
4. **Update backend/.env**:
   ```env
   BLPAPI_ROOT=C:\blp\API\APIv3\C++API\v3.24.10.1\lib
   BLOOMBERG_HOST=localhost
   BLOOMBERG_PORT=8194
   ```

#### macOS/Linux Setup
1. **Download Bloomberg API** from Bloomberg Terminal
2. **Extract to /opt/bloomberg/** (or preferred location)
3. **Set environment variables**:
   ```bash
   export BLPAPI_ROOT=/opt/bloomberg/blpapi_cpp_3.24.10.1
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$BLPAPI_ROOT/lib
   ```
4. **Update backend/.env** accordingly

### Virtual Environment Paths

#### Python Virtual Environment
```bash
# Creation
python -m venv backend/venv

# Activation paths
Windows: backend\venv\Scripts\activate
macOS/Linux: backend/venv/bin/activate

# Deactivation
deactivate
```

#### Common Python Virtual Environment Issues
```bash
# If activation fails on Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If Python is not found
where python  # Windows
which python  # macOS/Linux

# Alternative Python commands
python3 -m venv venv
py -m venv venv  # Windows Python Launcher
```

## 🚦 Running the Application

### Method 1: Concurrently (Recommended)
```bash
# From root directory
npm run dev
```
This starts both backend and frontend simultaneously using `concurrently`.

### Method 2: Separate Terminals
```bash
# Terminal 1: Backend
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
uvicorn app.main:app --reload

# Terminal 2: Frontend  
cd frontend
npm run dev
```

### Method 3: Individual Services
```bash
# Backend only
npm run dev:backend

# Frontend only
npm run dev:frontend
```

## 🌐 Access Points

Once running:
- **Web Application**: http://localhost:5173
- **API Backend**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Redoc**: http://localhost:8000/redoc (Alternative docs)

## 🧪 Testing

### Run All Tests
```bash
npm test
```

### Backend Tests
```bash
cd backend
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
pytest
pytest --cov  # With coverage report
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Bloomberg API Not Found
```bash
# Check if Bloomberg Terminal is running
tasklist | findstr "Terminal"  # Windows
ps aux | grep -i bloomberg  # macOS/Linux

# Verify BLPAPI_ROOT path
echo %BLPAPI_ROOT%  # Windows
echo $BLPAPI_ROOT   # macOS/Linux
```

#### 2. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf backend/venv  # macOS/Linux
rmdir /s backend\venv  # Windows
cd backend
python -m venv venv
```

#### 3. Port Already in Use
```bash
# Kill processes on port 8000 (backend)
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux

# Kill processes on port 5173 (frontend)
netstat -ano | findstr :5173  # Windows
lsof -i :5173  # macOS/Linux
```

#### 4. Node.js/npm Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall node_modules
rm -rf node_modules package-lock.json
npm install
```

### Getting Help
1. Check the terminal output for specific error messages
2. Ensure all prerequisites are installed
3. Verify environment variables are set correctly
4. Check that Bloomberg Terminal is running (required for live data)
5. Consult the API documentation at http://localhost:8000/docs

## 📊 Supported Metals & Symbols

### Base Metals (LME)
- **LMCADS03** - Copper 3 Month
- **LMAHDS03** - Aluminum 3 Month  
- **LMPBDS03** - Lead 3 Month
- **LMZNDS03** - Zinc 3 Month
- **LMSNDS03** - Tin 3 Month
- **LMNIDS03** - Nickel 3 Month

### Precious Metals
- **XAU=** - Gold Spot
- **XAG=** - Silver Spot
- **XPT=** - Platinum Spot
- **XPD=** - Palladium Spot

### Equity Examples
- **AAPL US Equity** - Apple Inc.
- **CTCTVSQW INDEX** - Custom volatility index

## 🛠️ Tech Stack

### Frontend
- **Vite + React 18** - Modern build tooling and framework
- **TypeScript** - Type safety and developer experience
- **Plotly.js** - Professional charting and visualization
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - High-quality component library

### Backend  
- **FastAPI** - High-performance Python API framework
- **DuckDB** - Embedded analytics database
- **Bloomberg API (BLPAPI)** - Live market data integration
- **Pydantic** - Data validation and serialization

### Development
- **Jest + React Testing Library** - Frontend testing
- **Pytest** - Backend testing framework
- **ESLint + Prettier** - Code quality and formatting
- **GitHub Actions** - CI/CD automation

## 📈 Performance & Monitoring

### Current Metrics
- **Bundle Size**: 4.8MB (Plotly.js included)
- **API Response**: <100ms average
- **Test Coverage**: 100% critical paths
- **Code Quality**: 0 linting errors

### Real-time Features
- **Price Updates**: Every 30 seconds during market hours
- **Market Status**: Real-time open/closed detection
- **Error Recovery**: Automatic fallback to cached data
- **Performance**: Optimized for sub-second chart updates

---

**🔗 Repository**: https://github.com/Staysteady/metals-dashboard.git  
**📊 Live Demo**: Available when Bloomberg Terminal is connected  
**📱 Mobile**: Coming in Phase 5 (React Native)  
**☁️ Deployment**: Coming in Phase 6 (Docker + Cloud) 