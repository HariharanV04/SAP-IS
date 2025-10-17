@echo off
echo ========================================
echo GitHub Secrets Setup Helper
echo ========================================

echo 🔍 Getting your Cloud Foundry details for GitHub Secrets...
echo.

cf target >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Not logged into Cloud Foundry
    echo Please run: cf login -a https://api.cf.eu10-005.hana.ondemand.com
    pause
    exit /b 1
)

echo ✅ Getting CF details...
echo.

echo ========================================
echo 📋 COPY THESE VALUES TO GITHUB SECRETS
echo ========================================
echo.
echo Go to: https://github.com/DheepLearningITR/IMigrate/settings/secrets/actions
echo Click: "New repository secret"
echo.

for /f "tokens=2" %%i in ('cf target ^| findstr "Org:"') do (
    echo Secret Name: CF_ORG
    echo Secret Value: %%i
    echo.
)

for /f "tokens=2" %%i in ('cf target ^| findstr "Space:"') do (
    echo Secret Name: CF_SPACE
    echo Secret Value: %%i
    echo.
)

for /f "tokens=2" %%i in ('cf target ^| findstr "User:"') do (
    echo Secret Name: CF_USERNAME
    echo Secret Value: %%i
    echo.
)

echo Secret Name: CF_PASSWORD
echo Secret Value: [Your Cloud Foundry login password]
echo.

echo ========================================
echo 🔧 AFTER ADDING ALL 4 SECRETS:
echo ========================================
echo.
echo 1. Test the deployment:
echo    echo "# Test deployment" ^> README.md
echo    git add README.md
echo    git commit -m "test: trigger deployment with secrets"
echo    git push imigrate main
echo.
echo 2. Monitor the deployment:
echo    https://github.com/DheepLearningITR/IMigrate/actions
echo.
echo 3. Check deployed apps:
echo    cf apps
echo.

pause
