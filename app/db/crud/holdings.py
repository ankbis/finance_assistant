from sqlalchemy.orm import Session
from app.db.models import StockHolding
from app.schemas.holdings import StockHoldingCreate, StockHoldingUpdate
from datetime import datetime
import uuid


def create_stock_holding(db: Session, holding: StockHoldingCreate, user_id: str) -> StockHolding:
    db_holding = StockHolding(
        id=str(uuid.uuid4()),
        user_id=user_id,
        symbol=holding.symbol.upper(),
        quantity=holding.quantity,
        avg_price=holding.avg_price,
        current_price=holding.current_price,
        last_updated=datetime.utcnow()
    )
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    return db_holding


def get_user_stock_holdings(db: Session, user_id: str) -> list[StockHolding]:
    return db.query(StockHolding).filter(StockHolding.user_id == user_id).all()


def update_stock_holding(
    db: Session, holding_id: str, holding: StockHoldingUpdate, user_id: str
) -> StockHolding | None:
    db_holding = db.query(StockHolding).filter(
        StockHolding.id == holding_id,
        StockHolding.user_id == user_id
    ).first()
    
    if not db_holding:
        return None
    
    update_data = holding.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_holding, field, value)
    
    db_holding.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_holding)
    return db_holding


def delete_stock_holding(db: Session, holding_id: str, user_id: str) -> bool:
    db_holding = db.query(StockHolding).filter(
        StockHolding.id == holding_id,
        StockHolding.user_id == user_id
    ).first()
    
    if not db_holding:
        return False
    
    db.delete(db_holding)
    db.commit()
    return True