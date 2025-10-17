@echo off
echo Building and deploying Architecture Diagram to Cloud Foundry...

REM Get current timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"

echo [%timestamp%] Starting deployment process...

REM Create dist directory if it doesn't exist
if not exist "dist" mkdir dist

REM Copy all architecture diagram files to dist
echo [%timestamp%] Copying architecture diagram files...
xcopy /E /I /Y "..\architecture-showcase.html" "dist\"
xcopy /E /I /Y "..\architecture-diagram" "dist\architecture-diagram\"
xcopy /E /I /Y "..\d3-diagram" "dist\d3-diagram\"
xcopy /E /I /Y "..\static-svg-diagram" "dist\static-svg-diagram\"

REM Create index.html that redirects to architecture-showcase.html
echo ^<!DOCTYPE html^> > "dist\index.html"
echo ^<html^> >> "dist\index.html"
echo ^<head^> >> "dist\index.html"
echo ^<title^>Architecture Diagram Showcase^</title^> >> "dist\index.html"
echo ^<meta http-equiv="refresh" content="0; url=architecture-showcase.html"^> >> "dist\index.html"
echo ^</head^> >> "dist\index.html"
echo ^<body^> >> "dist\index.html"
echo ^<p^>Redirecting to ^<a href="architecture-showcase.html"^>Architecture Diagram Showcase^</a^>...^</p^> >> "dist\index.html"
echo ^</body^> >> "dist\index.html"
echo ^</html^> >> "dist\index.html"

echo [%timestamp%] Files copied successfully.

REM Deploy to Cloud Foundry
echo [%timestamp%] Deploying to Cloud Foundry...
cf push

if %ERRORLEVEL% EQU 0 (
    echo [%timestamp%] Deployment successful!
    echo.
    echo Architecture Diagram is now available at:
    echo https://architecture-diagram.cfapps.us10-001.hana.ondemand.com
    echo.
    echo Available diagrams:
    echo - React.js Interactive: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com/architecture-diagram/
    echo - D3.js Advanced: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com/d3-diagram/
    echo - Static SVG: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com/static-svg-diagram/architecture-diagram.svg
) else (
    echo [%timestamp%] Deployment failed!
    exit /b 1
)

pause
