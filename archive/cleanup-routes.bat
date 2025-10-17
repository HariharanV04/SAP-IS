@echo off
echo ===== IT Resonance Integration Flow Analyzer - Route Cleanup =====

REM Login to Cloud Foundry
echo Logging in to Cloud Foundry...
cf login -a https://api.cf.us10-001.hana.ondemand.com

if %ERRORLEVEL% neq 0 (
  echo Cloud Foundry login failed! Aborting cleanup.
  exit /b 1
)

REM List all routes
echo Current routes in your space:
cf routes

REM Delete orphaned routes (routes not mapped to any app)
echo Cleaning up orphaned routes...
cf delete-orphaned-routes -f

REM List routes again to confirm cleanup
echo Routes after cleanup:
cf routes

REM Check route quota
echo Checking route quota...
cf space dev | findstr routes

echo ===== Route cleanup completed! =====
echo If you still have route quota issues, you may need to manually delete some routes.
echo To delete a specific route, use: cf delete-route DOMAIN --hostname HOSTNAME
echo Example: cf delete-route cfapps.us10-001.hana.ondemand.com --hostname it-resonance-ui
