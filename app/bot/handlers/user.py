import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.client import get_lessons
from app.bot.callback import GroupCallbackFactory
from app.bot.FSM.states import FSMRegistration
from app.bot.keyboards.register import get_group_keyboard
from app.bot.reformat_lessons import reformat_lessons
from app.db.requests.users import get_user_group_id, update_user_group

logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(Command(commands="schedule"))
async def process_schedule_command(
    message: Message,
    conn: AsyncSession,
):
    user_group = await get_user_group_id(conn, user_id=message.from_user.id)  # ty:ignore[possibly-missing-attribute]
    if not user_group:
        await message.reply(
            "Вы сможете увидеть расписание только после регистрации. "
            "Для прохождения регистрации отправьте команду /register"
        )
        return
    msg = await message.reply("Подождите пожалуйста...")

    lessons = await get_lessons(user_group)
    if lessons:
        reformatted_lessons = reformat_lessons(lessons)
        await msg.edit_text(**reformatted_lessons.as_kwargs())
    else:
        await msg.edit_text("Уроков на этой неделе нет")


# хендлер срабатывает на команду /start вне состояний
# и предлагает перейти к регистрации, отправив команду /register
@user_router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text="Этот бот показывает расписание филиала РГУ им. И.М.Губкина в г. Ташкенте."
        "Чтобы зарегистрироваться - отправьте команду /register",
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
    await state.update_data(group_id=callback_data.group_id)
    await update_user_group(
        conn,
        user_id=callback.from_user.id,
        group_id=(await state.get_data()).get("group_id"),  # ty:ignore[invalid-argument-type]
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
