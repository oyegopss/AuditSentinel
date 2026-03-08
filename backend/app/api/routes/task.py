from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...agents import run_task_and_log_decision
from ...risk_engine import RiskLevel, is_high_risk, calculate_risk
from ...database import get_session, Task, AuditLogORM
from ...blockchain import build_audit_log_entry
from ...security_guard import detect_prompt_injection
from ...database.models import (
  TASK_STATUS_AWAITING_APPROVAL,
  TASK_STATUS_PROCESSING,
  TASK_STATUS_RISK_EVALUATED,
  TASK_STATUS_SUBMITTED,
)
from ...exceptions import AgentError
from ...logging_config import get_logger
from ...cache import get_decision_cache, make_decision_cache_key
from ...services.task_status import get_task_status, set_task_status

logger = get_logger("api.task")
router = APIRouter(prefix="", tags=["task"])
TASK_TYPE_DEFAULT = "default"


class TaskRequest(BaseModel):
  """Request body for task submission."""
  description: str = Field(..., description="Free-text task description for the AI agent.")


class TaskResponse(BaseModel):
  """Response after task submission: AI decision and risk classification."""
  task_id: str = Field(..., description="Unique identifier for the submitted task.")
  output: str = Field(..., description="Agent decision output (e.g. auto-execute or require human review).")
  confidence: float = Field(..., description="Confidence score 0–1.")
  risk: str = Field(..., description="Risk level: low, medium, high, or critical.")
  risk_score: Optional[int] = Field(None, description="Risk score 0–100 from risk engine.")
  risk_level: Optional[str] = Field(None, description="Risk level (e.g. CRITICAL) from risk engine.")
  decision: Optional[str] = Field(None, description="Governance decision (e.g. REQUIRE_HUMAN_APPROVAL).")
  recommended_action: str = Field(..., description="Recommended governance action.")
  requires_human_approval: bool = Field(..., description="True when risk is high or critical.")
  reasoning_steps: Optional[list[str]] = Field(None, description="Reasoning steps (present when served from cache).")


class TaskStatusResponse(BaseModel):
  """Current task state and timestamps for each transition."""
  task_id: str = Field(..., description="Task identifier.")
  status: str = Field(..., description="Current state: submitted, processing, risk_evaluated, awaiting_approval, approved, executed, logged_on_chain.")
  state_timestamps: dict[str, str] = Field(..., description="ISO timestamps per state.")


@router.post(
  "/task",
  response_model=TaskResponse,
  summary="Submit AI task",
  description="Task submission: send a natural-language task; receive AI decision, risk level, and whether human approval is required.",
)
async def submit_task(
  request: TaskRequest,
  db: Session = Depends(get_session)
) -> TaskResponse:
  """
  Submit a natural-language task for the AI agent to process.

  The agent runs planning and risk detection on the task description. The response
  includes the agent's decision output, confidence score, risk classification
  (low/medium/high/critical), recommended action, and a flag indicating whether
  human approval is required before execution. When risk is high or critical,
  use the approval workflow before executing the action.
  """
  user_input = request.description or ""

  # ---------------------------------------------------------------------------
  # Prompt injection guard – block obviously malicious instructions early.
  # ---------------------------------------------------------------------------
  guard = detect_prompt_injection(user_input)
  if guard.get("blocked"):
    description = f"Prompt injection blocked: {user_input[:200]}"
    entry = build_audit_log_entry(
      description=description,
      risk=RiskLevel.CRITICAL,
      receipt=None,
      status="blocked_prompt_injection",
    )
    db_entry = AuditLogORM(
      action_hash=entry.action_hash,
      tx_hash=entry.tx_hash,
      timestamp=entry.timestamp,
      action_description=entry.action_description,
      risk=entry.risk,
      status=entry.status,
      created_at=entry.created_at,
    )
    db.add(db_entry)
    db.commit()

    blocked_task_id = str(uuid4())
    logger.warning(
      "Prompt injection attempt blocked",
      extra={
        "event": "prompt_injection_blocked",
        "task_id": blocked_task_id,
      },
    )
    return TaskResponse(
      task_id=blocked_task_id,
      output=guard.get(
        "message",
        "Prompt injection attempt detected. Execution blocked.",
      ),
      confidence=0.0,
      risk="critical",
      risk_score=95,
      risk_level="CRITICAL",
      decision="REQUIRE_HUMAN_APPROVAL",
      recommended_action="block_execution",
      requires_human_approval=True,
      reasoning_steps=[
        "Prompt injection attempt detected by security guard; task was blocked and not executed."
      ],
    )

  task_type = TASK_TYPE_DEFAULT
  cache_key = make_decision_cache_key(user_input, task_type)
  cache = get_decision_cache()

  cached = cache.get(cache_key)
  if cached is not None:
    task_id = str(uuid4())
    return TaskResponse(
      task_id=task_id,
      output=cached.get("output", ""),
      confidence=cached.get("confidence", 0.0),
      risk=cached.get("risk", "low"),
      risk_score=cached.get("risk_score"),
      risk_level=cached.get("risk_level"),
      decision=cached.get("decision"),
      recommended_action=cached.get("recommended_action", "require_human_approval"),
      requires_human_approval=cached.get("requires_human_approval", True),
      reasoning_steps=cached.get("reasoning_steps"),
    )

  task_id = uuid4()
  now_iso = datetime.now(timezone.utc).isoformat()
  task_row = Task(
    id=task_id,
    description=user_input,
    status=TASK_STATUS_SUBMITTED,
    state_timestamps={TASK_STATUS_SUBMITTED: now_iso},
  )
  db.add(task_row)
  db.commit()

  set_task_status(db, task_id, TASK_STATUS_PROCESSING)
  logger.info(
    "Task submitted",
    extra={
      "event": "task_submitted",
      "description_len": len(user_input),
      "task_id": str(task_id),
    },
  )
  try:
    task_id, trace = run_task_and_log_decision(user_input, db=db, task_id=task_id)
  except Exception as e:
    raise AgentError(message=str(e)[:200], status_code=502) from e
  # Risk evaluation: destructive-keyword rule overrides AI model output.
  risk_summary = calculate_risk(user_input)
  requires_approval = bool(
    risk_summary.get("auto_execute") is False
    or risk_summary.get("requires_human_approval", is_high_risk(trace.risk))
  )
  # When risk engine returns decision/auto_execute, use them to override trace.
  decision = risk_summary.get("decision")
  if decision:
    recommended_action = decision.lower().replace(" ", "_")
  else:
    recommended_action = trace.recommended_action
  output_text = trace.output
  if risk_summary.get("auto_execute") is False and risk_summary.get("risk_level") == "CRITICAL":
    output_text = (
      "Task requires human review before execution. "
      "Destructive-action rule override: CRITICAL risk; autonomous execution not allowed."
    )

  set_task_status(db, task_id, TASK_STATUS_RISK_EVALUATED)
  if requires_approval:
    set_task_status(db, task_id, TASK_STATUS_AWAITING_APPROVAL)
  confidence_val = risk_summary.get("confidence", trace.confidence)
  risk_score = risk_summary.get("risk_score")
  if risk_score is None and confidence_val is not None:
    risk_score = int(round(float(confidence_val) * 100))
  risk_level = risk_summary.get("risk_level") or (
    (risk_summary.get("risk") or "").upper() or None
  )
  decision_val = risk_summary.get("decision")
  cache.set(
    cache_key,
    {
      "output": output_text,
      "confidence": confidence_val,
      "risk": risk_summary.get("risk", trace.risk.value),
      "risk_score": risk_score,
      "risk_level": risk_level,
      "decision": decision_val,
      "recommended_action": recommended_action,
      "requires_human_approval": requires_approval,
      "reasoning_steps": (
        list(trace.reasoning_steps)
        if trace.reasoning_steps
        else risk_summary.get("reasoning_steps", [])
      ),
    },
  )
  return TaskResponse(
    task_id=str(task_id),
    output=output_text,
    confidence=confidence_val,
    risk=risk_summary.get("risk", trace.risk.value),
    risk_score=risk_score,
    risk_level=risk_level,
    decision=decision_val,
    recommended_action=recommended_action,
    requires_human_approval=requires_approval,
    reasoning_steps=(
      list(trace.reasoning_steps)
      if trace.reasoning_steps
      else risk_summary.get("reasoning_steps")
    ),
  )


@router.get(
  "/task-status/{task_id}",
  response_model=TaskStatusResponse,
  summary="Get task status",
  description="Return current state and timestamps for a task. States: submitted, processing, risk_evaluated, awaiting_approval, approved, executed, logged_on_chain.",
)
async def get_task_status_endpoint(
  task_id: str,
  db: Session = Depends(get_session),
) -> TaskStatusResponse:
  """Return task status and state_timestamps. 404 if task not found."""
  try:
    uid = UUID(task_id)
  except ValueError:
    raise HTTPException(status_code=404, detail="Task not found")
  data = get_task_status(db, uid)
  if data is None:
    raise HTTPException(status_code=404, detail="Task not found")
  return TaskStatusResponse(**data)
