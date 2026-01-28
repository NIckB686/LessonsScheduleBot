from typing import Literal

from aiogram.filters.callback_data import CallbackData


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_id: int


class ScheduleCallbackFactory(CallbackData, prefix="lessons"):
    week: Literal["curr", "next"]
