import logging
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject, Update, User

    from app.db.requests.users import SQLRepo

logger = logging.getLogger(__name__)


class ShadowBanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:  # ty:ignore[invalid-method-override]
        user: User = data.get("event_from_user")  # ty:ignore[invalid-assignment]

        if user is None:
            return await handler(event, data)

        repo: SQLRepo = data.get("repo")  # ty:ignore[invalid-assignment]
        if repo is None:
            logger.error("Database connection not found in middleware data.")
            raise RuntimeError("Missing database connection for shadow ban check.")

        user_banned_status = await repo.get_user_banned_status_by_id(user_id=user.id)

        if user_banned_status:
            logger.warning("Shadow-banned user tried to interact: %d", user.id)
            if event.callback_query:
                await event.callback_query.answer()
            return None

        return await handler(event, data)
