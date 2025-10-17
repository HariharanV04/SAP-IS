@echo off
echo ===== Redeploying Backend API with Updated CORS Configuration =====

cd app

echo Checking CORS helper implementation...
type utils\cors_helper.py | findstr "Access-Control-Allow-Origin"
echo.

echo Deploying to Cloud Foundry...
call cf push

if %ERRORLEVEL% neq 0 (
  echo Deployment failed!
  exit /b 1
)

echo Getting the API route...
for /f "tokens=2" %%a in ('cf app it-resonance-api ^| findstr routes') do set API_ROUTE=%%a

echo Deployment completed successfully!
echo Backend API is now available at: https://%API_ROUTE%

echo Testing CORS headers...
echo You can test the CORS headers with the following curl command:
echo curl -v -X OPTIONS https://%API_ROUTE%/api/health -H "Origin: https://it-resonance-ui-interested-wildebeest-nc.cfapps.us10-001.hana.ondemand.com" -H "Access-Control-Request-Method: GET"

cd ..

echo ===== Backend API redeployment completed! =====
