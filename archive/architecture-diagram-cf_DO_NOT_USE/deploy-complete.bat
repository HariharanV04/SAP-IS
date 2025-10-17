@echo off
echo ========================================
echo  React Architecture Diagram CF Deployment
echo ========================================

REM Get current timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"

echo [%timestamp%] Starting React app deployment process...

REM Navigate to React app directory
cd ..\architecture-diagram

REM Clean previous build
echo [%timestamp%] Cleaning previous build...
if exist "build" rmdir /s /q "build"

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo [%timestamp%] Installing dependencies...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [%timestamp%] Failed to install dependencies!
        exit /b 1
    )
)

REM Build the React app
echo [%timestamp%] Building React app for production...
npm run build

if %ERRORLEVEL% NEQ 0 (
    echo [%timestamp%] React build failed!
    exit /b 1
)

echo [%timestamp%] React build completed successfully.

REM Navigate back to CF deployment directory
cd ..\architecture-diagram-cf

REM Copy build files to CF deployment directory
echo [%timestamp%] Copying build files...
if exist "build" rmdir /s /q "build"
xcopy /E /I /Y "..\architecture-diagram\build" "build\"

echo [%timestamp%] Build files copied successfully.

REM Deploy to Cloud Foundry
echo [%timestamp%] Deploying to Cloud Foundry...
cf push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  DEPLOYMENT SUCCESSFUL!
    echo ========================================
    echo [%timestamp%] React Architecture Diagram deployed successfully!
    echo.
    echo Application URL: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com
    echo.
    echo Features:
    echo - Interactive React.js architecture diagram
    echo - Drag and drop components
    echo - Zoom, pan, and minimap controls
    echo - Component details on click
    echo - Responsive design
    echo.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  DEPLOYMENT FAILED!
    echo ========================================
    echo [%timestamp%] Deployment failed! Check the logs above.
    exit /b 1
)

pause
