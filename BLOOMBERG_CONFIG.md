# 📈 Bloomberg API Configuration Guide

Comprehensive guide to configure live Bloomberg data for the Metals Dashboard.

## 🔑 Bloomberg Prerequisites

### Required Access
- **Bloomberg Terminal License** with API permissions
- **BLPAPI SDK** downloaded from Bloomberg
- **Active Bloomberg Session** (must be logged into terminal)
- **API Permissions** for metals pricing data

### Supported Bloomberg Symbols
The dashboard is configured for these metals tickers:
- **LMCADS03** - LME Copper 3 Month
- **LMAHDS03** - LME Aluminum 3 Month  
- **LMPBDS03** - LME Lead 3 Month
- **LMZNDS03** - LME Zinc 3 Month
- **LMSNDS03** - LME Tin 3 Month
- **LMNIDS03** - LME Nickel 3 Month
- **XAU=** - Gold Spot
- **XAG=** - Silver Spot
- **XPT=** - Platinum Spot
- **XPD=** - Palladium Spot

## 🛠️ Windows Installation Steps

### 1. Download Bloomberg API SDK

1. **Log into Bloomberg Terminal**
2. **Type `WAPI <GO>`** to access API downloads
3. **Download C++ API** (latest version, typically 3.21.x)
4. **Extract to**: `C:\blp\API\APIv3\C++API\v3.21.2.1\`

### 2. Install Python Bloomberg Library

```powershell
# In your backend virtual environment
cd metals-dashboard\backend
venv\Scripts\Activate.ps1

# Install blpapi (this connects to the C++ API)
pip install blpapi
```

### 3. Set Environment Variables

#### Method A: PowerShell (Session-based)
```powershell
# Set for current session
$env:BLPAPI_ROOT = "C:\blp\API\APIv3\C++API\v3.21.2.1"
$env:PATH += ";$env:BLPAPI_ROOT\bin"
```

#### Method B: System Environment Variables (Permanent)
1. **Open System Properties**:
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"

2. **Add System Variables**:
   - Click "New" under System variables
   - Variable name: `BLPAPI_ROOT`
   - Variable value: `C:\blp\API\APIv3\C++API\v3.21.2.1`

3. **Update PATH**:
   - Find "Path" in System variables
   - Click "Edit" → "New"
   - Add: `%BLPAPI_ROOT%\bin`

### 4. Configure Backend Environment

Create `.env` file in `backend/` directory:

```env
# Bloomberg Configuration
USE_DUMMY_DATA=false
BLOOMBERG_HOST=localhost
BLOOMBERG_PORT=8194
BLPAPI_ROOT=C:\blp\API\APIv3\C++API\v3.21.2.1

# Database
DATABASE_PATH=.\data\metals.duckdb

# API Settings
API_TIMEOUT=30000
MAX_RETRIES=3
CACHE_DURATION=300
```

## 🧪 Testing Bloomberg Connection

### 1. Basic Connection Test
```powershell
cd backend
venv\Scripts\Activate.ps1

# Test Python can import Bloomberg API
python -c "import blpapi; print('✅ Bloomberg API imported successfully')"
```

### 2. Terminal Connection Test
```powershell
# Test Bloomberg Terminal connection
python -c "
import blpapi
options = blpapi.SessionOptions()
options.setServerHost('localhost')
options.setServerPort(8194)
session = blpapi.Session(options)
if session.start():
    print('✅ Bloomberg Terminal connection successful')
else:
    print('❌ Bloomberg Terminal connection failed')
session.stop()
"
```

### 3. Data Retrieval Test
Start the backend server and test API endpoints:

```powershell
# Start backend
uvicorn app.main:app --reload

# In another terminal, test endpoints:
curl http://localhost:8000/prices/latest
curl http://localhost:8000/prices/market-status
```

## 🔄 Data Source Management

### Toggle Between Data Sources

The dashboard includes a **Data Source Toggle** that allows switching between:
- **Bloomberg** - Live market data
- **Dummy Data** - Simulated data for development

### Backend Configuration

The Bloomberg service automatically:
- **Detects Bloomberg availability**
- **Falls back to dummy data** if Bloomberg unavailable
- **Caches data** for performance
- **Handles API errors** gracefully

### Monitoring Data Source

Check backend logs for status messages:
```
INFO: Using Bloomberg live data
WARNING: Bloomberg API not available, falling back to dummy data
INFO: Cached 6 real-time price records
```

## 🚨 Troubleshooting Bloomberg Issues

### Common Problems

#### 1. "Bloomberg API not available"
**Causes**:
- Bloomberg Terminal not running
- Terminal not logged in
- API permissions not enabled
- BLPAPI not installed correctly

**Solutions**:
```powershell
# Check Bloomberg Terminal is running
Get-Process | Where-Object {$_.ProcessName -like "*bbg*"}

# Verify environment variables
echo $env:BLPAPI_ROOT
echo $env:PATH

# Reinstall blpapi
pip uninstall blpapi
pip install blpapi
```

#### 2. "Connection timeout"
**Causes**:
- Bloomberg Terminal firewall blocking
- Incorrect host/port configuration
- Network connectivity issues

**Solutions**:
```powershell
# Test network connectivity
telnet localhost 8194

# Check firewall settings
# Allow Python.exe through Windows Firewall
```

#### 3. "No data returned"
**Causes**:
- Insufficient Bloomberg permissions
- Invalid ticker symbols
- Market closed (for real-time data)

**Solutions**:
- Verify ticker symbols in Bloomberg Terminal
- Check API permissions with Bloomberg support
- Test with dummy data first

### 4. Debug Mode

Enable detailed logging in `.env`:
```env
LOG_LEVEL=DEBUG
BLOOMBERG_DEBUG=true
```

## 📊 Data Flow Architecture

### Real-time Data Flow
```
Bloomberg Terminal → BLPAPI → Python Service → FastAPI → React Frontend
```

### Fallback Flow
```
Bloomberg Unavailable → Dummy Data Service → FastAPI → React Frontend
```

### Caching Strategy
- **Real-time prices**: 30-second cache
- **Historical data**: 5-minute cache
- **Market status**: 1-minute cache

## 🔐 Security Considerations

### Bloomberg Security
- **Keep terminal logged in** during market hours
- **Limit API access** to authorized applications
- **Monitor usage** through Bloomberg's API monitoring

### Application Security
- **Local development only** (no external access)
- **Environment variables** for sensitive config
- **No Bloomberg credentials** stored in code

## 📈 Performance Optimization

### Bloomberg API Efficiency
- **Batch requests** where possible
- **Cache frequently accessed data**
- **Limit concurrent connections**
- **Handle rate limits** gracefully

### Application Performance
- **Lazy loading** of historical data
- **Real-time updates** only when needed
- **Efficient data structures** for pricing data

## 🎯 Bloomberg Data Fields

### Available Fields per Symbol
- **px_last** - Last traded price
- **chg_net_1d** - Net change from previous day
- **chg_pct_1d** - Percentage change from previous day
- **volume** - Trading volume
- **bid** - Current bid price
- **ask** - Current ask price
- **open** - Opening price
- **high** - Day's high price
- **low** - Day's low price

### Historical Data
- **Daily prices** up to 1 year
- **Intraday data** (if available)
- **Volume data**
- **OHLC data** for charting

---

**🔗 Bloomberg Developer Portal**: [Open API Documentation](https://www.bloomberg.com/professional/support/api-library/)  
**📞 Bloomberg Support**: Available through terminal `HELP <GO>`  
**⚠️ Important**: Bloomberg API requires active terminal session 