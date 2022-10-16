import logging.config
import logging
from os import path

import environs
from environs import Env


class Environment:

    def __init__(self, _env: Env):
        self.telegram_token = _env("TELEGRAM_TOKEN")
        self.redis_host = _env.str('REDIS_HOST', 'localhost')
        self.redis_port = _env.str('REDIS_PORT', '6379')
        self.re_for_date_text_parse = _env('RE_FOR_DATE_LETTERS', '')
        self.logging_level = _env.str("LOGGING_LEVEL")

    @property
    def redis_uri(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    @staticmethod
    def get_env_logger():
        log_file_path = path.join(path.dirname(path.abspath("__file__")), 'logging.ini')
        logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger


def init_environment() -> Environment:
    logger = Environment.get_env_logger()
    logger.info("Init environment")
    try:
        env = Env()
        env.read_env()
        return Environment(_env=env)
    except environs.EnvError as err:
        logger.exception(err)
        raise
