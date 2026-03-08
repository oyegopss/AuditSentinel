from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_session
from ...services.risk_analytics import get_risk_distribution as compute_risk_distribution


router = APIRouter()


class RiskDistributionResponse(BaseModel):
  low: int
  medium: int
  high: int
  critical: int


@router.get(
  "/risk-analytics",
  response_model=RiskDistributionResponse,
  summary="Get risk analytics (distribution across tasks)",
  description="Counts per risk level (low, medium, high, critical). Query: source=tasks|actions|combined.",
)
async def risk_analytics(
  db: Session = Depends(get_session),
  source: str = "tasks",
) -> RiskDistributionResponse:
  """
  Return risk level distribution: counts for low, medium, high, and critical.
  Source: tasks (decision traces), actions (audit log), or combined.
  """
  d = compute_risk_distribution(db, source=source)
  return RiskDistributionResponse(
    low=d.low,
    medium=d.medium,
    high=d.high,
    critical=d.critical,
  )


@router.get(
  "/risk-distribution",
  response_model=RiskDistributionResponse,
  summary="Get risk level distribution (legacy)",
  description="Same as GET /risk-analytics.",
)
async def get_risk_distribution(
  db: Session = Depends(get_session),
  source: str = "tasks",
) -> RiskDistributionResponse:
  """Same as /risk-analytics. Source: tasks, actions, or combined."""
  d = compute_risk_distribution(db, source=source)
  return RiskDistributionResponse(
    low=d.low,
    medium=d.medium,
    high=d.high,
    critical=d.critical,
  )
