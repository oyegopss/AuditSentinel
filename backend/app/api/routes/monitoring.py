from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy import text

from ...agents import get_latest_decision_trace
from ...risk_engine import classify_text_risk
from ...blockchain import compute_action_hash
from ...database import engine


router = APIRouter()

ComponentStatus = Literal["active", "processing", "completed", "error"]


class SystemHealthResponse(BaseModel):
  """System health check: AI agent, database, blockchain RPC, risk engine."""
  ai_service: str = "healthy"
  database: str = "connected"
  blockchain: str = "connected"
  risk_engine: str = "running"


class ComponentState(BaseModel):
  id: str
  name: str
  status: ComponentStatus
  message: str
  last_check: str


def _check_planning_agent() -> tuple[ComponentStatus, str]:
  try:
    get_latest_decision_trace()
    return "active", "Planning agent ready"
  except Exception as e:
    return "error", str(e)[:80]


def _check_execution_agent() -> tuple[ComponentStatus, str]:
  try:
    get_latest_decision_trace()
    return "active", "Execution agent ready"
  except Exception as e:
    return "error", str(e)[:80]


def _check_risk_engine() -> tuple[ComponentStatus, str]:
  try:
    classify_text_risk("test")
    return "active", "Risk engine ready"
  except Exception as e:
    return "error", str(e)[:80]


def _check_blockchain_logger() -> tuple[ComponentStatus, str]:
  try:
    compute_action_hash("test", datetime.now(timezone.utc), "system")
    return "active", "Blockchain logger ready"
  except Exception as e:
    return "error", str(e)[:80]


def _check_database() -> tuple[ComponentStatus, str]:
  try:
    with engine.connect() as conn:
      conn.execute(text("SELECT 1"))
    return "active", "Database connected"
  except Exception as e:
    return "error", str(e)[:80]


@router.get(
  "/system-health",
  response_model=SystemHealthResponse,
  summary="System health check",
  description="Status of AI agent service, database connection, blockchain RPC, and risk engine.",
)
async def system_health() -> SystemHealthResponse:
  """
  Return health status for AI agent service, database, blockchain RPC, and risk engine.
  Values: ai_service (healthy/unhealthy), database (connected/disconnected),
  blockchain (connected/disconnected), risk_engine (running/down).
  """
  ai_status, _ = _check_planning_agent()
  db_status, _ = _check_database()
  chain_status, _ = _check_blockchain_logger()
  risk_status, _ = _check_risk_engine()
  return SystemHealthResponse(
    ai_service="healthy" if ai_status == "active" else "unhealthy",
    database="connected" if db_status == "active" else "disconnected",
    blockchain="connected" if chain_status == "active" else "disconnected",
    risk_engine="running" if risk_status == "active" else "down",
  )


@router.get(
  "/agent-status",
  response_model=list[ComponentState],
  summary="Get status of system components",
  description="Status of Planning Agent, Execution Agent, Risk Engine, Blockchain Logger, and Database (active, processing, completed, error).",
)
async def get_agent_status() -> list[ComponentState]:
  """
  Return status of Planning Agent, Execution Agent, Risk Engine, Blockchain Logger, and Database.
  Status values: active, processing, completed, or error. Updates dynamically per request.
  """
  now = datetime.now(timezone.utc).isoformat()
  checks = [
    ("planning_agent", "Planning Agent", _check_planning_agent),
    ("execution_agent", "Execution Agent", _check_execution_agent),
    ("risk_engine", "Risk Engine", _check_risk_engine),
    ("blockchain_logger", "Blockchain Logger", _check_blockchain_logger),
    ("database", "Database", _check_database),
  ]
  result = []
  for cid, name, fn in checks:
    status, msg = fn()
    result.append(
      ComponentState(
        id=cid,
        name=name,
        status=status,
        message=msg,
        last_check=now,
      )
    )
  return result
