#!/bin/bash
echo "Building and deploying Architecture Diagram to Cloud Foundry..."

# Get current timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$timestamp] Starting deployment process..."

# Create dist directory if it doesn't exist
mkdir -p dist

# Copy all architecture diagram files to dist
echo "[$timestamp] Copying architecture diagram files..."
cp -r ../architecture-showcase.html dist/
cp -r ../architecture-diagram dist/
cp -r ../d3-diagram dist/
cp -r ../static-svg-diagram dist/

# Create index.html that redirects to architecture-showcase.html
cat > dist/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<title>Architecture Diagram Showcase</title>
<meta http-equiv="refresh" content="0; url=architecture-showcase.html">
</head>
<body>
<p>Redirecting to <a href="architecture-showcase.html">Architecture Diagram Showcase</a>...</p>
</body>
</html>
EOF

echo "[$timestamp] Files copied successfully."

# Deploy to Cloud Foundry
echo "[$timestamp] Deploying to Cloud Foundry..."
cf push

if [ $? -eq 0 ]; then
    echo "[$timestamp] Deployment successful!"
    echo ""
    echo "Architecture Diagram is now available at:"
    echo "https://architecture-diagram.cfapps.us10-001.hana.ondemand.com"
    echo ""
    echo "Available diagrams:"
    echo "- React.js Interactive: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com/architecture-diagram/"
    echo "- D3.js Advanced: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com/d3-diagram/"
    echo "- Static SVG: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com/static-svg-diagram/architecture-diagram.svg"
else
    echo "[$timestamp] Deployment failed!"
    exit 1
fi
