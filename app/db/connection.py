import logging
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

logger = logging.getLogger(__name__)


def get_pg_url(
    db_name: str,
    host: str,
    port: int,
    user: str,
    password: str,
) -> str:
    conn_info = f"postgresql+psycopg://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{db_name}"
    logger.debug(
        "Building PostgreSQL connection string (password omitted): postgresql://%s@%s:%s/%s",
        quote_plus(user),
        host,
        port,
        db_name,
    )
    return conn_info


async def log_db_version(session: AsyncSession) -> None:
    try:
        async with session as s:
            result = await s.execute(text("SELECT version();"))
            db_version = result.scalar()
            logger.info("Connected to PostgreSQL version: %s", db_version)
    except Exception as e:
        logger.warning("Failed to fetch PostgreSQL version: %s", e)


async def get_pg_engine(
    db_name: str,
    host: str,
    port: int,
    user: str,
    password: str,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_timeout: float = 10.0,
    *,
    echo: bool = True,
) -> AsyncEngine:
    db_url = get_pg_url(db_name=db_name, host=host, port=port, user=user, password=password)

    try:
        engine = create_async_engine(
            db_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            echo=echo,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        async with AsyncSession(engine) as session:
            await log_db_version(session)
        logger.info("PostgreSQL engine created: pool_size=%s, max_overflow=%s", pool_size, max_overflow)
        return engine
    except Exception as e:
        logger.exception("Failed to initialize PostgreSQL engine: %s", e)
        raise
