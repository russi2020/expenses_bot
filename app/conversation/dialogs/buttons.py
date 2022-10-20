from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.conversation.dialogs.dialogs import buttons_callbacks, buttons_names, msg


def authorize() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('Авторизоваться', callback_data='authorize'))
    return kb


def confirm_or_not_confirm_kb(confirm: str, not_confirm: str) -> InlineKeyboardMarkup:
    """
    Подтверждаем или не подтверждаем введенные данные
    :return: InlineKeyboardMarkup
    """
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton('Да', callback_data=confirm),
        InlineKeyboardButton('Нет', callback_data=not_confirm)
    )
    return kb


class ExpensesButtons:

    @classmethod
    def daily_schedule_kb(cls) -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        kb.add(
            KeyboardButton(buttons_names.weekday_tasks),
            KeyboardButton(buttons_names.weekend_tasks)
        )
        return kb


class MenuButtons:

    @classmethod
    def main_kb(cls):
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        kb.add(
            KeyboardButton(buttons_names.insert_expenses),
            KeyboardButton(buttons_names.get_expenses_info),
        )
        return kb

    @staticmethod
    def back_to_menu() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        kb.add(buttons_names.back_to_menu)
        return kb
