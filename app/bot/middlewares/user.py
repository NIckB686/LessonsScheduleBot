import logging
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

if TYPE_CHECKING:
    import collections.abc

    from aiogram.types import Update, User

    from app.db.requests.users import SQLRepo

logger = logging.getLogger(__name__)


class UserAddMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: collections.abc.Callable[[Update, dict[str, Any]], collections.abc.Awaitable[Any]],
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
