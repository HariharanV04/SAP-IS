@echo off
echo ========================================
echo Push Codebase to New GitHub Repository
echo ========================================

if "%1"=="" (
    echo Usage: push-to-github.bat [repository-url]
    echo.
    echo Example:
    echo   push-to-github.bat https://github.com/yourusername/ifa-project.git
    echo.
    echo Or with SSH:
    echo   push-to-github.bat git@github.com:yourusername/ifa-project.git
    echo.
    pause
    exit /b 1
)

set REPO_URL=%1

cd /d "%~dp0..\.."

echo 🔍 Checking if this is already a Git repository...
if not exist ".git" (
    echo 📦 Initializing new Git repository...
    git init
    echo   ✅ Git repository initialized
) else (
    echo ✅ Git repository already exists
)

echo.
echo 🔧 Setting up Git configuration...
git config user.name "Deepan"
git config user.email "deepan@itresonance.com"

echo.
echo 📝 Adding all files to Git...
git add .

echo.
echo 📊 Checking what will be committed...
git status

echo.
echo 💾 Creating initial commit...
git commit -m "Initial commit: IFA Project - Complete deployment automation system

Features:
- Main API for documentation generation
- MuleToIS API for MuleSoft to SAP Integration Suite
- BoomiToIS API for Boomi to SAP Integration Suite  
- React frontend with Vite
- Complete deployment automation
- CI/CD pipeline with GitHub Actions
- Local development environment setup
- Cloud Foundry production deployment

Components:
- Python Flask APIs with OAuth integration
- React frontend with platform-aware routing
- SAP Integration Suite deployment automation
- Environment management and configuration
- Comprehensive documentation and guides"

if %ERRORLEVEL% neq 0 (
    echo ❌ Commit failed!
    pause
    exit /b 1
)

echo.
echo 🔗 Adding remote repository...
git remote add origin %REPO_URL%

echo.
echo 🚀 Pushing to GitHub...
echo This may take a few minutes for the initial push...
git push -u origin main

if %ERRORLEVEL% neq 0 (
    echo.
    echo ⚠️ Push failed. This might be because:
    echo 1. The repository already has content
    echo 2. Authentication issues
    echo 3. Network connectivity
    echo.
    echo 🔧 Trying force push (use with caution)...
    set /p confirm="Force push? This will overwrite remote repository (y/N): "
    if /i "%confirm%"=="y" (
        git push -u origin main --force
    ) else (
        echo Push cancelled.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo ✅ Successfully pushed to GitHub!
echo ========================================
echo.
echo 🌐 Repository URL: %REPO_URL%
echo.
echo 📋 Next steps:
echo 1. Go to your GitHub repository
echo 2. Set up GitHub Secrets for CI/CD:
echo    - CF_ORG
echo    - CF_SPACE
echo    - CF_USERNAME  
echo    - CF_PASSWORD
echo 3. Test the CI/CD pipeline
echo.
echo 🔧 Setup CI/CD:
echo   deployment\scripts\get-cf-details.bat
echo.
pause
