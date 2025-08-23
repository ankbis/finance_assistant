import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Normalize scheme to psycopg driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql" + DATABASE_URL[len("postgres"):]
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://",
                                        "postgresql+psycopg://", 1)

# psycopg (libpq) happily accepts Neon’s default params like sslmode, channel_binding
# so no need to rewrite them.

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
