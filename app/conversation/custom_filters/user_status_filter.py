import logging
from functools import wraps

from aiogram import types
from aiogram.dispatcher import FSMContext

from app.conversation.dialogs.buttons import authorize
from redis_repository.redis_repository import RedisRepository


def restricted(redis: RedisRepository):
    """Restrict usage of func to allowed users only and replies if necessary"""

    def restricted_decorator(func):
        @wraps(func)
        async def wrapped(message: types.Message, *args):
            user_id = message.from_user.id
            status = await redis.get_auth_status_by_telegram_id(user_id)
            if status in ["not_active", None]:
                logging.warning(f"WARNING: Unauthorized access denied for {user_id}.")
                return await message.answer(text="Приветствую тебя, для начала тебе необходимо зарегистрироваться👇",
                                            reply_markup=authorize())
            return

        return wrapped
    return restricted_decorator


def check_authorised(redis: RedisRepository):
    """Декоратор для проверки статуса авторизации пользователя"""

    def auth_decorator(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id
            status = await redis.get_auth_status_by_telegram_id(user_id)
            if status:
                decoded_status = status.decode(encoding="utf-8", errors='strict')
                if decoded_status == "active":
                    await message.answer("Вы уже авторизованы.")
                    return
            return await func(message, *args, **kwargs)
        return wrapper
    return auth_decorator
