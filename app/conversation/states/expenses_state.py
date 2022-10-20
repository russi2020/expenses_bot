from aiogram.dispatcher.filters.state import StatesGroup, State


class ExpensesInsertState(StatesGroup):
    expenses_string = State()
