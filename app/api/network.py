import logging
from typing import Any

from aiohttp import ClientSession

from app.api.errors import GubkinRegisterError

logger = logging.getLogger(__name__)


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
                raise GubkinRegisterError(f"Не удалось зарегистрироваться в Gubkin API. Статус: {resp.status}")
            self._registered = True
            logger.debug("Успешная регистрация в Gubkin API")

    async def get_faculties(self) -> dict[str, Any]:
        url = f"{self.API_URL}?act=list&method=getFaculties"
        return await self._make_request(url)

    async def get_groups_by_faculty_id(self, faculty_id: int) -> dict[str, Any]:
        url = f"{self.API_URL}?act=list&method=getFacultyGroups&facultyId={faculty_id}"
        return await self._make_request(url)

    async def get_schedule_by_date(self, group_id: int, date: str | None = None) -> dict[str, Any]:
        url = f"{self.API_URL}?act=schedule&date={date}&groupId={group_id}"
        return await self._make_request(url)
