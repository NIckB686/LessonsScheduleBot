import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.handlers.router import router
from settings import settings

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
LOCAL_WEBAPP_HOST = "0.0.0.0"
LOCAL_WEBAPP_PORT = 8080
WEBHOOK_BASE_URL = 'https://pgaga-213-230-82-212.a.free.pinggy.link'
WEBHOOK_PATH = '/bots/webhook'


def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    bot = Bot(settings.tg_bot_token.get_secret_value())
    app = web.Application()
    webhook_request_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, )
    webhook_request_handler.register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=settings.webapp_host, port=settings.webapp_port)


async def startup(bot: Bot):
    await bot.set_webhook(settings.webhook_url)
    logging.info(f"Bot started up: {await bot.get_me()}")


async def shutdown(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot shutting down...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Bot stopped")
