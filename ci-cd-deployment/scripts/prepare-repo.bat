@echo off
echo ========================================
echo Prepare Repository for GitHub Push
echo ========================================

cd /d "%~dp0..\.."

echo 🧹 Cleaning up repository...

echo 1. Removing temporary files and build artifacts...
if exist "IFA-Project\frontend\dist" (
    rmdir /s /q "IFA-Project\frontend\dist"
    echo   ✅ Removed frontend dist folder
)

if exist "IFA-Project\frontend\node_modules" (
    rmdir /s /q "IFA-Project\frontend\node_modules"
    echo   ✅ Removed frontend node_modules
)

echo 2. Removing .env files (will be auto-generated)...
for %%f in (app\.env MuleToIS-API\.env BoomiToIS-API\.env IFA-Project\frontend\.env) do (
    if exist "%%f" (
        del "%%f"
        echo   ✅ Removed %%f
    )
)

echo 3. Removing Python cache files...
for /r %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
    )
)

for /r %%f in (*.pyc) do (
    if exist "%%f" (
        del "%%f" 2>nul
    )
)

echo 4. Removing log files and temporary data...
if exist "app\logs" (
    rmdir /s /q "app\logs"
    echo   ✅ Removed app logs
)

if exist "MuleToIS-API\logs" (
    rmdir /s /q "MuleToIS-API\logs"
    echo   ✅ Removed MuleToIS-API logs
)

if exist "BoomiToIS-API\logs" (
    rmdir /s /q "BoomiToIS-API\logs"
    echo   ✅ Removed BoomiToIS-API logs
)

if exist "results" (
    rmdir /s /q "results"
    echo   ✅ Removed results folder
)

echo 5. Creating/updating .gitignore...
echo # Auto-generated .gitignore for IFA Project > .gitignore
echo. >> .gitignore
echo # Environment files >> .gitignore
echo .env >> .gitignore
echo *.env >> .gitignore
echo .env.local >> .gitignore
echo .env.development >> .gitignore
echo .env.production >> .gitignore
echo. >> .gitignore
echo # Python >> .gitignore
echo __pycache__/ >> .gitignore
echo *.py[cod] >> .gitignore
echo *.so >> .gitignore
echo *.egg-info/ >> .gitignore
echo dist/ >> .gitignore
echo build/ >> .gitignore
echo. >> .gitignore
echo # Node.js >> .gitignore
echo node_modules/ >> .gitignore
echo npm-debug.log* >> .gitignore
echo yarn-debug.log* >> .gitignore
echo yarn-error.log* >> .gitignore
echo. >> .gitignore
echo # Frontend build >> .gitignore
echo IFA-Project/frontend/dist/ >> .gitignore
echo IFA-Project/frontend/.vite/ >> .gitignore
echo. >> .gitignore
echo # Logs >> .gitignore
echo logs/ >> .gitignore
echo *.log >> .gitignore
echo. >> .gitignore
echo # Runtime data >> .gitignore
echo results/ >> .gitignore
echo temp/ >> .gitignore
echo tmp/ >> .gitignore
echo. >> .gitignore
echo # IDE >> .gitignore
echo .vscode/ >> .gitignore
echo .idea/ >> .gitignore
echo *.swp >> .gitignore
echo *.swo >> .gitignore
echo. >> .gitignore
echo # OS >> .gitignore
echo .DS_Store >> .gitignore
echo Thumbs.db >> .gitignore
echo desktop.ini >> .gitignore

echo   ✅ Created .gitignore file

echo 6. Checking Git status...
git status

echo.
echo ========================================
echo ✅ Repository prepared for GitHub push!
echo ========================================
echo.
echo 📋 Next steps:
echo 1. Create new GitHub repository (if not done)
echo 2. Run: deployment\scripts\push-to-github.bat [repo-url]
echo.
echo 📁 Files ready to commit:
git ls-files --others --exclude-standard
echo.
pause
