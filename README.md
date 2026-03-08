# AuditSentinel

AuditSentinel is a full‑stack, agentic governance demo that shows how to run AI
tasks through **risk detection, human approval, and blockchain audit logging**.

## Stack

- **Frontend**: Next.js, TailwindCSS (Shadcn‑style components)
- **Backend**: FastAPI (Python)
- **AI Agents**: LangChain (stubbed for demo)
- **Blockchain**: Solidity contract on Polygon testnet (`AuditSentinelAudit.sol`)
- **Database**: PostgreSQL (not wired yet; current demo uses in‑memory stores)

## High‑level flow

User Task → AI Agent → Risk Detection → Human Approval → Blockchain Log → Audit Report

1. A task is submitted from the `Task submission` page (`/`).
2. FastAPI endpoint `/task` calls a LangChain‑style decision service, producing:
   - decision output
   - reasoning steps
   - confidence score
   - risk classification
   - recommended action
3. The latest decision trace is available via `/decision-trace` and visualised in
   the **AI decision explainability** page (`/decision`).
4. The **Human approval** page (`/approve`) lets you simulate risky scenarios
   (`/simulate-risk`) and approve / reject them (`/approve-action`).
5. Approved high‑risk actions are passed to `blockchain_logger.py`, which
   computes an action hash and (in this demo) fabricates a Polygon tx hash.
   The result is stored in an in‑memory audit log and exposed via
   `/audit-log` (`/audit-logs` alias).
6. The **Blockchain audit log** page (`/audit-logs`) renders an audit table and
   provides a **View on Polygon** link for each transaction hash.

## Running the project

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The key endpoints are:

- `POST /task` – submit a free‑form AI task
- `GET /decision-trace` – latest explainability trace (XAI)
- `POST /simulate-risk` – simulate a pre‑built risky scenario
- `POST /approve-action` – human approval + blockchain logging
- `GET /audit-log` / `GET /audit-logs` – audit entries

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

By default the frontend expects the API at `http://localhost:8000`.

### Deploying to Vercel

The Next.js app lives in the **`frontend`** directory. For Vercel to detect Next.js and build correctly:

1. In your Vercel project, go to **Settings** → **General**.
2. Under **Root Directory**, click **Edit** and set it to **`frontend`**.
3. Save and redeploy.

If Root Directory is left at the repo root, Vercel will show "Could not identify Next.js version" because the app and its `package.json` are in `frontend/`.

### Smart contract (Polygon testnet)

Contract: `smart-contracts/AuditSentinelAudit.sol`

You can deploy it using your preferred toolchain (Hardhat, Foundry, Remix) to a
Polygon testnet such as **Amoy**. After deployment, update the backend
`blockchain_logger.py` to use the real contract address and call `logAction`
instead of emitting a stub transaction hash.

## Notes

- The demo currently keeps decision traces and audit logs in memory so it is
  self‑contained; swap these out for PostgreSQL models for production.
- LangChain calls are abstracted behind `decision_service.py` and
  `risk_service.py` so you can drop in real agents and policies without
  changing the API surface.

