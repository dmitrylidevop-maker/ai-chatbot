from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration process"""
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_interests = State()
    waiting_for_language = State()
    waiting_for_bio = State()
