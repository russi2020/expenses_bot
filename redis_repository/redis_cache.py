import logging
import os

import redis
import ujson


class Cache(redis.StrictRedis):
    def __init__(self, host, port, password,
                 charset='utf-8',
                 decode_responses=True):
        super(Cache, self).__init__(host, port,
                            password=password,
                            charset=charset,
                            decode_responses=decode_responses)
        logging.info('Redis cache start')

    def jset(self, name, value, ex=0):
        """функция конвертирует python-объект в Json и сохранит"""
        return self.setex(name, ex, ujson.dumps(value))

    def jget(self, name):
        """функция возвращает Json и конвертирует в python-объект"""
        r = self.get(name)
        if r is None:
            return r
        return ujson.loads(r)


cache = Cache(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD')
)
