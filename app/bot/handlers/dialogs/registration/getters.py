from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_dialog import DialogManager


async def get_groups(dialog_manager: DialogManager, **kwargs) -> dict[str, tuple]:
    return {"groups": dialog_manager.dialog_data["groups"]}
