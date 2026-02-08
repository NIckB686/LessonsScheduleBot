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
