from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram_dialog import DialogManager


async def loading_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, str]:
    locale: dict[str, str] = dialog_manager.start_data["locale"]  # ty:ignore[not-subscriptable, invalid-argument-type]
    return {"text": locale["/register_loading"]}


async def get_groups(dialog_manager: DialogManager, **kwargs) -> dict[str, str | tuple[str, str]]:
    locale: dict[str, str] = dialog_manager.start_data["locale"]  # ty:ignore[invalid-argument-type, not-subscriptable]
    return {
        "groups": dialog_manager.dialog_data["groups"],
        "text": locale["/register"],
    }
