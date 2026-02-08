from datetime import date as dt
from datetime import timedelta
from typing import Literal

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import get_lessons
from app.bot.keyboards.lessons import get_lessons_keyboard
from app.bot.services.reformat_lessons import reformat_lessons
from app.db.requests.users import get_user_group_id


def resolve_target_date(week: Literal["curr", "next"]) -> dt:
    return dt.today() if week == "curr" else dt.today() + timedelta(days=7)


async def show_schedule(
        *,
        user_id: int,
        msg: Message,
        conn: AsyncSession,
        week: Literal["curr", "next"]
):
    user_group = await get_user_group_id(conn, user_id=user_id)
    if not user_group:
        await msg.edit_text(
            "Вы сможете увидеть расписание только после регистрации. "
            "Для прохождения регистрации отправьте команду /register",
        )
        return
    date = resolve_target_date(week)
    lessons = await get_lessons(group_id=user_group, date=date)
    reformatted_lessons = reformat_lessons(lessons, date)
    await msg.edit_text(**reformatted_lessons.as_kwargs(), reply_markup=get_lessons_keyboard(week))
