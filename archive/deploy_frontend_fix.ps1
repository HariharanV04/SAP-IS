Write-Host "Deploying static frontend to Cloud Foundry..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

# Navigate to the project directory
Set-Location -Path "$PSScriptRoot\project"

# Make sure the Staticfile exists with correct settings
$staticfileContent = @"
root: .
pushstate: enabled
directory: .
force_https: true
host_dot_files: true
status_codes:
  404: /index.html
"@

# Create or update the Staticfile
Set-Content -Path ".\dist\Staticfile" -Value $staticfileContent
Write-Host "Updated Staticfile configuration" -ForegroundColor Green

# Deploy to Cloud Foundry with --no-start option first
Write-Host "Pushing app without starting it first..." -ForegroundColor Yellow
cf push mulesoft-docs-ui -f manifest.yml --no-start

if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed. See errors above." -ForegroundColor Red
    exit 1
}

# Now explicitly set the command to null before starting
Write-Host "Setting start command to null..." -ForegroundColor Yellow
cf set-env mulesoft-docs-ui FORCE_HTTPS true

# Now start the app
Write-Host "Starting the application..." -ForegroundColor Yellow
cf start mulesoft-docs-ui

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend deployed successfully!" -ForegroundColor Green
    Write-Host "Your application is available at: https://mulesoft-docs-ui.cfapps.us10-001.hana.ondemand.com" -ForegroundColor Cyan
} else {
    Write-Host "Deployment failed. Please check the errors above." -ForegroundColor Red
}

# Return to original directory
Set-Location -Path $PSScriptRoot 