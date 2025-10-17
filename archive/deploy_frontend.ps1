# PowerShell script to build and deploy frontend to Cloud Foundry

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "         Frontend Deployment to Cloud Foundry           " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = Get-Location
$projectDir = "$baseDir\mule_cf_deployment\project"

# Check if Cloud Foundry CLI is installed
try {
    $cfVersion = cf --version
    Write-Host "Cloud Foundry CLI detected: $cfVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Cloud Foundry CLI is not installed or not in the PATH." -ForegroundColor Red
    Write-Host "Please install the Cloud Foundry CLI to continue." -ForegroundColor Red
    Write-Host "Download from: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html" -ForegroundColor Red
    exit
}

# Check if user is logged in to Cloud Foundry
Write-Host "Checking Cloud Foundry login status..." -ForegroundColor Yellow
$cfTarget = cf target 2>&1
if ($cfTarget -match "FAILED") {
    Write-Host "Not logged in to Cloud Foundry. Please log in:" -ForegroundColor Yellow
    cf login
} else {
    Write-Host "Already logged in to Cloud Foundry." -ForegroundColor Green
    Write-Host $cfTarget -ForegroundColor Gray
}

# Ask for frontend deployment configuration
Write-Host ""
Write-Host "Frontend Deployment Configuration:" -ForegroundColor Cyan
$frontendAppName = Read-Host "Enter frontend application name [mulesoft-docs-ui]"
if ([string]::IsNullOrWhiteSpace($frontendAppName)) {
    $frontendAppName = "mulesoft-docs-ui"
}

$frontendMemory = Read-Host "Enter frontend memory allocation (MB) [64M]"
if ([string]::IsNullOrWhiteSpace($frontendMemory)) {
    $frontendMemory = "64M"
}

$cfDomain = "cfapps.us10-001.hana.ondemand.com"
$frontendHost = Read-Host "Enter frontend hostname (without domain) [mulesoft-docs-ui]"
if ([string]::IsNullOrWhiteSpace($frontendHost)) {
    $frontendHost = "mulesoft-docs-ui"
}

$frontendRoute = "$frontendHost.$cfDomain"
Write-Host "Frontend route will be: $frontendRoute" -ForegroundColor Yellow

# Ask for backend URL
Write-Host ""
Write-Host "Backend Configuration:" -ForegroundColor Cyan
$useLocalBackend = Read-Host "Do you want to connect to a local backend for testing? (y/n)"

if ($useLocalBackend -eq "y") {
    $backendPort = Read-Host "Enter local backend port [8080]"
    if ([string]::IsNullOrWhiteSpace($backendPort)) {
        $backendPort = "8080"
    }
    $backendApiUrl = "http://localhost:$backendPort/api"
    Write-Host "Using local backend at: $backendApiUrl" -ForegroundColor Yellow
} else {
    $backendAppName = Read-Host "Enter backend application name [mulesoft-docs-api]"
    if ([string]::IsNullOrWhiteSpace($backendAppName)) {
        $backendAppName = "mulesoft-docs-api"
    }
    $backendApiUrl = "https://$backendAppName.$cfDomain/api"
    Write-Host "Using Cloud Foundry backend at: $backendApiUrl" -ForegroundColor Yellow
    
    # Verify the backend URL is accessible
    Write-Host "Verifying backend URL is accessible..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "$backendApiUrl/health" -Method Head
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend is accessible" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Backend returned status code: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Could not connect to backend. Deployment will continue, but frontend may not work correctly." -ForegroundColor Yellow
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Update .env.production file
Write-Host ""
Write-Host "Updating production environment configuration..." -ForegroundColor Cyan
$envProdContent = @"
# Production backend API URL
REACT_APP_API_URL=$backendApiUrl
VITE_API_URL=$backendApiUrl
"@
Set-Content -Path "$projectDir\.env.production" -Value $envProdContent -Force
Write-Host ".env.production updated with API URL: $backendApiUrl" -ForegroundColor Green

# Building the React app
Write-Host ""
Write-Host "Building React application for production..." -ForegroundColor Cyan
Set-Location $projectDir
Write-Host "Running: npm run build" -ForegroundColor Gray
npm run build
if ($LastExitCode -ne 0) {
    Write-Host "Error: Failed to build React application." -ForegroundColor Red
    exit
}
Write-Host "React application built successfully!" -ForegroundColor Green

# Create Staticfile for proper routing
Write-Host ""
Write-Host "Creating Staticfile for SPA routing..." -ForegroundColor Cyan
Set-Content -Path "$projectDir\dist\Staticfile" -Value "pushstate: enabled" -Force
Write-Host "Staticfile created with pushstate enabled for SPA routing." -ForegroundColor Green

# Create manifest.yml for Cloud Foundry
Write-Host ""
Write-Host "Creating Cloud Foundry manifest..." -ForegroundColor Cyan
$manifestContent = @"
---
applications:
- name: $frontendAppName
  memory: $frontendMemory
  buildpacks:
  - staticfile_buildpack
  path: dist
  routes:
  - route: $frontendRoute
  env:
    FORCE_HTTPS: true
"@
Set-Content -Path "$projectDir\manifest.yml" -Value $manifestContent -Force
Write-Host "manifest.yml created for Cloud Foundry deployment." -ForegroundColor Green

# Optional: Test the production build locally
Write-Host ""
$testLocally = Read-Host "Do you want to test the production build locally before deploying? (y/n)"
if ($testLocally -eq "y") {
    Write-Host "Testing production build locally..." -ForegroundColor Cyan
    # Try different ports to avoid conflicts
    $ports = @(4000, 4500, 5000, 5500, 8000)
    $portFound = $false
    
    foreach ($port in $ports) {
        Write-Host "Trying to serve on port $port..." -ForegroundColor Yellow
        try {
            Start-Process powershell -ArgumentList "cd '$projectDir' ; npx serve -s dist -l $port" -NoNewWindow
            Write-Host "Success! Production build is available at: http://localhost:$port" -ForegroundColor Green
            Write-Host "Press any key to continue with deployment (this will close the local server)..." -ForegroundColor Yellow
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            Get-Process -Name "node" | Where-Object { $_.CommandLine -like "*serve*" } | Stop-Process -Force
            $portFound = $true
            break
        } catch {
            Write-Host "Failed to start server on port $port. Trying another port..." -ForegroundColor Red
        }
    }
    
    if (-not $portFound) {
        Write-Host "Could not find an available port to test locally. Continuing with deployment..." -ForegroundColor Yellow
    }
}

# Deploy to Cloud Foundry
Write-Host ""
Write-Host "Deploying frontend to Cloud Foundry..." -ForegroundColor Cyan

# Check if app already exists
$appExists = cf app $frontendAppName 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Application '$frontendAppName' already exists." -ForegroundColor Yellow
    $deleteApp = Read-Host "Do you want to delete and recreate it? (y/n)"
    if ($deleteApp -eq "y") {
        Write-Host "Deleting existing application..." -ForegroundColor Yellow
        cf delete $frontendAppName -f
    }
}

Write-Host "Running: cf push" -ForegroundColor Gray
cf push
if ($LastExitCode -ne 0) {
    Write-Host "Error: Frontend deployment failed." -ForegroundColor Red
    Write-Host "Checking logs for more information..." -ForegroundColor Yellow
    cf logs $frontendAppName --recent
    exit
}

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "               Frontend Deployment Complete              " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your frontend application has been deployed to:" -ForegroundColor Green
Write-Host "https://$frontendRoute" -ForegroundColor White
Write-Host ""
Write-Host "It is configured to communicate with the backend at:" -ForegroundColor Green
Write-Host "$backendApiUrl" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "cf logs $frontendAppName --recent" -ForegroundColor White
Write-Host ""

# Return to the base directory
Set-Location $baseDir 