import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from app.bot.FSM.states import FSMRegistration
from app.bot.handlers.dialogs.registration.getters import get_groups, loading_getter
from app.bot.handlers.dialogs.registration.handlers import on_group_selected

loading_window = Window(
    Format("{text}"),
    getter=loading_getter,
    state=FSMRegistration.loading,
)

fill_group_window = Window(
    Format("{text}"),
    Group(
        Select(
            Format("{item[0]}"),
            id="s_groups",
            item_id_getter=operator.itemgetter(1),
            items="groups",
            on_click=on_group_selected,
        ),
        width=3,
    ),
    Cancel(Const("Отмена")),
    state=FSMRegistration.fill_group,
    getter=get_groups,
)


registration = Dialog(loading_window, fill_group_window)
