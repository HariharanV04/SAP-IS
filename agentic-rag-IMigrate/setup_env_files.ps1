# PowerShell Script to Setup .env Files for IMigrate + RAG Integration
# Run this script from the root directory

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "Setting up .env files for IMigrate + RAG Integration" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

# Create BoomiToIS-API .env
Write-Host "`n📁 Creating IMigrate/BoomiToIS-API/.env..." -ForegroundColor Yellow
@"
# BoomiToIS-API Configuration

# Anthropic API Key for documentation enhancement (OPTIONAL)
ANTHROPIC_API_KEY=

# RAG System Integration - MUST BE TRUE TO USE RAG AGENT
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010

# Main API URL
MAIN_API_URL=http://localhost:5000

# Port configuration
PORT=5003

# CORS Configuration
CORS_ORIGIN=http://localhost:5173
"@ | Out-File -FilePath "IMigrate\BoomiToIS-API\.env" -Encoding utf8 -Force
Write-Host "   ✅ Created IMigrate/BoomiToIS-API/.env" -ForegroundColor Green

# Create MuleToIS-API .env
Write-Host "`n📁 Creating IMigrate/MuleToIS-API/.env..." -ForegroundColor Yellow
@"
# MuleToIS-API Configuration

# Anthropic API Key for documentation enhancement (OPTIONAL)
ANTHROPIC_API_KEY=

# RAG System Integration - MUST BE TRUE TO USE RAG AGENT
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010

# Main API URL
MAIN_API_URL=http://localhost:5000

# Port configuration
PORT=5001

# CORS Configuration
CORS_ORIGIN=http://localhost:5173
"@ | Out-File -FilePath "IMigrate\MuleToIS-API\.env" -Encoding utf8 -Force
Write-Host "   ✅ Created IMigrate/MuleToIS-API/.env" -ForegroundColor Green

# Create Main API .env
Write-Host "`n📁 Creating IMigrate/app/.env..." -ForegroundColor Yellow
@"
# Main API Configuration

# Service URLs
BOOMI_API_URL=http://localhost:5003
MULE_API_URL=http://localhost:5001
GEMMA3_API_URL=http://localhost:5002

# RAG System Integration - MUST BE TRUE TO USE RAG AGENT
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010

# Port configuration
PORT=5000

# CORS Configuration
CORS_ORIGIN=http://localhost:5173

# Anthropic API Key (OPTIONAL)
ANTHROPIC_API_KEY=
"@ | Out-File -FilePath "IMigrate\app\.env" -Encoding utf8 -Force
Write-Host "   ✅ Created IMigrate/app/.env" -ForegroundColor Green

Write-Host "`n"+"="*80 -ForegroundColor Cyan
Write-Host "✅ All .env files created successfully!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

Write-Host "`n📋 Configuration Summary:" -ForegroundColor Cyan
Write-Host "   • RAG Generation: ENABLED (USE_RAG_GENERATION=true)" -ForegroundColor Green
Write-Host "   • RAG API URL: http://localhost:5010" -ForegroundColor White
Write-Host "   • Main API Port: 5000" -ForegroundColor White
Write-Host "   • BoomiToIS-API Port: 5003" -ForegroundColor White
Write-Host "   • MuleToIS-API Port: 5001" -ForegroundColor White
Write-Host "   • Frontend URL: http://localhost:5173" -ForegroundColor White

Write-Host "`n⚠️  Note: ANTHROPIC_API_KEY is optional and left blank." -ForegroundColor Yellow
Write-Host "   You can add it later if needed for documentation enhancement.`n" -ForegroundColor Yellow


