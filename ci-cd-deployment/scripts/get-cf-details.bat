@echo off
echo ========================================
echo Get Cloud Foundry Details for GitHub
echo ========================================

echo 🔍 Getting your Cloud Foundry details...
echo.

echo 1. Checking if you're logged into Cloud Foundry...
cf target >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Not logged into Cloud Foundry!
    echo.
    echo Please login first:
    echo   cf login -a https://api.cf.eu10-005.hana.ondemand.com
    echo.
    pause
    exit /b 1
)

echo ✅ Cloud Foundry login verified!
echo.

echo 2. Your Cloud Foundry Details:
echo ========================================
cf target

echo.
echo 3. GitHub Secrets to Add:
echo ========================================

echo Getting organization...
for /f "tokens=2" %%i in ('cf target ^| findstr "Org:"') do set CF_ORG=%%i

echo Getting space...
for /f "tokens=2" %%i in ('cf target ^| findstr "Space:"') do set CF_SPACE=%%i

echo Getting user...
for /f "tokens=2" %%i in ('cf target ^| findstr "User:"') do set CF_USER=%%i

echo.
echo 📋 Copy these values to GitHub Secrets:
echo.
echo Secret Name: CF_ORG
echo Secret Value: %CF_ORG%
echo.
echo Secret Name: CF_SPACE  
echo Secret Value: %CF_SPACE%
echo.
echo Secret Name: CF_USERNAME
echo Secret Value: %CF_USER%
echo.
echo Secret Name: CF_PASSWORD
echo Secret Value: [Your Cloud Foundry password]
echo.

echo 🔗 GitHub Repository Settings URL:
echo https://github.com/ITR-APPS/MULE2IS/settings/secrets/actions
echo.

echo 📝 Steps to add secrets:
echo 1. Go to the URL above
echo 2. Click "New repository secret"
echo 3. Add each secret with the name and value shown above
echo 4. For CF_PASSWORD, use your Cloud Foundry login password
echo.

echo ⚠️ IMPORTANT: Keep these values secure!
echo Don't share them or commit them to code.
echo.

pause
