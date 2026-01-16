import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.client import get_s
from app.bot.reformat_lessons import reformat_lessons
from app.db.requests.users import add_user, change_user_alive_status, get_user

logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
async def get_schedule(
        message: Message,
        conn: AsyncSession,
):
    user = await get_user(conn, user_id=message.from_user.id)  # ty:ignore[possibly-missing-attribute]
    if user is None:
        await add_user(
            conn,
            user_id=message.from_user.id,  # ty:ignore[possibly-missing-attribute]
            username=message.from_user.username,  # ty:ignore[possibly-missing-attribute]
        )
    else:
        await change_user_alive_status(
            conn,
            is_alive=True,
            user_id=message.from_user.id,  # ty:ignore[possibly-missing-attribute]
        )
    lessons = await get_s()
    if lessons:
        reformatted_lessons = reformat_lessons(lessons)
        await message.reply(**reformatted_lessons.as_kwargs())
    else:
        await message.reply("Уроков на этой неделе нет")
