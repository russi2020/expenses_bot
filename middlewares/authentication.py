import logging

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from redis_repository.redis_repository import RedisRepository


class AuthenticationMiddleware(BaseMiddleware):

    def __init__(self, redis_repository: RedisRepository):
        super().__init__()
        self.redis_repository = redis_repository
        self.logger = logging.getLogger(__name__)

    async def on_process_message(self, message: types.Message, *_, **__):
        is_active = await self.get_auth_user_status(message)
        setattr(message, "authorize", is_active)

    async def on_pre_process_message(self, message: types.Message, *_, **__):
        is_active = await self.get_auth_user_status(message)
        setattr(message, "authorize", is_active)

    async def on_process_callback_query(self, callback_query: types.CallbackQuery, *_, **__):
        is_active = await self.get_auth_user_status(callback_query.message)
        setattr(callback_query.message, "authorize", is_active)

    async def get_auth_user_status(self, message: types.Message):
        user = message.chat
        if user is None:
            return

        is_active = await self.redis_repository.get_auth_status_by_telegram_id(user.id)
        if is_active:
            if is_active.decode(encoding='utf-8', errors='strict') == 'active':
                return is_active.decode(encoding='utf-8', errors='strict')
            elif is_active.decode(encoding='utf-8', errors='strict') == 'not_active':
                return is_active.decode(encoding='utf-8', errors='strict')
        elif is_active is None:
            await self.redis_repository.set_user_active_status(user.id, status='not_active')
            is_active = "not_active"
            return is_active
