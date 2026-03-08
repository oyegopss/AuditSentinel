from __future__ import annotations

from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..domain.models import DecisionTrace
from ..risk_engine import RiskLevel, RiskAssessment, classify_text_risk
from ..database.models import DecisionTraceORM
from ..logging_config import get_logger


logger = get_logger("agents.decision")
_DECISION_TRACES: List[DecisionTrace] = []


def run_task_and_log_decision(
  task_text: str,
  db: Session | None = None,
  task_id: Optional[UUID] = None,
) -> Tuple[UUID, DecisionTrace]:
  if task_id is None:
    task_id = uuid4()
  risk_assessment: RiskAssessment = classify_text_risk(task_text)

  if risk_assessment.matched_phrases:
    keyword_str = ", ".join(risk_assessment.matched_phrases)
    detection_step = (
      f"Detected policy / risk keywords ({keyword_str}) and applied rules "
      f"→ classified as {risk_assessment.risk.value} risk."
    )
  else:
    detection_step = (
      f"Evaluated task against governance policies; no destructive keywords "
      f"found → classified as {risk_assessment.risk.value} risk."
    )

  reasoning_steps = [
    "Parsed task description and extracted core intent.",
    detection_step,
    "Checked whether this risk band requires human approval.",
    "Prepared recommended action with safeguards, logging, and human approval gates for high/critical risk.",
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

  logger.info(
    "AI decision generated",
    extra={
      "event": "agent_decision",
      "task_id": str(task_id),
      "risk": trace.risk.value,
      "recommended_action": trace.recommended_action,
      "confidence": trace.confidence,
    },
  )
  return task_id, trace


def get_latest_decision_trace() -> DecisionTrace | None:
  if not _DECISION_TRACES:
    return None
  return _DECISION_TRACES[-1]
