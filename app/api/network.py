import logging
from typing import TYPE_CHECKING

from app.api.errors import GubkinRegisterError

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class ScheduleClient:
    BASE_URL = "https://lk.gubkin.ru/schedule/"
    API_URL = f"{BASE_URL}api/api.php"

    def __init__(self, session: ClientSession, redis: Redis):
        self.redis = redis
        self.session = session

    async def _make_request(self, url: str) -> str:
        res = await self.redis.get(url)
        if res:
            return res
        await self.register()
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            res = await resp.text()
            await self.redis.set(url, res, ex=21600)
            return res

    async def register(self):
        async with self.session.get(f"{self.BASE_URL}/") as resp:
            if resp.status != 200:
                raise GubkinRegisterError(f"Не удалось зарегистрироваться в Gubkin API. Статус: {resp.status}")
            logger.debug("Успешная регистрация в Gubkin API")

    async def get_faculties(self) -> str:
        url = f"{self.API_URL}?act=list&method=getFaculties"
        return await self._make_request(url)

    async def get_groups_by_faculty_id(self, faculty_id: int) -> str:
        url = f"{self.API_URL}?act=list&method=getFacultyGroups&facultyId={faculty_id}"
        return await self._make_request(url)

    async def get_schedule_by_date(self, group_id: int, date: str) -> str:
        url = f"{self.API_URL}?act=schedule&date={date}&groupId={group_id}"
        return await self._make_request(url)
