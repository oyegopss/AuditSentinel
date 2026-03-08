from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter

from ...agents import get_latest_decision_trace


router = APIRouter()


class DecisionTraceResponse(BaseModel):
  task_id: Optional[str]
  output: str
  reasoning_steps: list[str]
  confidence: float
  risk: str
  recommended_action: str
  created_at: str


@router.get(
  "/decision-trace",
  response_model=DecisionTraceResponse,
  summary="Get latest AI decision trace",
  description="Latest AI decision from task submission: output, reasoning steps, confidence, risk, recommended action.",
)
async def get_decision_trace() -> DecisionTraceResponse:
  """
  Return the most recent AI decision trace for explainability (XAI) dashboards.

  Includes the agent's decision output, ordered reasoning steps, confidence score,
  risk level, recommended action, and creation timestamp. If no task has been
  submitted yet, returns a placeholder with idle state.
  """
  trace = get_latest_decision_trace()
  if trace is None:
    from datetime import datetime, timezone

    return DecisionTraceResponse(
      task_id=None,
      output="No tasks have been executed yet. Submit a task to see a live decision trace.",
      reasoning_steps=[
        "Awaiting first task submission.",
        "Once a task is executed, its reasoning steps will appear here."
      ],
      confidence=0.0,
      risk="low",
      recommended_action="idle",
      created_at=datetime.now(timezone.utc).isoformat()
    )

  return DecisionTraceResponse(
    task_id=str(trace.task_id) if trace.task_id else None,
    output=trace.output,
    reasoning_steps=trace.reasoning_steps,
    confidence=trace.confidence,
    risk=trace.risk.value,
    recommended_action=trace.recommended_action,
    created_at=trace.created_at.isoformat()
  )
