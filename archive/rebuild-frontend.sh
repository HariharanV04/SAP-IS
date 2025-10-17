#!/bin/bash

echo "===== Rebuilding and Redeploying Frontend with Clean Build ====="

cd project

echo "Checking .env.production file..."
cat .env.production
echo ""

echo "Cleaning node_modules and build directories..."
rm -rf node_modules
rm -rf dist
rm -rf .vite
rm -f .env.production.local

echo "Installing dependencies..."
npm install

echo "Building production version with environment variables..."
export VITE_API_URL="https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com/api"
export REACT_APP_API_URL="https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com/api"
npm run build

echo "Checking built files for API references..."
grep -r --include="*.*" -l "it-resonance-api.cfapps" dist/
grep -r --include="*.*" -l "it-resonance-api-wacky-panther-za" dist/
echo ""

echo "Deploying to Cloud Foundry..."
cf push

if [ $? -ne 0 ]; then
  echo "Deployment failed!"
  exit 1
fi

echo "Deployment completed successfully!"
echo "Frontend is now available at: https://it-resonance-ui-interested-wildebeest-nc.cfapps.us10-001.hana.ondemand.com/"
echo "Backend API is available at: https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com/"

cd ..

echo "===== Rebuild and redeploy completed! ====="
