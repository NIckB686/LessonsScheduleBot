import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.api.client import get_lessons
from app.bot.reformat_lessons import reformat_lessons

logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
async def get_schedule(
    message: Message,
):
    lessons = await get_lessons()
    if lessons:
        reformatted_lessons = reformat_lessons(lessons)
        await message.reply(**reformatted_lessons.as_kwargs())
    else:
        await message.reply("Уроков на этой неделе нет")
