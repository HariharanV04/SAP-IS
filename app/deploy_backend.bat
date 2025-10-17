@echo off
echo ===== Deploying IT Resonance API with Enhanced iFlow Matcher =====

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
echo API is now available at: https://it-resonance-api.cfapps.us10-001.hana.ondemand.com

echo Testing API health endpoint...
curl -I https://it-resonance-api.cfapps.us10-001.hana.ondemand.com/api/health
