# Complete Integration Guide - IMigrate + RAG System

## 🎯 Overview

This guide provides complete step-by-step instructions to set up and run the fully integrated IMigrate + RAG system.

**What we've integrated:**
- ✅ IMigrate frontend and backend (unchanged UI/UX)
- ✅ RAG AI Agent for intelligent iFlow generation
- ✅ Automatic fallback to template-based generation
- ✅ Comprehensive logging and error handling
- ✅ Proper file path management

---

## 📦 Step 1: Install Dependencies

### **1.1 Python Dependencies**

```powershell
# Root directory (RAG system)
pip install -r requirements.txt

# IMigrate Main API
cd IMigrate/app
pip install -r requirements.txt
cd ../..

# BoomiToIS-API
cd IMigrate/BoomiToIS-API
pip install -r requirements_essential.txt
cd ../..

# MuleToIS-API
cd IMigrate/MuleToIS-API
pip install -r requirements.txt
cd ../..
```

### **1.2 Frontend Dependencies**

```powershell
cd IMigrate/IFA-Project/frontend
npm install
cd ../../..
```

---

## ⚙️ Step 2: Setup Environment Variables

### **Option A: Quick Setup (Recommended)**

```powershell
# Run the PowerShell script
.\setup_env_files.ps1
```

This creates `.env` files with:
- `USE_RAG_GENERATION=true` (RAG enabled)
- `RAG_API_URL=http://localhost:5010`
- All proper port configurations

### **Option B: Manual Setup**

Create these three `.env` files:

**IMigrate/BoomiToIS-API/.env:**
```
ANTHROPIC_API_KEY=
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
MAIN_API_URL=http://localhost:5000
PORT=5003
CORS_ORIGIN=http://localhost:5173
```

**IMigrate/MuleToIS-API/.env:**
```
ANTHROPIC_API_KEY=
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
MAIN_API_URL=http://localhost:5000
PORT=5001
CORS_ORIGIN=http://localhost:5173
```

**IMigrate/app/.env:**
```
BOOMI_API_URL=http://localhost:5003
MULE_API_URL=http://localhost:5001
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
PORT=5000
CORS_ORIGIN=http://localhost:5173
ANTHROPIC_API_KEY=
```

---

## 🧪 Step 3: Test RAG API Independently

Before starting everything, test the RAG API alone:

```powershell
# Terminal 1: Start RAG API
python rag_api_service.py
```

Wait for: `RAG API SERVICE READY`

```powershell
# Terminal 2: Run tests
python test_rag_api.py
```

**Expected Results:**
- ✅ Health check passes
- ✅ Simple iFlow generated
- ✅ Markdown-based generation works
- ✅ Files created in `component_metadata/` and `generated_packages/`

If tests fail, check:
1. Neo4j credentials in `config.py`
2. OpenAI API key in `config.py`
3. No port conflicts on 5010

---

## 🚀 Step 4: Start All Services

### **Option A: Automated Start (Recommended)**

```powershell
.\START_ALL_SERVICES.ps1
```

This opens 5 terminal windows and starts everything automatically.

### **Option B: Manual Start**

**Terminal 1: RAG API Service**
```powershell
python rag_api_service.py
```
Wait for: `Running on http://0.0.0.0:5010`

**Terminal 2: Main API**
```powershell
cd IMigrate/app
python app.py
```
Wait for: `Running on http://localhost:5000`

**Terminal 3: BoomiToIS-API**
```powershell
cd IMigrate/BoomiToIS-API
python app.py
```
Wait for: `Running on http://localhost:5003`

**Terminal 4: MuleToIS-API**
```powershell
cd IMigrate/MuleToIS-API
python app.py
```
Wait for: `Running on http://localhost:5001`

**Terminal 5: Frontend**
```powershell
cd IMigrate/IFA-Project/frontend
npm run dev
```
Wait for: `Local: http://localhost:5173`

---

## ✅ Step 5: Verify System is Running

### **5.1 Check Health Endpoints**

```powershell
# RAG API
curl http://localhost:5010/api/health

# Main API
curl http://localhost:5000/api/health

# BoomiToIS-API
curl http://localhost:5003/api/health

# MuleToIS-API
curl http://localhost:5001/api/health
```

All should return `{"status": "ok"}`

### **5.2 Check Frontend**

Open browser: `http://localhost:5173`

You should see the IMigrate interface.

---

## 🧪 Step 6: End-to-End Test

### **Test Flow:**

1. **Upload Document**
   - Go to `http://localhost:5173`
   - Click "Upload" or "Generate iFlow"
   - Select a Boomi/MuleSoft XML or ZIP file
   - Click "Upload"

2. **Documentation Generation**
   - Wait for document processing
   - Documentation will be generated automatically
   - Check Main API terminal for progress

3. **Generate iFlow**
   - Click "Generate iFlow" button
   - **Watch BoomiToIS-API terminal**
   - Look for these log messages:

```
================================================================================
🔧 iFlow Generation Configuration:
   RAG Generation Enabled: True
   RAG API URL: http://localhost:5010
   Job ID: ...
   iFlow Name: ...
================================================================================
🚀 Using RAG API for iFlow generation
📡 Calling: http://localhost:5010/api/generate-iflow-from-markdown
```

4. **Verify RAG is Called**
   - **RAG API terminal** should show:
```
================================================================================
🚀 RAG API: Received iFlow generation request
================================================================================
📝 iFlow Name: ...
🔑 Job ID: ...
```

5. **Check Output**
   - Metadata saved to: `component_metadata/iflow_components_TIMESTAMP.json`
   - Package saved to: `generated_packages/PACKAGE_NAME.zip`
   - Download ZIP from frontend
   - Verify it's importable to SAP Integration Suite

---

## 📊 How to Confirm RAG is Actually Being Used

### **In BoomiToIS-API Logs, you MUST see:**

✅ **RAG Generation Enabled:**
```
🔧 iFlow Generation Configuration:
   RAG Generation Enabled: True   <-- MUST be True
```

✅ **RAG API Called:**
```
🚀 Using RAG API for iFlow generation
📡 Calling: http://localhost:5010/api/generate-iflow-from-markdown
```

✅ **Success Message:**
```
✅ RAG API generated iFlow successfully!
📦 Package: ...
📊 Metadata: ...
⚡ Method: RAG Agent (Dynamic)   <-- Confirms RAG was used
```

### **In RAG API Logs, you MUST see:**

```
🚀 RAG API: Received iFlow generation request
🔍 Analyzing markdown documentation...
🤖 Calling RAG Agent to generate iFlow...
✅ RAG Agent completed with status: success
💾 Metadata saved to: ...
✅ iFlow Generation SUCCESSFUL
```

### **If you see this instead:**

❌ **Template-based fallback:**
```
📋 Using template-based generation (fallback)
```

This means RAG API failed. Check:
1. Is RAG API service running?
2. Are .env files set correctly?
3. Check RAG API logs for errors

---

## 📁 Output Files

After successful generation:

### **Metadata File:**
```
component_metadata/iflow_components_20241016_143022.json
```

Contains:
- Component details
- Generation metadata
- Timestamp
- Generation method: "RAG Agent (Dynamic)"

### **Package File:**
```
generated_packages/GeneratedIFlow_abc123.zip
```

This is importable to SAP Integration Suite.

---

## 🐛 Troubleshooting

### **Issue 1: RAG API won't start**
```
Error: Cannot connect to Neo4j
```

**Solution:**
1. Check `config.py` Neo4j credentials
2. Test Neo4j connection manually
3. Ensure Neo4j Aura instance is running

### **Issue 2: Still using templates (not RAG)**
```
📋 Using template-based generation (fallback)
```

**Solution:**
1. Check .env files have `USE_RAG_GENERATION=true`
2. Ensure RAG API is running on port 5010
3. Check RAG API logs for errors

### **Issue 3: Port already in use**
```
Address already in use: 5010
```

**Solution:**
1. Find and kill process: `netstat -ano | findstr :5010`
2. Kill process: `taskkill /PID <pid> /F`
3. Or change port in .env files

### **Issue 4: Frontend not loading**
```
Cannot find module 'vite'
```

**Solution:**
```powershell
cd IMigrate/IFA-Project/frontend
npm install
npm run dev
```

### **Issue 5: Metadata/packages not in correct directory**
```
Files saved to wrong location
```

**Solution:**
- The RAG API service automatically uses absolute paths
- Check RAG API logs for exact paths
- Metadata: `component_metadata/`
- Packages: `generated_packages/`

---

## 🎯 Success Criteria

✅ All 5 services running
✅ Health checks pass
✅ Frontend accessible
✅ RAG API test passes
✅ Document upload works
✅ Documentation generates
✅ "Generate iFlow" button works
✅ BoomiToIS-API logs show "Using RAG API"
✅ RAG API logs show request received
✅ Metadata saved to `component_metadata/`
✅ Package saved to `generated_packages/`
✅ ZIP file is downloadable
✅ ZIP is importable to SAP Integration Suite

---

## 📝 Quick Command Reference

```powershell
# Setup
.\setup_env_files.ps1              # Create .env files

# Testing
python test_rag_api.py             # Test RAG API independently

# Start Services
.\START_ALL_SERVICES.ps1           # Start everything automatically

# Manual Start (in separate terminals)
python rag_api_service.py          # Terminal 1
cd IMigrate/app && python app.py   # Terminal 2
cd IMigrate/BoomiToIS-API && python app.py   # Terminal 3
cd IMigrate/MuleToIS-API && python app.py    # Terminal 4
cd IMigrate/IFA-Project/frontend && npm run dev  # Terminal 5

# Health Checks
curl http://localhost:5010/api/health
curl http://localhost:5000/api/health
curl http://localhost:5003/api/health
curl http://localhost:5001/api/health

# Open Frontend
start http://localhost:5173
```

---

## 🎉 You're Done!

If everything above works, you have a fully integrated IMigrate + RAG system where:

1. ✅ Users interact with IMigrate's frontend (unchanged)
2. ✅ Documents are processed by IMigrate (unchanged)
3. ✅ iFlows are generated by RAG Agent (NEW - intelligent, not hardcoded)
4. ✅ Automatic fallback to templates if RAG fails
5. ✅ All outputs in correct directories
6. ✅ Complete logging for debugging

**The best of both worlds!** 🚀

