#!/bin/bash

echo "===== Redeploying Backend API with Updated CORS Configuration ====="

cd app

echo "Checking CORS helper implementation..."
grep "Access-Control-Allow-Origin" utils/cors_helper.py
echo ""

echo "Deploying to Cloud Foundry..."
cf push

if [ $? -ne 0 ]; then
  echo "Deployment failed!"
  exit 1
fi

echo "Getting the API route..."
API_ROUTE=$(cf app it-resonance-api | grep routes | awk '{print $2}')

echo "Deployment completed successfully!"
echo "Backend API is now available at: https://$API_ROUTE"

echo "Testing CORS headers..."
echo "You can test the CORS headers with the following curl command:"
echo "curl -v -X OPTIONS https://$API_ROUTE/api/health -H \"Origin: https://it-resonance-ui-interested-wildebeest-nc.cfapps.us10-001.hana.ondemand.com\" -H \"Access-Control-Request-Method: GET\""

cd ..

echo "===== Backend API redeployment completed! ====="
