from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...services.decision_service import run_task_and_log_decision
from ...services.risk_service import is_high_risk
from ...db.session import get_session


router = APIRouter()


class TaskRequest(BaseModel):
  description: str


class TaskResponse(BaseModel):
  task_id: str
  output: str
  confidence: float
  risk: str
  recommended_action: str
  requires_human_approval: bool


@router.post("/task", response_model=TaskResponse)
async def submit_task(
  request: TaskRequest,
  db: Session = Depends(get_session)
) -> TaskResponse:
  """
  Entrypoint for AI tasks.

  The AI agent output is routed through the risk detection module; if the
  resulting risk is HIGH or CRITICAL, the response flags that human approval
  is required and the frontend will route the user to the approval panel
  before any irreversible actions are taken. Decision traces are persisted
  to PostgreSQL for later explainability.
  """
  task_id, trace = run_task_and_log_decision(request.description, db=db)
  requires_approval = is_high_risk(trace.risk)
  return TaskResponse(
    task_id=str(task_id),
    output=trace.output,
    confidence=trace.confidence,
    risk=trace.risk.value,
    recommended_action=trace.recommended_action,
    requires_human_approval=requires_approval
  )


