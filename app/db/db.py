from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import Config

config = Config.load().postgres
engine = create_async_engine(
    url=config.get_url,
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
