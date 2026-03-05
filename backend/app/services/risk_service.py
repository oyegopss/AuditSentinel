from __future__ import annotations

from typing import Tuple

from ..domain.models import RiskAssessment, RiskLevel


KEYWORD_RISK = {
  "delete": RiskLevel.CRITICAL,
  "drop table": RiskLevel.CRITICAL,
  "truncate": RiskLevel.CRITICAL,
  "transfer": RiskLevel.HIGH,
  "wire": RiskLevel.HIGH,
  "loan": RiskLevel.HIGH,
  "diagnosis": RiskLevel.HIGH,
  "trade": RiskLevel.MEDIUM
}


SCENARIO_RISK = {
  # loan approval above large amount → high
  "financial_loan_approval": (RiskLevel.HIGH, 0.82),
  # database deletion → critical
  "database_deletion": (RiskLevel.CRITICAL, 0.97),
  # healthcare diagnosis → high
  "healthcare_diagnosis": (RiskLevel.HIGH, 0.91),
  # automated trading → medium
  "automated_trading": (RiskLevel.MEDIUM, 0.7)
}


def classify_text_risk(text: str) -> RiskAssessment:
  lowered = text.lower()
  best_level = RiskLevel.LOW
  for keyword, level in KEYWORD_RISK.items():
    if keyword in lowered and level.value > best_level.value:
      best_level = level

  if "approval" in lowered and best_level == RiskLevel.LOW:
    best_level = RiskLevel.MEDIUM

  score = {
    RiskLevel.LOW: 0.2,
    RiskLevel.MEDIUM: 0.5,
    RiskLevel.HIGH: 0.8,
    RiskLevel.CRITICAL: 0.95
  }[best_level]

  explanation = (
    "No obviously dangerous operations detected."
    if best_level == RiskLevel.LOW
    else f"Detected high‑impact operation category matching {best_level.value} risk."
  )

  return RiskAssessment(
    scenario=None,
    risk=best_level,
    score=score,
    explanation=explanation
  )


def classify_scenario_risk(scenario: str) -> RiskAssessment:
  level, score = SCENARIO_RISK.get(scenario, (RiskLevel.MEDIUM, 0.6))
  explanation = f"Predefined scenario '{scenario}' mapped to {level.value} risk."
  return RiskAssessment(
    scenario=scenario,
    risk=level,
    score=score,
    explanation=explanation
  )


def is_high_risk(level: RiskLevel) -> bool:
  return level in {RiskLevel.HIGH, RiskLevel.CRITICAL}


def simple_scenario_risk(scenario: str) -> tuple[str, bool]:
  """
  Simple risk scoring helper that maps a scenario string into:
  - risk_level: low | medium | high | critical
  - requires_approval: True for high / critical
  """
  mapping = {
    "loan_approval": "high",
    "financial_loan_approval": "high",
    "database_deletion": "critical",
    "healthcare_diagnosis": "high",
    "automated_trading": "medium"
  }
  risk_level = mapping.get(scenario, "low")
  requires_approval = risk_level in {"high", "critical"}
  return risk_level, requires_approval




