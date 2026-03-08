#!/usr/bin/env bash
# Start AuditSentinel frontend on http://localhost:3000
cd "$(dirname "$0")/../frontend"
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/next" ]; then
  echo "Installing frontend dependencies..."
  rm -rf node_modules .next 2>/dev/null
  npm install
fi
echo "Starting frontend at http://localhost:3000"
npm run dev
