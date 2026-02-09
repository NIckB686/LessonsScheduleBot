import logging
from typing import TYPE_CHECKING

from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command, CommandStart
from aiogram.types import BotCommandScopeChat, CallbackQuery, ChatMemberUpdated, Message
from aiogram_dialog import DialogManager, StartMode

from app.bot.callback import ScheduleCallbackFactory
from app.bot.FSM.states import FSMRegistration
from app.bot.keyboards.main_menu import get_main_menu_commands
from app.bot.services.show_schedule import show_schedule

if TYPE_CHECKING:
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
):
    await message.answer(
        text="""📚 Расписание занятий РГУ нефти и газа (НИУ) им. И. М. Губкина — Ташкент

Этот бот помогает студентам филиала в Ташкенте быстро получать актуальное расписание занятий по своей группе.

Чтобы начать работу, пройди регистрацию и выбери свою учебную группу.

➡️ Отправь команду /register""",
    )
    await bot.set_my_commands(
        commands=get_main_menu_commands(),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT,
            chat_id=message.from_user.id,  # ty:ignore[possibly-missing-attribute]
        ),
    )


@user_router.message(Command(commands="register"))
async def process_register(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(FSMRegistration.fill_group, mode=StartMode.RESET_STACK)


@user_router.message(Command(commands="schedule"))
async def process_schedule_command(
    message: Message,
    repo: SQLRepo,
):
    msg = await message.reply("""📡 Загружаю расписание занятий…
Это может занять несколько секунд.""")
    await show_schedule(
        user_id=message.from_user.id,  # ty:ignore[possibly-missing-attribute]
        msg=msg,
        repo=repo,
        week="curr",
    )


@user_router.callback_query(ScheduleCallbackFactory.filter())
async def process_switching_week_btn(callback: CallbackQuery, callback_data: ScheduleCallbackFactory, repo: SQLRepo):
    await show_schedule(
        user_id=callback.from_user.id,
        msg=callback.message,  # ty:ignore[invalid-argument-type]
        repo=repo,
        week=callback_data.week,
    )
