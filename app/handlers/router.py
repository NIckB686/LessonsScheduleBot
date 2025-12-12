import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.api import get_lessons
from app.models import days_of_week

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def get_schedule(message: Message):
    lessons = await get_lessons()
    for day, group in lessons:
        text = f'{str(days_of_week[day])}\n\n' + '\n'.join(str(lesson) for lesson in group)
        await message.reply(text, parse_mode='HTML')
