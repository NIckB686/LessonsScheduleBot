from typing import Iterable

from aiohttp import ClientSession

from app.bot.api import network
from app.bot.api.models import Lesson
from app.bot.api.network import register
from app.bot.api.parsing import group_and_sort_lessons


async def get_lessons() -> Iterable[tuple[str, Iterable[Lesson]]]:
    async with ClientSession() as session:
        await register(session)
        lessons = [
            lesson
            for lesson in await network.get_sched(session)
            if not (lesson.is_canceled or lesson.is_moved)
        ]
        return group_and_sort_lessons(lessons) if lessons else []
