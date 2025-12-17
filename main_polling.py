import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.handlers.router import router
from settings import settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    dp = create_dispatcher()
    bot = create_bot()
    await dp.start_polling(bot)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    logger.debug("Создан диспетчер")
    return dp


def create_bot() -> Bot:
    bot = Bot(
        token=settings.tg_bot_token.get_secret_value(),
    )
    logger.debug("Бот создан")
    return bot


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
