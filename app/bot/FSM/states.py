from aiogram.fsm.state import State, StatesGroup


class FSMRegistration(StatesGroup):
    fill_group = State()
