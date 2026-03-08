"""
In-memory TTL cache for AI decision results.
Cache key: task_type + user_input. Expiration: 10 minutes.
"""
from __future__ import annotations

import hashlib
import threading
import time
from typing import Any, Optional

DEFAULT_TTL_SECONDS = 600  # 10 minutes


class _TTLCache:
  """Thread-safe in-memory cache with TTL."""

  def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS):
    self._ttl = ttl_seconds
    self._store: dict[str, tuple[Any, float]] = {}
    self._lock = threading.Lock()

  def get(self, key: str) -> Optional[Any]:
    with self._lock:
      if key not in self._store:
        return None
      value, expiry = self._store[key]
      if time.monotonic() > expiry:
        del self._store[key]
        return None
      return value

  def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
    ttl = ttl_seconds if ttl_seconds is not None else self._ttl
    expiry = time.monotonic() + ttl
    with self._lock:
      self._store[key] = (value, expiry)


_decision_cache: Optional[_TTLCache] = None


def get_decision_cache() -> _TTLCache:
  """Return the global AI decision cache (10 min TTL)."""
  global _decision_cache
  if _decision_cache is None:
    _decision_cache = _TTLCache(ttl_seconds=DEFAULT_TTL_SECONDS)
  return _decision_cache


def clear_decision_cache() -> None:
  """Flush all cached decisions so fresh risk scores are returned."""
  global _decision_cache
  _decision_cache = _TTLCache(ttl_seconds=DEFAULT_TTL_SECONDS)


def make_decision_cache_key(user_input: str, task_type: str = "default") -> str:
  """Cache key from user_input + task_type."""
  raw = f"{task_type}|{user_input or ''}"
  return hashlib.sha256(raw.encode("utf-8")).hexdigest()
