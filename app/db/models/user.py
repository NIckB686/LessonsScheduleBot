from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, BigInteger, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base

if TYPE_CHECKING:
    from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
    )
    group_id: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )
    username: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    is_alive: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    banned: Mapped[bool] = mapped_column(
        default=False,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
