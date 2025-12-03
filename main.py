import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

from app.handlers.router import router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
LOCAL_WEBAPP_HOST = "0.0.0.0"
LOCAL_WEBAPP_PORT = 8080
WEBHOOK_BASE_URL = 'https://nidmo-213-230-82-212.a.free.pinggy.link'
WEBHOOK_PATH = '/bots/webhook'


def main() -> None:
    load_dotenv()
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    bot = Bot(token=os.getenv("BOT_TOKEN"))  # type: ignore[arg-type]
    app = web.Application()
    webhook_request_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, )
    webhook_request_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=LOCAL_WEBAPP_HOST, port=LOCAL_WEBAPP_PORT)


async def startup(bot: Bot):
    await bot.set_webhook(f'{WEBHOOK_BASE_URL}{WEBHOOK_PATH}')
    logging.info("Bot started up...")


async def shutdown(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot shutting down...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Bot stopped")
