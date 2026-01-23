from aiogram.types import BotCommand


def get_main_menu_commands() -> list[BotCommand]:
    return [
        BotCommand(
            command="/start",
            description="Перезапустить бота",
        ),
        BotCommand(
            command="/register",
            description="Выбрать группу",
        ),
        BotCommand(
        command="/schedule",
            description="Получить расписание",
        )
    ]
