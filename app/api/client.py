from typing import Iterable

from aiohttp import ClientSession

from app.api import network
from app.api.network import register
from app.api.parsing import group_and_sort_lessons
from app.models import Lesson


async def get_lessons() -> Iterable[tuple[str, Iterable[Lesson]]]:
    async with ClientSession() as session:
        await register(session)
        lessons = await network.get_sched(session)
        return group_and_sort_lessons(lessons)
