@echo off
echo ===== Opening IT Resonance MuleSoft Documentation Generator =====

if "%1"=="" (
    echo Usage: open-app.bat [development^|production]
    echo.
    echo Examples:
    echo   open-app.bat development   - Open development environment
    echo   open-app.bat production    - Open production environment
    exit /b 1
)

set ENV=%1

if /i "%ENV%"=="development" (
    echo Opening DEVELOPMENT environment in browser...
    start http://localhost:5173/projects/1/flow
) else if /i "%ENV%"=="production" (
    echo Opening PRODUCTION environment in browser...
    start https://ifa-frontend.cfapps.us10-001.hana.ondemand.com/projects/1/flow
) else (
    echo Invalid environment: %ENV%
    echo Valid options are: development, production
    exit /b 1
)

echo.
echo Browser opened to %ENV% environment.
echo.
echo NOTE: Make sure all services are running before opening the application:
echo   - Main API
echo   - iFlow API
echo   - Frontend
