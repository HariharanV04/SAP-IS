@echo off
echo ===== IT Resonance iFlow Generator API Minimal Deployment =====

echo Checking required files...
if not exist app_minimal.py (
  echo Error: app_minimal.py not found!
  exit /b 1
)

if not exist requirements_minimal.txt (
  echo Error: requirements_minimal.txt not found!
  exit /b 1
)

echo All required files found.

echo Renaming requirements files for minimal deployment...
if exist requirements.txt (
  ren requirements.txt requirements.txt.bak
)
ren requirements_minimal.txt requirements.txt

echo Deploying to Cloud Foundry...
echo API Endpoint: https://api.cf.us10-001.hana.ondemand.com
echo Organization: IT Resonance Inc_itr-internal-2hco92jx

call cf push

if %ERRORLEVEL% neq 0 (
  echo Deployment failed!
  
  echo Restoring original requirements file...
  if exist requirements.txt (
    del requirements.txt
  )
  if exist requirements.txt.bak (
    ren requirements.txt.bak requirements.txt
  )
  
  exit /b 1
)

echo Restoring original requirements file...
if exist requirements.txt (
  del requirements.txt
)
if exist requirements.txt.bak (
  ren requirements.txt.bak requirements.txt
)

echo Deployment completed successfully!
echo API is now available at: https://mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com
