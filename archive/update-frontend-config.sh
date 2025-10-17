#!/bin/bash

echo "===== IT Resonance Frontend Configuration Update ====="

# Get the API route
echo "Getting the API route..."
API_ROUTE=$(cf app it-resonance-api | grep routes | awk '{print $2}')

if [ -z "$API_ROUTE" ]; then
  echo "Error: Could not retrieve API route. Make sure the API is deployed."
  exit 1
fi

echo "API route found: $API_ROUTE"

# Update the .env.production file
echo "Updating .env.production file with new API URL..."
cat > project/.env.production << EOF
# Production backend API URL for Cloud Foundry deployment
REACT_APP_API_URL=https://$API_ROUTE/api
VITE_API_URL=https://$API_ROUTE/api
# Disable continuous polling
VITE_DISABLE_AUTO_POLLING=true
EOF

echo ".env.production file updated successfully."

# Ask if user wants to rebuild and redeploy the frontend
read -p "Do you want to rebuild and redeploy the frontend now? (y/n): " rebuild

if [ "$rebuild" = "y" ] || [ "$rebuild" = "Y" ]; then
  echo "Rebuilding and redeploying frontend..."
  cd project
  
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
  
  # Get the frontend route
  UI_ROUTE=$(cf app it-resonance-ui | grep routes | awk '{print $2}')
  
  echo "Deployment completed successfully!"
  echo "Frontend is now available at: https://$UI_ROUTE"
  echo "Backend API is available at: https://$API_ROUTE"
  
  cd ..
else
  echo "Skipping rebuild and redeploy."
  echo "To rebuild and redeploy later, run:"
  echo "  cd project"
  echo "  npm run build"
  echo "  cf push"
fi

echo "===== Configuration update completed! ====="
