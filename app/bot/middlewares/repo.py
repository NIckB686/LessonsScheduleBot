from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

from app.db.requests.users import SQLRepo

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject, Update


class RepoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:  # ty:ignore[invalid-method-override]
        conn = data["conn"]
        repo = SQLRepo(conn)
        data["repo"] = repo
        return await handler(event, data)
