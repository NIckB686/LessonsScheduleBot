from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.api.client import get_groups
from app.bot.callback import GroupCallbackFactory


async def get_group_keyboard() -> InlineKeyboardMarkup:
    groups = await get_groups()
    builder = InlineKeyboardBuilder()

    res = [
        InlineKeyboardButton(text=group.code, callback_data=GroupCallbackFactory(group_id=group.id).pack())
        for group in groups
    ]
    builder.row(*res, width=2)
    builder.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    return builder.as_markup()
