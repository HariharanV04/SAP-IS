@echo off
echo ========================================
echo SAP CPI API Test Tool
echo ========================================

cd /d "%~dp0..\.."

if "%1"=="" (
    echo Usage: test-sap-cpi.bat [command] [options]
    echo.
    echo Commands:
    echo   all                                    - Run all API tests
    echo   list                                   - List all integration artifacts
    echo   get [artifact-id] [version]           - Get specific artifact details
    echo   download [artifact-id] [version] [file] - Download artifact as ZIP
    echo.
    echo Examples:
    echo   test-sap-cpi.bat all
    echo   test-sap-cpi.bat list
    echo   test-sap-cpi.bat get SFTP_2_IDOC_MigrateFlow 1.0.1
    echo   test-sap-cpi.bat download SFTP_2_IDOC_MigrateFlow 1.0.1 artifact.zip
    echo.
    set /p choice="Press Enter to run all tests, or Ctrl+C to cancel: "
    python deployment\scripts\sap_cpi_api_test.py
    goto :end
)

if /i "%1"=="all" (
    echo 🧪 Running all SAP CPI API tests...
    python deployment\scripts\sap_cpi_api_test.py
    goto :end
)

if /i "%1"=="list" (
    echo 📋 Listing all integration artifacts...
    python deployment\scripts\sap_cpi_api_test.py --list-only
    goto :end
)

if /i "%1"=="get" (
    if "%2"=="" (
        echo ❌ Artifact ID required for get command
        echo Usage: test-sap-cpi.bat get [artifact-id] [version]
        goto :error
    )
    
    if "%3"=="" (
        echo 📄 Getting artifact details for: %2 (default version)
        python deployment\scripts\sap_cpi_api_test.py --get-only --artifact-id %2
    ) else (
        echo 📄 Getting artifact details for: %2 (v%3)
        python deployment\scripts\sap_cpi_api_test.py --get-only --artifact-id %2 --version %3
    )
    goto :end
)

if /i "%1"=="download" (
    if "%2"=="" (
        echo ❌ Artifact ID required for download command
        echo Usage: test-sap-cpi.bat download [artifact-id] [version] [file]
        goto :error
    )
    
    if "%4"=="" (
        echo ❌ Output file required for download command
        echo Usage: test-sap-cpi.bat download [artifact-id] [version] [file]
        goto :error
    )
    
    if "%3"=="" (
        echo 💾 Downloading artifact: %2 (default version) to %4
        python deployment\scripts\sap_cpi_api_test.py --artifact-id %2 --download %4
    ) else (
        echo 💾 Downloading artifact: %2 (v%3) to %4
        python deployment\scripts\sap_cpi_api_test.py --artifact-id %2 --version %3 --download %4
    )
    goto :end
)

echo ❌ Unknown command: %1
echo Run 'test-sap-cpi.bat' without parameters to see available commands.
goto :error

:end
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Command failed!
    pause
    exit /b 1
)

echo.
echo ✅ Command completed successfully!
pause
exit /b 0

:error
echo.
pause
exit /b 1
