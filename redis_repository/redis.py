import aioredis
from aioredis import Redis

from environment import Environment


async def init_redis(environment: Environment) -> Redis:
    pool = aioredis.ConnectionPool.from_url(url=environment.redis_uri, max_connections=10)
    return await aioredis.Redis(connection_pool=pool)
