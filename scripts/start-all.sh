#!/usr/bin/env bash
# Start backend + frontend so the app is fully active when you open the website.
# Backend: http://localhost:8000  |  Frontend: http://localhost:3000

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

cleanup() {
  echo ""
  echo "Stopping backend (PID $BACKEND_PID)..."
  kill "$BACKEND_PID" 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

# 1. Backend
echo "Starting backend at http://localhost:8000"
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -r requirements.txt -q 2>/dev/null || true
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$ROOT"

# Give backend time to bind
sleep 3
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo "Backend failed to start. Run ./scripts/start-backend.sh in a separate terminal to see errors."
else
  echo "Backend running (PID $BACKEND_PID)."
fi

# 2. Frontend
echo "Starting frontend at http://localhost:3000"
cd "$ROOT/frontend"
[ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/next" ] && npm install
npm run dev
