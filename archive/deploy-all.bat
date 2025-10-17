@echo off
echo ===== IT Resonance Integration Flow Analyzer - Full Deployment =====

rem Login to Cloud Foundry
echo Logging in to Cloud Foundry...
call cf login -a https://api.cf.us10-001.hana.ondemand.com

if %ERRORLEVEL% neq 0 (
  echo Cloud Foundry login failed! Aborting deployment.
  exit /b 1
)

rem Deploy Backend API
echo Deploying Backend API...
cd app

echo Preparing backend for deployment...
python prepare_deployment.py

if %ERRORLEVEL% neq 0 (
  echo Deployment preparation failed! Aborting.
  exit /b 1
)

call cf push

if %ERRORLEVEL% neq 0 (
  echo Backend API deployment failed! Aborting.
  exit /b 1
)

rem Deploy Frontend UI
echo Building and deploying Frontend UI...
cd ..\project
call npm install
call npm run build
call cf push

if %ERRORLEVEL% neq 0 (
  echo Frontend UI deployment failed!
  exit /b 1
)

echo ===== Full deployment completed successfully! =====
echo Your application components are now available at:
echo Frontend: https://it-resonance-ui.cfapps.us10-001.hana.ondemand.com
echo Backend API: https://it-resonance-api.cfapps.us10-001.hana.ondemand.com
