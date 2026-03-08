# Run AuditSentinel on localhost

**Backend (port 8000)** and **frontend (port 3000)** must both be running for Task submission, AI decision viewer, Human approval panel, Blockchain audit logs, Agent monitoring, and Live governance activity to be active.

---

## Quick start — activate everything

From the project root:

```bash
chmod +x scripts/start-all.sh
./scripts/start-all.sh
```

Then open **http://localhost:3000**. Press `Ctrl+C` to stop both servers.

---

## 1. Backend — http://localhost:8000

Open a terminal and run:

```bash
cd backend
python3 -m venv .venv   # only if .venv doesn't exist
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Using `.venv/bin/uvicorn` ensures the venv's Python is used even if the shell didn't activate correctly.

Or use the script:

```bash
cd /Users/gopaljidwivedi/AuditSentinel
chmod +x scripts/start-backend.sh
./scripts/start-backend.sh
```

When it’s running you should see something like: `Uvicorn running on http://0.0.0.0:8000`.  
Then open **http://localhost:8000/docs** in the browser to confirm.

---

## 2. Frontend — http://localhost:3000

Open a **second** terminal and run:

```bash
cd /Users/gopaljidwivedi/AuditSentinel/frontend
rm -rf node_modules .next
npm install
npm run dev
```

Or use the script:

```bash
cd /Users/gopaljidwivedi/AuditSentinel
chmod +x scripts/start-frontend.sh
./scripts/start-frontend.sh
```

When it’s running you should see: `Local: http://localhost:3000`.  
Open **http://localhost:3000** in the browser for the app.

---

## Summary

| Service  | URL                  | Command (from project root)        |
|----------|----------------------|------------------------------------|
| Backend  | http://localhost:8000  | `./scripts/start-backend.sh` or `cd backend && . .venv/bin/activate && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| Frontend | http://localhost:3000  | `cd frontend && npm run dev`       |

**If “localhost refused to connect”:**  
The server for that port isn’t running. Start the backend in one terminal and the frontend in another, then try again.
