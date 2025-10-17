@echo off
echo ===== Rebuilding and Redeploying IT Resonance UI =====

echo Checking .env.production file...
type .env.production
echo.

echo Cleaning build directory...
if exist dist rmdir /s /q dist

echo Installing dependencies...
call npm install

echo Building production version...
call npm run build

echo Deploying to Cloud Foundry...
call cf push

if %ERRORLEVEL% neq 0 (
  echo Deployment failed!
  exit /b 1
)

echo Deployment completed successfully!
echo Frontend is now available at: https://it-resonance-ui.cfapps.us10-001.hana.ondemand.com
