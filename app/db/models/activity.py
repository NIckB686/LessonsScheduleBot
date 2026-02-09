from datetime import date, datetime  # noqa

from sqlalchemy import TIMESTAMP, BigInteger, Date, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Activity(Base):
    __tablename__ = "activity"

    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    activity_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    actions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )

    __table_args__ = (
        Index(
            "idx_activity_user_day",
            "user_id",
            "activity_date",
            unique=True,
        ),
    )
