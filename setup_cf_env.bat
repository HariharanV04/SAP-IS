@echo off
REM Cloud Foundry Environment Variables Setup Script (Windows Batch)
REM This script sets all environment variables for CF deployment

echo 🚀 Setting up Cloud Foundry Environment Variables for All APIs
echo ================================================================

REM Check if CF CLI is available
cf --version >nul 2>&1
if errorlevel 1 (
    echo ❌ CF CLI not found. Please install it first.
    pause
    exit /b 1
)

echo ✅ CF CLI found

REM Working SAP BTP Credentials
set SAP_BTP_CLIENT_ID=sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895^|it!b410334
set SAP_BTP_CLIENT_SECRET=5813ca83-4ba6-4231-96e1-1a48a80eafec$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w=
set SAP_BTP_OAUTH_URL=https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token
set SAP_BTP_TENANT_URL=https://itr-internal-2hco92jx.it-cpi034.cfapps.us10-002.hana.ondemand.com
set SAP_BTP_DEFAULT_PACKAGE=ConversionPackages

REM API Key (update this with your actual key)
set ANTHROPIC_API_KEY=sk-ant-api03-yTb9vL3wgKQrUjKrEuFGPtCg9R5uPGAUAy1MzZK5sBHhMgQmyPr7kl0nLU2Q8xZ_

echo.
echo 📋 Setting Cloud Foundry Environment Variables...
echo.

REM Main API
echo 🔧 Configuring Main API...
cf set-env it-resonance-main-api SAP_BTP_CLIENT_ID "%SAP_BTP_CLIENT_ID%"
cf set-env it-resonance-main-api SAP_BTP_CLIENT_SECRET "%SAP_BTP_CLIENT_SECRET%"
cf set-env it-resonance-main-api SAP_BTP_OAUTH_URL "%SAP_BTP_OAUTH_URL%"
cf set-env it-resonance-main-api SAP_BTP_TENANT_URL "%SAP_BTP_TENANT_URL%"
cf set-env it-resonance-main-api SAP_BTP_DEFAULT_PACKAGE "%SAP_BTP_DEFAULT_PACKAGE%"
cf set-env it-resonance-main-api ANTHROPIC_API_KEY "%ANTHROPIC_API_KEY%"
cf set-env it-resonance-main-api IFLOW_API_URL "https://mule-to-is-api.cfapps.eu10.hana.ondemand.com"
cf set-env it-resonance-main-api BOOMI_API_URL "https://boomi-to-is-api.cfapps.eu10.hana.ondemand.com"

REM MuleToIS API
echo 🔧 Configuring MuleToIS API...
cf set-env mule-to-is-api SAP_BTP_CLIENT_ID "%SAP_BTP_CLIENT_ID%"
cf set-env mule-to-is-api SAP_BTP_CLIENT_SECRET "%SAP_BTP_CLIENT_SECRET%"
cf set-env mule-to-is-api SAP_BTP_OAUTH_URL "%SAP_BTP_OAUTH_URL%"
cf set-env mule-to-is-api SAP_BTP_TENANT_URL "%SAP_BTP_TENANT_URL%"
cf set-env mule-to-is-api SAP_BTP_DEFAULT_PACKAGE "%SAP_BTP_DEFAULT_PACKAGE%"
cf set-env mule-to-is-api ANTHROPIC_API_KEY "%ANTHROPIC_API_KEY%"
cf set-env mule-to-is-api MAIN_API_URL "https://it-resonance-main-api.cfapps.eu10.hana.ondemand.com"

REM BoomiToIS API
echo 🔧 Configuring BoomiToIS API...
cf set-env boomi-to-is-api SAP_BTP_CLIENT_ID "%SAP_BTP_CLIENT_ID%"
cf set-env boomi-to-is-api SAP_BTP_CLIENT_SECRET "%SAP_BTP_CLIENT_SECRET%"
cf set-env boomi-to-is-api SAP_BTP_OAUTH_URL "%SAP_BTP_OAUTH_URL%"
cf set-env boomi-to-is-api SAP_BTP_TENANT_URL "%SAP_BTP_TENANT_URL%"
cf set-env boomi-to-is-api SAP_BTP_DEFAULT_PACKAGE "%SAP_BTP_DEFAULT_PACKAGE%"
cf set-env boomi-to-is-api ANTHROPIC_API_KEY "%ANTHROPIC_API_KEY%"
cf set-env boomi-to-is-api MAIN_API_URL "https://it-resonance-main-api.cfapps.eu10.hana.ondemand.com"

echo.
echo ✅ All Cloud Foundry environment variables have been set!
echo.
echo 📝 Next Steps:
echo 1. ✅ ANTHROPIC_API_KEY is already set with the correct key
echo 2. Restart all applications:
echo    cf restart it-resonance-main-api
echo    cf restart mule-to-is-api
echo    cf restart boomi-to-is-api
echo.
echo 🔍 To verify environment variables:
echo    cf env it-resonance-main-api
echo.
pause
