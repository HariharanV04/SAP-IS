# PowerShell script to test the production build of the frontend with the backend
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "       Testing Production Build with Backend API         " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = Get-Location
$appDir = "$baseDir\mule_cf_deployment\app"
$projectDir = "$baseDir\mule_cf_deployment\project"

# Function to check if a port is in use
function Test-PortInUse {
    param(
        [int]$Port
    )
    $connections = netstat -ano | Select-String -Pattern ".*:$Port\s.*LISTENING"
    return $connections.Count -gt 0
}

# Check if the backend is running on port 5000
$backendPort = $null
if (Test-PortInUse -Port 5000) {
    Write-Host "✅ Backend detected on port 5000" -ForegroundColor Green
    $backendPort = 5000
} elseif (Test-PortInUse -Port 8080) {
    Write-Host "✅ Backend detected on port 8080" -ForegroundColor Green
    $backendPort = 8080
} else {
    Write-Host "❌ Backend not detected on port 5000 or 8080" -ForegroundColor Red
    $startBackend = Read-Host "Do you want to start the backend on port 5000? (y/n)"
    if ($startBackend -eq "y") {
        Write-Host "Starting Flask backend..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "cd '$appDir'; python run_app.py" -NoNewWindow
        Start-Sleep -Seconds 5
        if (Test-PortInUse -Port 5000) {
            Write-Host "✅ Backend started on port 5000" -ForegroundColor Green
            $backendPort = 5000
        } else {
            Write-Host "❌ Failed to start backend" -ForegroundColor Red
            exit
        }
    } else {
        Write-Host "Please start the backend manually and run this script again." -ForegroundColor Yellow
        exit
    }
}

# Update the environment configuration
Write-Host ""
Write-Host "Updating environment configuration for production test..." -ForegroundColor Yellow
$envTestContent = @"
# Test environment for production build
VITE_API_URL=http://localhost:$backendPort/api
"@
Set-Content -Path "$projectDir\.env.production.local" -Value $envTestContent -Force
Write-Host "✅ Created .env.production.local with backend URL: http://localhost:$backendPort/api" -ForegroundColor Green

# Build the production version
Write-Host ""
Write-Host "Building production version..." -ForegroundColor Yellow
Set-Location $projectDir
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build production version" -ForegroundColor Red
    exit
}
Write-Host "✅ Production build successful" -ForegroundColor Green

# Choose a port for serving the frontend
$availablePorts = @(4500, 5500, 6000, 7000, 8500)
$frontendPort = $null
foreach ($port in $availablePorts) {
    if (-not (Test-PortInUse -Port $port)) {
        $frontendPort = $port
        Write-Host "✅ Selected port $frontendPort for frontend" -ForegroundColor Green
        break
    }
}

if ($null -eq $frontendPort) {
    Write-Host "❌ Could not find an available port for the frontend" -ForegroundColor Red
    exit
}

# Start serving the production build
Write-Host ""
Write-Host "Starting production build server on port $frontendPort..." -ForegroundColor Yellow
Write-Host "Your backend is running on port $backendPort" -ForegroundColor Yellow
Write-Host ""
Write-Host "After the server starts, open these URLs:" -ForegroundColor Cyan
Write-Host "1. Application: http://localhost:$frontendPort" -ForegroundColor White
Write-Host "2. API Test Tool: http://localhost:$frontendPort/api_test.html" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server when you're done testing" -ForegroundColor Yellow
Write-Host ""

# Copy the API test file to the dist directory
Copy-Item "$baseDir\mule_cf_deployment\api_test.html" -Destination "$projectDir\dist\api_test.html" -Force
Write-Host "✅ Copied API test tool to dist directory" -ForegroundColor Green

# Start the server
Set-Location $projectDir
npx serve -s dist -l $frontendPort 