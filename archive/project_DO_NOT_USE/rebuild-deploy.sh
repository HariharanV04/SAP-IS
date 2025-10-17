#!/bin/bash

echo "===== Rebuilding and Redeploying IT Resonance UI ====="

echo "Checking .env.production file..."
cat .env.production
echo ""

echo "Cleaning build directory..."
rm -rf dist

echo "Installing dependencies..."
npm install

echo "Building production version..."
npm run build

echo "Deploying to Cloud Foundry..."
cf push

if [ $? -ne 0 ]; then
  echo "Deployment failed!"
  exit 1
fi

echo "Deployment completed successfully!"
echo "Frontend is now available at: https://it-resonance-ui.cfapps.us10-001.hana.ondemand.com"
