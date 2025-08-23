import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# 1) normalize scheme
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql" + DATABASE_URL[len("postgres"):]

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# 2) parse & clean query params for asyncpg
parts = urlparse(DATABASE_URL)
qs = dict(parse_qsl(parts.query, keep_blank_values=True))

# map libpq sslmode -> asyncpg ssl
if "sslmode" in qs and "ssl" not in qs:
    # Neon wants 'require'
    qs["ssl"] = "require" if qs["sslmode"] in {"require", "verify-full", "verify-ca"} else "disable"
    qs.pop("sslmode", None)

# drop libpq-only params that asyncpg doesn't accept
for bad in ("channel_binding", "target_session_attrs"):
    qs.pop(bad, None)

# default to ssl=require if nothing set
qs.setdefault("ssl", "require")

# rebuild URL
DATABASE_URL = urlunparse(parts._replace(query=urlencode(qs)))

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
