import datetime
from itertools import groupby
from typing import Iterable

from aiohttp import ClientSession

from app.api import network
from app.api.network import register
from app.models import Lesson


async def get_lessons() -> Iterable[tuple[int, Iterable[Lesson]]]:
    async with ClientSession() as session:
        await register(session)
        lessons = await network.get_sched(session)
        return group_and_sort_lessons(lessons)


def group_and_sort_lessons(lessons: Iterable[Lesson]) -> Iterable[tuple[int, Iterable[Lesson]]]:
    sorted_lessons = sorted(lessons, key=lambda x: (x.week_day_number, time_key(x)))
    grouped_lessons = groupby(sorted_lessons, key=lambda x: x.week_day_number)
    return grouped_lessons


def time_key(lesson: Lesson) -> datetime.datetime:
    start = lesson.time.split("-")[0]
    return datetime.datetime.strptime(start, "%H:%M")
