@echo off
echo UTEP Professor Ranking Starter
echo Killing old uvicorn and vite processes...

taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo checking for processes on port 5173
for /f "tokens=5" %%B in ('netstat -ano ^| findstr ":5173"') do (
    echo Freeing port 5173 (PID %%B)
    taskkill /F /PID %%B >nul 2>&1
)

cd /d "%~dp0"

echo Starting FastAPI backend...
start cmd /k "python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting react frontend...
npm run dev