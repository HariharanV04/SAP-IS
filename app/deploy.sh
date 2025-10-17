#!/bin/bash

echo "===== IT Resonance API Deployment ====="

echo "Checking required files..."
if [ ! -f app.py ]; then
  echo "Error: app.py not found!"
  exit 1
fi

if [ ! -f iflow_matcher.py ]; then
  echo "Error: iflow_matcher.py not found!"
  exit 1
fi

if [ ! -f Procfile ]; then
  echo "Error: Procfile not found!"
  exit 1
fi

if [ ! -f manifest.yml ]; then
  echo "Error: manifest.yml not found!"
  exit 1
fi

echo "All required files found."

echo "Deploying to Cloud Foundry..."
cf push

if [ $? -ne 0 ]; then
  echo "Deployment failed!"
  exit 1
fi

echo "Deployment completed successfully!"
echo "API is now available at: https://it-resonance-api.cfapps.us10-001.hana.ondemand.com"
