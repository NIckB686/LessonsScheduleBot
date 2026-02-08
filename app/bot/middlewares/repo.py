from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.db.requests.users import SQLRepo


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
        return handler(event, data)
