# PowerShell Script to Start All Services for IMigrate + RAG Integration
# This script opens multiple terminals and starts each service

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "Starting ALL Services for IMigrate + RAG Integration" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

Write-Host "`n📋 This will open 5 terminal windows:" -ForegroundColor Yellow
Write-Host "   1. RAG API Service (Port 5010)" -ForegroundColor White
Write-Host "   2. IMigrate Main API (Port 5000)" -ForegroundColor White
Write-Host "   3. BoomiToIS-API (Port 5003)" -ForegroundColor White
Write-Host "   4. MuleToIS-API (Port 5001)" -ForegroundColor White
Write-Host "   5. Frontend (Port 5173)" -ForegroundColor White

Write-Host "`n⚠️  Important: Keep all terminal windows open!" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C in any terminal to stop that service.`n" -ForegroundColor Yellow

$response = Read-Host "Continue? (Y/N)"
if ($response -ne "Y" -and $response -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Red
    exit
}

Write-Host "`n🚀 Starting services..." -ForegroundColor Green

# Terminal 1: RAG API Service
Write-Host "`n📡 Starting RAG API Service..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host '  RAG API SERVICE (Port 5010)' -ForegroundColor Cyan; Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; python rag_api_service.py"

Start-Sleep -Seconds 5

# Terminal 2: Main API
Write-Host "📡 Starting Main API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host '  MAIN API (Port 5000)' -ForegroundColor Cyan; Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; cd IMigrate\app; python app.py"

Start-Sleep -Seconds 3

# Terminal 3: BoomiToIS-API
Write-Host "📡 Starting BoomiToIS-API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host '  BOOMI-TO-IS API (Port 5003)' -ForegroundColor Cyan; Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; cd IMigrate\BoomiToIS-API; python app.py"

Start-Sleep -Seconds 3

# Terminal 4: MuleToIS-API
Write-Host "📡 Starting MuleToIS-API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host '  MULE-TO-IS API (Port 5001)' -ForegroundColor Cyan; Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; cd IMigrate\MuleToIS-API; python app.py"

Start-Sleep -Seconds 3

# Terminal 5: Frontend
Write-Host "📡 Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host '  FRONTEND (Port 5173)' -ForegroundColor Cyan; Write-Host '═════════════════════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; cd IMigrate\IFA-Project\frontend; npm run dev"

Write-Host "`n"+"="*80 -ForegroundColor Green
Write-Host "✅ All services are starting!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Green

Write-Host "`n📊 Service URLs:" -ForegroundColor Cyan
Write-Host "   • RAG API:        http://localhost:5010/api/health" -ForegroundColor White
Write-Host "   • Main API:       http://localhost:5000/api/health" -ForegroundColor White
Write-Host "   • BoomiToIS-API:  http://localhost:5003/api/health" -ForegroundColor White
Write-Host "   • MuleToIS-API:   http://localhost:5001/api/health" -ForegroundColor White
Write-Host "   • Frontend:       http://localhost:5173" -ForegroundColor White

Write-Host "`n⏰ Wait 30 seconds for all services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "`n🔍 Checking service health..." -ForegroundColor Cyan

# Check each service
$services = @(
    @{Name="RAG API"; URL="http://localhost:5010/api/health"},
    @{Name="Main API"; URL="http://localhost:5000/api/health"},
    @{Name="BoomiToIS-API"; URL="http://localhost:5003/api/health"},
    @{Name="MuleToIS-API"; URL="http://localhost:5001/api/health"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $($service.Name) is running" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "   ⚠️  $($service.Name) may still be starting..." -ForegroundColor Yellow
    }
}

Write-Host "`n🌐 Opening frontend in browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"

Write-Host "`n"+"="*80 -ForegroundColor Green
Write-Host "✅ SYSTEM READY!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Green

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. The frontend should open in your browser" -ForegroundColor White
Write-Host "   2. Upload a Boomi/MuleSoft document" -ForegroundColor White
Write-Host "   3. Wait for documentation generation" -ForegroundColor White
Write-Host "   4. Click 'Generate iFlow' button" -ForegroundColor White
Write-Host "   5. Check BoomiToIS-API terminal for RAG integration logs" -ForegroundColor White
Write-Host "   6. Look for 'Using RAG API for iFlow generation'" -ForegroundColor White

Write-Host "`nWARNING: To stop all services: Close each terminal window or press Ctrl+C" -ForegroundColor Yellow

