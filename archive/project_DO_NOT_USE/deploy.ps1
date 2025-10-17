# PowerShell script to deploy React frontend

Write-Host "Building React application for production..." -ForegroundColor Green
npm run build

Write-Host "Copying build files to deployment directory..." -ForegroundColor Green
Copy-Item -Path "dist\*" -Destination "C:\Users\Deepan\OneDrive\Documents\DheepLearningNew\66_FINAL MULE_TO_IS\mule_cf_deployment\frontend" -Recurse -Force

Write-Host "Frontend build completed and copied to deployment directory." -ForegroundColor Green
Write-Host "To deploy to Cloud Foundry:" -ForegroundColor Yellow
Write-Host "cd C:\Users\Deepan\OneDrive\Documents\DheepLearningNew\66_FINAL MULE_TO_IS\mule_cf_deployment\frontend" -ForegroundColor White
Write-Host "cf push -f manifest.yml" -ForegroundColor White
