@echo off
echo ========================================
echo IFA Project - Local Development Setup
echo ========================================

cd /d "%~dp0..\.."

echo 🏠 Setting up local development environment...
python deployment/deploy.py local

if %ERRORLEVEL% neq 0 (
    echo ❌ Local setup failed!
    pause
    exit /b 1
)

echo.
echo ✅ Local development environment ready!
echo.
echo 🚀 To start development servers:
echo   Main API:     cd app ^&^& python app.py
echo   MuleToIS API: cd MuleToIS-API ^&^& python app.py  
echo   BoomiToIS API: cd BoomiToIS-API ^&^& python app.py
echo   Frontend:     cd IFA-Project/frontend ^&^& npm run dev
echo.
echo 🌐 Local URLs:
echo   Frontend:     http://localhost:3000
echo   Main API:     http://localhost:5000
echo   MuleToIS API: http://localhost:5001
echo   BoomiToIS API: http://localhost:5002
echo.
pause
