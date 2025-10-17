# IT Resonance Integration Flow Analyzer

A modern web application for analyzing MuleSoft integration flows and finding SAP Integration Suite equivalents.

## Features

- Upload and analyze MuleSoft XML files
- Generate comprehensive documentation
- Find SAP Integration Suite equivalents
- Generate SAP API/iFlow definitions
- Deploy to SAP Integration Suite

## Deployment to SAP BTP Cloud Foundry

### Prerequisites

1. SAP BTP Cloud Foundry account
2. Cloud Foundry CLI installed
3. Node.js and npm installed

### Deployment Steps

#### 1. Build the Production Version

```bash
# Install dependencies
npm install

# Build the production version
npm run build
```

#### 2. Deploy to Cloud Foundry

```bash
# Login to Cloud Foundry
cf login -a https://api.cf.us10-001.hana.ondemand.com

# Deploy the application
cf push
```

Alternatively, you can use the provided deployment scripts:

**On Linux/macOS:**
```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

**On Windows:**
```bash
# Run the deployment script
deploy.bat
```

### Configuration

The application uses environment variables for configuration. These are set in the `.env.production` file:

```
REACT_APP_API_URL=https://mulesoft-docs-api.cfapps.us10-001.hana.ondemand.com/api
VITE_API_URL=https://mulesoft-docs-api.cfapps.us10-001.hana.ondemand.com/api
```

### Troubleshooting

If you encounter CORS issues:

1. Make sure the backend API has the correct CORS headers:
   ```
   Access-Control-Allow-Origin: https://it-resonance-integration-analyzer.cfapps.us10-001.hana.ondemand.com
   Access-Control-Allow-Methods: GET, POST, OPTIONS
   Access-Control-Allow-Headers: Content-Type, Authorization
   Access-Control-Allow-Credentials: true
   ```

2. Check that the frontend is using the correct API URL

3. Verify that the Cloud Foundry routes are correctly configured

## Development

For local development:

```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```

## License

© 2024 IT Resonance. All rights reserved.
