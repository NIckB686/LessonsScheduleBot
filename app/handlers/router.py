import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.api import get_lessons
from app.reformat_lessons import reformat_lessons

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def get_schedule(message: Message):
    lessons = await get_lessons()
    reformatted_lessons = reformat_lessons(lessons)
    await message.reply(**reformatted_lessons.as_kwargs())
