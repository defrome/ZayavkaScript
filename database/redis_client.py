import json
import os
from datetime import date, datetime
from fnmatch import fnmatch
from typing import Any

import redis
from redis.exceptions import RedisError


def _json_serializer(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


class CacheClient:
    def __init__(self) -> None:
        self.enabled = os.getenv("REDIS_ENABLED", "1") == "1"
        self.default_ttl = int(os.getenv("REDIS_DEFAULT_TTL", "300"))
        self._fallback: dict[str, str] = {}

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        self._client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    def _serialize(self, value: Any) -> str:
        return json.dumps(value, default=_json_serializer)

    @staticmethod
    def _deserialize(raw: str | None) -> Any:
        if raw is None:
            return None
        return json.loads(raw)

    def get_json(self, key: str) -> Any:
        if not self.enabled:
            return None

        try:
            raw = self._client.get(key)
            return self._deserialize(raw)
        except RedisError:
            raw = self._fallback.get(key)
            return self._deserialize(raw)

    def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        if not self.enabled:
            return

        effective_ttl = ttl or self.default_ttl
        payload = self._serialize(value)

        try:
            self._client.setex(key, effective_ttl, payload)
        except RedisError:
            self._fallback[key] = payload

    def delete(self, key: str) -> None:
        if key in self._fallback:
            del self._fallback[key]

        if not self.enabled:
            return

        try:
            self._client.delete(key)
        except RedisError:
            return

    def delete_pattern(self, pattern: str) -> None:
        fallback_keys = [key for key in self._fallback if fnmatch(key, pattern)]
        for key in fallback_keys:
            del self._fallback[key]

        if not self.enabled:
            return

        try:
            keys = list(self._client.scan_iter(match=pattern))
            if keys:
                self._client.delete(*keys)
        except RedisError:
            return


cache = CacheClient()


def set_cache(key: str, data: Any, expire: int | None = None) -> None:
    cache.set_json(key, data, ttl=expire)


def get_cache(key: str) -> Any:
    return cache.get_json(key)


def delete_cache(key: str) -> None:
    cache.delete(key)


def delete_cache_by_pattern(pattern: str) -> None:
    cache.delete_pattern(pattern)
