from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_session
from ...services.governance_score import compute_governance_score


router = APIRouter(prefix="", tags=["governance"])


class GovernanceScoreResponse(BaseModel):
  """Governance score and component counts for dashboard."""
  governance_score: int = Field(..., description="Composite score 0–100.")
  total_tasks: int = Field(..., description="Total number of tasks.")
  high_risk_tasks: int = Field(..., description="Count of high/critical risk tasks.")
  rejected_actions: int = Field(..., description="Count of rejected approval actions.")


@router.get(
  "/governance-score",
  response_model=GovernanceScoreResponse,
  summary="Get AI governance score",
  description="Governance score (0–100) derived from high-risk actions, rejected decisions, and blockchain-verified logs; includes total_tasks, high_risk_tasks, rejected_actions.",
)
async def governance_score(
  db: Session = Depends(get_session)
) -> GovernanceScoreResponse:
  """
  Return the aggregate AI governance score (0–100) and component counts.

  The score penalizes high-risk actions and rewards rejected decisions and
  blockchain-verified logs. Use for dashboard circular progress and breakdowns.
  """
  result = compute_governance_score(db)
  return GovernanceScoreResponse(
    governance_score=result.score,
    total_tasks=result.total_tasks,
    high_risk_tasks=result.high_risk_actions,
    rejected_actions=result.rejected_decisions,
  )
