from typing import Literal

from aiogram.filters.callback_data import CallbackData


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_id: int
    group_name: str


class ScheduleCallbackFactory(CallbackData, prefix="lessons"):
    week: Literal["curr", "next"]
