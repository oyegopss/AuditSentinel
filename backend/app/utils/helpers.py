from __future__ import annotations

from datetime import datetime


def fmt_ts(d: datetime | None) -> str:
  if d is None:
    return "—"
  return d.strftime("%Y-%m-%d %H:%M:%S UTC")
