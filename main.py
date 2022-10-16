import logging.config
import logging
from os import path

from aiogram.utils.executor import Executor
from environs import Env

from app.start_bot import init_bot, start_bot
from db.db_functions import DbFunctions
from environment import init_environment


def start_app():

    log_file_path = path.join(path.dirname(path.abspath("__file__")), 'logging.ini')
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("Starting app")

    environment = init_environment()
    bot, dispatcher = init_bot(environment)
    executor = Executor(dispatcher)

    env = Env()
    env.read_env()

    db_connect_info = {
        "database": env('BOT_DB_NAME', ''),
        "user": env('BOT_DB_USER', ''),
        "password": env('BOT_DB_PASSWORD', ''),
        "host": env('BOT_DB_HOST', ''),
        "port": env('BOT_DB_PORT', '')
    }

    async def on_startup(*_, **__):
        db = DbFunctions(db_connect_info)

    async def on_shutdown(*_, **__):
        pass

    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)
    start_bot(executor=executor, environment=environment)
