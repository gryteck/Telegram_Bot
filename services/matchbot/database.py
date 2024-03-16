import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings

if settings.MODE == 'TEST':
    engine = create_async_engine(settings.TEST_PG_URL)
    redis = aioredis.from_url(url=settings.TEST_RD_URL)
else:
    engine = create_async_engine(settings.PG_URL)
    redis = aioredis.from_url(url=settings.RD_URL)

pg_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

