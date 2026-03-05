from __future__ import annotations

from typing import List, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..domain.models import DecisionTrace, RiskLevel
from .risk_service import classify_text_risk
from ..db.models import DecisionTraceORM


_DECISION_TRACES: List[DecisionTrace] = []


def run_task_and_log_decision(
  task_text: str,
  db: Session | None = None
) -> Tuple[UUID, DecisionTrace]:
  """
  Lightweight stand‑in for a LangChain agent run wired into risk detection.

  Flow:
  - Agent receives a task description and produces a decision output
  - Risk module scores the task to determine LOW/MEDIUM/HIGH/CRITICAL
  - For HIGH/CRITICAL, the frontend is instructed to route via human approval
  - Decision trace is stored in memory and persisted to PostgreSQL (if a
    session is provided).
  """
  risk_assessment = classify_text_risk(task_text)

  reasoning_steps = [
    "Parsed task description and extracted core intent.",
    f"Matched task against policy and risk rules → {risk_assessment.risk.value} risk.",
    "Checked if human approval is required for this risk band.",
    "Prepared recommended action with safeguards and logging hooks."
  ]

  recommended_action = (
    "auto_execute_with_logging"
    if risk_assessment.risk in (RiskLevel.LOW, RiskLevel.MEDIUM)
    else "require_human_approval"
  )

  decision_output = (
    "Task approved for autonomous execution with audit logging."
    if recommended_action == "auto_execute_with_logging"
    else "Task requires human review before execution."
  )

  trace = DecisionTrace(
    output=decision_output,
    reasoning_steps=reasoning_steps,
    confidence=risk_assessment.score,
    risk=risk_assessment.risk,
    recommended_action=recommended_action
  )

  _DECISION_TRACES.append(trace)
  task_id = uuid4()
  trace.task_id = task_id

  if db is not None:
    db_obj = DecisionTraceORM(
      task_id=task_id,
      output=trace.output,
      reasoning="\n".join(trace.reasoning_steps),
      confidence=trace.confidence,
      risk=trace.risk,
      recommended_action=trace.recommended_action,
      created_at=trace.created_at
    )
    db.add(db_obj)
    db.commit()

  return task_id, trace


def get_latest_decision_trace() -> DecisionTrace | None:
  if not _DECISION_TRACES:
    return None
  return _DECISION_TRACES[-1]


