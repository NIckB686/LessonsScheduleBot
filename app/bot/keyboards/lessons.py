from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callback import ScheduleCallbackFactory

_buttons = {
    "curr": InlineKeyboardButton(text=">>", callback_data=ScheduleCallbackFactory(week="next").pack()),
    "next": InlineKeyboardButton(text="<<", callback_data=ScheduleCallbackFactory(week="curr").pack()),
}


def get_lessons_keyboard(pressed: Literal["curr", "next"] = "curr") -> InlineKeyboardMarkup:  # noqa: FBT001
    builder = InlineKeyboardBuilder()
    btn = _buttons[pressed]
    builder.row(btn)
    return builder.as_markup()
