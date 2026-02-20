from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_dialog import DialogManager


async def loading_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, str]:
    return {"text": dialog_manager.start_data["locale"]["/register_loading"]}  # ty:ignore[invalid-argument-type, not-subscriptable]


async def get_groups(dialog_manager: DialogManager, **kwargs) -> dict[str, str | tuple[str, str]]:
    return {
        "groups": dialog_manager.dialog_data["groups"],
        "text": dialog_manager.start_data["locale"]["/register"],  # ty:ignore[invalid-argument-type, not-subscriptable]
    }
