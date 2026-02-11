import logging
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject, Update
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


class DataBaseMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.db_pool = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:  # ty:ignore[invalid-method-override]
        async with self.db_pool() as connection:
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
