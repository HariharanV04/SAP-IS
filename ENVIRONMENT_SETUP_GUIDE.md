# Environment Setup Guide

This guide explains how to set up environment variables for both local development and Cloud Foundry deployment.

## 🚀 Cloud Foundry Environment Setup

We've created scripts to handle the special characters and escaping issues when setting CF environment variables.

### Option 1: Python Script (Recommended)

The Python script handles all edge cases and provides better error handling:

```bash
# Navigate to the IMigrate directory
cd IMigrate

# Run the Python setup script
python setup_cf_env.py
```

**Features:**
- ✅ Handles special characters properly
- ✅ Checks CF CLI installation and login status
- ✅ Provides progress feedback
- ✅ Option to restart applications automatically
- ✅ Environment variable verification
- ✅ Cross-platform compatible

### Option 2: Windows Batch Script

For Windows users who prefer batch files:

```cmd
cd IMigrate
setup_cf_env.bat
```

### Option 3: Manual PowerShell (Use Separate Commands)

If you need to set individual variables:

```powershell
# Set variables one by one to avoid escaping issues
cf set-env it-resonance-main-api SAP_BTP_CLIENT_ID "sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895|it!b410334"
cf set-env it-resonance-main-api SAP_BTP_CLIENT_SECRET "5813ca83-4ba6-4231-96e1-1a48a80eafec`$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w="
# ... etc
```

## 🏠 Local Development Environment Setup

### Quick Setup Script

```bash
cd IMigrate
python setup-local-env.ps1
```

This will copy the environment template files to the correct locations:

### Manual Setup

1. **Copy Environment Files:**
   ```bash
   # Main API
   cp environment-setup/main-api.env app/.env
   
   # MuleToIS API  
   cp environment-setup/mulesoft-api.env MuleToIS-API/.env
   
   # BoomiToIS API
   cp environment-setup/boomi-api.env BoomiToIS-API/.env
   
   # Frontend
   cp environment-setup/frontend.env IFA-Project/frontend/.env
   ```

2. **Update API Keys:**
   Edit each `.env` file and replace `your-key-here` with your actual API keys.

## 🔑 Required API Keys

### Anthropic Claude API
- Required for: Main API, MuleToIS API, BoomiToIS API
- Get from: https://console.anthropic.com/
- Set in: `ANTHROPIC_API_KEY`

### RunPod API (Optional - for Gemma-3)
- Required for: Gemma-3 API only
- Get from: https://runpod.io/
- Set in: `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID`

## 🏢 SAP BTP Credentials

The SAP BTP credentials are already configured with working values:

- **Client ID:** `sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895|it!b410334`
- **Client Secret:** `5813ca83-4ba6-4231-96e1-1a48a80eafec$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w=`
- **OAuth URL:** `https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token`
- **Tenant URL:** `https://itr-internal-2hco92jx.it-cpi034.cfapps.us10-002.hana.ondemand.com`
- **Default Package:** `ConversionPackages`

## 🔍 Verification

### Check CF Environment Variables
```bash
cf env it-resonance-main-api
cf env it-resonance-mule-api
cf env it-resonance-boomi-api
```

### Test Local Setup
```bash
# Test MuleToIS API
cd MuleToIS-API
python app.py

# Test unified deployment (in another terminal)
cd ..
python test_unified_deployment.py
```

## 🔄 Restart Applications

After setting environment variables, restart all CF applications:

```bash
cf restart it-resonance-main-api
cf restart it-resonance-mule-api  
cf restart it-resonance-boomi-api
cf restart it-resonance-gemma3-api
cf restart ifa-project
```

## 🐛 Troubleshooting

### PowerShell Special Character Issues
- **Problem:** `&&` not recognized, special characters in environment values
- **Solution:** Use the Python script instead of PowerShell

### CF CLI Not Found
- **Problem:** `cf` command not recognized
- **Solution:** Install CF CLI from https://github.com/cloudfoundry/cli/releases

### Not Logged In to CF
- **Problem:** CF commands fail with authentication error
- **Solution:** Run `cf login` first

### Environment Variables Not Applied
- **Problem:** Applications don't see new environment variables
- **Solution:** Restart the applications with `cf restart <app-name>`

## 📂 File Structure

```
IMigrate/
├── setup_cf_env.py              # Python script for CF env setup
├── setup_cf_env.bat             # Windows batch script for CF env setup  
├── setup-local-env.ps1          # PowerShell script for local env setup
├── environment-setup/           # Template environment files
│   ├── main-api.env
│   ├── mulesoft-api.env
│   ├── boomi-api.env
│   └── frontend.env
└── ENVIRONMENT_SETUP_GUIDE.md   # This file
```

## ✅ Success Indicators

Your environment is properly set up when:

1. ✅ All CF applications show environment variables with `cf env <app-name>`
2. ✅ MuleToIS API starts without errors on port 5001
3. ✅ Unified deployment test passes: `python test_unified_deployment.py`
4. ✅ Frontend can connect to all backend APIs
5. ✅ SAP BTP deployment works from the frontend deploy button





















