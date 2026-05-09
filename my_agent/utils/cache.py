import time
import hashlib
import json
from functools import wraps
from typing import Any
from my_agent.utils.logging import get_logger

_log = get_logger(__name__)


class TTLCache:
    """Simple in-process TTL cache. For multi-instance deployments, replace
    the store with a Redis client (e.g. redis.StrictRedis.get / .setex)."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> tuple[bool, Any]:
        if key in self._store:
            value, expires_at = self._store[key]
            if time.monotonic() < expires_at:
                return True, value
            _log.debug("Cache expired: %s", key[:16])
            del self._store[key]
        return False, None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (value, time.monotonic() + ttl_seconds)
        _log.debug("Cache set: %s (ttl=%ds)", key[:16], ttl_seconds)


_cache = TTLCache()


def cached(ttl_seconds: int = 300):
    """Decorator that caches a function's return value for `ttl_seconds`.
    The cache key is derived from the function name and all arguments.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            raw_key = json.dumps({"fn": fn.__qualname__, "args": args, "kwargs": kwargs},
                                 sort_keys=True, default=str)
            key = hashlib.sha256(raw_key.encode()).hexdigest()
            hit, value = _cache.get(key)
            if hit:
                _log.debug("Cache HIT: %s(%s)", fn.__name__, args)
                return value
            value = fn(*args, **kwargs)
            _cache.set(key, value, ttl_seconds)
            _log.debug("Cache MISS: %s(%s) — result cached for %ds", fn.__name__, args, ttl_seconds)
            return value
        return wrapper
    return decorator
