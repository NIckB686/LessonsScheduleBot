from typing import TYPE_CHECKING

from app.bot.FSM.states import FSMRegistration

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery
    from aiogram_dialog import BaseDialogManager, DialogManager
    from aiogram_dialog.widgets.kbd import Select

    from app.api import ScheduleService
    from app.db.requests.users import SQLRepo


async def load_groups(dialog_manager: BaseDialogManager, service: ScheduleService):
    groups = await service.get_groups()
    await dialog_manager.update({"groups": tuple((group.code, group.id) for group in groups)})
    await dialog_manager.switch_to(FSMRegistration.fill_group)


async def on_group_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    repo: SQLRepo = dialog_manager.middleware_data.get("repo")  # ty:ignore[invalid-assignment]
    await repo.update_user_group(
        user_id=callback.from_user.id,
        group_id=int(item_id),
    )
    await callback.message.edit_text(  # ty:ignore[possibly-missing-attribute]
        """✅ Регистрация завершена

Ты успешно зарегистрирован и привязан к выбранной группе.

📅 Чтобы получить расписание занятий, отправь команду /schedule""",
    )
    await dialog_manager.done()
