import logging

from aiogram import Bot, Router
from aiogram.enums import BotCommandScopeType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommandScopeChat, CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.callback import ScheduleCallbackFactory
from app.bot.FSM.states import FSMRegistration
from app.bot.keyboards.main_menu import get_main_menu_commands
from app.bot.services.show_schedule import show_schedule

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


# # этот хендлер срабатывает на команду /register и переключает бота в состояние ожидания ввода группы
# @user_router.message(Command(commands="register"))
# async def process_register(message: Message, state: FSMContext):
#     msg = await message.reply("⏳ Получаю список учебных групп…")
#     kb = await get_group_keyboard()
#     await msg.edit_text(
#         text="""👥 Выбор учебной группы
#
# Пожалуйста, выбери свою группу из списка ниже 👇
# Если допустил ошибку, группу можно будет изменить позже.""",
#         reply_markup=kb,
#     )
#     await state.set_state(FSMRegistration.fill_group)
#
#
# # этот хендлер будет срабатывать если пользователь выбрал группу
# @user_router.callback_query(GroupCallbackFactory.filter())
# async def process_group_press(
#     callback: CallbackQuery,
#     state: FSMContext,
#     conn: AsyncSession,
#     callback_data: GroupCallbackFactory,
# ):
#     group_id = callback_data.group_id
#     await update_user_group(
#         conn,
#         user_id=callback.from_user.id,
#         group_id=group_id,
#     )
#     await state.clear()
#     await callback.message.edit_text(  # ty:ignore[possibly-missing-attribute]
#         """✅ Регистрация завершена
#
# Ты успешно зарегистрирован и привязан к выбранной группе.
#
# 📅 Чтобы получить расписание занятий, отправь команду /schedule""",
#     )
#
#
# # этот хендлер срабатывает если пользователь нажимает на кнопку отмены при выборе группы и сбрасывает состояние
# @user_router.callback_query(StateFilter(FSMRegistration.fill_group), F.data.in_(["cancel"]))
# async def process_cancel_registration(state: FSMContext, callback: CallbackQuery):
#     await callback.message.delete()  # ty:ignore[possibly-missing-attribute]
#     await state.clear()


@user_router.message(Command(commands="schedule"))
async def process_schedule_command(
    message: Message,
    conn: AsyncSession,
):
    msg = await message.reply("""📡 Загружаю расписание занятий…
Это может занять несколько секунд.""")
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
