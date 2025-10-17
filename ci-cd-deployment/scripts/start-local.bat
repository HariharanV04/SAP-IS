@echo off
echo ========================================
echo IFA Project - Start Local Development
echo ========================================

cd /d "%~dp0..\.."

echo 🔍 Checking if .env files exist...
if not exist "app\.env" (
    echo ⚠️ .env files not found. Setting up local environment...
    call deployment\scripts\deploy-local.bat
)

echo.
echo 🚀 Starting all development servers...
echo.

echo Starting Main API (Port 5000)...
start "Main API" cmd /k "cd app && python app.py"
timeout /t 3 /nobreak >nul

echo Starting MuleToIS API (Port 5001)...
start "MuleToIS API" cmd /k "cd MuleToIS-API && python app.py"
timeout /t 3 /nobreak >nul

echo Starting BoomiToIS API (Port 5002)...
start "BoomiToIS API" cmd /k "cd BoomiToIS-API && python app.py"
timeout /t 3 /nobreak >nul

echo Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd IFA-Project\frontend && npm run dev"

echo.
echo ✅ All servers starting...
echo.
echo 🌐 Local URLs:
echo   Frontend:     http://localhost:3000
echo   Main API:     http://localhost:5000
echo   MuleToIS API: http://localhost:5001
echo   BoomiToIS API: http://localhost:5002
echo.
echo 📝 Check the individual terminal windows for server status
echo 🛑 Close terminal windows to stop servers
echo.
pause
