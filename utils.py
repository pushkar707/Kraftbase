import bcrypt
from redis import Redis
import uuid

redis_client = Redis('localhost', 6379)


def hash_password(plain_text_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_session_id():
    id = uuid.uuid4()
    if (redis_client.exists(f'session:{id}')):
        return generate_session_id()
    return id
