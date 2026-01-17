from aiogram.filters.callback_data import CallbackData


class GroupCallbackFactory(CallbackData, prefix="group"):
    group_id: int
