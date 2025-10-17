@echo off
echo ====================================================================
echo   MuleSoft Documentation Generator - Production Build Server
echo ====================================================================
echo.
echo This script will serve your production build with direct connection 
echo to the Cloud Foundry backend at:
echo https://mulesoft-docs-api.cfapps.us10-001.hana.ondemand.com/api
echo.
echo First, let's make sure your build is up to date with the latest changes:
echo.
echo Building production version...
call npm run build
echo.
echo Build complete! Starting server on http://localhost:4500
echo.
echo IMPORTANT: If you experience CORS issues, try using Chrome with web security disabled:
echo chrome.exe --disable-web-security --user-data-dir="%TEMP%\chrome-dev"
echo.
npx serve -s dist -l 4500 