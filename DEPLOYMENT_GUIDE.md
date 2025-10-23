# IMigrate Deployment Guide

Complete setup, configuration, and troubleshooting guide for the SAP Integration Suite migration platform.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Configuration Files](#configuration-files)
4. [Database Setup](#database-setup)
5. [Service Startup](#service-startup)
6. [SAP BTP Configuration](#sap-btp-configuration)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### **Required Software**
```bash
# Check versions
python --version    # 3.9+
node --version      # 18+
npm --version       # 9+
docker --version    # 20+
```

### **Required Accounts**
- ✅ Supabase account (free tier: https://supabase.com)
- ✅ Anthropic API key (https://console.anthropic.com/)
- ✅ Neo4j AuraDB account (https://neo4j.com/cloud/aura/) OR local Docker
- ✅ SAP BTP trial account (optional, for deployment)

### **System Requirements**
- 8GB RAM minimum
- 10GB free disk space
- Internet connection

---

## Environment Setup

### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd IMigrate
```

### **Step 2: Install Python Dependencies**
```bash
# Main API
cd app
pip install -r requirements.txt
cd ..

# BoomiToIS-API
cd BoomiToIS-API
pip install -r requirements.txt
cd ..

# RAG Agent
cd agentic-rag-IMigrate
pip install -r requirements.txt
cd ..
```

### **Step 3: Install Frontend Dependencies**
```bash
cd IFA-Project/frontend
npm install
cd ../..
```

### **Step 4: Setup Databases**

#### **Option A: Neo4j AuraDB (Cloud)**
1. Go to https://neo4j.com/cloud/aura/
2. Create free instance
3. Save connection URL + credentials

#### **Option B: Neo4j Docker (Local)**
```bash
docker run -d   --name neo4j   -p 7474:7474 -p 7687:7687   -e NEO4J_AUTH=neo4j/password123   neo4j:5.0
```

#### **Supabase Setup**
1. Go to https://supabase.com/dashboard
2. Create new project
3. Save Project URL + anon/service_role keys
4. Run SQL scripts:
   - `supabase_feedback_schema.sql`
   - `supabase_intent_training_schema.sql`
   - `supabase_intent_training_seed_data.sql`

---

## Configuration Files

### **1. Main API: `app/.env`**
```bash
cp app/.env.example app/.env
```

Edit `app/.env`:
```env
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Other APIs
BOOMI_API_URL=http://localhost:5003
MULE_API_URL=http://localhost:5002

# AWS S3 (optional, for file storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=your-bucket
```

### **2. BoomiToIS-API: `BoomiToIS-API/.env.development`**
```bash
cp BoomiToIS-API/.env.example BoomiToIS-API/.env.development
```

Edit `BoomiToIS-API/.env.development`:
```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Supabase (same as Main API)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here

# SAP BTP (optional, for deployment)
SAP_BTP_TENANT_URL=https://itr-internal-xxxxx.integrationsuite.cfapps.us10-002.hana.ondemand.com
SAP_BTP_CLIENT_ID=sb-xxxxx
SAP_BTP_CLIENT_SECRET='your-secret-with-special-chars'
SAP_BTP_OAUTH_URL=https://xxxxx.authentication.us10.hana.ondemand.com/oauth/token
SAP_BTP_DEFAULT_PACKAGE=IMigratePackage

# RAG API
RAG_API_URL=http://localhost:8001
RAG_API_TIMEOUT=1200
USE_RAG_API=true
```

**Important:** Wrap `SAP_BTP_CLIENT_SECRET` in single quotes if it contains special characters.

### **3. RAG Agent: `agentic-rag-IMigrate/.env`**
```bash
cp agentic-rag-IMigrate/.env.example agentic-rag-IMigrate/.env
```

Edit `agentic-rag-IMigrate/.env`:
```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123

# OpenAI (for embeddings)
OPENAI_API_KEY=sk-xxxxx

# Main API callback
MAIN_API_URL=http://localhost:5000
```

### **4. Frontend: `IFA-Project/frontend/.env.development`**
```bash
cp IFA-Project/frontend/.env.example IFA-Project/frontend/.env.development
```

Edit `IFA-Project/frontend/.env.development`:
```env
# Main API
VITE_API_URL=/api
VITE_MAIN_API_HOST=localhost:5000
VITE_MAIN_API_PROTOCOL=http

# iFlow API (BoomiToIS-API)
VITE_IFLOW_API_URL=http://localhost:5003/api
VITE_IFLOW_API_HOST=localhost:5003
VITE_IFLOW_API_PROTOCOL=http

# MuleSoft API
VITE_MULESOFT_API_URL=http://localhost:5002/api
VITE_MULESOFT_API_HOST=localhost:5002
VITE_MULESOFT_API_PROTOCOL=http

# Polling
VITE_DISABLE_AUTO_POLLING=false
```

---

## Database Setup

### **Supabase Tables**

Run these SQL scripts in Supabase SQL Editor (https://supabase.com/dashboard/project/YOUR_PROJECT/sql):

#### **1. Feedback System**
```bash
# Copy content from supabase_feedback_schema.sql and run in Supabase
```

**Creates 6 tables:**
- `migration_feedback` - User feedback on conversions
- `documentation_feedback` - Documentation quality feedback
- `component_mapping_feedback` - Component accuracy feedback
- `learned_migration_patterns` - AI-learned patterns
- `platform_connector_mappings` - Platform-specific mappings
- `feedback_analytics` - Aggregated analytics view

#### **2. Intent Learning System**
```bash
# Copy content from supabase_intent_training_schema.sql and run
# Then run supabase_intent_training_seed_data.sql
```

**Creates 5 tables:**
- `component_pattern_library` - Learned component patterns
- `intent_training_examples` - Historical training examples
- `component_co_occurrence` - Component relationships
- `intent_prompt_versions` - Prompt evolution tracking
- `generation_feedback` - Per-generation feedback

**Seeds with 45+ patterns:**
- SFTP, Timer, GroovyScript, RequestReply, Router, ContentModifier, etc.
- 5 training examples
- 8 co-occurrence patterns

### **Neo4j Setup**

**Option A: Load from existing iFlow data**
```python
cd agentic-rag-IMigrate
python -c "
from agent.iflow_similarity import IFlowSimilaritySearch
search = IFlowSimilaritySearch()
# Add your iFlow XML files here
"
```

**Option B: Start empty** (patterns loaded on-demand during generation)

---

## Service Startup

### **Start All Services (4 Terminals)**

#### **Terminal 1: Main API**
```bash
cd app
python app.py

# Output:
# * Running on http://127.0.0.1:5000
```

#### **Terminal 2: BoomiToIS-API**
```bash
cd BoomiToIS-API
python app.py

# Output:
# * Running on http://127.0.0.1:5003
```

#### **Terminal 3: RAG Agent API**
```bash
cd agentic-rag-IMigrate
python rag_api_service.py

# Output:
# * Running on http://127.0.0.1:8001
```

#### **Terminal 4: Frontend**
```bash
cd IFA-Project/frontend
npm run dev

# Output:
# VITE v5.x.x ready in xxx ms
# ➜ Local: http://localhost:5173/
```

### **Verify All Services Running**
```bash
# Check ports
netstat -an | findstr "5000 5003 8001 5173"

# Should see:
# TCP 0.0.0.0:5000 LISTENING
# TCP 0.0.0.0:5003 LISTENING
# TCP 0.0.0.0:8001 LISTENING
# TCP 0.0.0.0:5173 LISTENING
```

---

## SAP BTP Configuration

### **Step 1: Create Service Instance**

In SAP BTP Cockpit:
1. Navigate to your subaccount
2. Go to **Services → Instances and Subscriptions**
3. Create new instance:
   - Service: **Process Integration Runtime**
   - Plan: **integration-flow**
4. Create service key with these roles:
   ```json
   {
     "roles": [
       "WorkspacePackagesEdit",
       "WorkspaceArtifactsEdit",
       "AuthGroup.IntegrationDeveloper"
     ]
   }
   ```

### **Step 2: Extract Credentials**

From service key JSON:
```json
{
  "oauth": {
    "url": "https://xxxxx.authentication.us10.hana.ondemand.com",
    "clientid": "sb-xxxxx!xxxxx",
    "clientsecret": "xxxxx=",
    "tokenurl": "https://xxxxx.authentication.us10.hana.ondemand.com/oauth/token"
  },
  "url": "https://itr-internal-xxxxx.integrationsuite.cfapps.us10-002.hana.ondemand.com"
}
```

### **Step 3: Update `.env.development`**
```env
SAP_BTP_TENANT_URL=<url from above>
SAP_BTP_CLIENT_ID=<clientid>
SAP_BTP_CLIENT_SECRET='<clientsecret>'  # Use quotes!
SAP_BTP_OAUTH_URL=<tokenurl>
SAP_BTP_DEFAULT_PACKAGE=IMigrateTest
```

### **Step 4: Create Package in SAP**

Option A: Via UI (recommended first time)
1. Open SAP Integration Suite
2. Go to **Design → Integrations**
3. Create package: `IMigrateTest`

Option B: Auto-create (code does it automatically)
- Package created on first deployment

---

## Verification

### **Test 1: Health Checks**
```bash
# Main API
curl http://localhost:5000/api/health

# BoomiToIS-API
curl http://localhost:5003/api/health

# RAG Agent
curl http://localhost:8001/health
```

**Expected:** All return `{"status": "ok"}`

### **Test 2: Upload File**
1. Open http://localhost:5173
2. Select platform: **Boomi**
3. Upload sample Boomi XML
4. Click "Generate Documentation"
5. Wait for status: **"Documentation ready!"**

**Check logs:**
- Main API: `Job xxx: Dell Boomi documentation generation completed`
- Status: `documentation_completed`

### **Test 3: Generate iFlow**
1. Click "Generate SAP API/iFlow"
2. Watch console logs (should see RAG agent logs)
3. Wait 2-5 minutes
4. Button should change to "SAP API/iFlow Generated" ✅

**Check logs:**
- BoomiToIS-API: `✅ RAG Agent completed`
- RAG Agent: `✅ iFlow Generation SUCCESSFUL`
- ZIP file created in `agentic-rag-IMigrate/generated_packages/`

### **Test 4: Deploy to SAP** (Optional)
1. Click "Deploy to SAP Integration Suite"
2. Wait 10-20 seconds
3. Check SAP Integration Suite UI
4. iFlow should appear in your package

---

## Troubleshooting

### **Problem: Services Won't Start**

**Symptom:** `Address already in use`

**Fix:**
```bash
# Find process using port
netstat -ano | findstr "5000"

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### **Problem: "Generate iFlow" Button Shows "Generated" Immediately**

**Symptom:** Button changes before logs finish

**Fix:**
1. Restart Main API
2. Restart Frontend
3. Clear browser cache
4. Verify `app/app.py` line 1726 has:
   ```python
   'status': 'documentation_completed',  # Not 'completed'!
   ```

### **Problem: iFlow Generation Fails**

**Symptom:** Status stuck on "Generating..." or fails

**Check:**
1. RAG Agent logs: `agentic-rag-IMigrate/rag_api_service.py`
2. Anthropic API key valid:
   ```bash
   curl https://api.anthropic.com/v1/messages      -H "x-api-key: $ANTHROPIC_API_KEY"      -H "anthropic-version: 2023-06-01"      -H "content-type: application/json"      -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":100,"messages":[{"role":"user","content":"test"}]}'
   ```
3. Neo4j running:
   ```bash
   docker ps | findstr neo4j
   ```

**Fallback:** If RAG fails, system uses template-based generation automatically.

### **Problem: Deployment to SAP BTP Fails**

**Symptom:** 401 Unauthorized or 404 Package not found

**Check:**
1. Service key has correct roles:
   - `WorkspacePackagesEdit`
   - `WorkspaceArtifactsEdit`
   - `AuthGroup.IntegrationDeveloper`
2. Client secret wrapped in quotes (special chars)
3. Package exists in SAP:
   ```bash
   # Test OAuth token
   curl -X POST "$SAP_BTP_OAUTH_URL"      -H "Content-Type: application/x-www-form-urlencoded"      -d "grant_type=client_credentials&client_id=$SAP_BTP_CLIENT_ID&client_secret=$SAP_BTP_CLIENT_SECRET"
   ```
4. Package name doesn't contain special chars (use `IMigrateTest`, not `IMigrate_Test`)

### **Problem: Feedback Submission Fails**

**Symptom:** 500 error when submitting feedback

**Check:**
1. Supabase credentials in `BoomiToIS-API/.env.development`:
   ```env
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-key
   ```
2. Feedback tables exist in Supabase (run `supabase_feedback_schema.sql`)
3. Frontend sending to correct port (5003):
   ```javascript
   // IFA-Project/frontend/vite.config.js
   '/api/feedback': {
       target: 'http://localhost:5003',
       ...
   }
   ```

### **Problem: Pattern Library Not Working**

**Symptom:** Agent generates components incorrectly

**Check:**
1. Seed data loaded: run `supabase_intent_training_seed_data.sql`
2. Check pattern count:
   ```sql
   SELECT COUNT(*) FROM component_pattern_library;
   -- Should return 45+
   ```
3. Agent querying correctly:
   ```python
   # Check logs for:
   "📚 Retrieved X learned patterns from pattern library"
   ```

### **Problem: Neo4j Connection Fails**

**Symptom:** `Could not connect to Neo4j`

**Fix:**
1. Check Neo4j running:
   ```bash
   docker logs neo4j
   ```
2. Verify credentials in `.env`:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=password123
   ```
3. Test connection:
   ```bash
   pip install neo4j
   python -c "from neo4j import GraphDatabase; GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123')).verify_connectivity()"
   ```

---

## Production Deployment

### **Environment Variables**
Use `.env.production` files:
- `app/.env.production`
- `BoomiToIS-API/.env.production`
- `IFA-Project/frontend/.env.production`

### **Frontend Build**
```bash
cd IFA-Project/frontend
npm run build
# Outputs to dist/
```

### **Docker Deployment** (Coming Soon)
```bash
docker-compose up -d
```

---

## Logs & Monitoring

### **Log Locations**
- Main API: Console output + `app/logs/`
- BoomiToIS-API: Console output
- RAG Agent: Console output + `agentic-rag-IMigrate/query_logs/`
- Frontend: Browser console

### **Key Log Messages**
```bash
# Successful documentation generation
"Job xxx: Dell Boomi documentation generation completed successfully"

# iFlow generation started
"📝 Using template-based iFlow generation (RAG disabled)" OR
"🤖 RAG API enabled - calling agentic-rag-IMigrate service"

# iFlow generation completed
"✅ RAG Agent completed"
"Package Path: generated_packages/*.zip"

# Deployment successful
"✅ Deployment completed successfully"
```

---

## Next Steps

- ✅ Services running? → Upload a file!
- ✅ iFlow generated? → Deploy to SAP BTP
- ✅ Deployed? → Provide feedback
- 📚 Read `FEEDBACK_AND_LEARNING.md` to understand how your feedback improves the system
- 🛠️ Read `DEVELOPMENT.md` to contribute or customize

---

**Need help?** Check logs first, then see specific error fixes above.
