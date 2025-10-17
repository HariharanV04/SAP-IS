Write-Host "Building and deploying the frontend to Cloud Foundry..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

# Navigate to the project directory
Set-Location -Path "$PSScriptRoot\project"

# Check for required dependencies
Write-Host "Checking for required dependencies..." -ForegroundColor Yellow
$packageJsonPath = ".\package.json"
if (-not (Test-Path $packageJsonPath)) {
    Write-Host "Error: package.json not found!" -ForegroundColor Red
    exit 1
}

# Check if react-hot-toast is installed
$packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
$dependencies = $packageJson.dependencies
$devDependencies = $packageJson.devDependencies

$hasToast = $false
$hasAxios = $false

if ($dependencies.PSObject.Properties.Name -contains "react-hot-toast") {
    $hasToast = $true
}
if ($dependencies.PSObject.Properties.Name -contains "axios") {
    $hasAxios = $true
}

if (-not $hasToast) {
    Write-Host "Installing react-hot-toast..." -ForegroundColor Yellow
    npm install react-hot-toast --save
}

if (-not $hasAxios) {
    Write-Host "Installing axios..." -ForegroundColor Yellow
    npm install axios --save
}

# Build the project
Write-Host "Building the React application..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""

# Create Staticfile if it doesn't exist
$staticfilePath = ".\dist\Staticfile"
Write-Host "Creating/updating Staticfile..." -ForegroundColor Yellow
@"
root: .
pushstate: enabled
directory: .
force_https: true
host_dot_files: true
status_codes:
  404: /index.html
"@ | Out-File -FilePath $staticfilePath -Encoding utf8
Write-Host "Staticfile updated successfully!" -ForegroundColor Green
Write-Host ""

# Update the frontend manifest
$frontendManifestPath = ".\frontend-manifest.yml"
Write-Host "Creating/updating frontend manifest..." -ForegroundColor Yellow
@"
---
applications:
- name: mulesoft-docs-ui
  memory: 64M
  buildpacks:
  - staticfile_buildpack
  path: ./dist
  command: null  # Explicitly set to null to use buildpack's default
  routes:
  - route: mulesoft-docs-ui.cfapps.us10-001.hana.ondemand.com
  env:
    FORCE_HTTPS: true
"@ | Out-File -FilePath $frontendManifestPath -Encoding utf8
Write-Host "Frontend manifest updated!" -ForegroundColor Green
Write-Host ""

# Deploy to Cloud Foundry
Write-Host "Deploying to Cloud Foundry..." -ForegroundColor Yellow
cf push -f $frontendManifestPath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Frontend deployed successfully!" -ForegroundColor Green
    Write-Host "Your application is available at: https://mulesoft-docs-ui.cfapps.us10-001.hana.ondemand.com" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Deployment failed. Please check the logs above for details." -ForegroundColor Red
}

# Return to the original directory
Set-Location -Path $PSScriptRoot 