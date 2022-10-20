from aiogram.dispatcher.filters.state import StatesGroup, State


class AuthorizationState(StatesGroup):
    email_check = State()
