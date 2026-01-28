import logging

from aiogram import Bot, F, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.callback import GroupCallbackFactory, ScheduleCallbackFactory
from app.bot.FSM.states import FSMRegistration
from app.bot.keyboards.main_menu import get_main_menu_commands
from app.bot.keyboards.register import get_group_keyboard
from app.bot.services.show_schedule import show_schedule
from app.db.requests.users import update_user_group

logger = logging.getLogger(__name__)

user_router = Router()


# хендлер срабатывает на команду /start вне состояний
# и предлагает перейти к регистрации, отправив команду /register
@user_router.message(CommandStart())
async def process_start_command(
    message: Message,
    bot: Bot,
):
    await message.answer(
        text="Этот бот показывает расписание филиала РГУ им. И.М.Губкина в г. Ташкенте."
        "Чтобы зарегистрироваться - отправьте команду /register",
    )
    await bot.set_my_commands(
        commands=get_main_menu_commands(),
        scope=BotCommandScopeChat(
            type=BotCommandScopeType.CHAT,
            chat_id=message.from_user.id,  # ty:ignore[possibly-missing-attribute]
        ),
    )


# этот хендлер срабатывает на команду /register и переключает бота в состояние ожидания ввода группы
@user_router.message(Command(commands="register"))
async def process_register(message: Message, state: FSMContext):
    msg = await message.reply("Пожалуйста подождите...")
    kb = await get_group_keyboard()
    await msg.edit_text(
        text="Пожалуйста, выберите группу:",
        reply_markup=kb,
    )
    await state.set_state(FSMRegistration.fill_group)


# этот хендлер будет срабатывать если пользователь выбрал группу
@user_router.callback_query(GroupCallbackFactory.filter())
async def proces_group_press(
    callback: CallbackQuery,
    state: FSMContext,
    conn: AsyncSession,
    callback_data: GroupCallbackFactory,
):
    group_id = callback_data.group_id
    await update_user_group(
        conn,
        user_id=callback.from_user.id,
        group_id=group_id,
    )
    await state.clear()
    await callback.message.edit_text(  # ty:ignore[possibly-missing-attribute]
        "Вы прошли регистрацию, теперь вы можете получить расписание, отправив команду /schedule",
    )


# этот хендлер срабатывает если пользователь нажимает на кнопку отмены при выборе группы и сбрасывает состояние
@user_router.callback_query(StateFilter(FSMRegistration.fill_group), F.data.in_(["cancel"]))
async def process_cancel_registration(state: FSMContext, callback: CallbackQuery):
    await callback.message.delete()  # ty:ignore[possibly-missing-attribute]
    await state.clear()


@user_router.message(Command(commands="schedule"))
async def process_schedule_command(
    message: Message,
    conn: AsyncSession,
):
    msg = await message.reply("Подождите пожалуйста...")
    await show_schedule(
        user_id=message.from_user.id,  # ty:ignore[possibly-missing-attribute]
        msg=msg,
        conn=conn,
        week="curr",
    )


@user_router.callback_query(ScheduleCallbackFactory.filter())
async def process_switching_week_btn(
    callback: CallbackQuery, callback_data: ScheduleCallbackFactory, conn: AsyncSession
):
    await show_schedule(
        user_id=callback.from_user.id,
        msg=callback.message,  # ty:ignore[invalid-argument-type]
        conn=conn,
        week=callback_data.week,
    )
