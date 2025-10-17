@echo off
echo ========================================
echo CI/CD Pipeline Setup Verification
echo ========================================

echo 🔍 Checking CI/CD setup requirements...
echo.

echo 1. Checking if GitHub Actions workflow exists...
if exist ".github\workflows\deploy.yml" (
    echo ✅ GitHub Actions workflow found
) else (
    echo ❌ GitHub Actions workflow not found
    echo    Expected: .github\workflows\deploy.yml
    goto :error
)

echo.
echo 2. Checking Cloud Foundry login status...
cf target >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Cloud Foundry login verified
    echo.
    echo 📋 Current CF Target:
    cf target
) else (
    echo ❌ Not logged into Cloud Foundry
    echo    Please run: cf login -a https://api.cf.eu10-005.hana.ondemand.com
    goto :error
)

echo.
echo 3. Checking if apps exist in Cloud Foundry...
set apps_exist=true

cf app it-resonance-main-api >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ it-resonance-main-api exists
) else (
    echo ❌ it-resonance-main-api not found
    set apps_exist=false
)

cf app mule-to-is-api >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ mule-to-is-api exists
) else (
    echo ❌ mule-to-is-api not found
    set apps_exist=false
)

cf app boomi-to-is-api >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ boomi-to-is-api exists
) else (
    echo ❌ boomi-to-is-api not found
    set apps_exist=false
)

cf app ifa-frontend >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ ifa-frontend exists
) else (
    echo ❌ ifa-frontend not found
    set apps_exist=false
)

if "%apps_exist%"=="false" (
    echo.
    echo ⚠️ Some apps are missing. Deploy them first:
    echo    deployment\scripts\deploy-production.bat
    goto :error
)

echo.
echo 4. Testing API health endpoints...
echo 🔍 Testing Main API...
curl -s -f https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Main API is healthy
) else (
    echo ⚠️ Main API health check failed
)

echo 🔍 Testing MuleToIS API...
curl -s -f https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ MuleToIS API is healthy
) else (
    echo ⚠️ MuleToIS API health check failed
)

echo 🔍 Testing BoomiToIS API...
curl -s -f https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ BoomiToIS API is healthy
) else (
    echo ⚠️ BoomiToIS API health check failed
)

echo.
echo ========================================
echo ✅ CI/CD Setup Verification Complete!
echo ========================================
echo.
echo 📋 Next Steps:
echo 1. Add GitHub Secrets (see deployment\setup-cicd.md)
echo    - CF_ORG
echo    - CF_SPACE  
echo    - CF_USERNAME
echo    - CF_PASSWORD
echo.
echo 2. Test the pipeline:
echo    - Push to main branch, OR
echo    - Use GitHub Actions manual trigger
echo.
echo 3. Monitor deployment:
echo    - Go to GitHub → Actions tab
echo    - Watch the workflow progress
echo.
echo 🌐 Production URLs:
echo   Frontend:     https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com
echo   Main API:     https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com
echo   MuleToIS API: https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com
echo   BoomiToIS API: https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com
echo.
goto :end

:error
echo.
echo ========================================
echo ❌ CI/CD Setup Issues Found
echo ========================================
echo.
echo Please fix the issues above before setting up CI/CD.
echo See deployment\setup-cicd.md for detailed instructions.
echo.

:end
pause
