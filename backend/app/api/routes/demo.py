"""Demo scenarios for UI and seeding."""
from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter


router = APIRouter(prefix="", tags=["demo"])


class DemoScenario(BaseModel):
  id: str
  name: str
  description: str
  risk_level: str
  ai_decision: str


DEMO_SCENARIOS = [
  DemoScenario(
    id="loan_approval",
    name="Loan approval",
    description="Approve the $2M loan application for customer Y based on credit model and income verification.",
    risk_level="high",
    ai_decision="Task requires human review before execution. Risk classification: high. Recommended action: require_human_approval.",
  ),
  DemoScenario(
    id="database_deletion",
    name="Delete database",
    description="Execute database cleanup: truncate legacy audit table and drop deprecated schema.",
    risk_level="critical",
    ai_decision="Task requires human review before execution. Risk classification: critical. Recommended action: require_human_approval.",
  ),
  DemoScenario(
    id="medical_diagnosis",
    name="Medical diagnosis",
    description="Generate draft differential diagnosis from patient notes for physician review.",
    risk_level="high",
    ai_decision="Task requires human review before execution. Risk classification: high. Recommended action: require_human_approval.",
  ),
  DemoScenario(
    id="automated_trading",
    name="Automated trading",
    description="Execute algo trade: buy 1000 shares ETF-X within configured volatility band.",
    risk_level="medium",
    ai_decision="Task approved for autonomous execution with audit logging. Risk classification: medium. Recommended action: auto_execute_with_logging.",
  ),
]


@router.get(
  "/demo-scenarios",
  response_model=list[DemoScenario],
  summary="List demo scenarios",
  description="Predefined scenarios (loan approval, delete database, medical diagnosis, automated trading) with risk level and AI decision.",
)
async def get_demo_scenarios() -> list[DemoScenario]:
  """
  Return predefined demo scenarios for UI and testing.

  Each scenario includes id, name, description, risk_level, and ai_decision.
  """
  return DEMO_SCENARIOS
