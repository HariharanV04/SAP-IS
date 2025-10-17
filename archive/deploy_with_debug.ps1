# PowerShell script for deploying to Cloud Foundry with debugging

Write-Host "=== MuleSoft Documentation Generator CF Deployment Script ===" -ForegroundColor Cyan
Write-Host "This script will deploy the app to Cloud Foundry with debugging enabled" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan

# Check if CF CLI is installed
try {
    $cfVersion = cf --version
    Write-Host "Cloud Foundry CLI detected: $cfVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Cloud Foundry CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://github.com/cloudfoundry/cli#installers-and-compressed-binaries" -ForegroundColor Yellow
    exit 1
}

# Ensure user is logged in
Write-Host "Checking CF login status..." -ForegroundColor Cyan
$loginStatus = cf target
if ($LASTEXITCODE -ne 0) {
    Write-Host "You need to log in to Cloud Foundry first." -ForegroundColor Yellow
    Write-Host "Use: cf login -a <your-api-endpoint>" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "You are logged in to Cloud Foundry:" -ForegroundColor Green
    Write-Host $loginStatus -ForegroundColor Gray
}

# Check if app already exists
$appName = "mulesoft-documentation-generator"
$appExists = cf app $appName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Application '$appName' already exists in the target space." -ForegroundColor Yellow
    $response = Read-Host "Do you want to delete and recreate it? (y/n)"
    if ($response -eq "y") {
        Write-Host "Deleting existing application..." -ForegroundColor Cyan
        cf delete $appName -f
    } else {
        Write-Host "Updating existing application..." -ForegroundColor Cyan
    }
}

# Set environment variables for more verbose debugging
$env:CF_TRACE = "true"
$env:CF_VERBOSE_OUTPUT = "true"
$env:CF_STAGING_TIMEOUT = "15"
$env:CF_STARTUP_TIMEOUT = "5"

Write-Host "Setting up for deployment:" -ForegroundColor Cyan
Write-Host "1. Verbose CF output enabled" -ForegroundColor Gray
Write-Host "2. Extended timeouts configured" -ForegroundColor Gray

# Optional: Create temporary manifest for deployment
$tempManifest = $false
if (Test-Path "manifest.yml") {
    Write-Host "Checking manifest.yml for health check configuration..." -ForegroundColor Cyan
    $manifestContent = Get-Content -Path "manifest.yml" -Raw
    if (-not ($manifestContent -match "health-check-type")) {
        Write-Host "Adding health check configuration to manifest..." -ForegroundColor Yellow
        $manifestContent = $manifestContent -replace "applications:", "applications:`n- health-check-type: http`n  health-check-http-endpoint: /health`n  timeout: 180"
        Set-Content -Path "manifest.yml.tmp" -Value $manifestContent
        $tempManifest = $true
    }
}

# Deploy the application
Write-Host "Deploying application to Cloud Foundry..." -ForegroundColor Cyan
if ($tempManifest) {
    cf push -f manifest.yml.tmp
} else {
    cf push
}

# Check deployment status
if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed. Getting application logs for debugging..." -ForegroundColor Red
    cf logs $appName --recent
    
    Write-Host "Checking application health..." -ForegroundColor Yellow
    cf app $appName
    
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Check that your application listens on the port specified by the PORT environment variable." -ForegroundColor Gray
    Write-Host "2. Ensure your application responds to HTTP health checks at /health with a 200 status code." -ForegroundColor Gray
    Write-Host "3. Review logs for any errors during startup." -ForegroundColor Gray
    Write-Host "4. Make sure all dependencies are properly specified in requirements.txt." -ForegroundColor Gray
} else {
    Write-Host "Deployment successful!" -ForegroundColor Green
    cf app $appName
    
    # Get the application URL
    $appInfo = cf app $appName 
    $appUrl = ($appInfo | Select-String -Pattern "routes:").ToString() -replace "routes:\s+", ""
    
    Write-Host "Your application is available at: https://$appUrl" -ForegroundColor Cyan
}

# Clean up
if ($tempManifest) {
    Remove-Item -Path "manifest.yml.tmp"
}

# Restore environment variables
$env:CF_TRACE = $null
$env:CF_VERBOSE_OUTPUT = $null
$env:CF_STAGING_TIMEOUT = $null
$env:CF_STARTUP_TIMEOUT = $null

Write-Host "Deployment process completed." -ForegroundColor Cyan 