@echo off
echo ========================================
echo Starting MuleToIS-API-Gemma3 (Development)
echo ========================================

set FLASK_ENV=development
set PORT=5002
python app.py

pause
