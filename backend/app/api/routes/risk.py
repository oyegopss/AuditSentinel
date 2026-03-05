from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...domain.models import RiskLevel
from ...services.risk_service import classify_scenario_risk, is_high_risk, simple_scenario_risk
from ...blockchain_logger import (
  BlockchainReceipt,
  build_audit_log_entry,
  log_high_risk_action_to_chain
)
from ...db.session import get_session
from ...db.models import AuditLogORM


router = APIRouter()


class RiskSimulationRequest(BaseModel):
  scenario: str
  description: str


class RiskSimulationResponse(BaseModel):
  scenario: str
  risk: str
  score: float
  explanation: str
  requires_human_approval: bool


class ApprovalRequest(BaseModel):
  scenario: str
  description: str
  approved: bool
  user: str


class ApprovalResponse(BaseModel):
  status: str
  risk: str
  action_hash: str | None = None
  tx_hash: str | None = None
  timestamp: str | None = None


class SimpleRiskRequest(BaseModel):
  scenario: str


class SimpleRiskResponse(BaseModel):
  scenario: str
  risk_level: str
  requires_approval: bool


@router.post("/simulate-risk", response_model=RiskSimulationResponse)
async def simulate_risk(body: RiskSimulationRequest) -> RiskSimulationResponse:
  assessment = classify_scenario_risk(body.scenario)
  return RiskSimulationResponse(
    scenario=assessment.scenario or body.scenario,
    risk=assessment.risk.value,
    score=assessment.score,
    explanation=assessment.explanation,
    requires_human_approval=is_high_risk(assessment.risk)
  )


@router.post("/risk-score", response_model=SimpleRiskResponse)
async def risk_score(body: SimpleRiskRequest) -> SimpleRiskResponse:
  """
  Simple risk scoring endpoint.

  Example mappings:
  - loan approval above large amount → high
  - database deletion → critical
  - healthcare diagnosis → high
  - automated trading → medium
  """
  risk_level, requires_approval = simple_scenario_risk(body.scenario)
  return SimpleRiskResponse(
    scenario=body.scenario,
    risk_level=risk_level,
    requires_approval=requires_approval
  )


@router.post("/approve-action", response_model=ApprovalResponse)
async def approve_action(
  body: ApprovalRequest,
  db: Session = Depends(get_session)
) -> ApprovalResponse:
  """
  Human approval checkpoint for risky AI actions.

  - Evaluates scenario risk
  - If rejected, stores an audit row with status=rejected
  - If approved and risk is high/critical, calls blockchain_logger to
    compute an action hash and (in production) write to Polygon.
  - Persists the resulting audit entry in PostgreSQL.
  """
  assessment = classify_scenario_risk(body.scenario)

  if not body.approved:
    entry = build_audit_log_entry(
      description=body.description,
      risk=assessment.risk,
      receipt=None,
      status="rejected"
    )
    db_entry = AuditLogORM(
      action_hash=entry.action_hash,
      tx_hash=entry.tx_hash,
      timestamp=entry.timestamp,
      action_description=entry.action_description,
      risk=entry.risk,
      status=entry.status,
      created_at=entry.created_at
    )
    db.add(db_entry)
    db.commit()

    return ApprovalResponse(
      status="rejected",
      risk=assessment.risk.value,
      action_hash=entry.action_hash
    )

  receipt: BlockchainReceipt | None = None
  if is_high_risk(assessment.risk):
    receipt = await log_high_risk_action_to_chain(
      action_description=body.description,
      user=body.user
    )

  entry = build_audit_log_entry(
    description=body.description,
    risk=assessment.risk,
    receipt=receipt,
    status="approved"
  )
  db_entry = AuditLogORM(
    action_hash=entry.action_hash,
    tx_hash=entry.tx_hash,
    timestamp=entry.timestamp,
    action_description=entry.action_description,
    risk=entry.risk,
    status=entry.status,
    created_at=entry.created_at
  )
  db.add(db_entry)
  db.commit()

  return ApprovalResponse(
    status="approved",
    risk=assessment.risk.value,
    action_hash=entry.action_hash,
    tx_hash=entry.tx_hash,
    timestamp=entry.timestamp.isoformat() if entry.timestamp else None
  )


