#!/bin/zsh
# Start the full-stack Estado de Cuenta system
# Usage: ./start.sh

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "═══════════════════════════════════════════"
echo "  Estado de Cuenta — Full-Stack System"
echo "═══════════════════════════════════════════"

# Kill any existing processes on these ports
echo "\n⏹  Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 1

# ── Backend ──────────────────────────────────────────────────────────────────
echo "\n▶ Starting FastAPI backend on http://localhost:8000 ..."
source "$PROJECT_DIR/.venv/bin/activate"
cd "$PROJECT_DIR"
uvicorn main:app --port 8000 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"
sleep 2

# ── Frontend ─────────────────────────────────────────────────────────────────
echo "\n▶ Starting React frontend on http://localhost:5173 ..."
cd "$PROJECT_DIR/frontend"
# CI=true disables Vite's interactive stdin (prevents SIGTTOU in background)
CI=true npm run dev -- --port 5173 &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"
sleep 3

echo "\n─────────────────────────────────────────────"
echo "  ✅ Backend  → http://localhost:8000"
echo "  ✅ Frontend → http://localhost:5173"
echo "  📖 API Docs → http://localhost:8000/docs"
echo "─────────────────────────────────────────────"
echo "  Press Ctrl+C to stop both servers\n"

# Clean up on exit
trap "echo '\nStopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait

