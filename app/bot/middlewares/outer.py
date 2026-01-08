import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


class DataBaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async_session_maker: async_sessionmaker[AsyncSession] = data.get(
            "session_maker",
        )  # ty:ignore[invalid-assignment]
        if async_session_maker is None:
            logger.error("Session maker not provided in middleware data.")
            raise RuntimeError("Missing session_maker in middleware context.")
        async with async_session_maker() as session:
            try:
                async with session.begin():
                    data["db_session"] = session
                    result = await handler(event, data)
            except Exception as e:
                logger.exception("Transaction rolled back due to error: %s", e)
                raise
        return result
