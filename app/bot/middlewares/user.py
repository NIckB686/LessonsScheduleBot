import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import Update, User

if TYPE_CHECKING:
    from app.db.requests.users import SQLRepo

logger = logging.getLogger(__name__)


class UserAddMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:  # ty:ignore[invalid-method-override]
        repo: SQLRepo = data.get("repo")  # ty:ignore[invalid-assignment]
        if repo is None:
            logger.error("No database connection found in middleware data.")
            raise RuntimeError("Missing database connection for adding user")
        event_user: User = data.get("event_from_user")  # ty:ignore[invalid-assignment]
        user_id = event_user.id
        user = await repo.get_user(user_id=user_id)
        if user is None:
            await repo.add_user(
                user_id=event_user.id,
                username=event_user.username,
            )
        else:
            await repo.change_user_alive_status(
                is_alive=True,
                user_id=event_user.id,
            )
        return await handler(event, data)
