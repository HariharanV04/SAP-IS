# Quick Start - IMigrate + RAG Integration

## 🚀 30-Second Start

```powershell
# 1. Setup environment
.\setup_env_files.ps1

# 2. Install dependencies (first time only)
pip install -r requirements.txt
cd IMigrate/app && pip install -r requirements.txt && cd ../..
cd IMigrate/BoomiToIS-API && pip install -r requirements_essential.txt && cd ../..
cd IMigrate/MuleToIS-API && pip install -r requirements.txt && cd ../..
cd IMigrate/IFA-Project/frontend && npm install && cd ../../..

# 3. Test RAG API (recommended)
python rag_api_service.py         # Start in Terminal 1
python test_rag_api.py             # Run in Terminal 2

# 4. Start everything
.\START_ALL_SERVICES.ps1

# 5. Open browser
start http://localhost:5173
```

## ✅ Verification Checklist

- [ ] 5 terminal windows opened
- [ ] All services show "Running" in logs
- [ ] Frontend opens in browser
- [ ] Can upload document
- [ ] Documentation generates
- [ ] "Generate iFlow" button appears
- [ ] BoomiToIS-API logs show "🚀 Using RAG API"
- [ ] Files appear in `component_metadata/` and `generated_packages/`

## 🔍 How to Confirm RAG is Working

**In BoomiToIS-API terminal, look for:**
```
================================================================================
🔧 iFlow Generation Configuration:
   RAG Generation Enabled: True   <-- Must be True!
================================================================================
🚀 Using RAG API for iFlow generation
📡 Calling: http://localhost:5010/api/generate-iflow-from-markdown
...
✅ RAG API generated iFlow successfully!
⚡ Method: RAG Agent (Dynamic)   <-- Confirms RAG was used!
```

**If you see "template-based" instead:**
- Check .env files have `USE_RAG_GENERATION=true`
- Ensure RAG API service is running
- Check RAG API logs for errors

## 📁 Output Locations

- **Metadata**: `component_metadata/iflow_components_TIMESTAMP.json`
- **Packages**: `generated_packages/IFLOW_NAME.zip`

## 🐛 Common Issues

**Port conflicts:**
```powershell
netstat -ano | findstr ":5010"    # Find process
taskkill /PID <pid> /F            # Kill it
```

**RAG not being used:**
```powershell
# Check .env files
Get-Content IMigrate/BoomiToIS-API/.env | Select-String "USE_RAG"
Get-Content IMigrate/MuleToIS-API/.env | Select-String "USE_RAG"
Get-Content IMigrate/app/.env | Select-String "USE_RAG"

# All should show: USE_RAG_GENERATION=true
```

**Frontend won't start:**
```powershell
cd IMigrate/IFA-Project/frontend
npm install
npm run dev
```

## 📞 Need Help?

See `COMPLETE_INTEGRATION_GUIDE.md` for detailed instructions.

