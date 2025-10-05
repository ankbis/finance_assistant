from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import StockHolding
from app.schemas.holdings import StockHoldingCreate, StockHoldingUpdate
from datetime import datetime
import uuid


async def create_stock_holding(db: AsyncSession, holding: StockHoldingCreate, user_id: str) -> StockHolding:
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
    await db.commit()
    await db.refresh(db_holding)
    return db_holding


async def get_user_stock_holdings(db: AsyncSession, user_id: str) -> list[StockHolding]:
    result = await db.execute(
        select(StockHolding).filter(StockHolding.user_id == user_id)
    )
    return result.scalars().all()


async def update_stock_holding(
    db: AsyncSession, holding_id: str, holding: StockHoldingUpdate, user_id: str
) -> StockHolding | None:
    result = await db.execute(
        select(StockHolding).filter(
            StockHolding.id == holding_id,
            StockHolding.user_id == user_id
        )
    )
    db_holding = result.scalar_one_or_none()
    
    if not db_holding:
        return None
    
    update_data = holding.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_holding, field, value)
    
    db_holding.last_updated = datetime.utcnow()
    await db.commit()
    await db.refresh(db_holding)
    return db_holding


async def delete_stock_holding(db: AsyncSession, holding_id: str, user_id: str) -> bool:
    result = await db.execute(
        select(StockHolding).filter(
            StockHolding.id == holding_id,
            StockHolding.user_id == user_id
        )
    )
    db_holding = result.scalar_one_or_none()
    
    if not db_holding:
        return False
    
    await db.delete(db_holding)
    await db.commit()
    return True