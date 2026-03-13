@echo off
echo Stopping any existing processes on ports 8000 and 3000...

REM Kill any processes using port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /f /pid %%a 2>nul
)

REM Kill any processes using port 3000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    taskkill /f /pid %%a 2>nul
)

echo Waiting for ports to be released...
timeout /t 3 /nobreak >nul

echo Starting backend server...
cd /d %~dp0backend
start cmd /k "echo Starting backend server on port 8000... && python run_server.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting frontend server...
cd /d %~dp0frontend
start cmd /k "echo Starting frontend server on port 3000... && npm run dev"

echo.
echo Services are starting...
echo - Backend: http://127.0.0.1:8000
echo - Frontend: http://localhost:3000
echo.
echo Please wait about 10-15 seconds for both services to fully start before accessing them.
echo.
pause