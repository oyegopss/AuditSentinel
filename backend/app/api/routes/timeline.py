from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_session, AuditLogORM, DecisionTraceORM


router = APIRouter()


class TimelineEvent(BaseModel):
  event_type: str
  timestamp: str
  status: str
  task_id: Optional[str] = None
  summary: str
  extra: Optional[dict[str, Any]] = None


class ActivityEvent(BaseModel):
  event: str
  timestamp: str
  task_id: Optional[str] = None


def _dt_iso(d: Optional[datetime]) -> str:
  if d is None:
    return ""
  return d.isoformat()


@router.get(
  "/decision-timeline",
  response_model=list[TimelineEvent],
  summary="Get chronological decision timeline",
  description="Chronological events: task submitted, AI decision, risk detection, approval request, approval decision, blockchain logging; each with timestamp and status.",
)
async def get_decision_timeline(
  db: Session = Depends(get_session),
  limit: int = 50,
) -> list[TimelineEvent]:
  """
  Return a chronological list of events for AI tasks and approvals.

  Merges events from decision traces (task_submitted, ai_decision, risk_detection)
  and audit logs (approval_decision, blockchain_logging). Sorted by timestamp
  descending. Query: limit (default 50).
  """
  events: list[tuple[datetime, TimelineEvent]] = []

  for row in (
    db.query(DecisionTraceORM)
    .order_by(DecisionTraceORM.created_at.desc())
    .limit(limit)
    .all()
  ):
    ts = row.created_at
    task_id_str = str(row.task_id) if row.task_id else None

    events.append((
      ts,
      TimelineEvent(
        event_type="task_submitted",
        timestamp=_dt_iso(ts),
        status="completed",
        task_id=task_id_str,
        summary="Task submitted",
        extra={"output_preview": (row.output or "")[:80]},
      ),
    ))
    events.append((
      ts,
      TimelineEvent(
        event_type="ai_decision",
        timestamp=_dt_iso(ts),
        status="completed",
        task_id=task_id_str,
        summary="AI decision generated",
        extra={"output": row.output, "recommended_action": row.recommended_action},
      ),
    ))
    events.append((
      ts,
      TimelineEvent(
        event_type="risk_detection",
        timestamp=_dt_iso(ts),
        status="completed",
        task_id=task_id_str,
        summary="Risk detection",
        extra={"risk": row.risk.value, "confidence": row.confidence},
      ),
    ))
    if (row.recommended_action or "").lower() == "require_human_approval":
      events.append((
        ts,
        TimelineEvent(
          event_type="human_approval_request",
          timestamp=_dt_iso(ts),
          status="requested",
          task_id=task_id_str,
          summary="Human approval request",
          extra={"risk": row.risk.value},
        ),
      ))

  for row in (
    db.query(AuditLogORM)
    .order_by(AuditLogORM.created_at.desc())
    .limit(limit)
    .all()
  ):
    ts = row.created_at or row.timestamp
    if not ts:
      continue

    events.append((
      ts,
      TimelineEvent(
        event_type="approval_decision",
        timestamp=_dt_iso(ts),
        status=row.status or "unknown",
        task_id=None,
        summary="Approval decision",
        extra={
          "action_description": (row.action_description or "")[:80],
          "risk": row.risk.value,
        },
      ),
    ))
    tx_ts = row.timestamp or row.created_at
    events.append((
      tx_ts or ts,
      TimelineEvent(
        event_type="blockchain_logging",
        timestamp=_dt_iso(tx_ts or ts),
        status="completed" if row.tx_hash else "skipped",
        task_id=None,
        summary="Blockchain logging",
        extra={"tx_hash": row.tx_hash, "action_hash": row.action_hash} if row.tx_hash else None,
      ),
    ))

  events.sort(key=lambda x: x[0], reverse=True)
  return [e for _, e in events[:limit]]


@router.get(
  "/activity-feed",
  response_model=list[ActivityEvent],
  summary="Live governance activity feed",
  description=(
    "Latest governance events across the system: task submission, AI decision, "
    "risk classification, human approval, and blockchain logging."
  ),
)
async def get_activity_feed(
  db: Session = Depends(get_session),
  limit: int = 50,
) -> list[ActivityEvent]:
  """
  Return a flattened activity feed for the governance dashboard.

  Events are derived from decision traces (task submitted, AI decision,
  risk classification, human approval required) and audit logs
  (human approval completed, blockchain log recorded).
  """
  items: list[tuple[datetime, ActivityEvent]] = []

  for row in (
    db.query(DecisionTraceORM)
    .order_by(DecisionTraceORM.created_at.desc())
    .limit(limit)
    .all()
  ):
    ts = row.created_at
    task_id_str = str(row.task_id) if row.task_id else None

    items.append((
      ts,
      ActivityEvent(
        event="Task submitted",
        timestamp=_dt_iso(ts),
        task_id=task_id_str,
      ),
    ))
    items.append((
      ts,
      ActivityEvent(
        event="AI decision generated",
        timestamp=_dt_iso(ts),
        task_id=task_id_str,
      ),
    ))

    # Risk classification, including band in the message.
    risk_label = (row.risk.value.upper() if row.risk else "UNKNOWN")
    items.append((
      ts,
      ActivityEvent(
        event=f"Risk classified: {risk_label}",
        timestamp=_dt_iso(ts),
        task_id=task_id_str,
      ),
    ))

    if (row.recommended_action or "").lower() == "require_human_approval":
      items.append((
        ts,
        ActivityEvent(
          event="Human approval required",
          timestamp=_dt_iso(ts),
          task_id=task_id_str,
        ),
      ))

  for row in (
    db.query(AuditLogORM)
    .order_by(AuditLogORM.created_at.desc())
    .limit(limit)
    .all()
  ):
    ts = row.created_at or row.timestamp
    if not ts:
      continue

    # Human approval completed (approved / rejected).
    items.append((
      ts,
      ActivityEvent(
        event=f"Human approval completed: {row.status or 'unknown'}",
        timestamp=_dt_iso(ts),
        task_id=None,
      ),
    ))

    # Blockchain log recorded (only when we have a tx hash).
    if row.tx_hash:
      tx_ts = row.timestamp or row.created_at or ts
      items.append((
        tx_ts,
        ActivityEvent(
          event="Blockchain log recorded",
          timestamp=_dt_iso(tx_ts),
          task_id=None,
        ),
      ))

  items.sort(key=lambda x: x[0], reverse=True)
  return [e for _, e in items[:limit]]
