import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, CHAR, JSON

from ..risk_engine import RiskLevel
from .session import Base


class GUID(TypeDecorator):
  """Portable UUID type (SQLite stores as 36-char string; works with PostgreSQL too)."""
  impl = CHAR
  cache_ok = True

  def load_dialect_impl(self, dialect):
    if dialect.name == "postgresql":
      from sqlalchemy.dialects.postgresql import UUID as PGUUID
      return dialect.type_descriptor(PGUUID(as_uuid=True))
    return dialect.type_descriptor(CHAR(36))

  def process_bind_param(self, value, dialect):
    if value is None:
      return value
    if dialect.name == "postgresql":
      return value
    return str(value) if isinstance(value, uuid.UUID) else value

  def process_result_value(self, value, dialect):
    if value is None:
      return value
    if isinstance(value, uuid.UUID):
      return value
    return uuid.UUID(value)

TASK_STATUS_SUBMITTED = "submitted"
TASK_STATUS_PROCESSING = "processing"
TASK_STATUS_RISK_EVALUATED = "risk_evaluated"
TASK_STATUS_AWAITING_APPROVAL = "awaiting_approval"
TASK_STATUS_APPROVED = "approved"
TASK_STATUS_EXECUTED = "executed"
TASK_STATUS_LOGGED_ON_CHAIN = "logged_on_chain"


class Task(Base):
  __tablename__ = "tasks"

  id = Column(GUID, primary_key=True, default=uuid.uuid4)
  description = Column(Text, nullable=False)
  status = Column(String(32), nullable=False, default=TASK_STATUS_SUBMITTED)
  state_timestamps = Column(JSON, nullable=False, default=dict)
  created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
  updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

  decision_traces = relationship(
    "DecisionTraceORM",
    back_populates="task",
    foreign_keys="DecisionTraceORM.task_id",
    cascade="all, delete-orphan",
  )
  audit_logs = relationship(
    "AuditLog",
    back_populates="task",
    foreign_keys="AuditLog.task_id",
  )


class DecisionTraceORM(Base):
  __tablename__ = "decision_traces"

  id = Column(GUID, primary_key=True, default=uuid.uuid4)
  task_id = Column(GUID, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
  output = Column(Text, nullable=False)
  reasoning = Column(Text, nullable=False)
  confidence = Column(Float, nullable=False)
  risk = Column(SAEnum(RiskLevel), nullable=False)
  recommended_action = Column(String(128), nullable=False)
  created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

  task = relationship("Task", back_populates="decision_traces", foreign_keys=[task_id])


class AuditLog(Base):
  __tablename__ = "audit_logs"

  id = Column(GUID, primary_key=True, default=uuid.uuid4)
  task_id = Column(GUID, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
  action_hash = Column(String(128), nullable=False, index=True)
  tx_hash = Column(String(128), nullable=True)
  timestamp = Column(DateTime(timezone=True), nullable=True)
  action_description = Column(Text, nullable=False)
  risk = Column(SAEnum(RiskLevel), nullable=False)
  status = Column(String(32), nullable=False)
  created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
  updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

  task = relationship("Task", back_populates="audit_logs", foreign_keys=[task_id])


class GovernanceMetrics(Base):
  __tablename__ = "governance_metrics"

  id = Column(GUID, primary_key=True, default=uuid.uuid4)
  score = Column(Integer, nullable=False)
  high_risk_actions = Column(Integer, nullable=False, default=0)
  rejected_decisions = Column(Integer, nullable=False, default=0)
  blockchain_verified_logs = Column(Integer, nullable=False, default=0)
  created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
  updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
