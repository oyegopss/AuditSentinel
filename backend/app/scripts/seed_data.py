"""
Seed data: sample AI tasks and risk scenarios for demo purposes.

Run from backend (with venv activated and deps installed):
  cd backend && python -m app.scripts.seed_data

Inserts:
- 5 sample AI tasks with decision traces (low/medium/high/critical risk).
- 5 sample audit log entries (loan, DB delete, healthcare, trading; approved/rejected).
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from ..database import get_session
from ..database.models import Task, DecisionTraceORM, AuditLog
from ..risk_engine import RiskLevel
from ..utils.hashing import sha256_action_hash


# ---------------------------------------------------------------------------
# Sample AI tasks (description, expected risk, output, reasoning)
# ---------------------------------------------------------------------------
SAMPLE_AI_TASKS = [
    {
        "description": "Summarize the quarterly compliance report for the board.",
        "risk": RiskLevel.LOW,
        "score": 0.2,
        "output": "Task approved for autonomous execution with audit logging.",
        "reasoning": "Parsed task description and extracted core intent.\nMatched task against policy and risk rules → low risk.\nChecked if human approval is required for this risk band.\nPrepared recommended action with safeguards and logging hooks.",
        "recommended_action": "auto_execute_with_logging",
    },
    {
        "description": "Check vendor Acme Corp for sanctions and reputational risk.",
        "risk": RiskLevel.MEDIUM,
        "score": 0.5,
        "output": "Task approved for autonomous execution with audit logging.",
        "reasoning": "Parsed task description and extracted core intent.\nMatched task against policy and risk rules → medium risk.\nChecked if human approval is required for this risk band.\nPrepared recommended action with safeguards and logging hooks.",
        "recommended_action": "auto_execute_with_logging",
    },
    {
        "description": "Approve the $2M loan application for customer Y based on credit model.",
        "risk": RiskLevel.HIGH,
        "score": 0.82,
        "output": "Task requires human review before execution.",
        "reasoning": "Parsed task description and extracted core intent.\nMatched task against policy and risk rules → high risk.\nChecked if human approval is required for this risk band.\nPrepared recommended action with safeguards and logging hooks.",
        "recommended_action": "require_human_approval",
    },
    {
        "description": "Execute database cleanup: truncate legacy audit table.",
        "risk": RiskLevel.CRITICAL,
        "score": 0.97,
        "output": "Task requires human review before execution.",
        "reasoning": "Parsed task description and extracted core intent.\nMatched task against policy and risk rules → critical risk.\nChecked if human approval is required for this risk band.\nPrepared recommended action with safeguards and logging hooks.",
        "recommended_action": "require_human_approval",
    },
    {
        "description": "Generate draft diagnosis summary from patient notes for review.",
        "risk": RiskLevel.HIGH,
        "score": 0.91,
        "output": "Task requires human review before execution.",
        "reasoning": "Parsed task description and extracted core intent.\nMatched task against policy and risk rules → high risk.\nChecked if human approval is required for this risk band.\nPrepared recommended action with safeguards and logging hooks.",
        "recommended_action": "require_human_approval",
    },
]

# ---------------------------------------------------------------------------
# Sample audit log entries (risk scenarios: approved/rejected, with optional tx)
# ---------------------------------------------------------------------------
SAMPLE_AUDIT_ENTRIES = [
    {
        "scenario": "financial_loan_approval",
        "action_description": "Approve $500k loan for applicant REF-8821 based on credit score and income.",
        "risk": RiskLevel.HIGH,
        "status": "approved",
        "tx_hash": "0x7a3f2e1b4c5d6e8f9a0b1c2d3e4f5a6b7c8d9e0f",
        "user": "analyst-jane",
    },
    {
        "scenario": "database_deletion",
        "action_description": "DROP TABLE legacy_customers; requested by data team.",
        "risk": RiskLevel.CRITICAL,
        "status": "rejected",
        "tx_hash": None,
        "user": "ops-admin",
    },
    {
        "scenario": "healthcare_diagnosis",
        "action_description": "AI-generated differential diagnosis for case #4412 for physician review.",
        "risk": RiskLevel.HIGH,
        "status": "approved",
        "tx_hash": "0x9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2e1f0d",
        "user": "dr-smith",
    },
    {
        "scenario": "automated_trading",
        "action_description": "Execute algo trade: buy 1000 shares ETF-X within volatility band.",
        "risk": RiskLevel.MEDIUM,
        "status": "approved",
        "tx_hash": None,
        "user": "trader-bot",
    },
    {
        "scenario": "financial_loan_approval",
        "action_description": "Reject loan application REF-8822 — policy threshold exceeded.",
        "risk": RiskLevel.HIGH,
        "status": "rejected",
        "tx_hash": None,
        "user": "analyst-jane",
    },
]


def run_seed(db) -> None:
    """Insert sample tasks, decision traces, and audit log entries."""
    # Create tasks and decision traces
    for sample in SAMPLE_AI_TASKS:
        task_id = uuid4()
        task = Task(
            id=task_id,
            description=sample["description"],
            status="completed",
        )
        db.add(task)
        db.flush()

        trace = DecisionTraceORM(
            task_id=task_id,
            output=sample["output"],
            reasoning=sample["reasoning"],
            confidence=sample["score"],
            risk=sample["risk"],
            recommended_action=sample["recommended_action"],
        )
        db.add(trace)

    # Create audit log entries
    for sample in SAMPLE_AUDIT_ENTRIES:
        ts = datetime.now(timezone.utc)
        action_hash = sha256_action_hash(
            sample["action_description"],
            ts,
            sample["user"],
        )
        entry = AuditLog(
            action_hash=action_hash,
            tx_hash=sample["tx_hash"],
            timestamp=ts,
            action_description=sample["action_description"],
            risk=sample["risk"],
            status=sample["status"],
        )
        db.add(entry)

    db.commit()


def main() -> None:
    gen = get_session()
    db = next(gen)
    try:
        run_seed(db)
        print(
            "Seed data loaded: %d tasks/traces, %d audit entries."
            % (len(SAMPLE_AI_TASKS), len(SAMPLE_AUDIT_ENTRIES))
        )
    finally:
        try:
            next(gen)
        except StopIteration:
            pass


if __name__ == "__main__":
    main()
