@echo off
echo ===== IT Resonance Frontend Configuration Update =====

REM Get the API route
echo Getting the API route...
for /f "tokens=2" %%a in ('cf app it-resonance-api ^| findstr routes') do set API_ROUTE=%%a

if "%API_ROUTE%"=="" (
  echo Error: Could not retrieve API route. Make sure the API is deployed.
  exit /b 1
)

echo API route found: %API_ROUTE%

REM Update the .env.production file
echo Updating .env.production file with new API URL...
(
echo # Production backend API URL for Cloud Foundry deployment
echo REACT_APP_API_URL=https://%API_ROUTE%/api
echo VITE_API_URL=https://%API_ROUTE%/api
echo # Disable continuous polling
echo VITE_DISABLE_AUTO_POLLING=true
) > project\.env.production

echo .env.production file updated successfully.

REM Ask if user wants to rebuild and redeploy the frontend
set /p rebuild=Do you want to rebuild and redeploy the frontend now? (y/n): 

if /i "%rebuild%"=="y" (
  echo Rebuilding and redeploying frontend...
  cd project
  
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
  
  REM Get the frontend route
  for /f "tokens=2" %%a in ('cf app it-resonance-ui ^| findstr routes') do set UI_ROUTE=%%a
  
  echo Deployment completed successfully!
  echo Frontend is now available at: https://%UI_ROUTE%
  echo Backend API is available at: https://%API_ROUTE%
  
  cd ..
) else (
  echo Skipping rebuild and redeploy.
  echo To rebuild and redeploy later, run:
  echo   cd project
  echo   npm run build
  echo   cf push
)

echo ===== Configuration update completed! =====
