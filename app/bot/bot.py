import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.handlers.user import user_router
from app.bot.middlewares.database import DataBaseMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.statistics import ActivityCounterMiddleware
from app.db.connection import get_pg_engine
from config import Config

logger = logging.getLogger(__name__)


async def main(config: Config) -> None:
    bot = create_bot(config)
    dp = create_dispatcher(config)
    engine = await get_pg_engine(
        db_name=config.postgres.DB,
        host=config.postgres.HOST,
        port=config.postgres.PORT,
        user=config.postgres.USER,
        password=config.postgres.PASSWORD,
    )
    session_maker = async_sessionmaker(engine)
    logger.info("Including routers...")
    dp.include_routers(user_router)

    logger.info("Including middlewares...")
    dp.update.middleware(DataBaseMiddleware())  # ty:ignore[invalid-argument-type]
    dp.update.middleware(ShadowBanMiddleware())  # ty:ignore[invalid-argument-type]
    dp.update.middleware(ActivityCounterMiddleware())  # ty:ignore[invalid-argument-type]

    try:
        await dp.start_polling(
            bot,
            session_maker=session_maker,
        )
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.exception(e)
    finally:
        await engine.dispose()
        logger.info("Connection to Postgres closed")


def create_dispatcher(config: Config) -> Dispatcher:
    return Dispatcher(storage=get_storage(config))


def create_bot(config: Config) -> Bot:
    return Bot(
        token=config.tg.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def get_storage(config: Config):
    # TODO: нужно будет сделать проверку и возвращать MemoryStorage или RedisStorage в зависимости от значения в конфиге
    return MemoryStorage()
