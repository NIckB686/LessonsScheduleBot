from datetime import date as dt
from datetime import timedelta
from typing import TYPE_CHECKING, Literal

from app.bot.keyboards.lessons import get_lessons_keyboard
from app.bot.services.reformat_lessons import reformat_lessons

if TYPE_CHECKING:
    from aiogram.types import Message

    from app.api import ScheduleService
    from app.db.requests.users import SQLRepo


def resolve_target_date(week: Literal["curr", "next"]) -> dt:
    return dt.today() if week == "curr" else dt.today() + timedelta(days=7)  # noqa: DTZ011


async def show_schedule(
    *, user_id: int, msg: Message, repo: SQLRepo, week: Literal["curr", "next"], service: ScheduleService
):
    user_group = await repo.get_user_group_id(user_id=user_id)
    if not user_group:
        await msg.edit_text(
            "Вы сможете увидеть расписание только после регистрации. "
            "Для прохождения регистрации отправьте команду /register",
        )
        return
    date = resolve_target_date(week)
    lessons = await service.get_lessons(group_id=user_group, date=date)
    reformatted_lessons = reformat_lessons(lessons, date)
    await msg.edit_text(**reformatted_lessons.as_kwargs(), reply_markup=get_lessons_keyboard(week))
