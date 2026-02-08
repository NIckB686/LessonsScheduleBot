import operator

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, Group, Select
from aiogram_dialog.widgets.text import Const, Format

import app.api.client
from app.bot.FSM.states import FSMRegistration
from app.db.requests.users import update_user_group


async def get_groups(**kwargs) -> dict[str, tuple]:
    groups = await app.api.client.get_groups()
    return {"groups": tuple((group.code, group.id) for group in groups)}


async def on_group_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    await update_user_group(
        dialog_manager.middleware_data["conn"],
        user_id=callback.from_user.id,
        group_id=int(item_id),
    )
    await callback.message.edit_text(  # ty:ignore[possibly-missing-attribute]
        """✅ Регистрация завершена

Ты успешно зарегистрирован и привязан к выбранной группе.

📅 Чтобы получить расписание занятий, отправь команду /schedule""",
    )
    await dialog_manager.done()


fill_group_window = Window(
    Const(
        text="""👥 Выбор учебной группы

Пожалуйста, выбери свою группу из списка ниже 👇
Если допустил ошибку, группу можно будет изменить позже.""",
    ),
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

registration = Dialog(
    fill_group_window,
)
