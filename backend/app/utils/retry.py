"""
Retry with exponential backoff for async callables.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


async def async_retry(
  fn: Callable[..., Awaitable[T]],
  *args: Any,
  max_attempts: int = 3,
  base_delay_seconds: float = 1.0,
  logger: logging.Logger | None = None,
  **kwargs: Any,
) -> T:
  """
  Run async fn(*args, **kwargs) with up to max_attempts, exponential backoff.
  Retry-only options (max_attempts, base_delay_seconds, logger) are taken from
  kwargs if present and not passed to fn.
  On final failure, log error and re-raise.
  """
  opts_max = kwargs.pop("max_attempts", None)
  opts_delay = kwargs.pop("base_delay_seconds", None)
  opts_log = kwargs.pop("logger", None)
  attempts = opts_max if opts_max is not None else max_attempts
  delay = opts_delay if opts_delay is not None else base_delay_seconds
  log = opts_log or logger or logging.getLogger("app.retry")
  last_error: BaseException | None = None
  for attempt in range(attempts):
    try:
      return await fn(*args, **kwargs)
    except Exception as e:
      last_error = e
      if attempt < attempts - 1:
        backoff = delay * (2**attempt)
        log.warning(
          "Blockchain transaction attempt failed, retrying",
          extra={
            "attempt": attempt + 1,
            "max_attempts": attempts,
            "delay_seconds": backoff,
            "error": str(e)[:200],
          },
        )
        await asyncio.sleep(backoff)
      else:
        log.error(
          "Blockchain transaction failed after all retries",
          extra={
            "attempts": attempts,
            "error": str(e)[:200],
          },
        )
  if last_error is not None:
    raise last_error
  raise RuntimeError("retry exhausted with no exception")
