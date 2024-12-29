import os
import aioredis
import json
from config import SESSION_TIME

redis_client = aioredis.from_url(os.environ.get('REDIS_URL'))


async def add_redis_session_key(session_id: str, user):
    await redis_client.setex(
        name=f'session:{session_id}',
        time=SESSION_TIME,
        value=json.dumps({'email': user.email, 'id': user.id})
    )


async def key_exists(key: str):
    await redis_client.exists(f'session:{id}')


async def delete_redis_key(key: str):
    await redis_client.delete(key)


async def get_redis_value(key: str):
    await redis_client.get(key)
