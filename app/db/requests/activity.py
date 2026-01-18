import logging

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.activity import Activity

logger = logging.getLogger(__name__)


async def add_user_activity(
    session: AsyncSession,
    *,
    user_id: int,
) -> None:
    stmt = insert(Activity).values(user_id=user_id)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "activity_date"],
        set_={"actions": Activity.actions + 1},
    )
    await session.execute(stmt)

    logger.info("User activity updated. table=`activity`, user_id=%d", user_id)


async def get_statistics(session: AsyncSession) -> list[tuple[int, int]] | None:
    stmt = (
        select(
            Activity.user_id,
            func.sum(Activity.actions).label("total_actions"),
        )
        .group_by(Activity.user_id)
        .order_by(text("total_actions DESC"))
        .limit(5)
    )
    data = await session.execute(stmt)
    rows = data.all()
    logger.info("Users activity got from table=`activity`")
    return [*rows] if rows else None
