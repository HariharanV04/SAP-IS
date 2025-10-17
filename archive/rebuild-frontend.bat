@echo off
echo ===== Rebuilding and Redeploying Frontend with Clean Build =====

cd project

echo Checking .env.production file...
type .env.production
echo.

echo Cleaning node_modules and build directories...
if exist node_modules rmdir /s /q node_modules
if exist dist rmdir /s /q dist
if exist .vite rmdir /s /q .vite
if exist .env.production.local del .env.production.local

echo Installing dependencies...
call npm install

echo Building production version with environment variables...
set "VITE_API_URL=https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com/api"
set "REACT_APP_API_URL=https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com/api"
call npm run build

echo Checking built files for API references...
findstr /s /i /m "it-resonance-api.cfapps" dist\*.*
findstr /s /i /m "it-resonance-api-wacky-panther-za" dist\*.*
echo.

echo Deploying to Cloud Foundry...
call cf push

if %ERRORLEVEL% neq 0 (
  echo Deployment failed!
  exit /b 1
)

echo Deployment completed successfully!
echo Frontend is now available at: https://it-resonance-ui-interested-wildebeest-nc.cfapps.us10-001.hana.ondemand.com/
echo Backend API is available at: https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com/

cd ..

echo ===== Rebuild and redeploy completed! =====
