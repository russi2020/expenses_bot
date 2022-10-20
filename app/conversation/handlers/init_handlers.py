import logging
from os import path

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
    log_file_path = path.join(path.dirname(path.abspath("__file__")), "logging.ini")
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.info("Start expenses_insert handler")

    dp.middleware.setup(LoggingMiddleware())
    dp.middleware.setup(AuthenticationMiddleware(redis_repository=redis))
    init_authorization_handlers(dp=dp, db=db, _env=env, redis=redis)
    init_expenses_handler(dp=dp, db=db, _env=env, redis=redis)
