@echo off
echo ========================================
echo Cloud Foundry Deployment Validation
echo ========================================

cd /d "%~dp0..\.."

echo 🔍 Running comprehensive deployment validation...
echo This will check all prerequisites for CF deployment.
echo.

python deployment\scripts\validate-cf-deployment.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================
    echo ✅ VALIDATION PASSED!
    echo ========================================
    echo.
    echo Your project is ready for deployment!
    echo.
    echo 🚀 Next steps:
    echo 1. Set up GitHub Secrets:
    echo    - Go to: https://github.com/DheepLearningITR/IMigrate/settings/secrets/actions
    echo    - Add CF_ORG, CF_SPACE, CF_USERNAME, CF_PASSWORD
    echo.
    echo 2. Test deployment:
    echo    - Push a small change to main branch
    echo    - Watch GitHub Actions: https://github.com/DheepLearningITR/IMigrate/actions
    echo.
    echo 3. Manual deployment (if needed):
    echo    - Run: deployment\scripts\deploy-production.bat
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ VALIDATION FAILED!
    echo ========================================
    echo.
    echo Please fix the issues above before deploying.
    echo.
    echo 🔧 Common fixes:
    echo - Install CF CLI: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html
    echo - Login to CF: cf login -a https://api.cf.eu10-005.hana.ondemand.com
    echo - Check manifest files exist in each app directory
    echo - Verify environment configuration
    echo.
)

pause
