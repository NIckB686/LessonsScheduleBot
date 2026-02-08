import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


class DataBaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:  # ty:ignore[invalid-method-override]
        db_pool: async_sessionmaker[AsyncSession] = data.get("session_maker")  # ty:ignore[invalid-assignment]

        if db_pool is None:
            logger.error("Database pool is not provided in middleware data.")
            raise RuntimeError("Missing db_pool in middleware context.")

        async with db_pool() as connection:
            try:
                data["conn"] = connection
                result = await handler(event, data)
                await connection.commit()
                logger.debug(
                    "Transaction commited successfully for update_id=%s",
                    event.update_id,
                )
            except Exception as e:
                logger.exception("Transaction rolled back due to error: %s", e)
                raise

        # Здесь может быть какой-то код, который выполнится в случае успешного завершения транзакции

        return result
