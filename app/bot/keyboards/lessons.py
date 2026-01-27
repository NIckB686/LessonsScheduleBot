from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callback import ScheduleCallbackFactory


def get_lessons_keyboard(current: str, week_offset: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(*(
        InlineKeyboardButton(
            text="<<",
            callback_data=ScheduleCallbackFactory(
                current="",
                week_offset=week_offset - 1,
            ).pack(),
        ),
        InlineKeyboardButton(
            text=">>",
            callback_data=ScheduleCallbackFactory(
                current="",
                week_offset=week_offset,
            ).pack(),
        ),
    ))
    return builder.as_markup()
