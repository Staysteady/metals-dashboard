from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductCategory(str, Enum):
    """Product categories for metals - kept for backward compatibility"""

    AH = "AH"  # Aluminum
    CA = "CA"  # Copper
    ZN = "ZN"  # Zinc
    PB = "PB"  # Lead
    NI = "NI"  # Nickel
    SN = "SN"  # Tin
    ALL = "ALL"  # All metals


class TickerBase(BaseModel):
    """Base ticker model"""

    symbol: str = Field(..., description="Bloomberg ticker symbol")
    description: str = Field(default="", description="Human readable description")
    product_category: Optional[str] = Field(default="OTHER", description="Product category (flexible)")
    is_custom: bool = Field(
        default=True, description="Whether this is a custom instrument"
    )


class TickerCreate(BaseModel):
    """Model for creating a new ticker - only symbol is required"""

    symbol: str = Field(..., description="Bloomberg ticker symbol")
    description: Optional[str] = Field(default=None, description="Human readable description")
    product_category: Optional[str] = Field(default="OTHER", description="Product category")
    is_custom: bool = Field(default=True, description="Whether this is a custom instrument")


class TickerUpdate(BaseModel):
    """Model for updating a ticker"""

    description: Optional[str] = None
    product_category: Optional[str] = None


class Ticker(TickerBase):
    """Complete ticker model with database fields"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PriceData(BaseModel):
    """Price data for a ticker"""

    ticker_id: int = Field(..., description="Ticker ID")
    symbol: str = Field(..., description="Ticker symbol")
    date: datetime = Field(..., description="Price date")
    px_last: float = Field(..., description="Last price")
    px_open: Optional[float] = Field(None, description="Opening price")
    px_high: Optional[float] = Field(None, description="High price")
    px_low: Optional[float] = Field(None, description="Low price")
    px_volume: Optional[float] = Field(None, description="Volume")

    class Config:
        from_attributes = True


class PriceDataResponse(BaseModel):
    """Response model for price data queries"""

    ticker: Ticker
    prices: List[PriceData]
    total_records: int


class CustomInstrument(BaseModel):
    """Custom instrument definition (switch or weighted index)"""

    id: int
    name: str = Field(..., description="Custom instrument name")
    type: str = Field(..., description="Type: 'switch' or 'weighted_index'")
    definition: dict = Field(..., description="JSON definition of the instrument")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomInstrumentCreate(BaseModel):
    """Model for creating custom instruments"""

    name: str
    type: str = Field(..., pattern="^(switch|weighted_index)$")
    definition: dict


class SettlementPrice(BaseModel):
    """Settlement price data"""

    id: int
    symbol: str
    date: datetime
    settlement_price: float
    product_category: ProductCategory

    class Config:
        from_attributes = True


class TickerData(BaseModel):
    """Real-time ticker data model"""

    symbol: str
    description: str
    product_category: str
    px_last: float
    change: Optional[float] = None
    change_pct: Optional[float] = None
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class HistoricalDataPoint(BaseModel):
    """Historical price data point"""

    date: str
    price: float


class HistoricalData(BaseModel):
    """Historical data response"""

    symbol: str
    data_points: List[HistoricalDataPoint]
    start_date: str
    end_date: str


class MarketStatus(BaseModel):
    """Market status information"""

    is_open: bool
    message: str
    next_open: Optional[datetime] = None
    next_close: Optional[datetime] = None
