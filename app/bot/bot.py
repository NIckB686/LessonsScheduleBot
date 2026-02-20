import logging
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from aiohttp import ClientSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api import ScheduleService
from app.bot.handlers.dialogs.registration import registration
from app.bot.handlers.user import user_router
from app.bot.locales import RU
from app.bot.middlewares.db_conn import DataBaseMiddleware
from app.bot.middlewares.repo import RepoMiddleware
from app.bot.middlewares.shadow_ban import ShadowBanMiddleware
from app.bot.middlewares.statistics import ActivityCounterMiddleware
from app.bot.middlewares.user import UserAddMiddleware
from app.db.connection import get_pg_engine

if TYPE_CHECKING:
    from config import Config

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
    )
}


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
    setup_dialogs(dp)
    dp.include_router(user_router)
    dp.include_router(registration)

    logger.info("Including middlewares...")
    dp.update.middleware(DataBaseMiddleware(session_maker))  # ty:ignore[invalid-argument-type]
    dp.update.middleware(RepoMiddleware())  # ty:ignore[invalid-argument-type]
    dp.update.middleware(ShadowBanMiddleware())  # ty:ignore[invalid-argument-type]
    dp.update.middleware(UserAddMiddleware())  # ty:ignore[invalid-argument-type]
    dp.update.middleware(ActivityCounterMiddleware())  # ty:ignore[invalid-argument-type]
    locale = RU

    try:
        async with ClientSession(headers=headers) as session:
            schedule_service = ScheduleService(session)
            await dp.start_polling(bot, schedule_service=schedule_service, locale=locale)
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.exception(e)
    finally:
        logger.info("Bot is shutting down...")
        await bot.session.close()
        await engine.dispose()
        logger.info("Connection to Postgres closed")


def create_dispatcher(config: Config) -> Dispatcher:
    return Dispatcher(
        storage=get_storage(config),
    )


def create_bot(config: Config) -> Bot:
    return Bot(
        token=config.tg.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def get_storage(config: Config):
    return RedisStorage(
        redis=Redis(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.database,
            password=config.redis.password.get_secret_value(),
            username=config.redis.username,
        ),
        key_builder=DefaultKeyBuilder(with_destiny=True),
        state_ttl=300,
        data_ttl=600,
    )
