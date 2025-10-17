@echo off
echo ===== IT Resonance Integration Flow Analyzer Deployment =====
echo Building production version...

:: Build the production version
call npm run build

if %ERRORLEVEL% neq 0 (
  echo Build failed! Aborting deployment.
  exit /b 1
)

echo Build successful!
echo Deploying to SAP BTP Cloud Foundry...

:: Login to Cloud Foundry (this will prompt for credentials if not already logged in)
echo Please log in to Cloud Foundry if prompted:
call cf login -a https://api.cf.us10-001.hana.ondemand.com

if %ERRORLEVEL% neq 0 (
  echo Cloud Foundry login failed! Aborting deployment.
  exit /b 1
)

:: Deploy the application
call cf push

if %ERRORLEVEL% neq 0 (
  echo Deployment failed!
  exit /b 1
)

echo ===== Deployment completed successfully! =====
echo Your application is now available at: https://it-resonance-integration-analyzer.cfapps.us10-001.hana.ondemand.com
