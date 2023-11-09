from database import Base, engine
from sqlalchemy import Column, SmallInteger, BigInteger, Text, ARRAY, DateTime, Boolean
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    user_id = Column(SmallInteger, primary_key=True, index=True)
    id = Column(BigInteger, unique=True, nullable=False)
    username = Column(Text)
    name = Column(Text, nullable=False)
    age = Column(SmallInteger, nullable=False)
    photo = Column(Text)
    text = Column(Text)
    gender = Column(Text, nullable=False)
    interest = Column(Text, nullable=False)
    liked = Column(ARRAY(BigInteger), default=[], nullable=False)
    join_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    active_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    view_count = Column(SmallInteger, default=0, nullable=False)
    claims_count = Column(SmallInteger, default=0, nullable=False)
    claims = Column(ARRAY(SmallInteger), default=[], nullable=False)
    banned = Column(Boolean, default=False, nullable=False)
    noticed = Column(ARRAY(BigInteger), default=[], nullable=False)
    visible = Column(Boolean, default=True, nullable=False)


Base.metadata.create_all(bind=engine)
