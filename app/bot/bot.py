import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers.user import router
from config import Config

logger = logging.getLogger(__name__)


async def main(config: Config) -> None:
    dp = create_dispatcher(config)
    bot = create_bot(config)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.exception(e)


def create_dispatcher(config: Config) -> Dispatcher:
    dp = Dispatcher(storage=get_storage(config))
    dp.include_router(router)
    return dp


def create_bot(config: Config) -> Bot:
    return Bot(
        token=config.tg.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def get_storage(config: Config):
    # TODO: нужно будет сделать проверку и возвращать MemoryStorage или RedisStorage в зависимости от значения в конфиге
    return MemoryStorage()
