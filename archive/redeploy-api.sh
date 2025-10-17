#!/bin/bash

echo "===== IT Resonance Integration Flow Analyzer - API Redeployment ====="

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

# Navigate to the app directory
cd app

# Prepare for deployment
echo "Preparing backend for deployment..."
python prepare_deployment.py

if [ $? -ne 0 ]; then
  echo "Deployment preparation failed! Aborting."
  exit 1
fi

# Deploy the API
echo "Deploying Backend API with updated CORS configuration..."
cf push

if [ $? -ne 0 ]; then
  echo "Backend API deployment failed!"
  exit 1
fi

# Get the API route
echo "Getting the API route..."
API_ROUTE=$(cf app it-resonance-api | grep routes | awk '{print $2}')

echo "===== API Redeployment completed successfully! ====="
echo "Your API is now available at: https://$API_ROUTE"
echo "CORS should now be properly configured to allow requests from your frontend application."
