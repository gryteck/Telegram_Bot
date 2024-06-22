from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from sqlalchemy import SmallInteger, BigInteger, Text, ARRAY, DateTime, Boolean, TIMESTAMP
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    photo: Mapped[str | None] = mapped_column(Text, nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    gender: Mapped[str] = mapped_column(Text, nullable=False)
    interest: Mapped[str] = mapped_column(Text, nullable=False)
    liked: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), default=[], nullable=False)
    join_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    active_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    view_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    claims_count: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    claims: Mapped[list] = mapped_column(ARRAY(Text), default=[], nullable=False)
    banned: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    noticed: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), default=[], nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Actions(Base):
    __tablename__ = 'actions'

    action_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    from_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(Text, nullable=False)
    to_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    action_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
