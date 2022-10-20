import logging
from os import path

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from app.conversation.dialogs.buttons import MenuButtons
from app.conversation.dialogs.dialogs import buttons_names, msg
from app.conversation.states.expenses_state import ExpensesInsertState
from db.db_functions import DbFunctions
from environment import Environment
from redis_repository.redis_repository import RedisRepository


def init_expenses_handler(dp: Dispatcher, db: DbFunctions, _env: Environment, redis: RedisRepository):
    log_file_path = path.join(path.dirname(path.abspath("__file__")), "logging.ini")
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("Start expenses_insert handler")

    @dp.message_handler(lambda m: m.text == buttons_names.back_to_menu, state="*")
    async def go_to_main_menu(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.answer(msg.back_to_menu,
                             reply_markup=MenuButtons.main_kb())

    @dp.message_handler(lambda m: m.text == buttons_names.get_expenses_info, state="*")
    async def start_expenses_insert(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=msg.back_to_menu,
            reply_markup=MenuButtons.back_to_menu()
        )
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=msg.insert_expense,
            reply_markup=None
        )
        await ExpensesInsertState.expenses_string.set()

    @dp.message_handler(lambda m: m.text not in buttons_names.__dict__.values(),
                        state=ExpensesInsertState.expenses_string)
    async def expenses_insert(message: types.Message, state: FSMContext):
        spending_sum, currency, category = message.text.split(" ")
        try:
            spending_sum = int(spending_sum)
        except ValueError:
            await message.answer(text="Введенная сумма не является числом")
            await start_expenses_insert
            return

        currency_id = db.check_currency(currency)
        if not currency_id:
            await message.answer(text="Введенной валюты нет в базе данных")
            await go_to_main_menu(message, state)
            return

        category_id = db.check_category(category)
        if not category_id:
            await message.answer(text="Введенной категории нет в базе данных")
            await go_to_main_menu(message, state)
            return

        telegram_id = db.get_user_id_by_telegram_id(telegram_id=message.from_user.id)
        db.insert_expense(spending_sum, currency_id, category_id, telegram_id)

        await message.answer("Расходы внесены")
