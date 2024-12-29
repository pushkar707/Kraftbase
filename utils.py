import bcrypt
import aioredis
import uuid
import os

redis_client = aioredis.from_url(os.environ.get('REDIS_URL'))


def hash_password(plain_text_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def generate_session_id():
    id = uuid.uuid4()
    if (await redis_client.exists(f'session:{id}')):
        return generate_session_id()
    return id


def get_simple_type(value):
    if isinstance(value, str):
        return "string"
    elif isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, bool):
        return "boolean"
    return 'NA'
