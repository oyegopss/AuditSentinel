from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...database import get_session, AuditLogORM, DecisionTraceORM, Task
from ...risk_engine import RiskLevel


router = APIRouter(tags=["dashboard"])


class DashboardMetrics(BaseModel):
  total_tasks: int
  high_risk_tasks: int
  human_interventions: int
  blockchain_verified: int


class HighRiskTask(BaseModel):
  task_id: Optional[str]
  description: str
  risk: str
  status: str
  timestamp: Optional[str]


class RiskKeyword(BaseModel):
  keyword: str
  count: int


class DashboardData(BaseModel):
  metrics: DashboardMetrics
  recent_high_risk: List[HighRiskTask]
  top_keywords: List[RiskKeyword]


RISK_KEYWORDS = [
  "delete", "drop", "erase", "remove", "truncate", "destroy", "wipe",
  "production database", "customer records", "override", "access internal records",
  "user data", "financial records", "transfer funds", "shutdown",
]


@router.get("/dashboard-metrics", response_model=DashboardData)
async def dashboard_metrics(db: Session = Depends(get_session)) -> DashboardData:
  total_tasks = db.query(func.count(Task.id)).scalar() or 0
  high_risk_tasks = (
    db.query(func.count(AuditLogORM.id))
    .filter(AuditLogORM.risk.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]))
    .scalar() or 0
  )
  human_interventions = (
    db.query(func.count(AuditLogORM.id))
    .filter(AuditLogORM.status.in_(["approved", "rejected"]))
    .scalar() or 0
  )
  blockchain_verified = (
    db.query(func.count(AuditLogORM.id))
    .filter(AuditLogORM.tx_hash.isnot(None))
    .scalar() or 0
  )

  high_risk_rows = (
    db.query(AuditLogORM)
    .filter(AuditLogORM.risk.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]))
    .order_by(AuditLogORM.created_at.desc())
    .limit(8)
    .all()
  )
  recent_high_risk = [
    HighRiskTask(
      task_id=str(r.task_id) if r.task_id else None,
      description=(r.action_description or "")[:120],
      risk=r.risk.value if r.risk else "unknown",
      status=r.status or "—",
      timestamp=r.timestamp.isoformat() if r.timestamp else None,
    )
    for r in high_risk_rows
  ]

  all_descriptions = [
    (r.action_description or "").lower()
    for r in db.query(AuditLogORM.action_description).all()
  ]
  keyword_counts: dict[str, int] = {}
  for kw in RISK_KEYWORDS:
    count = sum(1 for d in all_descriptions if kw in d)
    if count > 0:
      keyword_counts[kw] = count
  top_keywords = sorted(
    [RiskKeyword(keyword=k, count=v) for k, v in keyword_counts.items()],
    key=lambda x: x.count,
    reverse=True,
  )[:10]

  return DashboardData(
    metrics=DashboardMetrics(
      total_tasks=total_tasks,
      high_risk_tasks=high_risk_tasks,
      human_interventions=human_interventions,
      blockchain_verified=blockchain_verified,
    ),
    recent_high_risk=recent_high_risk,
    top_keywords=top_keywords,
  )
