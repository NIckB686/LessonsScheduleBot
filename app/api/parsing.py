import datetime
import logging
from itertools import groupby
from typing import TYPE_CHECKING

from app.api.errors import GubkinParsingError
from app.api.models.faculty import Faculty, FacultyData
from app.api.models.group import Group, GroupData
from app.api.models.lesson import LessonsData

if TYPE_CHECKING:
    from collections.abc import Iterable

    from app.api.models import Lesson

logger = logging.getLogger(__name__)


def group_and_sort_lessons(
    lessons: Iterable[Lesson],
) -> Iterable[tuple[str, Iterable[Lesson]]]:
    sorted_lessons: list[Lesson] = sorted(lessons, key=lambda x: (x.week_day_number, time_key(x)))
    return groupby(sorted_lessons, key=(lambda x: " ".join((str(x.week_day), str(x.date)))))


def time_key(lesson: Lesson) -> datetime.datetime:
    start = lesson.time.split("-")[0]  # ty:ignore[unresolved-attribute]
    return datetime.datetime.strptime(start, "%H:%M")  # noqa: DTZ007


class ScheduleParser:
    @staticmethod
    def parse_lessons(
        lessons_data: dict[str, object],
        organization_name: str,
    ) -> Iterable[tuple[str, Iterable[Lesson]]]:
        data = LessonsData.model_validate(lessons_data)
        for org in data.rows.organizations:
            if org.name == organization_name:
                logger.debug("Расписание получено, организация %s", org)
                return group_and_sort_lessons(org.lessons)
        raise GubkinParsingError("Organization '%s' not found", organization_name)

    @staticmethod
    def parse_groups(group_data: dict[str, object]) -> list[Group]:
        return GroupData.model_validate(group_data).rows

    @staticmethod
    def parse_faculties(faculty_data: dict[str, object]) -> list[Faculty]:
        return FacultyData.model_validate(faculty_data).rows
