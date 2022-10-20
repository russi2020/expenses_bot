import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from typing import List, Union

from aiogram.types.base import Integer

from app.conversation.custom_filters.user_status_filter import check_authorised, restricted
from app.conversation.dialogs.buttons import authorize, confirm_or_not_confirm_kb, MenuButtons
from app.conversation.dialogs.dialogs import msg, confirmation_callbacks
from app.conversation.states.authorization_states import AuthorizationState
from db.db_functions import DbFunctions
from environment import Environment
from redis_repository.redis_repository import RedisRepository


def init_authorization_handlers(dp: Dispatcher, db: DbFunctions, _env: Environment, redis: RedisRepository):

    async def _start_handler(message: types.Message, state: FSMContext):
        await state.reset_state()
        await message.answer("Приветствую тебя, для начала тебе необходимо зарегистрироваться👇",
                             reply_markup=authorize())

    @dp.callback_query_handler(lambda c: c.data == "authorize")
    async def authorize_handler(callback: types.CallbackQuery):
        await callback.message.answer(msg.write_email)
        await AuthorizationState.email_check.set()

    @dp.message_handler(state=AuthorizationState.email_check)
    async def input_email(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["email_check"] = message.text
            await message.answer(
                text=f"Вы внесли почту {data['email_check']}. Все верно внесено?",
                reply_markup=confirm_or_not_confirm_kb(
                    confirm=confirmation_callbacks.email_confirm,
                    not_confirm=confirmation_callbacks.email_not_confirm)
            )

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.email_not_confirm,
                               state=AuthorizationState.email_check)
    async def repeat_input_email(callback: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await authorize_handler(callback)

    @dp.callback_query_handler(lambda c: c.data == confirmation_callbacks.email_confirm,
                               state=AuthorizationState.email_check)
    async def check_email(callback: types.CallbackQuery, state: FSMContext):
        state_data: dict = dict(await state.get_data())
        email = state_data.get("email_check")
        try:
            response: str = db.find_user_by_email(email)
            if email == response:
                user_id: Integer = callback.message.chat.id
                await state.finish()
                await dp.bot.send_message(chat_id=callback.message.chat.id, text=msg.authorization_success,
                                          reply_markup=MenuButtons.main_kb())
                await redis.set_user_active_status(telegram_id=user_id, status="active")
                setattr(callback.message, "authorize", "active")
                await state.finish()
        except TypeError as err:
            logging.warning(err)
            await callback.message.answer("Введеный email отсутствует в базе данных. Проверьте внесенные данные")
            await _start_handler(callback.message, state)

    @dp.message_handler(state="*", commands={"reset", "start", "menu"})
    async def reset(message: types.Message, state: FSMContext):
        await _start_handler(message, state)

    @dp.message_handler(lambda message: getattr(message.from_user, 'authorize', None) == "not_active")
    async def check_auth_status(message: types.Message, state: FSMContext):
        status: Union[bytes, str, None] = await redis.get_auth_status_by_telegram_id(message.from_user.id)
        if status is not None and status.decode(encoding='utf-8', errors='strict') == "not_active":
            await _start_handler(message, state)
