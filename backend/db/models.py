from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, String, DateTime


class Base(DeclarativeBase):
    pass


class UserBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column()
    user_name: Mapped[str] = mapped_column(String(32))
    time_zone: Mapped[int] = mapped_column(default=7)

    def __repr__(self) -> str:
        return f"UserBase(telegram_id={self.telegram_id}, user_name={self.user_name}, time_zone={self.time_zone})"


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(String(3000))
    deadline: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(nullable=False)
