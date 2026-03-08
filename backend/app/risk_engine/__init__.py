from typing import Any, Dict, List

from .models import RiskAssessment, RiskLevel
from .classifier import (
  classify_text_risk,
  classify_scenario_risk,
  is_high_risk,
  simple_scenario_risk,
)

# Destructive-action keywords: if task contains ANY of these, return CRITICAL immediately.
# This rule runs first and overrides all other risk scoring (including AI model output).
DESTRUCTIVE_KEYWORDS = [
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


def calculate_risk(description: str) -> Dict[str, Any]:
  """
  Risk evaluation entrypoint. Destructive-keyword rule runs first and overrides
  normal scoring. Only if no destructive keywords are found does normal risk logic run.

  Returns a dict with keys:
  - risk_level: "low" | "medium" | "high" | "critical"
  - risk_score: int 0–100
  - decision: "REQUIRE_HUMAN_APPROVAL" | "AUTO_EXECUTE_WITH_LOGGING"
  - auto_execute: bool (False for CRITICAL/high risk)
  - risk, confidence, requires_human_approval, reasoning_steps (backward compat)
  """
  # 1. Convert to lowercase for keyword checks.
  lowered = (description or "").lower()

  # 2. Destructive-keyword check: if any match, return CRITICAL immediately.
  # This rule must override the AI model output; do not run normal risk scoring.
  for keyword in DESTRUCTIVE_KEYWORDS:
    if keyword in lowered:
      return {
        "risk_level": "CRITICAL",
        "risk_score": 95,
        "decision": "REQUIRE_HUMAN_APPROVAL",
        "auto_execute": False,
        "risk": "critical",
        "confidence": 0.95,
        "requires_human_approval": True,
        "reasoning_steps": [
          f"Destructive keyword '{keyword}' detected; rule override → CRITICAL. "
          "REQUIRE_HUMAN_APPROVAL; auto_execute disabled."
        ],
      }

  # 4. Only if no destructive keywords: run normal risk scoring logic.
  assessment: RiskAssessment = classify_text_risk(description)
  requires_approval = is_high_risk(assessment.risk)
  reasoning_steps: List[str] = []
  if assessment.explanation:
    reasoning_steps.append(assessment.explanation)

  risk_score = int(round(assessment.score * 100))
  decision = (
    "REQUIRE_HUMAN_APPROVAL"
    if requires_approval
    else "AUTO_EXECUTE_WITH_LOGGING"
  )
  auto_execute = not requires_approval

  return {
    "risk_level": assessment.risk.value,
    "risk_score": risk_score,
    "decision": decision,
    "auto_execute": auto_execute,
    "risk": assessment.risk.value,
    "confidence": assessment.score,
    "requires_human_approval": requires_approval,
    "reasoning_steps": reasoning_steps,
  }


__all__ = [
  "RiskLevel",
  "RiskAssessment",
  "classify_text_risk",
  "classify_scenario_risk",
  "is_high_risk",
  "simple_scenario_risk",
  "calculate_risk",
]
