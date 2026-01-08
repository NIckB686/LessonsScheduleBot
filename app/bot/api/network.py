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

    def __init__(self, session: ClientSession):
        self.session = session
        self._registered = False

    async def _make_request(self, url: str) -> dict[str, Any]:
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def register(self):
        async with self.session.get(f"{self.BASE_URL}/") as resp:
            if resp.status != 200:
                raise GubkinAPIError(f"Не удалось зарегистрироваться в Gubkin API. Статус: {resp.status}")
            self._registered = True
            logger.debug("Успешная регистрация в Gubkin API")

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

    async def get_lessons_for_group(self,
                                    faculty_code: str,
                                    group_code: str,
                                    org_name: str,
                                    date: str | None = None,
                                    ) -> list[Lesson]:
        try:
            group_id = await self.get_group_id(faculty_code, group_code)
            schedule = await self.get_schedule_by_date(group_id, date)

            organizations = schedule.get("rows", {}).get("organizations", [])
            for org in organizations:
                if org.get("name") == org_name:
                    logger.debug("Расписание получено для группы %s, организация %s" % (group_code, org_name))
                    return LessonsData.model_validate(org).lessons

            logger.info("Расписание для организации %s не найдено в группе %s" % (org_name, group_code))
            return []

        except GubkinAPIError as e:
            logger.error("Ошибка при получении расписания: %s", e)
            raise


async def get_sched(
        session: ClientSession,
        faculty_code: str = "ТАШКЕНТ",
        group_code: str = "УГЦ-24-05",
        org_name: str = "Ташкент",
        date: str | None = None,
) -> list[Lesson]:
    client = ScheduleClient(session)
    await client.register()
    return await client.get_lessons_for_group(
        faculty_code=faculty_code,
        group_code=group_code,
        org_name=org_name,
        date=date,
    )
