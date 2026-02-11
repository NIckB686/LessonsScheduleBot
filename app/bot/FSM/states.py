from aiogram.fsm.state import State, StatesGroup


class FSMRegistration(StatesGroup):
    loading = State()
    fill_group = State()
