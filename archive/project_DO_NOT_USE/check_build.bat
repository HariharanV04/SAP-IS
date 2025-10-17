@echo off
echo ===== Checking Build Files for API References =====

if not exist dist (
  echo Build directory (dist) not found. Please run 'npm run build' first.
  exit /b 1
)

echo Searching for "mulesoft-docs-api" in build files...
findstr /s /i /m "mulesoft-docs-api" dist\*.*
echo.

echo Searching for "mulesoft" in build files...
findstr /s /i /m "mulesoft" dist\*.*
echo.

echo Searching for "cfapps.us10-001.hana.ondemand.com" in build files...
findstr /s /i /m "cfapps.us10-001.hana.ondemand.com" dist\*.*
echo.

echo Checking environment variables in build files...
findstr /s /i /m "VITE_API_URL" dist\*.*
findstr /s /i /m "REACT_APP_API_URL" dist\*.*
echo.

echo Build check completed!
