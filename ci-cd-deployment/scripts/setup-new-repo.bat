@echo off
echo ========================================
echo Complete New Repository Setup
echo ========================================

echo This script will:
echo 1. Clean up the codebase
echo 2. Prepare for Git
echo 3. Push to new GitHub repository
echo 4. Set up CI/CD instructions
echo.

if "%1"=="" (
    echo Usage: setup-new-repo.bat [repository-url]
    echo.
    echo Example:
    echo   setup-new-repo.bat https://github.com/yourusername/ifa-project.git
    echo.
    echo Steps to get repository URL:
    echo 1. Go to https://github.com
    echo 2. Click "+" → "New repository"
    echo 3. Name: ifa-project
    echo 4. Description: IFA Project - Integration Flow Automation
    echo 5. Create repository
    echo 6. Copy the repository URL
    echo.
    pause
    exit /b 1
)

set REPO_URL=%1

echo 🚀 Starting complete repository setup...
echo Repository URL: %REPO_URL%
echo.

set /p confirm="Continue with repository setup? (y/N): "
if /i not "%confirm%"=="y" (
    echo Setup cancelled.
    exit /b 0
)

echo.
echo ========================================
echo Step 1: Preparing Repository
echo ========================================
call "%~dp0prepare-repo.bat"

if %ERRORLEVEL% neq 0 (
    echo ❌ Repository preparation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Pushing to GitHub
echo ========================================
call "%~dp0push-to-github.bat" %REPO_URL%

if %ERRORLEVEL% neq 0 (
    echo ❌ GitHub push failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 3: CI/CD Setup Instructions
echo ========================================

echo 🔐 Getting your Cloud Foundry details for GitHub Secrets...
call "%~dp0get-cf-details.bat"

echo.
echo ========================================
echo ✅ Repository Setup Complete!
echo ========================================
echo.
echo 🌐 Your new repository: %REPO_URL%
echo.
echo 📋 What's been set up:
echo   ✅ Complete codebase pushed to GitHub
echo   ✅ Deployment automation scripts
echo   ✅ CI/CD pipeline configuration
echo   ✅ Local development environment
echo   ✅ Production deployment scripts
echo.
echo 🔧 Next steps:
echo 1. Go to your GitHub repository
echo 2. Add the GitHub Secrets shown above
echo 3. Test the deployment pipeline
echo.
echo 🚀 Quick commands:
echo   Local setup:    deployment\scripts\deploy-local.bat
echo   Start local:    deployment\scripts\start-local.bat
echo   Deploy prod:    deployment\scripts\deploy-production.bat
echo   Management:     deployment\scripts\manage-env.bat
echo.
pause
