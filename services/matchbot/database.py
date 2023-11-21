import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config import pg_url, env

engine = create_async_engine(pg_url)
pg_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

redis = aioredis.from_url(
                    url=f"redis://{env['REDIS_HOST']}",
                    password=env['REDIS_PASSWORD'],
                    db=1,
                    encoding="utf-8",
                    decode_responses=True
                )
