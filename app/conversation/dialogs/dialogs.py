from dataclasses import dataclass
from typing import Dict


months = {
    "01": ("january", "январь",),
    "02": ("february", "февраль",),
    "03": ("march", "март",),
    "04": ("april", "апрель",),
    "05": ("may", "май",),
    "06": ("june", "июнь",),
    "07": ("july", "июль",),
    "08": ("august", "август",),
    "09": ("september", "сентябрь",),
    "10": ("october", "октябрь",),
    "11": ("november", "ноябрь",),
    "12": ("december", "декабрь",),
}


@dataclass(frozen=True)
class Messages:
    main: str = "Что будем делать?"
    btn_back: str = "<- Назад"
    btn_forward: str = "Вперед ->"
    back_to_menu: str = "В меню"
    write_email: str = "Укажите вашу почту"
    insert_expense: str = "Введите информацию о расходах в формате 'Сумма валюта категория'. Например, 100 рублей " \
                          "продукты "
    authorization_success: str = "Добро пожаловать!"


@dataclass(frozen=True)
class ConfirmationCallbacks:
    email_confirm: str = "correct_email"
    email_not_confirm: str = "not_correct_email"


@dataclass(frozen=True)
class ButtonNames:
    back_to_menu: str = "Вернуться в меню"
    insert_expenses: str = "Внести информацию о расходах"
    get_expenses_info: str = "Получить статистику по расходам"


@dataclass(frozen=True)
class ButtonCallbacks:
    pass


msg = Messages()
confirmation_callbacks = ConfirmationCallbacks()
buttons_callbacks = ButtonCallbacks()
buttons_names = ButtonNames()
