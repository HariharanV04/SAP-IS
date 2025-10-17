#!/bin/bash

# Deployment script for IT Resonance Integration Flow Analyzer

echo "===== IT Resonance Integration Flow Analyzer Deployment ====="
echo "Building production version..."

# Build the production version
npm run build

if [ $? -ne 0 ]; then
  echo "Build failed! Aborting deployment."
  exit 1
fi

echo "Build successful!"
echo "Deploying to SAP BTP Cloud Foundry..."

# Login to Cloud Foundry (this will prompt for credentials if not already logged in)
echo "Please log in to Cloud Foundry if prompted:"
cf login -a https://api.cf.us10-001.hana.ondemand.com

if [ $? -ne 0 ]; then
  echo "Cloud Foundry login failed! Aborting deployment."
  exit 1
fi

# Deploy the application
cf push

if [ $? -ne 0 ]; then
  echo "Deployment failed!"
  exit 1
fi

echo "===== Deployment completed successfully! ====="
echo "Your application is now available at: https://it-resonance-integration-analyzer.cfapps.us10-001.hana.ondemand.com"
