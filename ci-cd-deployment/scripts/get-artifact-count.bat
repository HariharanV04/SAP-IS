@echo off
echo ========================================
echo SAP CPI Artifact Count Tool
echo ========================================

cd /d "%~dp0..\.."

if "%1"=="" (
    echo Usage: get-artifact-count.bat [options]
    echo.
    echo Examples:
    echo   get-artifact-count.bat                                    - Get count for SFTP_2_IDOC_MigrateFlow
    echo   get-artifact-count.bat --artifact-id MyFlow              - Get count for specific artifact
    echo   get-artifact-count.bat --details                         - Get detailed information
    echo   get-artifact-count.bat --resources                       - List all resources
    echo   get-artifact-count.bat --list-all                        - List all artifacts
    echo.
    echo Default artifact: SFTP_2_IDOC_MigrateFlow (v1.0.1)
    echo.
    set /p choice="Press Enter to run with default settings, or type 'list' to see all artifacts: "
    if /i "%choice%"=="list" (
        python deployment\scripts\get_artifact_count.py --list-all
    ) else (
        python deployment\scripts\get_artifact_count.py
    )
) else (
    python deployment\scripts\get_artifact_count.py %*
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Script failed!
    pause
    exit /b 1
)

echo.
echo ✅ Script completed successfully!
pause
