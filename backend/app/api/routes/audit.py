from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.session import get_session
from ...db.models import AuditLogORM


router = APIRouter()


class AuditLogItem(BaseModel):
  action_description: str
  action_hash: str
  tx_hash: str | None
  timestamp: str | None
  risk: str
  status: str


def _serialize(entry: AuditLogORM) -> AuditLogItem:
  return AuditLogItem(
    action_description=entry.action_description,
    action_hash=entry.action_hash,
    tx_hash=entry.tx_hash,
    timestamp=entry.timestamp.isoformat() if entry.timestamp else None,
    risk=entry.risk.value,
    status=entry.status
  )


@router.get("/audit-log", response_model=list[AuditLogItem])
async def list_audit_log(
  db: Session = Depends(get_session)
) -> list[AuditLogItem]:
  entries = (
    db.query(AuditLogORM)
    .order_by(AuditLogORM.created_at.desc())
    .all()
  )
  return [_serialize(e) for e in entries]


@router.get("/audit-logs", response_model=list[AuditLogItem])
async def list_audit_logs_alias(
  db: Session = Depends(get_session)
) -> list[AuditLogItem]:
  return await list_audit_log(db=db)


