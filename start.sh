#!/bin/bash

echo "==============================="
echo "🚀 UTEP Professor Ranking Starter"
echo "==============================="

echo "🔪 Killing old uvicorn and vite processes..."
pkill -f "uvicorn" 2>/dev/null
pkill -f "vite" 2>/dev/null

# Free common dev ports
for port in 8000 5173; do
  pid=$(lsof -ti :$port)
  if [ -n "$pid" ]; then
    echo "🧹 Freeing port $port (PID $pid)..."
    kill -9 $pid 2>/dev/null
  fi
done

cd "$(dirname "$0")"

echo "🐍 Starting FastAPI backend..."
(
  python3 -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
) &

echo "🌐 Starting React frontend..."
npm run dev
