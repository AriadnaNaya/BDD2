# redis_config.py
import os
import redis

def get_redis_client():
    # Leer variables de entorno
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = int(os.environ.get("REDIS_PORT", 6379))
    redis_db = int(os.environ.get("REDIS_DB", 0))
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    return r
