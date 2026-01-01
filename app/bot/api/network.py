import datetime
import logging
from typing import Any

from aiohttp import ClientSession

from app.bot.api.models import Lesson, LessonsData

logger = logging.getLogger(__name__)

class GubkinAPIError(Exception):
    pass

class ScheduleClient:
    BASE_URL = "https://lk.gubkin.ru/schedule/"
    API_URL = f"{BASE_URL}/api/api.php"

    TARGET_FACULTY_CODE = "ТАШКЕНТ"
    TARGET_GROUP_CODE = "УГЦ-24-05"
    TARGET_ORG_NAME = "Ташкент"

    def __init__(self, session: ClientSession):
        self.session = session

    async def _make_request(self, url: str) -> dict[str, Any]:
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def register(self) -> int:
        async with self.session.get(f"{self.BASE_URL}/") as resp:
            return resp.status

    async def get_faculties(self) -> dict[str, Any]:
        url = f"{self.API_URL}?act=list&method=getFaculties"
        return await self._make_request(url)

    async def get_faculty_id(self, faculty_code: str) -> int:
        faculties = await self.get_faculties()
        for row in faculties.get("rows", []):
            if row.get("code") == faculty_code:
                return row["id"]

        raise GubkinAPIError(f"Факультет с кодом {faculty_code} не найден")

    async def get_groups_by_faculty(self, faculty_id: int) -> dict[str, Any]:
        url = f"{self.API_URL}?act=list&method=getFacultyGroups&facultyId={faculty_id}"
        return await self._make_request(url)

    async def get_group_id(self, faculty_code: str, group_code: str) -> int:
        faculty_id = await self.get_faculty_id(faculty_code)
        groups = await self.get_groups_by_faculty(faculty_id)

        for group in groups.get("rows", []):
            if group.get("code") == group_code:
                return group["id"]

        raise GubkinAPIError(f"Группа {group_code} не найдена на факультете {faculty_code}")

    async def get_schedule_by_date(self, group_id: int, date: str | None = None) -> dict[str, Any]:
        if date is None:
            date = datetime.date.today().strftime("%d-%m-%Y")

        url = f"{self.API_URL}?act=schedule&date={date}&groupId={group_id}"
        return await self._make_request(url)

    async def get_organization_schedule(self, org_name: str, date: str | None = None) -> dict[str, Any] | None:
        group_id = await self.get_group_id(self.TARGET_FACULTY_CODE, self.TARGET_GROUP_CODE)
        schedule = await self.get_schedule_by_date(group_id, date)
        organizations = schedule.get("rows", {}).get("organizations", [])
        for org in organizations:
            if org.get("name") == org_name:
                return org

        return None

    async def get_lessons(self, date: str | None = None) -> list[Lesson]:
        schedule = await self.get_organization_schedule(self.TARGET_ORG_NAME, date)

        if schedule is None:
            logger.warning("Расписание не найдено, возвращается пустой список")
            return []

        logger.debug("Расписание получено и передано в парсер")
        return LessonsData.model_validate(schedule).lessons


async def get_sched(session: ClientSession) -> list[Lesson]:
    client = ScheduleClient(session)
    if (resp := await client.register()) == 200:
        return await client.get_lessons()
    else:
        raise GubkinAPIError(f"Сервер вернул неверный ответ: {resp}")
