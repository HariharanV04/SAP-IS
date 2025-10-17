@echo off
echo ===== IT Resonance API Deployment =====

echo Checking required files...
if not exist app.py (
  echo Error: app.py not found!
  exit /b 1
)

if not exist iflow_matcher.py (
  echo Error: iflow_matcher.py not found!
  exit /b 1
)

if not exist Procfile (
  echo Error: Procfile not found!
  exit /b 1
)

if not exist manifest.yml (
  echo Error: manifest.yml not found!
  exit /b 1
)

echo All required files found.

echo Deploying to Cloud Foundry...
call cf push

if %ERRORLEVEL% neq 0 (
  echo Deployment failed!
  exit /b 1
)

echo Deployment completed successfully!
echo API is now available at: https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com
