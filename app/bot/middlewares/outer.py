import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, logger=__name__):
        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)

        self.logger = logger

        super(LoggingMiddleware, self).__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        self.logger.debug("Got new event: %s", event.__class__.__name__)
        try:
            result = await handler(event, data)
            self.logger.debug("Handled event: %s")
            return result
        except Exception as e:
            self.logger.exception("Error in handler: %s", e)
            raise
