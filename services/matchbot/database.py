from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

from config import pg_url


# Создание базовой модели для хранения вопроса
Base = declarative_base()
engine = create_engine(pg_url)
Base.metadata.bind = engine
DBSession = sessionmaker(autocommit=True, bind=engine)

SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
