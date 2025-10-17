@echo off
echo ===== IT Resonance Cloud Foundry CORS Update =====

echo Checking if logged in to Cloud Foundry...
cf target
if %ERRORLEVEL% neq 0 (
    echo You need to log in to Cloud Foundry first.
    echo Run: cf login -a https://api.cf.us10-001.hana.ondemand.com
    exit /b 1
)

echo.
echo Updating CORS configuration for main API...
call cf set-env it-resonance-api-wacky-panther-za CORS_ALLOW_CREDENTIALS true
call cf set-env it-resonance-api-wacky-panther-za CORS_ORIGIN https://ifa-frontend.cfapps.us10-001.hana.ondemand.com

echo.
echo Updating CORS configuration for iFlow API...
call cf set-env mulesoft-iflow-api CORS_ALLOW_CREDENTIALS true
call cf set-env mulesoft-iflow-api CORS_ORIGIN https://ifa-frontend.cfapps.us10-001.hana.ondemand.com

echo.
echo Restarting applications to apply changes...
call cf restart it-resonance-api-wacky-panther-za
call cf restart mulesoft-iflow-api

echo.
echo CORS configuration updated successfully!
echo.
echo Main API: https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com
echo iFlow API: https://mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com
echo Frontend: https://ifa-frontend.cfapps.us10-001.hana.ondemand.com
