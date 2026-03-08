# FastAPI Routes Reference

## Task submission
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/task` | Submit an AI task. Body: `{ "description": "string" }`. Returns task_id, output, confidence, risk, recommended_action, requires_human_approval. |

## Risk simulation
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/simulate-risk` | Run risk simulation. Body: `{ "scenario": "string", "description": "string" }`. Returns scenario, risk, score, explanation, requires_human_approval. |
| `POST` | `/risk-score` | Simple risk score. Body: `{ "scenario": "string" }`. Returns scenario, risk_level, requires_approval. |

## Approval workflow
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/approve-action` | Approve or reject a risky action. Body: `{ "scenario": "string", "description": "string", "approved": boolean, "user": "string" }`. Returns status, risk, action_hash, tx_hash (if approved high-risk), timestamp. |

## Audit logs
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/audit-log` | List all audit log entries (action_description, action_hash, tx_hash, timestamp, risk, status). |
| `GET` | `/audit-logs` | Alias for `/audit-log`. |

## Governance score retrieval
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/governance-score` | Get governance score (0–100) and counts: high_risk_actions, rejected_decisions, blockchain_verified_logs. |

---
Interactive docs: run the backend and open `/docs` (Swagger UI) or `/redoc`.

## Demo seed data

To preload sample AI tasks and risk-scenario audit entries for demos, run from the backend directory (with your venv activated):

```bash
cd backend && python -m app.scripts.seed_data
```

This inserts 5 sample tasks with decision traces (varying risk levels) and 5 sample audit log entries (e.g. loan approval, DB deletion, healthcare, trading; approved/rejected, some with mock tx hashes).
