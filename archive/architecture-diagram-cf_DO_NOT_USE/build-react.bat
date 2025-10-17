@echo off
echo Building React.js Architecture Diagram...

REM Get current timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"

echo [%timestamp%] Building React application...

REM Navigate to React app directory
cd ..\architecture-diagram

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

if %ERRORLEVEL% EQU 0 (
    echo [%timestamp%] React build successful!
    
    REM Copy build files to CF deployment directory
    echo [%timestamp%] Copying build files...
    cd ..\architecture-diagram-cf
    if not exist "dist" mkdir dist
    if not exist "dist\architecture-diagram" mkdir "dist\architecture-diagram"
    
    xcopy /E /I /Y "..\architecture-diagram\build\*" "dist\architecture-diagram\"
    
    echo [%timestamp%] React build files copied successfully.
) else (
    echo [%timestamp%] React build failed!
    exit /b 1
)

cd ..\architecture-diagram-cf
echo [%timestamp%] React build process completed.
