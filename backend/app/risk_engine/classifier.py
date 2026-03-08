from __future__ import annotations

from typing import Tuple

from .models import RiskAssessment, RiskLevel
from ..logging_config import get_logger


logger = get_logger("risk_engine")

# Rule-based destructive-action keywords: if task description contains ANY of these,
# classify as CRITICAL immediately (before normal risk scoring). No autonomous execution.
DESTRUCTIVE_CRITICAL_KEYWORDS = [
  "delete",
  "drop",
  "erase",
  "remove",
  "truncate",
  "destroy",
  "wipe",
  "production database",
  "customer records",
  "user data",
  "financial records",
]

# Critical / destructive phrases (always CRITICAL when present) – checked after destructive keywords.
HIGH_RISK_KEYWORDS = [
  "delete database",
  "delete entire",
  "delete production",
  "drop database",
  "wipe database",
  "remove all data",
  "shutdown server",
  "transfer funds",
  "override diagnosis",
  "execute trading bot",
]

# Moderate-risk phrases.
MODERATE_KEYWORDS = [
  "loan approval",
  "financial transaction",
  "data export",
]


SCENARIO_RISK = {
  # Moderate scenarios
  "financial_loan_approval": (RiskLevel.MEDIUM, 0.6),
  # Destructive / high‑impact scenarios
  "database_deletion": (RiskLevel.CRITICAL, 0.97),
  "delete_production_customer_database": (RiskLevel.CRITICAL, 0.97),
  "healthcare_diagnosis": (RiskLevel.HIGH, 0.91),
  "healthcare_diagnosis_override": (RiskLevel.HIGH, 0.92),
  "automated_trading": (RiskLevel.MEDIUM, 0.7),
  "automated_stock_trading_decision": (RiskLevel.HIGH, 0.85),
  "transfer_5m_to_vendor": (RiskLevel.HIGH, 0.88),
}


def classify_text_risk(text: str) -> RiskAssessment:
  lowered = text.lower()
  matched_phrases: list[str] = []

  # Rule-based destructive-action classifier: runs BEFORE normal risk scoring.
  # Any match → CRITICAL, confidence 0.95, REQUIRE_HUMAN_APPROVAL (no autonomous execution).
  for keyword in DESTRUCTIVE_CRITICAL_KEYWORDS:
    if keyword in lowered:
      matched_phrases.append(keyword)
  if matched_phrases:
    logger.info(
      "Risk detection completed",
      extra={
        "event": "risk_detection",
        "source": "destructive_keywords",
        "risk": RiskLevel.CRITICAL.value,
        "score": 0.95,
      },
    )
    return RiskAssessment(
      scenario=None,
      risk=RiskLevel.CRITICAL,
      score=0.95,
      explanation=(
        "Detected destructive-action keywords "
        f"({', '.join(matched_phrases)}) → CRITICAL risk. "
        "Action: REQUIRE_HUMAN_APPROVAL; autonomous execution not allowed."
      ),
      matched_phrases=matched_phrases,
    )

  # Then, look for destructive / sensitive operations (legacy high-risk phrases).
  for phrase in HIGH_RISK_KEYWORDS:
    if phrase in lowered:
      matched_phrases.append(phrase)

  if matched_phrases:
    level = RiskLevel.CRITICAL
    score = 0.95
    explanation = (
      "Detected destructive or highly sensitive operation keywords "
      f"({', '.join(matched_phrases)}) → classified as critical risk requiring human approval."
    )
  else:
    # Then check for moderate-risk operations.
    for phrase in MODERATE_KEYWORDS:
      if phrase in lowered:
        matched_phrases.append(phrase)

    if matched_phrases:
      level = RiskLevel.MEDIUM
      score = 0.75
      explanation = (
        "Detected moderate-risk financial or data operation keywords "
        f"({', '.join(matched_phrases)}) → classified as medium risk; human approval recommended."
      )
    else:
      # Default: low risk.
      level = RiskLevel.LOW
      score = 0.30
      explanation = "No destructive or moderate‑risk keywords detected; classified as low risk."

  logger.info(
    "Risk detection completed",
    extra={
      "event": "risk_detection",
      "source": "text",
      "risk": level.value,
      "score": score,
    },
  )
  return RiskAssessment(
    scenario=None,
    risk=level,
    score=score,
    explanation=explanation,
    matched_phrases=matched_phrases or None,
  )


def classify_scenario_risk(scenario: str) -> RiskAssessment:
  level, score = SCENARIO_RISK.get(scenario, (RiskLevel.MEDIUM, 0.6))
  explanation = f"Predefined scenario '{scenario}' mapped to {level.value} risk."
  logger.info(
    "Risk detection completed",
    extra={
      "event": "risk_detection",
      "source": "scenario",
      "scenario": scenario,
      "risk": level.value,
      "score": score,
    },
  )
  return RiskAssessment(
    scenario=scenario,
    risk=level,
    score=score,
    explanation=explanation
  )


def is_high_risk(level: RiskLevel) -> bool:
  return level in {RiskLevel.HIGH, RiskLevel.CRITICAL}


def simple_scenario_risk(scenario: str) -> Tuple[str, bool]:
  if scenario in SCENARIO_RISK:
    level, _ = SCENARIO_RISK[scenario]
    risk_str = level.value
  else:
    mapping = {
      "loan_approval": "medium",
    }
    risk_str = mapping.get(scenario, "low")
  requires_approval = risk_str in {"high", "critical"}
  return risk_str, requires_approval
