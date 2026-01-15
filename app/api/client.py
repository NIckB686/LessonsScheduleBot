from collections.abc import Iterable

from aiohttp import ClientSession

from app.api import network
from app.api.models import Lesson
from app.api.parsing import group_and_sort_lessons


async def get_lessons() -> Iterable[tuple[str, Iterable[Lesson]]]:
    async with ClientSession() as session:
        lessons = [
            lesson
            for lesson in await network.get_sched(session)
            if not (lesson.is_canceled or lesson.is_moved)
        ]
        return group_and_sort_lessons(lessons) if lessons else []
