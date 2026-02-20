from aiogram.types import BotCommand


def get_main_menu_commands(locale: dict[str, str]) -> list[BotCommand]:
    return [
        BotCommand(
            command="/start",
            description=locale["/start_description"],
        ),
        BotCommand(
            command="/register",
            description=locale["/register_description"],
        ),
        BotCommand(
            command="/schedule",
            description=locale["/schedule_description"],
        ),
    ]
