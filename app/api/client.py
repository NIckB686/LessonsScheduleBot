import logging
from datetime import date as dt
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from app.api.network import ScheduleClient
from app.api.parsing import ScheduleParser

if TYPE_CHECKING:
    from collections.abc import Iterable

    from app.api.models import Lesson
    from app.api.models.faculty import Faculty
    from app.api.models.group import Group

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
    )
}


async def get_lessons(
    group_id: int,
    org_name: str = "Ташкент",
    date: dt | None = None,
) -> Iterable[tuple[str, Iterable[Lesson]]]:
    async with ClientSession(headers=headers) as session:
        client = ScheduleClient(session)
        parser = ScheduleParser()
        if not date:
            date: dt = dt.today()
        date: str = date.strftime("%d-%m-%Y")
        await client.register()
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
    async with ClientSession(headers=headers) as session:
        client = ScheduleClient(session)
        parser = ScheduleParser()
        await client.register()
        faculties = await client.get_faculties()
        return parser.parse_faculties(faculties)


async def get_groups(
    faculty_code: str = "ТАШКЕНТ",
) -> list[Group]:
    async with ClientSession(headers=headers) as session:
        client = ScheduleClient(session)
        parser = ScheduleParser()
        await client.register()
        faculties = await client.get_faculties()
        faculties = parser.parse_faculties(faculties)
        faculty_id = _get_faculty_id(faculties, faculty_code)
        groups = await client.get_groups_by_faculty_id(faculty_id)
        return parser.parse_groups(groups)
