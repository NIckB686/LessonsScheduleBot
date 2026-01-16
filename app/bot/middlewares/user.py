import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import Update

from app.db.requests.users import add_user, change_user_alive_status, get_user

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserAddMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:  # ty:ignore[invalid-method-override]
        conn: AsyncSession = data.get("conn")  # ty:ignore[invalid-assignment]
        if conn is None:
            logger.error("No database connection found in middleware data.")
            raise RuntimeError("Missing database connection for activity logging.")

        user = await get_user(conn, user_id=event.message.from_user.id)  # ty:ignore[possibly-missing-attribute]
        if user is None:
            await add_user(
                conn,
                user_id=event.message.from_user.id,  # ty:ignore[possibly-missing-attribute]
                username=event.message.from_user.username,  # ty:ignore[possibly-missing-attribute]
            )
        else:
            await change_user_alive_status(
                conn,
                is_alive=True,
                user_id=event.message.from_user.id,  # ty:ignore[possibly-missing-attribute]
            )
        return await handler(event, data)
