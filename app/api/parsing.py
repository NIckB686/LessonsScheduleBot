import datetime
import logging
from collections.abc import Iterable
from itertools import groupby

from app.api.models import Lesson
from app.api.models.faculty import Faculty, FacultyData
from app.api.models.group import Group, GroupData
from app.api.models.lesson import LessonsData

logger = logging.getLogger(__name__)


def group_and_sort_lessons(
    lessons: Iterable[Lesson],
) -> Iterable[tuple[str, Iterable[Lesson]]]:
    sorted_lessons = sorted(lessons, key=lambda x: (x.week_day_number, time_key(x)))
    return groupby(sorted_lessons, key=lambda x: x.week_day)


def time_key(lesson: Lesson) -> datetime.datetime:
    start = lesson.time.split("-")[0]
    return datetime.datetime.strptime(start, "%H:%M")


class ScheduleParser:
    @staticmethod
    def parse_lessons(
        lessons_data: dict[str, object],
        organization_name: str,
    ) -> Iterable[tuple[str, Iterable[Lesson]]]:
        data = LessonsData.model_validate(lessons_data)
        for org in data.rows.organizations:
            if org.name == organization_name:
                logger.debug("Расписание получено для группы %s, организация %s", org)
                return group_and_sort_lessons(org.lessons)
        raise

    @staticmethod
    def parse_groups(group_data: dict[str, object]) -> list[Group]:
        return GroupData.model_validate(group_data).rows

    @staticmethod
    def parse_faculties(faculty_data: dict[str, object]) -> list[Faculty]:
        return FacultyData.model_validate(faculty_data).rows
