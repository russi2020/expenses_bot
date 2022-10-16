from aiogram import Bot
from aiogram.utils.executor import Executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from environment import Environment


def init_bot(environment: Environment):
    bot = Bot(token=environment.telegram_token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.middleware.setup(LoggingMiddleware())

    return bot, dp


async def _close_dispatcher(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def start_bot(executor: Executor, environment: Environment):
    # if environment.telegram_webhook:
    #     executor.start_webhook(webhook_path=environment.telegram_webhook_path, host="0.0.0.0", port=8080)
    # else:
    #     executor.start_polling()
    executor.start_polling()
