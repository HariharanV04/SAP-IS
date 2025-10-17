@echo off
echo ===== IT Resonance Integration Flow Analyzer - API Redeployment =====

REM Login to Cloud Foundry
echo Logging in to Cloud Foundry...
cf login -a https://api.cf.us10-001.hana.ondemand.com

if %ERRORLEVEL% neq 0 (
  echo Cloud Foundry login failed! Aborting deployment.
  exit /b 1
)

REM Clean up unused routes to avoid quota issues
echo Cleaning up unused routes...
cf delete-orphaned-routes -f

REM Navigate to the app directory
cd app

REM Prepare for deployment
echo Preparing backend for deployment...
python prepare_deployment.py

if %ERRORLEVEL% neq 0 (
  echo Deployment preparation failed! Aborting.
  exit /b 1
)

REM Deploy the API
echo Deploying Backend API with updated CORS configuration...
cf push

if %ERRORLEVEL% neq 0 (
  echo Backend API deployment failed!
  exit /b 1
)

REM Get the API route
echo Getting the API route...
for /f "tokens=2" %%a in ('cf app it-resonance-api ^| findstr routes') do set API_ROUTE=%%a

echo ===== API Redeployment completed successfully! =====
echo Your API is now available at: https://%API_ROUTE%
echo CORS should now be properly configured to allow requests from your frontend application.

cd ..
