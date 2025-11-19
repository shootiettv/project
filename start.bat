@echo off
setlocal enabledelayedexpansion

echo ===============================
echo UTEP Professor Ranking Starter (Windows)
echo ===============================

echo Killing old uvicorn and Vite processes...

:: Kill uvicorn and node (vite) processes
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo Checking for processes on ports 8000 and 5173...

:: Kill processes using ports 8000 and 5173
for %%P in (8000 5173) do (
    for /f "tokens=5" %%A in ('netstat -ano ^| findstr :%%P') do (
        echo Freeing port %%P (PID %%A)...
        taskkill /F /PID %%A >nul 2>&1
    )
)

:: Move to script directory
cd /d "%~dp0"

echo Starting FastAPI backend...
start cmd /k "python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting React frontend...
npm run dev

endlocal

