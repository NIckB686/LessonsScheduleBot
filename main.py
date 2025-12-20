import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.handlers.router import router
from app.setup_logging import setup_logging
from settings import settings

logger = logging.getLogger(__name__)


def main() -> None:
    dp = create_dispatcher()
    bot = create_bot()
    app = web.Application()
    webhook_request_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_request_handler.register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=settings.webapp_host, port=settings.webapp_port)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    logger.debug("Создан диспетчер")
    return dp


def create_bot() -> Bot:
    bot = Bot(
        token=settings.tg_bot_token.get_secret_value(),
    )
    logger.debug("Бот создан")
    return bot


async def startup(bot: Bot) -> None:
    await bot.set_webhook(url=settings.webhook_url, drop_pending_updates=True)


async def shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Вебхук удалён")


if __name__ == "__main__":
    try:
        setup_logging()
        main()
    except KeyboardInterrupt:
        logger.info("Бот завершает работу")
