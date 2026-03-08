"""Task status tracking: set status and record timestamps."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from ..database.models import Task


def _now_iso() -> str:
  return datetime.now(timezone.utc).isoformat()


def set_task_status(
  db: Session,
  task_id: UUID,
  status: str,
) -> None:
  """Set task status and append timestamp for this state."""
  task = db.query(Task).filter(Task.id == task_id).first()
  if not task:
    return
  task.status = status
  timestamps = dict(task.state_timestamps or {})
  timestamps[status] = _now_iso()
  task.state_timestamps = timestamps
  db.commit()


def get_task_status(db: Session, task_id: UUID) -> dict | None:
  """Return task status and state_timestamps for API response, or None if not found."""
  task = db.query(Task).filter(Task.id == task_id).first()
  if not task:
    return None
  return {
    "task_id": str(task.id),
    "status": task.status,
    "state_timestamps": task.state_timestamps or {},
  }
