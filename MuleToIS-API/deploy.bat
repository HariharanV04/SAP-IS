@echo off
echo ===== IT Resonance iFlow Generator API Deployment =====

echo Checking required files...
if not exist app.py (
  echo Error: app.py not found!
  exit /b 1
)

if not exist iflow_generator_api.py (
  echo Error: iflow_generator_api.py not found!
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

if not exist requirements.txt (
  echo Error: requirements.txt not found!
  exit /b 1
)

if not exist .env (
  echo Warning: .env file not found! Make sure your environment variables are set.
)

echo All required files found.

echo Loading environment variables from .env file...
for /F "tokens=*" %%A in (.env) do (
  set %%A
)
echo Environment variables loaded.

echo Deploying to Cloud Foundry...
echo API Endpoint: https://api.cf.us10-001.hana.ondemand.com
echo Organization: IT Resonance Inc_itr-internal-2hco92jx

call cf push

if %ERRORLEVEL% neq 0 (
  echo Deployment failed!
  exit /b 1
)

echo Deployment completed successfully!
echo API is now available at: https://mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com
