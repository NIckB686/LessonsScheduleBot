from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callback import GroupCallbackFactory

if TYPE_CHECKING:
    from app.api import ScheduleService


async def get_group_keyboard(schedule_service: ScheduleService) -> InlineKeyboardMarkup:
    groups = await schedule_service.get_groups()
    builder = InlineKeyboardBuilder()

    res = [
        InlineKeyboardButton(text=group.code, callback_data=GroupCallbackFactory(group_id=group.id).pack())
        for group in groups
    ]
    builder.row(*res, width=3)
    builder.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return builder.as_markup()
