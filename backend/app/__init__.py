"""
AuditSentinel FastAPI application package.

Modular layout:
- api: FastAPI routers (task, decision, risk, audit, governance, timeline, monitoring, report, analytics)
- agents: decision/task execution (planning, execution agent logic)
- risk_engine: risk classification (RiskLevel, classify_text_risk, classify_scenario_risk, etc.)
- blockchain: action hashing and on-chain logging
- database: SQLAlchemy session, engine, ORM models (DecisionTraceORM, AuditLogORM)
- services: governance score, report generator
- utils: shared helpers (e.g. fmt_ts)
- domain: shared domain models (DecisionTrace, AuditLogEntry) used across modules
"""

