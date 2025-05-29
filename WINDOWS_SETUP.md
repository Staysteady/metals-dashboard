# 🖥️ Windows Setup Guide - Metals Dashboard

Complete guide to set up the Metals Trading Dashboard on Windows with live Bloomberg data.

## 📋 Prerequisites

### Required Software
1. **Git for Windows** - [Download here](https://git-scm.com/download/win)
2. **Node.js 18+** - [Download here](https://nodejs.org/en/download/)
3. **Python 3.9+** - [Download here](https://www.python.org/downloads/windows/)
4. **Bloomberg Terminal** - Required for live data (must be running)
5. **Visual Studio Code** (recommended) - [Download here](https://code.visualstudio.com/)

### Bloomberg Setup Requirements
- **Bloomberg Terminal License** with API access
- **Bloomberg API SDK (BLPAPI)** - Available from Bloomberg
- **Active Bloomberg Session** - Terminal must be logged in

## 🚀 Quick Setup (5 Steps)

### Step 1: Clone Repository
```powershell
# Open PowerShell or Command Prompt
git clone https://github.com/Staysteady/metals-dashboard.git
cd metals-dashboard
```

### Step 2: Backend Setup
```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
venv\Scripts\Activate.ps1
# OR for Command Prompt:
# venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup
```powershell
# Open new terminal window
cd metals-dashboard\frontend
npm install
```

### Step 4: Bloomberg API Configuration

#### Option A: Live Bloomberg Data
```powershell
# In backend directory, create .env file
# Copy the template below and adjust paths

# Create .env file in backend directory:
USE_DUMMY_DATA=false
BLOOMBERG_HOST=localhost
BLOOMBERG_PORT=8194
BLPAPI_ROOT=C:\blp\API\APIv3\C++API\v3.21.2.1
DATABASE_PATH=.\data\metals.duckdb
```

#### Option B: Development Mode (Dummy Data)
```powershell
# Create .env file in backend directory:
USE_DUMMY_DATA=true
DATABASE_PATH=.\data\metals.duckdb
```

### Step 5: Run Application
```powershell
# Terminal 1: Start Backend (in metals-dashboard\backend)
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Start Frontend (in metals-dashboard\frontend)
npm run dev
```

## 🔧 Bloomberg API Setup (Windows Specific)

### 1. Install Bloomberg API SDK
1. **Download BLPAPI** from Bloomberg (requires terminal license)
2. **Extract to standard location**: `C:\blp\API\APIv3\C++API\v3.21.2.1\`
3. **Update PATH** environment variable to include API libraries

### 2. Configure Environment Variables
```powershell
# Method 1: PowerShell (temporary)
$env:BLPAPI_ROOT = "C:\blp\API\APIv3\C++API\v3.21.2.1"
$env:PATH += ";$env:BLPAPI_ROOT\bin"

# Method 2: System Environment Variables (permanent)
# 1. Open System Properties > Environment Variables
# 2. Add BLPAPI_ROOT = C:\blp\API\APIv3\C++API\v3.21.2.1
# 3. Add to PATH: %BLPAPI_ROOT%\bin
```

### 3. Install Python Bloomberg Library
```powershell
# In backend virtual environment
pip install blpapi
```

### 4. Verify Bloomberg Connection
```powershell
# Test connection (Bloomberg Terminal must be running)
cd backend
python -c "import blpapi; print('Bloomberg API imported successfully')"
```

## 📍 Accessing the Application

Once both servers are running:

- **Frontend (Web App)**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing Setup

### Run All Tests
```powershell
# Backend Tests
cd backend
venv\Scripts\Activate.ps1
pytest

# Frontend Tests
cd frontend
npm test
```

### Verify Bloomberg Data
1. **Check Data Source Toggle** in the web interface
2. **Switch from "Dummy Data" to "Bloomberg"**
3. **Verify real-time prices** are loading

## 🚨 Troubleshooting

### Common Issues

#### Bloomberg Connection Failed
```powershell
# Check Bloomberg Terminal is running
# Verify API license is active
# Test with dummy data first:
# Set USE_DUMMY_DATA=true in .env
```

#### Port Already in Use
```powershell
# Check for running processes
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Kill process if needed
taskkill /PID <process_id> /F
```

#### Python Virtual Environment Issues
```powershell
# Ensure you're in the correct directory
cd metals-dashboard\backend

# Recreate virtual environment
rmdir /s venv
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Node.js/NPM Issues
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rmdir /s node_modules
del package-lock.json
npm install
```

## 🔄 Data Source Switching

The application supports both live and dummy data:

### Switch to Live Bloomberg Data
1. **Ensure Bloomberg Terminal is running**
2. **Set environment**: `USE_DUMMY_DATA=false`
3. **Restart backend server**
4. **Use toggle in web interface**

### Switch to Dummy Data (Development)
1. **Set environment**: `USE_DUMMY_DATA=true`
2. **Restart backend server**
3. **Use toggle in web interface**

## 🏗️ Development Workflow

### Daily Development
```powershell
# Start development servers (2 terminals)

# Terminal 1: Backend
cd metals-dashboard\backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd metals-dashboard\frontend
npm run dev
```

### Before Committing
```powershell
# Run linting and tests
npm run lint
npm test
```

## 📊 Monitoring & Debugging

### Check Bloomberg Data Flow
- **API Logs**: Monitor backend terminal for Bloomberg API calls
- **Network Tab**: Check browser dev tools for API requests
- **Data Source Status**: Use toggle to verify connection

### Performance Tips
- **Plotly.js Bundle**: First load may be slow (4.8MB)
- **Caching**: Data is cached for performance
- **Real-time Updates**: Prices update every 30 seconds

## 🆘 Support

If you encounter issues:
1. **Check Prerequisites**: Verify all software is installed
2. **Bloomberg License**: Ensure your terminal has API access
3. **Environment Variables**: Double-check .env configuration
4. **Logs**: Monitor both backend and frontend console output

## 🚀 Next Steps

Once running successfully:
1. **Explore the Home page** with interactive Plotly charts
2. **Test Portfolio page** with sample data
3. **Customize charts** and add new pages
4. **Connect live Bloomberg feeds** for real trading data

---

**🔗 Repository**: https://github.com/Staysteady/metals-dashboard.git  
**💻 Platform**: Optimized for Windows 10/11  
**📈 Bloomberg**: Requires active terminal session 