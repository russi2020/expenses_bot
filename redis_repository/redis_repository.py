from aioredis import Redis

ENCODING = 'utf-8'


class RedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_auth_status_by_telegram_id(self, telegram_id):
        status = await self.redis.get(telegram_id)
        return status

    async def set_user_active_status(self, telegram_id: int, status: str):
        await self.redis.set(name=str(telegram_id), value=status, ex=3600)
