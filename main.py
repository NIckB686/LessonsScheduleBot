import asyncio
import logging

from app import setup_logging
from app.bot import main
from config import Config

setup_logging()
logger = logging.getLogger(__name__)

config = Config.load()

if __name__ == "__main__":
    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        logger.info("Bot stopped")
