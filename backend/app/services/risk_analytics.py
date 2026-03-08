"""Risk analytics: distribution of risk levels across tasks/actions."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import AuditLogORM, DecisionTraceORM
from ..risk_engine import RiskLevel


@dataclass
class RiskDistribution:
  low: int
  medium: int
  high: int
  critical: int


def get_risk_distribution(
  db: Session,
  source: str = "tasks",
) -> RiskDistribution:
  """Counts per risk level. source: tasks, actions, or combined."""
  counts = {r.value: 0 for r in RiskLevel}

  if source in ("tasks", "combined"):
    for risk, cnt in (
      db.query(DecisionTraceORM.risk, func.count(DecisionTraceORM.id))
      .group_by(DecisionTraceORM.risk)
      .all()
    ):
      if risk:
        counts[risk.value] = counts.get(risk.value, 0) + cnt

  if source in ("actions", "combined"):
    for risk, cnt in (
      db.query(AuditLogORM.risk, func.count(AuditLogORM.id))
      .group_by(AuditLogORM.risk)
      .all()
    ):
      if risk:
        counts[risk.value] = counts.get(risk.value, 0) + cnt

  return RiskDistribution(
    low=counts.get("low", 0),
    medium=counts.get("medium", 0),
    high=counts.get("high", 0),
    critical=counts.get("critical", 0),
  )
