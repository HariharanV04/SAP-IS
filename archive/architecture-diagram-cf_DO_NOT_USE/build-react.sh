#!/bin/bash
echo "Building React.js Architecture Diagram..."

# Get current timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$timestamp] Building React application..."

# Navigate to React app directory
cd ../architecture-diagram

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

if [ $? -eq 0 ]; then
    echo "[$timestamp] React build successful!"
    
    # Copy build files to CF deployment directory
    echo "[$timestamp] Copying build files..."
    cd ../architecture-diagram-cf
    mkdir -p dist/architecture-diagram
    
    cp -r ../architecture-diagram/build/* dist/architecture-diagram/
    
    echo "[$timestamp] React build files copied successfully."
else
    echo "[$timestamp] React build failed!"
    exit 1
fi

cd ../architecture-diagram-cf
echo "[$timestamp] React build process completed."
