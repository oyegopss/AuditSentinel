from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


class RiskLevel(str, Enum):
  LOW = "low"
  MEDIUM = "medium"
  HIGH = "high"
  CRITICAL = "critical"


@dataclass
class DecisionTrace:
  id: UUID = field(default_factory=uuid4)
  task_id: Optional[UUID] = None
  output: str = ""
  reasoning_steps: List[str] = field(default_factory=list)
  confidence: float = 0.0
  risk: RiskLevel = RiskLevel.LOW
  recommended_action: str = ""
  created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditLogEntry:
  id: UUID = field(default_factory=uuid4)
  action_hash: str = ""
  tx_hash: Optional[str] = None
  timestamp: Optional[datetime] = None
  action_description: str = ""
  risk: RiskLevel = RiskLevel.LOW
  status: str = "pending"
  created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskAssessment:
  scenario: Optional[str]
  risk: RiskLevel
  score: float
  explanation: str


