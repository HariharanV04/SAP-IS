# Testing Commands for MuleSoft Documentation Generator

## Testing with Local Backend

### 1. Start the local Flask backend (in one terminal)
```powershell
cd mule_cf_deployment/app
python run_app.py
```
This will start your Flask backend on port 8080.

### 2. Build the frontend for local backend testing
```powershell
cd mule_cf_deployment/project
# Create local environment file pointing to local backend
echo "# Local production environment
VITE_API_URL=http://localhost:8080/api" > .env.production.local
# Build the application
npm run build
```

### 3. Serve the built frontend (on a port other than 3000)
```powershell
cd mule_cf_deployment/project
npx serve -s dist -l 4500
```
Then open http://localhost:4500 in your browser.

## Testing with Cloud Foundry Backend

### 1. Verify your backend is deployed on Cloud Foundry
Check the status of your app:
```powershell
cf apps
```

### 2. Build the frontend for Cloud Foundry backend
```powershell
cd mule_cf_deployment/project
# Create production environment file
$backendUrl = "https://your-backend-app-name.cfapps.us10-001.hana.ondemand.com/api"
echo "# Production environment
VITE_API_URL=$backendUrl" > .env.production
# Build the application
npm run build
```

### 3. Test locally before deploying
```powershell
cd mule_cf_deployment/project
npx serve -s dist -l 4500
```
Then open http://localhost:4500 in your browser.

### 4. Deploy to Cloud Foundry
```powershell
cd mule_cf_deployment
./deploy_frontend.ps1
```

## Troubleshooting

### Test API connectivity directly

Open this file in your browser to test the API directly:
```
mule_cf_deployment/api_test.html
```

### Check browser console for errors
Open the developer tools in your browser (F12) and check the console for any errors related to API calls. 