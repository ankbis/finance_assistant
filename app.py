from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_session, engine
from models import Base, Item
from schemas import ItemCreate, ItemOut

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="FinanceAssistant", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/items", response_model=list[ItemOut])
async def list_items(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Item))
    return [ItemOut.model_validate(i) for i in res.scalars().all()]


@app.post("/items", response_model=ItemOut, status_code=201)
async def create_item(payload: ItemCreate, session: AsyncSession = Depends(get_session)):
    item = Item(name=payload.name)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return ItemOut.model_validate(item)


@app.get("/")
async def root():
    return {"app": app.title, "docs": "/docs"}
