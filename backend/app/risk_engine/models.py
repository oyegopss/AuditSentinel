from __future__ import annotations

from enum import Enum
from typing import Optional

from dataclasses import dataclass
from typing import List


class RiskLevel(str, Enum):
  LOW = "low"
  MEDIUM = "medium"
  HIGH = "high"
  CRITICAL = "critical"


@dataclass
class RiskAssessment:
  scenario: Optional[str]
  risk: RiskLevel
  score: float
  explanation: str
  # Matched keywords or phrases that drove the classification (for explainability).
  matched_phrases: Optional[List[str]] = None
