@echo off
echo =======================================================
echo     AI-Enhanced Honeypot ^& Deception System Startup
echo =======================================================

echo.
echo [*] Starting Python Backend API ^& Honeypot Sensors...
start "AegisNet Backend" cmd /k "cd backend && .\venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [*] Starting React Visualization Dashboard...
start "AegisNet Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All services are booting up! 
echo Dashboard available at: http://localhost:5173/
echo Honeypot active on ports 8080 (HTTP) and 2222 (SSH).
echo.
pause
