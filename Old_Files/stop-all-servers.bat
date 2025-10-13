@echo off
echo ========================================
echo IS-Migration Platform - Stop All Servers
echo ========================================
echo.

:: Set colors for better visibility
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

echo %BLUE%Stopping all IS-Migration servers...%RESET%
echo.

:: Kill processes by port
echo %YELLOW%Stopping servers by port...%RESET%

:: Stop Main API (Port 5000)
echo %BLUE%Stopping Main API (Port 5000)...%RESET%
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Stop MuleToIS API (Port 5001)
echo %BLUE%Stopping MuleToIS API (Port 5001)...%RESET%
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Stop Gemma-3 API (Port 5002)
echo %BLUE%Stopping Gemma-3 API (Port 5002)...%RESET%
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5002') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Stop BoomiToIS API (Port 5003)
echo %BLUE%Stopping BoomiToIS API (Port 5003)...%RESET%
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5003') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Stop Frontend (Port 5173)
echo %BLUE%Stopping Frontend (Port 5173)...%RESET%
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: Also kill any remaining Python and Node processes related to our apps
echo %YELLOW%Cleaning up remaining processes...%RESET%
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq Main API*" >nul 2>&1
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq BoomiToIS*" >nul 2>&1
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq MuleToIS*" >nul 2>&1
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq Gemma*" >nul 2>&1
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq Frontend*" >nul 2>&1

echo.
echo %GREEN%========================================%RESET%
echo %GREEN%All servers have been stopped!%RESET%
echo %GREEN%========================================%RESET%
echo.

:: Clean up log files if they exist
if exist "logs" (
    echo %YELLOW%Cleaning up log files...%RESET%
    del /q logs\*.log >nul 2>&1
    echo %GREEN%Log files cleaned up.%RESET%
)

echo %GREEN%All IS-Migration servers have been stopped successfully.%RESET%
echo.
pause
