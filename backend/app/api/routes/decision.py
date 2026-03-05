from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from ...services.decision_service import get_latest_decision_trace


router = APIRouter()


class DecisionTraceResponse(BaseModel):
  task_id: str | None
  output: str
  reasoning_steps: list[str]
  confidence: float
  risk: str
  recommended_action: str
  created_at: str


@router.get("/decision-trace", response_model=DecisionTraceResponse)
async def get_decision_trace() -> DecisionTraceResponse:
  """
  Returns the latest decision trace captured from the agent run.
  Suitable for powering an XAI dashboard panel in the frontend.
  """
  trace = get_latest_decision_trace()
  if trace is None:
    # Provide a synthetic example to keep the demo self‑contained.
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


