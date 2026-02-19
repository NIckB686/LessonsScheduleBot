import logging
from datetime import date as dt
from typing import TYPE_CHECKING

from app.api.network import ScheduleClient
from app.api.parsing import ScheduleParser

if TYPE_CHECKING:
    from collections.abc import Iterable

    from aiohttp import ClientSession

    from app.api.models import Lesson
    from app.api.models.faculty import Faculty
    from app.api.models.group import Group

logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self, session: ClientSession):
        self.client = ScheduleClient(session)
        self.parser = ScheduleParser()

    async def get_lessons(
        self,
        group_id: int,
        org_name: str = "Ташкент",
        date: dt | None = None,
    ) -> Iterable[tuple[str, Iterable[Lesson]]]:
        date: str = (date or dt.today()).strftime("%d-%m-%Y")
        await self.client.register()
        schedule = await self.client.get_schedule_by_date(group_id, date)
        return self.parser.parse_lessons(schedule, org_name)

    async def get_faculties(self) -> list[Faculty]:
        await self.client.register()
        faculties = await self.client.get_faculties()
        return self.parser.parse_faculties(faculties)

    async def get_groups(
        self,
        faculty_code: str = "ТАШКЕНТ",
    ) -> list[Group]:

        await self.client.register()
        faculties = await self.client.get_faculties()
        faculties = self.parser.parse_faculties(faculties)
        faculty_id = _get_faculty_id(faculties, faculty_code)
        groups = await self.client.get_groups_by_faculty_id(faculty_id)
        return self.parser.parse_groups(groups)


def _get_faculty_id(faculties: Iterable[Faculty], faculty_code: str) -> int:
    for faculty in faculties:
        if faculty.code == faculty_code:
            return faculty.id
    raise ValueError(f"Факультет с кодом {faculty_code!r} не найден")


def _get_group_id(groups: Iterable[Group], group_code) -> int:
    for group in groups:
        if group.code == group_code:
            return group.id
    raise ValueError(f"Группа с кодом {group_code!r} не найдена")
