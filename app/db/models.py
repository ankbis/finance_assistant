"""
This file is kept for backward compatibility.
All models have been moved to the models/ directory.
"""
from app.db.models.base import Base
from app.db.models.user import User
from app.db.models.holdings import StockHolding

__all__ = ['Base', 'User', 'StockHolding']
