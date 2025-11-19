@echo off
echo ===============================
echo 🚀 UTEP Professor Ranking Starter (Windows)
echo ===============================

echo 🔪 Killing old uvicorn and Vite processes...

:: Kill uvicorn and vite processes if they exist
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

:: Free ports 8000 and 5173
echo Checking for processes on ports 8000 and 5173...

for %%p in (8000 5173) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p') do (
        echo 🧹 Freeing port %%p (PID %%a)...
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Move to script directory
cd /d "%~dp0"

echo 🐍 Starting FastAPI backend...
start cmd /k "python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"

echo 🌐 Starting React frontend...
npm run dev
