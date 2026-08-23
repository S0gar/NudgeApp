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
    time_zone: Mapped[str] = mapped_column(default="Europe/Samara")

    def __repr__(self) -> str:
        return f"UserBase(telegram_id={self.telegram_id}, user_name={self.user_name})"


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(String(30000))
    deadline: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(NotNullable=True)
