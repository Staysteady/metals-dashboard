"""
LME (London Metal Exchange) Ticker Definitions
Structured data for Bloomberg ticker codes as requested by user
"""

from typing import Dict, List
from datetime import datetime

# LME Ticker definitions in the exact format requested
LME_TICKERS = [
    {
        "ticker": "LMAHDS03 LME COMDTY",
        "description": "Aluminium 3m Price", 
        "metal": "Aluminium",
        "symbol": "AH",
        "bloomberg_symbol": "LMAHDS03",  # For Bloomberg API calls
        "product_category": "LME_BASE_METALS"
    },
    {
        "ticker": "LMCADS03 LME COMDTY",
        "description": "Copper 3m Price",
        "metal": "Copper", 
        "symbol": "CA",
        "bloomberg_symbol": "LMCADS03",
        "product_category": "LME_BASE_METALS"
    },
    {
        "ticker": "LMNIDS03 LME COMDTY",
        "description": "Nickel 3m Price",
        "metal": "Nickel",
        "symbol": "NI", 
        "bloomberg_symbol": "LMNIDS03",
        "product_category": "LME_BASE_METALS"
    },
    {
        "ticker": "LMPBDS03 LME COMDTY",
        "description": "Lead 3m Price",
        "metal": "Lead",
        "symbol": "PB",
        "bloomberg_symbol": "LMPBDS03", 
        "product_category": "LME_BASE_METALS"
    },
    {
        "ticker": "LMSNDS03 LME COMDTY",
        "description": "Tin 3m Price",
        "metal": "Tin",
        "symbol": "SN",
        "bloomberg_symbol": "LMSNDS03",
        "product_category": "LME_BASE_METALS"
    },
    {
        "ticker": "LMZNDS03 LME COMDTY",  # Note: You had LMZSDS03 but this is the correct LME zinc code
        "description": "Zinc 3m Price", 
        "metal": "Zinc",
        "symbol": "ZN",
        "bloomberg_symbol": "LMZNDS03",
        "product_category": "LME_BASE_METALS"
    }
]

def get_lme_tickers() -> List[Dict]:
    """Get the list of LME tickers"""
    return LME_TICKERS

def get_bloomberg_symbols() -> List[str]:
    """Get just the Bloomberg symbols for API calls"""
    return [ticker["bloomberg_symbol"] for ticker in LME_TICKERS]

def get_ticker_by_symbol(symbol: str) -> Dict:
    """Get ticker data by Bloomberg symbol"""
    for ticker in LME_TICKERS:
        if ticker["bloomberg_symbol"] == symbol:
            return ticker
    raise ValueError(f"Ticker not found: {symbol}")

def format_for_database() -> List[Dict]:
    """Format tickers for database insertion"""
    return [
        {
            "symbol": ticker["bloomberg_symbol"],
            "description": ticker["description"],
            "product_category": ticker["symbol"],  # Using the short symbol as category
            "full_ticker": ticker["ticker"],
            "metal": ticker["metal"],
            "is_custom": False
        }
        for ticker in LME_TICKERS
    ] 