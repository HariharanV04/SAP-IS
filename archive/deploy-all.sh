#!/bin/bash

echo "===== IT Resonance Integration Flow Analyzer - Full Deployment ====="

# Login to Cloud Foundry
echo "Logging in to Cloud Foundry..."
cf login -a https://api.cf.us10-001.hana.ondemand.com

if [ $? -ne 0 ]; then
  echo "Cloud Foundry login failed! Aborting deployment."
  exit 1
fi

# Clean up unused routes to avoid quota issues
echo "Cleaning up unused routes..."
cf delete-orphaned-routes -f

# Deploy Backend API (which includes GetIflowEquivalent)
echo "Deploying Backend API..."
cd app

echo "Preparing backend for deployment..."
python prepare_deployment.py

if [ $? -ne 0 ]; then
  echo "Deployment preparation failed! Aborting."
  exit 1
fi

cf push

if [ $? -ne 0 ]; then
  echo "Backend API deployment failed! Aborting."
  exit 1
fi

# Deploy Frontend UI
echo "Building and deploying Frontend UI..."
cd ../project
npm install
npm run build
cf push

if [ $? -ne 0 ]; then
  echo "Frontend UI deployment failed!"
  exit 1
fi

echo "===== Full deployment completed successfully! ====="
echo "Your application components are now available at:"
echo "Frontend: Check the Cloud Foundry console for the randomly generated route"
echo "Backend API: Check the Cloud Foundry console for the randomly generated route"
echo "You can find the routes by running:"
echo "  cf app it-resonance-ui"
echo "  cf app it-resonance-api"
