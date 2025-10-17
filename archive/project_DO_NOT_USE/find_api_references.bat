@echo off
echo ===== Searching for API URL References =====

echo Searching for "mulesoft-docs-api" in all files...
findstr /s /i /m "mulesoft-docs-api" *.*
echo.

echo Searching for "mulesoft" in all files...
findstr /s /i /m "mulesoft" *.*
echo.

echo Searching for "cfapps.us10-001.hana.ondemand.com" in all files...
findstr /s /i /m "cfapps.us10-001.hana.ondemand.com" *.*
echo.

echo Searching for hardcoded URLs in JavaScript files...
findstr /s /i /m "http://" *.js
findstr /s /i /m "https://" *.js
echo.

echo Searching for axios API calls...
findstr /s /i /m "axios" *.js
echo.

echo Searching for fetch API calls...
findstr /s /i /m "fetch(" *.js
echo.

echo Searching for XMLHttpRequest...
findstr /s /i /m "XMLHttpRequest" *.js
echo.

echo Searching for environment variables...
findstr /s /i /m "process.env" *.js
findstr /s /i /m "import.meta.env" *.js
echo.

echo Searching for API configuration...
findstr /s /i /m "baseURL" *.js
echo.

echo Searching in build artifacts...
if exist dist (
  echo Searching in dist directory...
  findstr /s /i /m "mulesoft-docs-api" dist\*.*
  echo.
)

echo Search completed!
