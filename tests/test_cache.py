from redis.exceptions import RedisError

from database.redis_client import cache, delete_cache, delete_cache_by_pattern, get_cache, set_cache


class BrokenRedisClient:
    def setex(self, *_args, **_kwargs):
        raise RedisError("redis down")

    def get(self, *_args, **_kwargs):
        raise RedisError("redis down")

    def delete(self, *_args, **_kwargs):
        raise RedisError("redis down")

    def scan_iter(self, *_args, **_kwargs):
        raise RedisError("redis down")


def test_cache_fallback_when_redis_unavailable():
    old_client = cache._client
    old_enabled = cache.enabled

    cache.enabled = True
    cache._client = BrokenRedisClient()
    cache._fallback.clear()

    try:
        set_cache("k1", {"ok": True}, expire=60)
        assert get_cache("k1") == {"ok": True}

        set_cache("applications:1", {"v": 1})
        set_cache("applications:2", {"v": 2})
        delete_cache("k1")
        assert get_cache("k1") is None

        delete_cache_by_pattern("applications:*")
        assert get_cache("applications:1") is None
        assert get_cache("applications:2") is None
    finally:
        cache._fallback.clear()
        cache._client = old_client
        cache.enabled = old_enabled
