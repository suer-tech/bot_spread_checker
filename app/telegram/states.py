from aiogram.fsm.state import StatesGroup, State


class SaveCommon(StatesGroup):
    waiting_for_save_start = State()


class TextSave(StatesGroup):
    waiting_for_entry = State()
    waiting_for_value_signal = State()
