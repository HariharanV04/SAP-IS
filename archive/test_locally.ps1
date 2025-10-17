# PowerShell script to run both backend and frontend locally for testing

Write-Host "=== MuleSoft Documentation Generator Local Testing ===" -ForegroundColor Cyan
Write-Host "This script will start both the Flask backend and React frontend for local testing." -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = Get-Location
$appDir = "$baseDir\mule_cf_deployment\app"
$reactDir = "$baseDir\mule_cf_deployment\project"

# Function to check if a port is in use
function Test-PortInUse {
    param(
        [int]$Port
    )
    $connections = netstat -ano | Select-String -Pattern ".*:$Port\s.*LISTENING"
    return $connections.Count -gt 0
}

# Check for required dependencies
Write-Host "Checking for required dependencies..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.x." -ForegroundColor Red
    exit
}

try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js." -ForegroundColor Red
    exit
}

# Check if the backend port is already in use
if (Test-PortInUse -Port 8080) {
    Write-Host "⚠️ Port 8080 is already in use. The backend may already be running." -ForegroundColor Yellow
    $response = Read-Host "Do you want to continue? (y/n)"
    if ($response -ne "y") {
        exit
    }
}

# Check if the frontend port is already in use
if (Test-PortInUse -Port 5173) {
    Write-Host "⚠️ Port 5173 is already in use. The frontend Vite server may already be running." -ForegroundColor Yellow
    $response = Read-Host "Do you want to continue? (y/n)"
    if ($response -ne "y") {
        exit
    }
}

# Create separate PowerShell jobs for backend and frontend
try {
    # Start the backend
    Write-Host "`n🔧 Starting Flask backend on port 8080..." -ForegroundColor Cyan
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:appDir
        Write-Host "Starting Flask backend at $(Get-Date)" -ForegroundColor Green
        python run_app.py
    }

    # Wait a moment for backend to start
    Start-Sleep -Seconds 3

    # Start the frontend
    Write-Host "`n🚀 Starting React frontend on port 5173..." -ForegroundColor Cyan
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:reactDir
        Write-Host "Starting React frontend at $(Get-Date)" -ForegroundColor Green
        npm run dev
    }

    # Display information to the user
    Write-Host "`n✅ Services started successfully!" -ForegroundColor Green
    Write-Host "🔗 Backend URL: http://localhost:8080" -ForegroundColor White
    Write-Host "🔗 Frontend URL: http://localhost:5173" -ForegroundColor White
    Write-Host "`n⚙️ Press Ctrl+C to stop all services when you're done testing." -ForegroundColor Yellow

    # Wait for the jobs and capture output
    while ($true) {
        $backendOutput = Receive-Job -Job $backendJob
        if ($backendOutput) {
            Write-Host "`n[BACKEND] $backendOutput" -ForegroundColor Cyan
        }

        $frontendOutput = Receive-Job -Job $frontendJob
        if ($frontendOutput) {
            Write-Host "`n[FRONTEND] $frontendOutput" -ForegroundColor Magenta
        }

        Start-Sleep -Seconds 1
    }
}
finally {
    # Clean up jobs when the script is interrupted
    if ($backendJob) {
        Stop-Job -Job $backendJob
        Remove-Job -Job $backendJob -Force
    }
    if ($frontendJob) {
        Stop-Job -Job $frontendJob
        Remove-Job -Job $frontendJob -Force
    }

    Write-Host "`n🛑 Local testing stopped. All services have been terminated." -ForegroundColor Red
}
