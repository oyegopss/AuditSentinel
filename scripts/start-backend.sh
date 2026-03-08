#!/usr/bin/env bash
# Start AuditSentinel backend on http://localhost:8000
set -e
BACKEND_DIR="$(cd "$(dirname "$0")/../backend" && pwd)"
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -r requirements.txt -q 2>/dev/null || true
echo "Starting backend at http://localhost:8000"
echo "Open http://localhost:8000 or http://localhost:8000/docs in your browser."
exec .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
