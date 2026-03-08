from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...risk_engine import classify_scenario_risk, is_high_risk, simple_scenario_risk
from ...blockchain import (
  BlockchainReceipt,
  build_audit_log_entry,
  log_high_risk_action_to_chain,
)
from ...database import get_session, AuditLogORM
from ...exceptions import BlockchainError
from ...logging_config import get_logger
from ...utils.retry import async_retry


logger = get_logger("api.approval")
router = APIRouter(prefix="", tags=["risk"])


class RiskSimulationRequest(BaseModel):
  """Request for risk simulation."""
  scenario: str = Field(..., description="Scenario id, e.g. financial_loan_approval, database_deletion, healthcare_diagnosis, automated_trading.")
  description: str = Field("", description="Optional context or action description.")


class RiskSimulationResponse(BaseModel):
  """Risk simulation result."""
  scenario: str = Field(..., description="Scenario identifier.")
  risk: str = Field(..., description="Classified risk: low, medium, high, or critical.")
  score: float = Field(..., description="Numeric risk score.")
  explanation: str = Field(..., description="Human-readable explanation.")
  requires_human_approval: bool = Field(..., description="True if high or critical risk.")


class ApprovalRequest(BaseModel):
  """Request to approve or reject a risky action."""
  scenario: str = Field(..., description="Scenario identifier.")
  description: str = Field(..., description="Action description.")
  approved: bool = Field(..., description="True to approve, false to reject.")
  user: str = Field(..., description="User or system identifier performing the approval.")


class ApprovalResponse(BaseModel):
  """Approval result; includes blockchain tx hash and timestamp when approved and high-risk."""
  status: str = Field(..., description="approved or rejected.")
  risk: str = Field(..., description="Risk level.")
  action_hash: Optional[str] = Field(None, description="SHA256 hash of action+timestamp+user.")
  transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash when logged.")
  tx_hash: Optional[str] = Field(None, description="Alias for transaction_hash.")
  timestamp: Optional[str] = Field(None, description="ISO timestamp when action was logged.")


class SimpleRiskRequest(BaseModel):
  """Request for simple risk level only."""
  scenario: str = Field(..., description="Scenario identifier.")


class SimpleRiskResponse(BaseModel):
  """Simple risk level and approval requirement."""
  scenario: str = Field(..., description="Scenario identifier.")
  risk_level: str = Field(..., description="low, medium, high, or critical.")
  requires_approval: bool = Field(..., description="True for high or critical.")


@router.post(
  "/simulate-risk",
  response_model=RiskSimulationResponse,
  summary="Simulate risk for a scenario",
  description="Risk simulation: evaluate a scenario (loan, DB delete, healthcare, trading) and get risk level, score, and whether human approval is required.",
)
async def simulate_risk(body: RiskSimulationRequest) -> RiskSimulationResponse:
  """
  Run a risk simulation for a predefined scenario (e.g. loan approval, database deletion).

  Evaluates the scenario against the risk engine and returns the classified risk level,
  numeric score, human-readable explanation, and whether the scenario requires human
  approval. Use this before calling the approval endpoint to show users the risk
  assessment.
  """
  assessment = classify_scenario_risk(body.scenario)
  return RiskSimulationResponse(
    scenario=assessment.scenario or body.scenario,
    risk=assessment.risk.value,
    score=assessment.score,
    explanation=assessment.explanation,
    requires_human_approval=is_high_risk(assessment.risk)
  )


@router.post(
  "/risk-score",
  response_model=SimpleRiskResponse,
  summary="Get simple risk level for a scenario",
  description="Lightweight risk level and requires_approval flag for a scenario.",
)
async def risk_score(body: SimpleRiskRequest) -> SimpleRiskResponse:
  """
  Return a simple risk level and approval requirement for a given scenario name.

  Maps the scenario to one of: low, medium, high, critical. Also returns whether
  human approval is required (true for high and critical).
  """
  risk_level, requires_approval = simple_scenario_risk(body.scenario)
  return SimpleRiskResponse(
    scenario=body.scenario,
    risk_level=risk_level,
    requires_approval=requires_approval
  )


@router.post(
  "/approve-action",
  response_model=ApprovalResponse,
  summary="Approve or reject a risky AI action",
  description="Approval workflow: human approve/reject. Approved high-risk actions trigger blockchain logging; response includes action_hash, transaction_hash, and timestamp.",
)
async def approve_action(
  body: ApprovalRequest,
  db: Session = Depends(get_session)
) -> ApprovalResponse:
  """
  Human-in-the-loop approval: approve or reject a risky AI action.

  If **rejected**, the action is recorded in the audit log with status `rejected`
  and no blockchain write. If **approved**, the action is stored in the audit log
  with status `approved`; for high- or critical-risk actions, an action hash is
  computed and sent to the blockchain logger (blockchain logging), and the returned
  `transaction_hash` and `timestamp` reflect that on-chain record.
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
    logger.info(
      "Approval action: rejected",
      extra={
        "event": "approval",
        "status": "rejected",
        "scenario": body.scenario,
        "user": body.user,
        "risk": assessment.risk.value,
        "action_hash": entry.action_hash,
      },
    )
    return ApprovalResponse(
      status="rejected",
      risk=assessment.risk.value,
      action_hash=entry.action_hash,
      transaction_hash=None,
      tx_hash=None,
      timestamp=entry.timestamp.isoformat() if entry.timestamp else None,
    )

  receipt: Optional[BlockchainReceipt] = None
  if is_high_risk(assessment.risk):
    try:
      receipt = await async_retry(
        log_high_risk_action_to_chain,
        action_description=body.description,
        user=body.user,
        risk_level=assessment.risk,
        max_attempts=3,
        base_delay_seconds=1.0,
        logger=logger,
      )
    except Exception as e:
      raise BlockchainError(message=str(e)[:200], status_code=503) from e

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
  logger.info(
    "Approval action: approved",
    extra={
      "event": "approval",
      "status": "approved",
      "scenario": body.scenario,
      "user": body.user,
      "risk": assessment.risk.value,
      "action_hash": entry.action_hash,
      "tx_hash": entry.tx_hash,
    },
  )
  ts_str = entry.timestamp.isoformat() if entry.timestamp else None
  return ApprovalResponse(
    status="approved",
    risk=assessment.risk.value,
    action_hash=entry.action_hash,
    transaction_hash=entry.tx_hash,
    tx_hash=entry.tx_hash,
    timestamp=ts_str,
  )
