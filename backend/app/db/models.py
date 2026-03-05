import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SAEnum, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ..domain.models import RiskLevel
from .session import Base


class DecisionTraceORM(Base):
  __tablename__ = "decision_traces"

  id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  task_id = Column(PGUUID(as_uuid=True), nullable=True, index=True)
  output = Column(Text, nullable=False)
  reasoning = Column(Text, nullable=False)  # newline‑separated steps
  confidence = Column(Float, nullable=False)
  risk = Column(SAEnum(RiskLevel), nullable=False)
  recommended_action = Column(String(128), nullable=False)
  created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLogORM(Base):
  __tablename__ = "audit_logs"

  id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  action_hash = Column(String(128), nullable=False, index=True)
  tx_hash = Column(String(128), nullable=True)
  timestamp = Column(DateTime, nullable=True)
  action_description = Column(Text, nullable=False)
  risk = Column(SAEnum(RiskLevel), nullable=False)
  status = Column(String(32), nullable=False)
  created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


