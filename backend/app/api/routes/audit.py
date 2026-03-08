from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_session, AuditLogORM


router = APIRouter(prefix="", tags=["audit"])


class AuditLogItem(BaseModel):
  """Single audit log entry; includes blockchain tx hash when action was logged on-chain."""
  action_description: str = Field(..., description="Description of the action.")
  action_hash: str = Field(..., description="SHA256 hash of action+timestamp+user.")
  tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash if logged on-chain.")
  timestamp: Optional[str] = Field(None, description="ISO timestamp.")
  risk: str = Field(..., description="Risk level.")
  status: str = Field(..., description="approved or rejected.")


def _serialize(entry: AuditLogORM) -> AuditLogItem:
  return AuditLogItem(
    action_description=entry.action_description,
    action_hash=entry.action_hash,
    tx_hash=entry.tx_hash,
    timestamp=entry.timestamp.isoformat() if entry.timestamp else None,
    risk=entry.risk.value,
    status=entry.status
  )


@router.get(
  "/audit-log",
  response_model=list[AuditLogItem],
  summary="List all audit log entries",
  description="Audit log of approved/rejected actions; each entry includes action, risk, status, and blockchain transaction hash when logged on-chain.",
)
async def list_audit_log(
  db: Session = Depends(get_session)
) -> list[AuditLogItem]:
  """
  Retrieve the full audit log of approved and rejected actions.

  Each entry includes action description, SHA256 action hash, optional blockchain
  transaction hash (for on-chain verification), timestamp, risk level, and approval status.
  Use for dashboards and explorer links via tx_hash.
  """
  entries = (
    db.query(AuditLogORM)
    .order_by(AuditLogORM.created_at.desc())
    .all()
  )
  return [_serialize(e) for e in entries]


@router.get(
  "/audit-logs",
  response_model=list[AuditLogItem],
  summary="List audit logs (alias)",
  description="Alias for GET /audit-log.",
)
async def list_audit_logs_alias(
  db: Session = Depends(get_session)
) -> list[AuditLogItem]:
  """Alias for GET /audit-log. Returns the same list of audit log entries."""
  return await list_audit_log(db=db)
