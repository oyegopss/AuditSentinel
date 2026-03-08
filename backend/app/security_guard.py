from __future__ import annotations

from typing import Any, Dict, List

from .logging_config import get_logger
from .risk_engine import RiskLevel


logger = get_logger("security_guard")

PROMPT_INJECTION_KEYWORDS: List[str] = [
  "ignore safety rules",
  "bypass safeguards",
  "override system",
  "delete everything",
  "disable security",
  "ignore instructions",
]


def detect_prompt_injection(text: str) -> Dict[str, Any]:
  """
  Lightweight prompt injection detector.

  Returns:
    { "blocked": True, "message": "..."} when a suspicious phrase is present,
    otherwise { "blocked": False }.
  """
  lowered = (text or "").lower()
  matched: List[str] = [p for p in PROMPT_INJECTION_KEYWORDS if p in lowered]

  if matched:
    logger.warning(
      "Prompt injection attempt detected",
      extra={
        "event": "prompt_injection_detected",
        "matched_phrases": matched,
      },
    )
    return {
      "blocked": True,
      "message": "Prompt injection attempt detected. Execution blocked.",
      "matched_phrases": matched,
      "risk": RiskLevel.CRITICAL.value,
    }

  return {"blocked": False}

