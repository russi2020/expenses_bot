from aiogram.dispatcher import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from app.conversation.handlers.authorization_handler import init_authorization_handlers
from app.conversation.handlers.expenses_insert_handler import init_expenses_handler
from db.db_functions import DbFunctions
from middlewares.authentication import AuthenticationMiddleware

from redis_repository.redis_repository import RedisRepository
from environment import Environment


def init_handlers(dp: Dispatcher, db: DbFunctions, env: Environment,
                  redis: RedisRepository):
    dp.middleware.setup(LoggingMiddleware())
    dp.middleware.setup(AuthenticationMiddleware(redis_repository=redis))
    init_authorization_handlers(dp=dp, db=db, _env=env, redis=redis)
    init_expenses_handler(dp=dp, db=db, _env=env, redis=redis)
