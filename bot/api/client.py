from typing import Iterable

from aiohttp import ClientSession

from bot.api import network
from bot.api.network import register
from bot.api.parsing import group_and_sort_lessons
from bot.models import Lesson


async def get_lessons() -> Iterable[tuple[str, Iterable[Lesson]]]:
    async with ClientSession() as session:
        await register(session)
        lessons = [
            lesson
            for lesson in await network.get_sched(session)
            if not (lesson.is_canceled or lesson.is_moved)
        ]
        return group_and_sort_lessons(lessons)
