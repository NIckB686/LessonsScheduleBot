import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import insert, select, update

from app.db.models.user import User

if TYPE_CHECKING:
    import sqlalchemy.ext.asyncio

logger = logging.getLogger(__name__)


class SQLRepo:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncSession):
        self.conn = conn

    async def add_user(
        self,
        *,
        user_id: int,
        username: str | None = None,
        is_alive: bool = True,
        banned: bool = False,
    ) -> None:
        stmt = insert(User).values(
            user_id=user_id,
            username=username,
            is_alive=is_alive,
            banned=banned,
        )
        await self.conn.execute(stmt)

        logger.info(
            "User added. Table=`%s`, user_id=%d, created_at='%s', is_alive=%s, banned=%s",
            "users",
            user_id,
            datetime.now(UTC),
            is_alive,
            banned,
        )

    async def get_user(
        self,
        *,
        user_id: int,
    ) -> User | None:
        stmt = select(User).where(User.user_id == user_id)
        data = await self.conn.execute(stmt)
        row = data.scalar_one_or_none()
        if row is not None:
            logger.info("Found user with 'user_id=%s'", row.user_id)
        else:
            logger.warning("No user with `user_id`=%s found in the database", user_id)
        return row

    async def get_user_group_id(
        self,
        *,
        user_id: int,
    ):
        stmt = select(User.group_id).where(User.user_id == user_id)
        data = await self.conn.execute(stmt)
        row = data.scalar_one_or_none()
        if row is not None:
            logger.info("The user with 'user_id=%s' has the group_id is %d", user_id, row)
        else:
            logger.warning("No user with `user_id`=%s found in the database", user_id)
        return row

    async def update_user_group(
        self,
        *,
        user_id: int,
        group_id: int,
    ) -> None:
        stmt = update(User).where(User.user_id == user_id).values(group_id=group_id)
        await self.conn.execute(stmt)
        logger.info("Updated 'user_id' to %d for user %d", group_id, user_id)

    async def change_user_alive_status(
        self,
        *,
        is_alive: bool,
        user_id: int,
    ) -> None:
        stmt = update(User).where(User.user_id == user_id).values(is_alive=is_alive)
        await self.conn.execute(stmt)
        logger.info("Updated `is_alive` status to `%s` for user %d", is_alive, user_id)

    async def change_user_banned_status_by_id(
        self,
        *,
        banned: bool,
        user_id: int,
    ) -> None:
        stmt = update(User).where(User.user_id == user_id).values(banned=banned)
        await self.conn.execute(stmt)
        logger.info("Updated `banned` status to `%s` for user %d", banned, user_id)

    async def change_user_banned_status_by_username(
        self,
        *,
        banned: bool,
        username: str,
    ) -> None:
        stmt = update(User).where(User.username == username).values(banned=banned)
        await self.conn.execute(stmt)
        logger.info("Updated `banned` status to `%s` for username %s", banned, username)

    async def get_user_alive_status(
        self,
        *,
        user_id: int,
    ) -> bool | None:
        stmt = select(User.is_alive).where(User.user_id == user_id)
        data = await self.conn.execute(stmt)
        row = data.scalar_one_or_none()
        if row is not None:
            logger.info("The user with `user_id`=%s has the is_alive status is %s", user_id, row)
        else:
            logger.warning("No user with `user_id`=%s found in the database", user_id)
        return row

    async def get_user_banned_status_by_id(
        self,
        *,
        user_id: int,
    ) -> bool | None:
        stmt = select(User.banned).where(User.user_id == user_id)
        data = await self.conn.execute(stmt)
        row = data.scalar_one_or_none()
        if row is not None:
            logger.info("The user with `user_id`=%s has the banned status is %s", user_id, row)
        else:
            logger.warning("No user with `user_id`=%s found in the database", user_id)
        return row

    async def get_user_banned_status_by_username(
        self,
        *,
        username: str,
    ) -> bool | None:
        stmt = select(User.banned).where(User.username == username)
        data = await self.conn.execute(stmt)
        row = data.scalar_one_or_none()
        if row is not None:
            logger.info("The user with `username`=%s has the banned status is %s", username, row)
        else:
            logger.warning("No user with `username`=%s found in the database", username)
        return row
