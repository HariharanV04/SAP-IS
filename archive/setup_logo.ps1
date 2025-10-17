# Setup Logo Script for MuleSoft Docs Generator
# This script helps set up the directory structure for your company logo.
param (
    [string]$logoPath = "",
    [string]$smallLogoPath = ""
)

$baseDir = $PSScriptRoot
$projectDir = Join-Path $baseDir "project"
$imageDir = Join-Path $projectDir "public\static\images"

# Function to display colorful messages
function Write-ColoredMessage {
    param (
        [string]$message,
        [string]$type = "info"
    )

    switch ($type) {
        "success" { Write-Host $message -ForegroundColor Green }
        "warning" { Write-Host $message -ForegroundColor Yellow }
        "error" { Write-Host $message -ForegroundColor Red }
        default { Write-Host $message -ForegroundColor Cyan }
    }
}

# Function to check if directory exists, create if not
function Ensure-DirectoryExists {
    param (
        [string]$dir
    )

    if (-not (Test-Path $dir)) {
        Write-ColoredMessage "Creating directory: $dir" "info"
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
        Write-ColoredMessage "Directory created successfully." "success"
    }
    else {
        Write-ColoredMessage "Directory already exists: $dir" "info"
    }
}

# Main script execution
Write-ColoredMessage "===== MuleSoft Docs Generator Logo Setup =====`n" "info"

# Check project directory
if (-not (Test-Path $projectDir)) {
    Write-ColoredMessage "Error: Project directory not found at $projectDir" "error"
    exit 1
}

# Create image directory structure
Write-ColoredMessage "Setting up logo directory structure..." "info"
Ensure-DirectoryExists $imageDir

# Handle logo files
if ($logoPath -and (Test-Path $logoPath)) {
    $destLogo = Join-Path $imageDir "company-logo.png"
    Copy-Item -Path $logoPath -Destination $destLogo -Force
    Write-ColoredMessage "Main logo copied to: $destLogo" "success"
}
else {
    Write-ColoredMessage "`nTo add your main company logo:" "warning"
    Write-ColoredMessage "1. Save your logo file as 'company-logo.png'" "warning"
    Write-ColoredMessage "2. Copy it to: $imageDir" "warning"
    Write-ColoredMessage "3. Recommended size: 180px width × 48px height`n" "warning"
}

if ($smallLogoPath -and (Test-Path $smallLogoPath)) {
    $destSmallLogo = Join-Path $imageDir "company-logo-small.png"
    Copy-Item -Path $smallLogoPath -Destination $destSmallLogo -Force
    Write-ColoredMessage "Small logo copied to: $destSmallLogo" "success"
}
else {
    Write-ColoredMessage "`nTo add your small company logo:" "warning"
    Write-ColoredMessage "1. Save your small logo file as 'company-logo-small.png'" "warning"
    Write-ColoredMessage "2. Copy it to: $imageDir" "warning"
    Write-ColoredMessage "3. Recommended size: 120px width × 32px height`n" "warning"
}

Write-ColoredMessage "`n===== Setup Complete =====`n" "success"
Write-ColoredMessage "After adding your logo files, run the application with 'npm run dev'" "info"
Write-ColoredMessage "For detailed instructions, see the LOGO_INSTRUCTIONS.md file." "info" 