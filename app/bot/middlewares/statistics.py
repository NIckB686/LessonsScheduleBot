import logging
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

from app.db.requests.activity import add_user_activity

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import Update, User
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ActivityCounterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:  # ty:ignore[invalid-method-override]

        user: User = data.get("event_from_user")  # ty:ignore[invalid-assignment]
        if user is None:
            return await handler(event, data)

        result = await handler(event, data)

        conn: AsyncSession = data.get("conn")  # ty:ignore[invalid-assignment]
        if conn is None:
            logger.error("No database connection found in middleware data.")
            raise RuntimeError("Missing database connection for activity logging.")

        await add_user_activity(conn, user_id=user.id)

        return result
