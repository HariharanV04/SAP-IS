# PowerShell script to update CORS settings for Cloud Foundry deployment

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Updating CORS settings for Cloud Foundry deployment" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = Get-Location
$appDir = "$baseDir\mule_cf_deployment\app"

# Check if the CORS helper file exists
$corsHelperPath = "$appDir\utils\cors_helper.py"
if (-not (Test-Path $corsHelperPath)) {
    Write-Host "Error: CORS helper file not found at $corsHelperPath" -ForegroundColor Red
    exit
}

# Update CORS settings to be more permissive for Cloud Foundry
$corsHelperContent = @"
# cors_helper.py - Helper for enabling CORS in Flask app

from flask import Flask, request
from flask_cors import CORS

def enable_cors(app):
    """
    Enable CORS for the Flask application with settings appropriate for Cloud Foundry
    """
    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Add CORS headers to all responses
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin', '*')
        # Always allow the actual origin that made the request
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        # Handle pre-flight OPTIONS requests
        if request.method == 'OPTIONS':
            return response
            
        return response
    
    return app
"@

# Backup the original file
$backupPath = "$corsHelperPath.bak"
if (-not (Test-Path $backupPath)) {
    Copy-Item $corsHelperPath $backupPath
    Write-Host "Backed up original CORS helper to $backupPath" -ForegroundColor Yellow
}

# Update the CORS helper
Set-Content -Path $corsHelperPath -Value $corsHelperContent
Write-Host "✅ Updated CORS helper with Cloud Foundry-friendly settings" -ForegroundColor Green

# Now create/update manifest.yml for Cloud Foundry deployment
$manifestPath = "$baseDir\mule_cf_deployment\manifest.yml"
$manifestContent = @"
---
applications:
- name: mulesoft-docs-api
  memory: 256M
  buildpacks:
  - python_buildpack
  command: python run_app.py
  path: app
  env:
    FLASK_ENV: production
    PYTHONUNBUFFERED: true
    CORS_ENABLED: true
  health-check-type: http
  health-check-http-endpoint: /api/health
"@

Set-Content -Path $manifestPath -Value $manifestContent
Write-Host "✅ Created/updated manifest.yml with health check settings" -ForegroundColor Green

Write-Host ""
Write-Host "✅ CORS and deployment configuration updated successfully." -ForegroundColor Green
Write-Host "To deploy to Cloud Foundry, run:" -ForegroundColor Yellow
Write-Host "cd $baseDir\mule_cf_deployment" -ForegroundColor White
Write-Host "cf push" -ForegroundColor White
