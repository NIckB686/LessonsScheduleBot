from collections.abc import Iterable

from aiohttp import ClientSession

from app.api import network
from app.api.models import Lesson
from app.api.models.faculty import Faculty
from app.api.models.group import Group
from app.api.network import ScheduleClient
from app.api.parsing import ScheduleParser, group_and_sort_lessons


async def get_lessons() -> Iterable[tuple[str, Iterable[Lesson]]]:
    async with ClientSession() as session:
        lessons = [lesson for lesson in await network.get_sched(session) if not (lesson.is_canceled or lesson.is_moved)]
        return group_and_sort_lessons(lessons) if lessons else []


async def get_s(
    faculty_code: str = "ТАШКЕНТ",
    group_code: str = "УГЦ-24-05",
    org_name: str = "Ташкент",
    date: str | None = None,
) -> Iterable[tuple[str, Iterable[Lesson]]]:
    async with ClientSession() as session:
        client = ScheduleClient(session)
        parser = ScheduleParser()
        await client.register()
        faculties = await client.get_faculties()
        faculties = parser.parse_faculties(faculties)
        faculty_id = _get_faculty_id(faculties, faculty_code)
        groups = await client.get_groups_by_faculty(faculty_id)
        groups = parser.parse_groups(groups)
        group_id = _get_group_id(groups, group_code)
        schedule = await client.get_schedule_by_date(group_id, date)
        return parser.parse_lessons(schedule, org_name)


def _get_faculty_id(faculties: Iterable[Faculty], faculty_code: str) -> int:
    for faculty in faculties:
        if faculty.code == faculty_code:
            return faculty.id
    raise


def _get_group_id(groups: Iterable[Group], group_code) -> int:
    for group in groups:
        if group.code == group_code:
            return group.id
    raise


async def get_faculties() -> list[Faculty]:
    async with ClientSession() as session:
        client = ScheduleClient(session)
        parser = ScheduleParser()
        await client.register()
        faculties = await client.get_faculties()
        return parser.parse_faculties(faculties)
