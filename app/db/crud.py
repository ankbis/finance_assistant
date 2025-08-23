from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Item
from app.schema.items import ItemCreate, ItemUpdate

async def create_item(db: AsyncSession, data: ItemCreate) -> Item:
    obj = Item(name=data.name, description=data.description)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get_item(db: AsyncSession, item_id: str) -> Item | None:
    res = await db.execute(select(Item).where(Item.id == item_id))
    return res.scalar_one_or_none()

async def list_items(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Item]:
    res = await db.execute(select(Item).offset(skip).limit(limit))
    return list(res.scalars())

async def update_item(db: AsyncSession, item_id: str, data: ItemUpdate) -> Item | None:
    values = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    if not values:
        return await get_item(db, item_id)
    await db.execute(update(Item).where(Item.id == item_id).values(**values))
    await db.commit()
    return await get_item(db, item_id)

async def delete_item(db: AsyncSession, item_id: str) -> bool:
    res = await db.execute(delete(Item).where(Item.id == item_id))
    await db.commit()
    return res.rowcount > 0
