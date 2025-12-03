import datetime
from itertools import groupby
from typing import Any, Iterable, LiteralString, Sequence

from aiohttp import ClientSession

from app.models import Lesson


async def _register(session: ClientSession) -> int:
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


async def get_my_group_id(session: ClientSession):
    faculty_id = await get_my_faculty(session)
    groups = await get_groups_by_faculty(session, faculty_id)
    for group in groups["rows"]:
        if group["code"] == "УГЦ-24-05":
            return group["id"]
    return None


async def get_schedule_by_date_and_group_id(
        session: ClientSession, date, group_id: int,
):
    async with session.get(
            f"https://lk.gubkin.ru/schedule/api/api.php?act=schedule&date={date}&groupId={group_id}",
    ) as resp:
        return await resp.json()


async def get_schedule(session: ClientSession):
    group_id = await get_my_group_id(session)
    date = datetime.date.today().strftime("%d-%m-%Y")
    schedule = await get_schedule_by_date_and_group_id(session, date, group_id)
    organisations = schedule["rows"]["organizations"]
    for org in organisations:
        if org["name"] == "Ташкент":
            lessons = org["lessons"]
            time_chunks = org["lessonsTimeChunks"]
            return lessons, time_chunks
    return None


def merge_strings(strings: Sequence[str]):
    if not strings:
        return ""

    return "".join((strings[0].split("-")[0], "-", strings[-1].split("-")[-1]))


def time_key(lesson: Lesson) -> datetime.datetime:
    start = lesson.time.split("-")[0]
    return datetime.datetime.strptime(start, "%H:%M")


def get_lesson_rooms(lesson: dict) -> tuple[str]:
    if "rooms" in lesson["changes"]:
        rooms = tuple(room["number"] for room in lesson["changes"]["rooms"])
    else:
        rooms = tuple(room["number"] for room in lesson["rooms"])
    return rooms


def get_lesson_teachers(lesson: dict) -> tuple[LiteralString, ...]:
    if "teachers" in lesson["changes"]:
        teachers_list = lesson['changes']['teachers']
    else:
        teachers_list = lesson['teachers']
    teachers = tuple(
        (' '.join(tuple((teacher['lastName'], teacher['firstName'], teacher['patronymic'])))
         for teacher in teachers_list))
    return teachers


subgroup_dict = {
    0: '',
    1: '1-группа',
    2: '2-группа',
}


def parse_schedule(lessons: dict, time_chunks: dict) -> set[Lesson]:
    res = set()
    for lesson in lessons:
        if lesson['isCanceled']:
            continue
        course = lesson["course"]["name"]
        groups = tuple(name["code"] for name in lesson["groups"])
        is_canceled = lesson["isCanceled"]
        is_moved = lesson["isMoved"]
        rooms = get_lesson_rooms(lesson)
        teachers = get_lesson_teachers(lesson)
        _type = lesson["type"]
        week_day_number = lesson["weekDayNumber"]
        subgroup = lesson['subgroup']
        time = merge_strings(
            tuple(time_chunks[chunk] for chunk in lesson["timeChunks"]),
        )
        res.add(
            Lesson(
                course=course,
                groups=groups,
                is_canceled=is_canceled,
                is_moved=is_moved,
                rooms=rooms,
                teachers=teachers,
                type=_type,
                subgroup=subgroup_dict[subgroup],
                week_day_number=week_day_number,
                time=time,
            ),
        )
    return res


def group_and_sort_lessons(lessons: Iterable[Lesson]):
    sorted_lessons = sorted(lessons, key=lambda x: (x.week_day_number, time_key(x)))
    grouped_lessons = groupby(sorted_lessons, key=lambda x: x.week_day_number)
    return [list(group) for _, group in grouped_lessons]


async def get_sched(session: ClientSession) -> set[Lesson]:
    schedule = await get_schedule(session)
    return parse_schedule(*schedule)
