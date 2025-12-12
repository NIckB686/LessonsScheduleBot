import datetime
import logging
from typing import Any

from aiohttp import ClientSession

from app.models import Lesson, LessonsData

logger = logging.getLogger(__name__)


async def register(session: ClientSession) -> int:
    async with session.get("https://lk.gubkin.ru/schedule/") as resp:
        return resp.status


async def get_faculties(session: ClientSession) -> Any:
    async with session.get(
            "https://lk.gubkin.ru/schedule/api/api.php?act=list&method=getFaculties",
    ) as resp:
        return await resp.json()


async def get_my_faculty(session: ClientSession):
    faculties = await get_faculties(session)
    for row in faculties["rows"]:
        if row["code"] == "ТАШКЕНТ":
            return row["id"]
    return None


async def get_groups_by_faculty(session: ClientSession, faculty_id: int):
    async with session.get(
            f"https://lk.gubkin.ru/schedule/api/api.php?act=list&method=getFacultyGroups&facultyId={faculty_id}",
    ) as resp:
        return await resp.json()


async def get_my_group_id(session: ClientSession) -> int | None:
    faculty_id = await get_my_faculty(session)
    groups = await get_groups_by_faculty(session, faculty_id)
    for group in groups["rows"]:
        if group["code"] == "УГЦ-24-05":
            return group["id"]
    return None


async def get_schedule_by_date_and_group_id(session: ClientSession, date, group_id: int) -> dict:
    async with session.get(
            f"https://lk.gubkin.ru/schedule/api/api.php?act=schedule&date={date}&groupId={group_id}",
    ) as resp:
        return await resp.json()


async def get_schedule(session: ClientSession) -> dict | None:
    group_id = await get_my_group_id(session)
    date = datetime.date.today().strftime("%d-%m-%Y")
    schedule = await get_schedule_by_date_and_group_id(session, date, group_id)
    organisations = schedule["rows"]["organizations"]
    for org in organisations:
        if org["name"] == "Ташкент":
            return org
    logger.debug('Расписание не найдено')
    return None


async def get_sched(session: ClientSession) -> list[Lesson]:
    schedule = await get_schedule(session)
    logger.debug('Расписание получено и передано в парсер')
    return LessonsData.model_validate(schedule).lessons
