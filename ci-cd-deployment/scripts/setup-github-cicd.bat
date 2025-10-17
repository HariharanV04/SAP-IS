@echo off
echo ========================================
echo GitHub CI/CD Setup Guide
echo ========================================

cd /d "%~dp0..\.."

echo 🔍 Checking GitHub CI/CD setup status...
echo.

echo Step 1: Checking if GitHub Actions workflow exists...
if exist ".github\workflows\deploy.yml" (
    echo ✅ GitHub Actions workflow file exists
) else (
    echo ❌ GitHub Actions workflow file missing
    echo    Expected location: .github\workflows\deploy.yml
    goto :setup_help
)

echo.
echo Step 2: Checking Cloud Foundry login...
cf target >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Logged into Cloud Foundry
    echo.
    echo 📋 Your CF Details for GitHub Secrets:
    echo ========================================
    cf target
    echo ========================================
) else (
    echo ❌ Not logged into Cloud Foundry
    echo    Please run: cf login -a https://api.cf.eu10-005.hana.ondemand.com
    goto :setup_help
)

echo.
echo Step 3: Checking Git repository status...
git remote -v | findstr "imigrate" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ IMigrate repository remote configured
) else (
    echo ❌ IMigrate repository remote not found
    echo    Expected: imigrate remote pointing to GitHub
    goto :setup_help
)

echo.
echo ========================================
echo ✅ SETUP STATUS: READY FOR GITHUB SECRETS
echo ========================================
echo.
echo 🔧 NEXT STEPS:
echo.
echo 1. Add GitHub Secrets:
echo    Go to: https://github.com/DheepLearningITR/IMigrate/settings/secrets/actions
echo    Click: "New repository secret"
echo.
echo    Add these 4 secrets:
for /f "tokens=2" %%i in ('cf target ^| findstr "Org:"') do set CF_ORG=%%i
for /f "tokens=2" %%i in ('cf target ^| findstr "Space:"') do set CF_SPACE=%%i
for /f "tokens=2" %%i in ('cf target ^| findstr "User:"') do set CF_USER=%%i

echo    - Name: CF_ORG          Value: %CF_ORG%
echo    - Name: CF_SPACE        Value: %CF_SPACE%
echo    - Name: CF_USERNAME     Value: %CF_USER%
echo    - Name: CF_PASSWORD     Value: [Your CF password]
echo.
echo 2. Test the CI/CD Pipeline:
echo    echo "# IMigrate Project" ^> README.md
echo    git add README.md
echo    git commit -m "test: trigger CI/CD pipeline"
echo    git push imigrate main
echo.
echo 3. Monitor Deployment:
echo    Go to: https://github.com/DheepLearningITR/IMigrate/actions
echo    Watch the "Deploy to Cloud Foundry" workflow
echo.
echo 4. Verify Deployment:
echo    Check: https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com
echo.
goto :end

:setup_help
echo.
echo ========================================
echo ❌ SETUP INCOMPLETE
echo ========================================
echo.
echo 🔧 Please complete these steps first:
echo.
if not exist ".github\workflows\deploy.yml" (
    echo - Ensure GitHub Actions workflow exists
    echo   Check if .github\workflows\deploy.yml was pushed to GitHub
)
echo.
cf target >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo - Login to Cloud Foundry:
    echo   cf login -a https://api.cf.eu10-005.hana.ondemand.com
)
echo.
git remote -v | findstr "imigrate" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo - Configure IMigrate repository remote:
    echo   git remote add imigrate https://github.com/DheepLearningITR/IMigrate.git
)
echo.
echo Then run this script again.
echo.

:end
pause
