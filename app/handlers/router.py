import logging
from itertools import groupby

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiohttp import ClientSession

from app.models import days_of_week
from app.network import _register, get_sched, time_key

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def get_schedule(message: Message):
    async with ClientSession() as session:
        await _register(session)
        lessons = groupby(sorted(await get_sched(session), key=lambda x: (x.week_day_number, time_key(x))),
                          key=lambda x: x.week_day_number)
    for day, group in lessons:
        text = f'{str(days_of_week[day])}\n\n' + '\n'.join(str(lesson) for lesson in group)
        await message.reply(text, parse_mode='HTML')
