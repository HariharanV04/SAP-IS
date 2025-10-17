@echo off
echo ========================================
echo IFA Project - Single App Deployment
echo ========================================

if "%1"=="" (
    echo Usage: deploy-single.bat [app_name]
    echo.
    echo Available apps:
    echo   main_api    - Main API
    echo   mule_api    - MuleToIS API
    echo   boomi_api   - BoomiToIS API
    echo   frontend    - Frontend Application
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0..\.."

echo 🔐 Checking Cloud Foundry login...
cf target
if %ERRORLEVEL% neq 0 (
    echo ❌ Not logged into Cloud Foundry!
    echo Please run: cf login
    pause
    exit /b 1
)

echo.
echo 🚀 Deploying %1 to Cloud Foundry...
python deployment/deploy.py deploy --app %1

if %ERRORLEVEL% neq 0 (
    echo ❌ Deployment of %1 failed!
    pause
    exit /b 1
)

echo.
echo ✅ %1 deployed successfully!
echo.
echo 📊 Checking deployment status...
python deployment/deploy.py status
echo.
pause
