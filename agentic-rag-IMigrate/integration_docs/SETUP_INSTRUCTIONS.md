# Complete Setup Instructions - IMigrate + RAG Integration

## 🚀 Step-by-Step Setup Guide

### **Step 1: Install Python Dependencies**

```bash
# In root directory (for RAG system)
pip install -r requirements.txt

# In IMigrate/app directory (for Main API)
cd IMigrate/app
pip install -r requirements.txt
cd ../..

# For BoomiToIS-API
cd IMigrate/BoomiToIS-API
pip install -r requirements_essential.txt
cd ../..

# For MuleToIS-API  
cd IMigrate/MuleToIS-API
pip install -r requirements.txt
cd ../..
```

### **Step 2: Install Frontend Dependencies**

```bash
# In IMigrate frontend directory
cd IMigrate/IFA-Project/frontend
npm install
cd ../../..
```

### **Step 3: Create Required Directories**

```bash
# These directories will be created automatically by the system
# But you can create them manually if needed:
mkdir -p component_metadata
mkdir -p generated_packages
mkdir -p IMigrate/app/uploads
mkdir -p IMigrate/app/results
```

### **Step 4: Start All Services (in order)**

#### Terminal 1: RAG API Service
```bash
python rag_api_service.py
```
Expected output: `* Running on http://0.0.0.0:5010`

#### Terminal 2: IMigrate Main API
```bash
cd IMigrate/app
python app.py
```
Expected output: `* Running on http://localhost:5000`

#### Terminal 3: BoomiToIS-API
```bash
cd IMigrate/BoomiToIS-API
python app.py
```
Expected output: `* Running on http://localhost:5003`

#### Terminal 4: MuleToIS-API
```bash
cd IMigrate/MuleToIS-API
python app.py
```
Expected output: `* Running on http://localhost:5001`

#### Terminal 5: Frontend
```bash
cd IMigrate/IFA-Project/frontend
npm run dev
```
Expected output: `Local: http://localhost:5173`

### **Step 5: Access the Application**

Open your browser and go to: `http://localhost:5173`

---

## 🔍 Verification Checklist

- [ ] RAG API Service running on port 5010
- [ ] Main API running on port 5000
- [ ] BoomiToIS-API running on port 5003
- [ ] MuleToIS-API running on port 5001
- [ ] Frontend accessible at http://localhost:5173
- [ ] component_metadata directory exists
- [ ] generated_packages directory exists

---

## 📋 Testing the System

### Test 1: Health Checks
```bash
# Test RAG API
curl http://localhost:5010/api/health

# Test Main API
curl http://localhost:5000/api/health

# Test BoomiToIS-API
curl http://localhost:5003/api/health

# Test MuleToIS-API
curl http://localhost:5001/api/health
```

### Test 2: End-to-End Flow
1. Upload Boomi/MuleSoft document via frontend
2. Wait for documentation generation
3. Click "Generate iFlow"
4. Check logs in BoomiToIS-API terminal
5. Verify RAG API is called (look for "Using RAG API for iFlow generation")
6. Check `component_metadata/` for metadata JSON
7. Check `generated_packages/` for iFlow ZIP file

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors
**Solution**: Install dependencies in all directories as shown in Step 1

### Issue: RAG API not responding
**Solution**: Check if Neo4j and Supabase credentials are correct in `config.py`

### Issue: Frontend not loading
**Solution**: Run `npm install` in `IMigrate/IFA-Project/frontend`

### Issue: iFlow still using templates
**Solution**: Check .env files have `USE_RAG_GENERATION=true`

---

## 📝 Important File Paths

- **Metadata Output**: `C:\Users\ASUS\vs code projects\ITR\agentic-rag-knowledge-graph\component_metadata`
- **iFlow Packages**: `C:\Users\ASUS\vs code projects\ITR\agentic-rag-knowledge-graph\generated_packages`
- **Logs**: Check terminal outputs for each service

