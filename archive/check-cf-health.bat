@echo off
echo ===== IT Resonance Cloud Foundry Health Check =====

echo Checking health of main API...
curl -s https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com/api/health
echo.

echo Checking health of iFlow API...
curl -s https://mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com/api/health
echo.

echo Checking if frontend is accessible...
curl -s -I https://ifa-frontend.cfapps.us10-001.hana.ondemand.com | findstr "HTTP"
echo.

echo All health checks completed.
echo.
echo Main API: https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com
echo iFlow API: https://mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com
echo Frontend: https://ifa-frontend.cfapps.us10-001.hana.ondemand.com/projects/1/flow
