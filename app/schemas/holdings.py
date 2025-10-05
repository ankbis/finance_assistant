from pydantic import BaseModel, Field
from datetime import datetime


class StockHoldingBase(BaseModel):
    symbol: str = Field(..., description="Stock symbol (NSE/BSE)")
    quantity: int = Field(..., description="Number of shares held")
    avg_price: float = Field(..., description="Average purchase price per share")
    current_price: float = Field(..., description="Current market price per share")


class StockHoldingCreate(StockHoldingBase):
    pass


class StockHoldingUpdate(BaseModel):
    quantity: int | None = Field(None, description="Number of shares held")
    avg_price: float | None = Field(None, description="Average purchase price per share")
    current_price: float | None = Field(None, description="Current market price per share")


class StockHolding(StockHoldingBase):
    id: str
    user_id: str
    last_updated: datetime
    total_investment: float
    current_value: float
    profit_loss: float
    profit_loss_percentage: float

    class Config:
        from_attributes = True