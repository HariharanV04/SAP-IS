@echo off
echo ========================================
echo IFA Project - Environment Management
echo ========================================

if "%1"=="" (
    echo Usage: manage-env.bat [command]
    echo.
    echo Available commands:
    echo   setup-local     - Setup local development environment
    echo   deploy-all      - Deploy all apps to production
    echo   deploy-single   - Deploy single app [app_name]
    echo   status          - Show deployment status
    echo   restart         - Restart all CF apps
    echo   clean           - Clean deployment artifacts
    echo   start-local     - Start all local development servers
    echo.
    echo Examples:
    echo   manage-env.bat setup-local
    echo   manage-env.bat deploy-all
    echo   manage-env.bat deploy-single frontend
    echo   manage-env.bat status
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0..\.."

if "%1"=="setup-local" (
    echo 🏠 Setting up local development environment...
    python deployment/deploy.py local
    goto :end
)

if "%1"=="deploy-all" (
    echo 🚀 Deploying all applications to production...
    python deployment/deploy.py deploy-all
    goto :end
)

if "%1"=="deploy-single" (
    if "%2"=="" (
        echo ❌ App name required for deploy-single
        echo Usage: manage-env.bat deploy-single [app_name]
        pause
        exit /b 1
    )
    echo 🚀 Deploying %2 to production...
    python deployment/deploy.py deploy --app %2
    goto :end
)

if "%1"=="status" (
    echo 📊 Checking deployment status...
    python deployment/deploy.py status
    goto :end
)

if "%1"=="restart" (
    echo 🔄 Restarting all Cloud Foundry applications...
    python deployment/deploy.py restart
    goto :end
)

if "%1"=="clean" (
    echo 🧹 Cleaning deployment artifacts...
    python deployment/deploy.py clean
    goto :end
)

if "%1"=="start-local" (
    echo 🚀 Starting local development servers...
    call deployment\scripts\start-local.bat
    goto :end
)

echo ❌ Unknown command: %1
echo Run 'manage-env.bat' without parameters to see available commands.

:end
if %ERRORLEVEL% neq 0 (
    echo ❌ Command failed!
    pause
    exit /b 1
)

echo ✅ Command completed successfully!
pause
