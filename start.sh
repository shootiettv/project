#!bin/bash

echo "🔪 Killing old uvicorn and vite processes..."
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

# Free common dev ports
for port in 8000 5173 5174 5175 5176 5177 5178 5179 5180 5181 5182; do
  pid=$(lsof -ti :$port)
  if [ -n "$pid" ]; then
    echo "🧹 Freeing port $port (PID $pid)..."
    kill -9 $pid 2>/dev/null
  fi
done

cd "$(dirname "$0")" #goes to the folder where start.sh lives

echo "Starting FastAPI backend..."
(python3 -m uvicorn main:app --reload --workers 1 &)

echo "Starting React frontend..."
npm run dev
