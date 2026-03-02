import logging
from typing import TYPE_CHECKING

from aiogram import Bot, F, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command, CommandStart, StateFilter
from aiogram.types import BotCommandScopeChat, CallbackQuery, ChatMemberUpdated, Message

from app.bot.callback import GroupCallbackFactory, ScheduleCallbackFactory
from app.bot.FSM.states import FSMRegistration
from app.bot.keyboards.main_menu import get_main_menu_commands
from app.bot.keyboards.register import get_group_keyboard
from app.bot.services.show_schedule import show_schedule

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

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
    message: Message,
    schedule_service: ScheduleService,
    state: FSMContext,
    locale: dict[str, str],
):
    msg = await message.reply(locale["/register_loading"])
    kb = await get_group_keyboard(schedule_service)
    await msg.edit_text(text=locale["/register"], reply_markup=kb)
    await state.set_state(FSMRegistration.fill_group)


@user_router.callback_query(GroupCallbackFactory.filter())
async def proces_group_press(
    callback: CallbackQuery,
    state: FSMContext,
    repo: SQLRepo,
    callback_data: GroupCallbackFactory,
    locale: dict[str, str],
):
    group_id = callback_data.group_id
    await repo.update_user_group(
        user_id=callback.from_user.id,
        group_id=group_id,
    )
    await state.clear()
    await callback.message.edit_text(locale["/register_successful"])  # ty:ignore[unresolved-attribute]


# этот хендлер срабатывает если пользователь нажимает на кнопку отмены при выборе группы и сбрасывает состояние
@user_router.callback_query(StateFilter(FSMRegistration.fill_group), F.data.in_(["cancel"]))
async def process_cancel_registration(state: FSMContext, callback: CallbackQuery):
    await callback.message.delete()  # ty:ignore[unresolved-attribute]
    await state.clear()


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
