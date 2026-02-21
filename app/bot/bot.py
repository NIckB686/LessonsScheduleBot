import logging
from typing import TYPE_CHECKING, Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiohttp import ClientSession, web
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

    extra_data: dict[str, Any] = {"locale": RU}

    try:
        async with ClientSession(headers=headers) as session:
            extra_data["schedule_service"] = ScheduleService(session)
            if config.tg.bot.use_webhook:
                ...
            else:
                await _run_polling(bot, dp, extra_data)
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.exception("Непредвиденная ошибка: %s", e)
    finally:
        logger.info("Bot is shutting down...")
        await bot.session.close()
        await engine.dispose()
        logger.info("Connection to Postgres closed")


async def _run_polling(bot: Bot, dp: Dispatcher, extra_data: dict[str, Any]):
    logger.info("Запуск в режиме polling")
    await dp.start_polling(bot, **extra_data)


async def _run_webhook(bot: Bot, dp: Dispatcher, config: Config, extra_data: dict[str, Any]):
    webhook_cfg = config.tg.webhook
    webapp_cfg = config.tg.webapp

    logger.info("Устанавливаю вебхук: %s", webhook_cfg.url)
    await bot.set_webhook(
        url=webhook_cfg.url,
        secret_token=webhook_cfg.secret.get_secret_value(),
        drop_pending_updates=config.tg.bot.drop_pending_updates,
    )
    app = web.Application()
    dp.workflow_data.update(extra_data)
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=webhook_cfg.secret.get_secret_value() if webhook_cfg.secret else None,
    ).register(app, path=webhook_cfg.path)

    setup_application(app, dp, bot=bot)
    logger.info("Запуск webhook-сервера на %s%s%s", webapp_cfg.host, webapp_cfg.port, webhook_cfg.path)
    await web._run_app(app, host=webapp_cfg.host, port=webapp_cfg.port)


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
