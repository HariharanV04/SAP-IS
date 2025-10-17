# PowerShell script to integrate React frontend with Flask backend
# This script will build the React app and copy the build files to the Flask app's static directory

Write-Host "=== React Frontend Integration with Flask Backend ===" -ForegroundColor Cyan
Write-Host "This script will build the React frontend and integrate it with the Flask backend" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan

# Set the base directory (where this script is located)
$baseDir = $PSScriptRoot
Write-Host "Base directory: $baseDir" -ForegroundColor Gray

# Set paths for React project and Flask app
$reactDir = Join-Path $baseDir "project"
$flaskDir = Join-Path $baseDir "app"
$flaskStaticDir = Join-Path $flaskDir "static"
$flaskTemplatesDir = Join-Path $flaskDir "templates"

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "Node.js detected: $nodeVersion" -ForegroundColor Green
    Write-Host "npm detected: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Node.js and npm are required to build the React application." -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if React directory exists
if (-not (Test-Path $reactDir)) {
    Write-Host "Error: React project directory not found at: $reactDir" -ForegroundColor Red
    exit 1
} else {
    Write-Host "React project found at: $reactDir" -ForegroundColor Green
}

# Check if Flask directory exists
if (-not (Test-Path $flaskDir)) {
    Write-Host "Error: Flask app directory not found at: $flaskDir" -ForegroundColor Red
    exit 1
} else {
    Write-Host "Flask app found at: $flaskDir" -ForegroundColor Green
}

# Create static directory if it doesn't exist
if (-not (Test-Path $flaskStaticDir)) {
    Write-Host "Creating static directory in Flask app..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $flaskStaticDir -Force | Out-Null
}

# Create templates directory if it doesn't exist
if (-not (Test-Path $flaskTemplatesDir)) {
    Write-Host "Creating templates directory in Flask app..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $flaskTemplatesDir -Force | Out-Null
}

# Step 1: Build the React application
Write-Host "Building React application..." -ForegroundColor Cyan
Set-Location $reactDir

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path (Join-Path $reactDir "node_modules"))) {
    Write-Host "Installing React dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install React dependencies." -ForegroundColor Red
        exit 1
    }
}

# Update proxy in package.json for local development
Write-Host "Updating proxy in package.json..." -ForegroundColor Yellow
$packageJsonPath = Join-Path $reactDir "package.json"
$packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
if (-not ($packageJson.proxy)) {
    $packageJson | Add-Member -NotePropertyName "proxy" -NotePropertyValue "http://localhost:5000"
    $packageJson | ConvertTo-Json -Depth 100 | Set-Content $packageJsonPath
    Write-Host "Added proxy to package.json" -ForegroundColor Green
} elseif ($packageJson.proxy -ne "http://localhost:5000") {
    $packageJson.proxy = "http://localhost:5000"
    $packageJson | ConvertTo-Json -Depth 100 | Set-Content $packageJsonPath
    Write-Host "Updated proxy in package.json" -ForegroundColor Green
}

# Build React app
Write-Host "Building React app for production..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to build React application." -ForegroundColor Red
    exit 1
}

# Step 2: Copy the build files to Flask's static directory
Write-Host "Copying React build to Flask static directory..." -ForegroundColor Cyan
$reactBuildDir = Join-Path $reactDir "dist"
if (-not (Test-Path $reactBuildDir)) {
    $reactBuildDir = Join-Path $reactDir "build" # Alternative build directory name
    if (-not (Test-Path $reactBuildDir)) {
        Write-Host "Error: React build directory not found." -ForegroundColor Red
        Write-Host "Expected at: $reactBuildDir" -ForegroundColor Yellow
        exit 1
    }
}

# Remove existing files in the static directory
Get-ChildItem -Path $flaskStaticDir -Recurse | Remove-Item -Force -Recurse

# Copy all build files to the static directory
Copy-Item -Path "$reactBuildDir\*" -Destination $flaskStaticDir -Recurse -Force
Write-Host "React build files copied to Flask static directory" -ForegroundColor Green

# Step 3: Create a Flask route to serve the React app
Write-Host "Updating Flask app to serve React app..." -ForegroundColor Cyan

# Define the content to look for in app.py
$serveReactAppFunction = @"
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
"@

# Check if Flask app already has the route to serve React app
$appPyPath = Join-Path $flaskDir "app.py"
$appPyContent = Get-Content $appPyPath -Raw

if ($appPyContent -match "def serve\(path\):") {
    Write-Host "Flask app already has route to serve React app" -ForegroundColor Yellow
} else {
    # Add the route to the end of app.py (before the if __name__ == '__main__': section)
    if ($appPyContent -match "if __name__ == '__main__':") {
        $updatedContent = $appPyContent -replace "if __name__ == '__main__':", "$serveReactAppFunction`n`nif __name__ == '__main__':"
        Set-Content -Path $appPyPath -Value $updatedContent
        Write-Host "Added route to serve React app in Flask app.py" -ForegroundColor Green
    } else {
        # If the if __name__ block is not found, add to the end of the file
        Add-Content -Path $appPyPath -Value "`n$serveReactAppFunction"
        Write-Host "Added route to serve React app in Flask app.py" -ForegroundColor Green
    }
}

# Step 4: Create a JSON manifest for API routes
Write-Host "Creating API routes manifest..." -ForegroundColor Cyan
$apiRoutesManifest = @{
    "api_routes" = @(
        @{
            "route" = "/api/generate-docs"
            "methods" = @("POST")
            "roles" = @("user", "admin")
        },
        @{
            "route" = "/api/jobs"
            "methods" = @("GET")
            "roles" = @("user", "admin")
        },
        @{
            "route" = "/api/jobs/<job_id>"
            "methods" = @("GET")
            "roles" = @("user", "admin")
        },
        @{
            "route" = "/api/docs/<job_id>/<file_type>"
            "methods" = @("GET")
            "roles" = @("user", "admin")
        }
    )
}

$apiRoutesManifestPath = Join-Path $flaskDir "api_routes.json"
$apiRoutesManifest | ConvertTo-Json -Depth 10 | Set-Content $apiRoutesManifestPath
Write-Host "API routes manifest created at: $apiRoutesManifestPath" -ForegroundColor Green

# Step 5: Update Flask app configuration to serve static files correctly
Write-Host "Ensuring Flask app is configured to serve static files..." -ForegroundColor Cyan

# Check if static_url_path is set correctly
if (-not ($appPyContent -match "static_url_path='/static'")) {
    # Add the static_url_path configuration to the Flask app initialization
    $appPattern = "app = Flask\(__name__\)"
    $appReplacement = "app = Flask(__name__, static_url_path='/static', static_folder='static')"
    $updatedContent = $appPyContent -replace $appPattern, $appReplacement
    Set-Content -Path $appPyPath -Value $updatedContent
    Write-Host "Updated Flask app static configuration" -ForegroundColor Green
}

Write-Host "Integration completed successfully!" -ForegroundColor Green
Write-Host "To run the integrated app locally:" -ForegroundColor Cyan
Write-Host "  1. Navigate to the Flask app directory: cd $flaskDir" -ForegroundColor Gray
Write-Host "  2. Run the Flask app: python run_app.py" -ForegroundColor Gray
Write-Host "  3. Open http://localhost:5000 in your browser" -ForegroundColor Gray
Write-Host "" -ForegroundColor White
Write-Host "To deploy to Cloud Foundry:" -ForegroundColor Cyan
Write-Host "  1. Navigate to the base directory: cd $baseDir" -ForegroundColor Gray
Write-Host "  2. Run the deployment script: .\deploy_with_debug.ps1" -ForegroundColor Gray
Write-Host "" -ForegroundColor White
Write-Host "Note: If you make changes to the React code, run this script again to rebuild and update the Flask app." -ForegroundColor Yellow 