@echo off
echo ========================================
echo IFA Project - Production Deployment
echo ========================================

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
echo 🚀 Starting complete production deployment...
echo This will deploy all applications to Cloud Foundry
echo.
set /p confirm="Continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo 🌐 Deploying all applications to Cloud Foundry...
python ci-cd-deployment/deploy.py deploy-all

if %ERRORLEVEL% neq 0 (
    echo ❌ Production deployment failed!
    pause
    exit /b 1
)

echo.
echo ✅ Production deployment complete!
echo.
echo 🌐 Application URLs:
echo   Frontend:     https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com
echo   Main API:     https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com
echo   MuleToIS API: https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com
echo   BoomiToIS API: https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com
echo.
pause
