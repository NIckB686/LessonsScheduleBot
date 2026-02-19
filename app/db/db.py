from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import Config

config = Config.load().postgres
engine = create_async_engine(
    url=config.url,
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
