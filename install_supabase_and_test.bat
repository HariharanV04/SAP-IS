@echo off
REM Install Supabase package and run test script
REM Run this in Windows Command Prompt (not WSL)

echo ================================================================================
echo Installing Supabase Package and Running Test
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing supabase package...
pip install supabase
if errorlevel 1 (
    echo ERROR: Failed to install supabase package
    pause
    exit /b 1
)

echo.
echo [2/3] Package installed successfully!
echo.

echo [3/3] Running Supabase job tracker test...
echo.
python test_supabase_job_tracker.py
if errorlevel 1 (
    echo.
    echo ERROR: Test script failed
    echo Check the error message above
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCCESS! All tests passed!
echo ================================================================================
echo.
echo Next steps:
echo 1. Check your Supabase dashboard to verify data was saved
echo 2. Go to Table Editor and check the iflow_jobs table
echo 3. You should see test job entries
echo.
pause
