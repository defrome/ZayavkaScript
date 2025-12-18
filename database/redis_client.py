import os

import redis
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def set_cache(key, data, expire=3600):
    r.setex(key, expire, json.dumps(data))

def get_cache(key):
    data = r.get(key)
    return json.loads(data) if data else None

def delete_cache(key):
    r.delete(key)