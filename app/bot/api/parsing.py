import datetime
from itertools import groupby
from typing import Iterable

from app.bot.models import Lesson


def group_and_sort_lessons(
    lessons: Iterable[Lesson],
) -> Iterable[tuple[str, Iterable[Lesson]]]:
    sorted_lessons = sorted(lessons, key=lambda x: (x.week_day_number, time_key(x)))
    grouped_lessons = groupby(sorted_lessons, key=lambda x: x.week_day)
    return grouped_lessons


def time_key(lesson: Lesson) -> datetime.datetime:
    start = lesson.time.split("-")[0]
    return datetime.datetime.strptime(start, "%H:%M")
