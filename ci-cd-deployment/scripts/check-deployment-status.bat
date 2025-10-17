@echo off
echo ========================================
echo Cloud Foundry Deployment Status Check
echo ========================================

echo 🔍 Checking Cloud Foundry deployment status...
echo.

echo Step 1: Checking CF login status...
cf target >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Logged into Cloud Foundry
    echo.
    echo 📋 Current CF Target:
    cf target
    echo.
) else (
    echo ❌ Not logged into Cloud Foundry
    echo Please run: cf login -a https://api.cf.eu10-005.hana.ondemand.com
    goto :end
)

echo Step 2: Checking deployed applications...
echo ========================================
cf apps
echo ========================================
echo.

echo Step 3: Testing API health endpoints...
echo.

echo 🔍 Testing Main API...
curl -s -f https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Main API is responding
) else (
    echo ❌ Main API not responding
)

echo 🔍 Testing MuleToIS API...
curl -s -f https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ MuleToIS API is responding
) else (
    echo ❌ MuleToIS API not responding
)

echo 🔍 Testing BoomiToIS API...
curl -s -f https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ BoomiToIS API is responding
) else (
    echo ❌ BoomiToIS API not responding
)

echo 🔍 Testing Frontend...
curl -s -f https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Frontend is responding
) else (
    echo ❌ Frontend not responding
)

echo.
echo Step 4: Checking recent app logs...
echo.
echo 📋 Recent Main API logs:
cf logs it-resonance-main-api --recent | tail -10

echo.
echo ========================================
echo 🌐 Application URLs:
echo ========================================
echo Frontend:     https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com
echo Main API:     https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com
echo MuleToIS API: https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com
echo BoomiToIS API: https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com
echo.
echo GitHub Actions: https://github.com/DheepLearningITR/IMigrate/actions
echo.

:end
pause
