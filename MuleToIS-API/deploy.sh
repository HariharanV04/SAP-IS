#!/bin/bash

echo "===== IT Resonance iFlow Generator API Deployment ====="

echo "Checking required files..."
if [ ! -f app.py ]; then
  echo "Error: app.py not found!"
  exit 1
fi

if [ ! -f iflow_generator_api.py ]; then
  echo "Error: iflow_generator_api.py not found!"
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

if [ ! -f requirements.txt ]; then
  echo "Error: requirements.txt not found!"
  exit 1
fi

if [ ! -f .env ]; then
  echo "Warning: .env file not found! Make sure your environment variables are set."
fi

echo "All required files found."

echo "Loading environment variables from .env file..."
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Environment variables loaded."
fi

echo "Deploying to Cloud Foundry..."
cf push

if [ $? -ne 0 ]; then
  echo "Deployment failed!"
  exit 1
fi

echo "Deployment completed successfully!"
echo "API is now available at: https://mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com"
