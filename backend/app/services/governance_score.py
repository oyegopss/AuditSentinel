from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import AuditLogORM, Task
from ..risk_engine import RiskLevel


@dataclass
class GovernanceScoreResult:
  score: int
  total_tasks: int
  high_risk_actions: int
  rejected_decisions: int
  blockchain_verified_logs: int


def compute_governance_score(db: Session) -> GovernanceScoreResult:
  total_tasks = db.query(func.count(Task.id)).scalar() or 0
  total_actions = db.query(func.count(AuditLogORM.id)).scalar() or 0

  high_risk_actions = (
    db.query(func.count(AuditLogORM.id))
    .filter(AuditLogORM.risk.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]))
    .scalar()
    or 0
  )

  rejected_decisions = (
    db.query(func.count(AuditLogORM.id))
    .filter(AuditLogORM.status == "rejected")
    .scalar()
    or 0
  )

  blockchain_verified_logs = (
    db.query(func.count(AuditLogORM.id))
    .filter(AuditLogORM.tx_hash.isnot(None))
    .scalar()
    or 0
  )

  if total_actions == 0:
    return GovernanceScoreResult(
      score=50,
      total_tasks=total_tasks,
      high_risk_actions=0,
      rejected_decisions=0,
      blockchain_verified_logs=0,
    )

  high_risk_ratio = high_risk_actions / total_actions
  rejected_ratio = rejected_decisions / total_actions
  onchain_ratio = blockchain_verified_logs / total_actions

  base = 50.0
  penalty = 30.0 * high_risk_ratio
  rejection_bonus = 20.0 * rejected_ratio
  onchain_bonus = 20.0 * onchain_ratio

  raw_score = base - penalty + rejection_bonus + onchain_bonus
  bounded = max(0, min(100, int(round(raw_score))))

  return GovernanceScoreResult(
    score=bounded,
    total_tasks=total_tasks,
    high_risk_actions=high_risk_actions,
    rejected_decisions=rejected_decisions,
    blockchain_verified_logs=blockchain_verified_logs,
  )
