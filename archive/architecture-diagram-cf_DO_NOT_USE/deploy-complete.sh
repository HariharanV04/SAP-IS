#!/bin/bash
echo "========================================"
echo " React Architecture Diagram CF Deployment"
echo "========================================"

# Get current timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$timestamp] Starting React app deployment process..."

# Navigate to React app directory
cd ../architecture-diagram

# Clean previous build
echo "[$timestamp] Cleaning previous build..."
rm -rf build

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "[$timestamp] Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[$timestamp] Failed to install dependencies!"
        exit 1
    fi
fi

# Build the React app
echo "[$timestamp] Building React app for production..."
npm run build

if [ $? -ne 0 ]; then
    echo "[$timestamp] React build failed!"
    exit 1
fi

echo "[$timestamp] React build completed successfully."

# Navigate back to CF deployment directory
cd ../architecture-diagram-cf

# Copy build files to CF deployment directory
echo "[$timestamp] Copying build files..."
rm -rf build
cp -r ../architecture-diagram/build .

echo "[$timestamp] Build files copied successfully."

# Deploy to Cloud Foundry
echo "[$timestamp] Deploying to Cloud Foundry..."
cf push

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo " DEPLOYMENT SUCCESSFUL!"
    echo "========================================"
    echo "[$timestamp] React Architecture Diagram deployed successfully!"
    echo ""
    echo "Application URL: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com"
    echo ""
    echo "Features:"
    echo "- Interactive React.js architecture diagram"
    echo "- Drag and drop components"
    echo "- Zoom, pan, and minimap controls"
    echo "- Component details on click"
    echo "- Responsive design"
    echo ""
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo " DEPLOYMENT FAILED!"
    echo "========================================"
    echo "[$timestamp] Deployment failed! Check the logs above."
    exit 1
fi
