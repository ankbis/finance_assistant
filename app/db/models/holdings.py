from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime
from app.db.models import Base
from datetime import datetime
import uuid


class StockHolding(Base):
    __tablename__ = "stock_holdings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    symbol: Mapped[str] = mapped_column(String(20), index=True)  # NSE/BSE Symbol
    quantity: Mapped[int] = mapped_column(Integer)
    avg_price: Mapped[float] = mapped_column(Float)
    current_price: Mapped[float] = mapped_column(Float)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    @property
    def total_investment(self) -> float:
        return self.quantity * self.avg_price

    @property
    def current_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def profit_loss(self) -> float:
        return self.current_value - self.total_investment

    @property
    def profit_loss_percentage(self) -> float:
        if self.total_investment == 0:
            return 0.0
        return (self.profit_loss / self.total_investment) * 100