import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command, CommandStart
from aiogram.types import BotCommandScopeChat, CallbackQuery, ChatMemberUpdated, Message
from aiogram_dialog import DialogManager, StartMode

from app.bot.callback import ScheduleCallbackFactory
from app.bot.FSM.states import FSMRegistration
from app.bot.handlers.dialogs.registration import load_groups
from app.bot.keyboards.main_menu import get_main_menu_commands
from app.bot.services.show_schedule import show_schedule

if TYPE_CHECKING:
    from app.api import ScheduleService
    from app.db.requests.users import SQLRepo

logger = logging.getLogger(__name__)

user_router = Router()


@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated, repo: SQLRepo):
    logger.info("Пользователь %s заблокировал бота. username: %s", event.from_user.id, event.from_user.username)
    await repo.change_user_alive_status(user_id=event.from_user.id, is_alive=False)


# хендлер срабатывает на команду /start вне состояний
# и предлагает перейти к регистрации, отправив команду /register
@user_router.message(CommandStart())
async def process_start_command(
    message: Message,
    bot: Bot,
    locale: dict[str, str],
):
    await message.answer(locale["/start"])
    await bot.set_my_commands(
        commands=get_main_menu_commands(locale),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT,
            chat_id=message.from_user.id,  # ty:ignore[unresolved-attribute]
        ),
    )


@user_router.message(Command(commands="register"))
async def process_register(
    message: Message, dialog_manager: DialogManager, schedule_service: ScheduleService, locale: dict[str, str]
):
    await dialog_manager.start(FSMRegistration.loading, mode=StartMode.RESET_STACK, data={"locale": locale})
    bg_manager = dialog_manager.bg(load=True)
    asyncio.create_task(load_groups(bg_manager, schedule_service))


@user_router.message(Command(commands="schedule"))
async def process_schedule_command(
    message: Message, repo: SQLRepo, schedule_service: ScheduleService, locale: dict[str, str]
):
    msg = await message.reply(locale["/schedule_loading"])
    await show_schedule(
        user_id=message.from_user.id,  # ty:ignore[unresolved-attribute]
        msg=msg,
        repo=repo,
        week="curr",
        service=schedule_service,
    )


@user_router.callback_query(ScheduleCallbackFactory.filter())
async def process_switching_week_btn(
    callback: CallbackQuery, callback_data: ScheduleCallbackFactory, repo: SQLRepo, schedule_service: ScheduleService
):
    await show_schedule(
        user_id=callback.from_user.id,
        msg=callback.message,  # ty:ignore[invalid-argument-type]
        repo=repo,
        week=callback_data.week,
        service=schedule_service,
    )
