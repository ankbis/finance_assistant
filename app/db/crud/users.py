from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.schemas.users import UserCreate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).filter(User.email == email)
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=user.hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    return result.scalar_one_or_none()