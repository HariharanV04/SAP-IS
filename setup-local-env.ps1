# PowerShell Script to Set Up Local Environment Variables
# This script copies the environment template files to the correct locations

Write-Host "🚀 Setting up Local Environment Variables" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# Function to copy environment file with confirmation
function Copy-EnvFile {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$ServiceName
    )
    
    Write-Host "📁 Setting up $ServiceName..." -ForegroundColor Yellow
    
    if (Test-Path $Source) {
        $destinationDir = Split-Path $Destination -Parent
        if (!(Test-Path $destinationDir)) {
            New-Item -Path $destinationDir -ItemType Directory -Force | Out-Null
        }
        
        if (Test-Path $Destination) {
            Write-Host "   ⚠️  $Destination already exists. Backing up..." -ForegroundColor Yellow
            Copy-Item $Destination "$Destination.backup" -Force
        }
        
        Copy-Item $Source $Destination -Force
        Write-Host "   ✅ Copied to: $Destination" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Source file not found: $Source" -ForegroundColor Red
    }
}

# Copy environment files
Copy-EnvFile "environment-setup/main-api.env" "app/.env" "Main API"
Copy-EnvFile "environment-setup/mulesoft-api.env" "MuleToIS-API/.env" "MuleToIS API"
Copy-EnvFile "environment-setup/boomi-api.env" "BoomiToIS-API/.env" "BoomiToIS API"
Copy-EnvFile "environment-setup/frontend.env" "IFA-Project/frontend/.env" "Frontend"

Write-Host ""
Write-Host "✅ Local environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Important Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update the ANTHROPIC_API_KEY in each .env file with your actual key"
Write-Host "2. The SAP BTP credentials are already configured with working values"
Write-Host "3. Test the MuleToIS API deployment fix:"
Write-Host ""
Write-Host "🧪 Testing Commands:" -ForegroundColor Cyan
Write-Host "   cd MuleToIS-API"
Write-Host "   python app.py    # Should start on port 5001"
Write-Host ""
Write-Host "   # In another terminal:"
Write-Host "   cd .."
Write-Host "   python test_unified_deployment.py"
Write-Host ""
Write-Host "📍 Environment Files Created:" -ForegroundColor Green
Write-Host "   ✅ IMigrate/app/.env"
Write-Host "   ✅ IMigrate/MuleToIS-API/.env"
Write-Host "   ✅ IMigrate/BoomiToIS-API/.env"
Write-Host "   ✅ IMigrate/IFA-Project/frontend/.env"





















