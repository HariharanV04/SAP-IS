# Environment Variables Setup Guide

## Required Environment Variables

You need to create `.env` files in the following directories:

### 1. IMigrate/BoomiToIS-API/.env
```bash
# Copy from template
cp IMigrate/BoomiToIS-API/.env.template IMigrate/BoomiToIS-API/.env

# Then edit and set:
ANTHROPIC_API_KEY=your_anthropic_key_here
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
MAIN_API_URL=http://localhost:5000
PORT=5003
CORS_ORIGIN=http://localhost:5173
```

### 2. IMigrate/MuleToIS-API/.env
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
MAIN_API_URL=http://localhost:5000
PORT=5001
CORS_ORIGIN=http://localhost:5173
```

### 3. IMigrate/app/.env
```bash
BOOMI_API_URL=http://localhost:5003
MULE_API_URL=http://localhost:5001
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
PORT=5000
CORS_ORIGIN=http://localhost:5173
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Quick Setup Script (Windows PowerShell)

```powershell
# Create .env files with default values

# BoomiToIS-API
@"
ANTHROPIC_API_KEY=
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
MAIN_API_URL=http://localhost:5000
PORT=5003
CORS_ORIGIN=http://localhost:5173
"@ | Out-File -FilePath "IMigrate\BoomiToIS-API\.env" -Encoding utf8

# MuleToIS-API
@"
ANTHROPIC_API_KEY=
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
MAIN_API_URL=http://localhost:5000
PORT=5001
CORS_ORIGIN=http://localhost:5173
"@ | Out-File -FilePath "IMigrate\MuleToIS-API\.env" -Encoding utf8

# Main API
@"
BOOMI_API_URL=http://localhost:5003
MULE_API_URL=http://localhost:5001
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
PORT=5000
CORS_ORIGIN=http://localhost:5173
ANTHROPIC_API_KEY=
"@ | Out-File -FilePath "IMigrate\app\.env" -Encoding utf8

Write-Host "✅ .env files created! Now edit them to add your API keys."
```

## Important Notes

1. **USE_RAG_GENERATION=true** - This MUST be set to `true` in all three .env files to use RAG agent
2. **RAG_API_URL** - Must point to the RAG API service (default: http://localhost:5010)
3. **ANTHROPIC_API_KEY** - Optional, only needed if you want to use Claude for documentation enhancement
4. All services must use the same CORS_ORIGIN to work with the frontend

## Verification

After creating .env files, verify them:

```bash
# Check if .env files exist
ls IMigrate/BoomiToIS-API/.env
ls IMigrate/MuleToIS-API/.env
ls IMigrate/app/.env

# Verify RAG setting is enabled
grep "USE_RAG_GENERATION" IMigrate/BoomiToIS-API/.env
grep "USE_RAG_GENERATION" IMigrate/MuleToIS-API/.env
grep "USE_RAG_GENERATION" IMigrate/app/.env
```

All three should show: `USE_RAG_GENERATION=true`

