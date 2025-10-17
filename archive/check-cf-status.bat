@echo off
echo ===== IT Resonance Cloud Foundry Status Check =====

echo Checking if logged in to Cloud Foundry...
cf target
if %ERRORLEVEL% neq 0 (
    echo You need to log in to Cloud Foundry first.
    echo Run: cf login -a https://api.cf.us10-001.hana.ondemand.com
    exit /b 1
)

echo.
echo Checking status of main API...
cf app it-resonance-api-wacky-panther-za

echo.
echo Checking status of iFlow API...
cf app mulesoft-iflow-api

echo.
echo Checking status of frontend...
cf app ifa-frontend

echo.
echo Checking routes...
cf routes | findstr "it-resonance-api-wacky-panther-za mulesoft-iflow-api ifa-frontend"

echo.
echo All status checks completed.
echo.
echo Main API: https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com
echo iFlow API: https://mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com
echo Frontend: https://ifa-frontend.cfapps.us10-001.hana.ondemand.com/projects/1/flow
