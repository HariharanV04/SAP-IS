# IMigrate + RAG System Integration Plan

## 📋 Executive Summary

**Goal**: Integrate IMigrate's frontend/backend with RAG system's intelligent iFlow generation, replacing IMigrate's hardcoded template-based generation with RAG's dynamic AI-powered generation.

**Key Principle**: Keep IMigrate's entire UI and backend workflow intact. Only replace the final iFlow generation step with RAG system.

---

## 🔍 Current System Analysis

### **IMigrate System Flow** (What We Keep)
```
User → Frontend UI → Upload Document (Boomi/MuleSoft XML/ZIP)
  ↓
Main API (Port 5000) → Document Processing
  ↓
1. Extract content from document
2. Generate documentation (Markdown)
3. Call Boomi/MuleSoft API for metadata generation
  ↓
BoomiToIS-API (Port 5003) OR MuleToIS-API (Port 5001)
  ↓
4. Analyze documentation with AI (Claude/GPT)
5. Generate metadata JSON
6. **CURRENT: Use template-based generator** ← WE REPLACE THIS
  ↓
7. Create importable SAP iFlow package (ZIP)
  ↓
8. Return to Main API → Frontend → User downloads
```

### **RAG System Flow** (What We Integrate)
```
User → Terminal Input → Query
  ↓
run_agent.py → SAPiFlowAgent
  ↓
1. Understand user intent
2. Search Knowledge Graph (Neo4j)
3. Search Vector Database (Supabase)
4. Generate strategic plan
5. Create components dynamically (NOT hardcoded)
6. Use IFlowPackager to create ZIP
  ↓
Output: SAP iFlow Package (ZIP)
```

---

## 🎯 Integration Point

**EXACT LOCATION TO INTEGRATE**:

**File**: `IMigrate/BoomiToIS-API/app.py` (and MuleToIS-API/app.py)
**Function**: `process_iflow_generation()` at line 315
**Current Code**:
```python
# Line 347-354
result = generate_iflow_from_markdown(
    markdown_content=markdown_content,
    api_key=ANTHROPIC_API_KEY,
    output_dir=job_result_dir,
    iflow_name=iflow_name,
    job_id=job_id,
    use_converter=False  # Template-based approach
)
```

**What We Replace**: The `generate_iflow_from_markdown()` call that uses IMigrate's template-based generator.

**What We Use Instead**: RAG system's `SAPiFlowAgent.create_complete_iflow_package()` method.

---

## 🏗️ Integration Architecture

### **Option 1: API Bridge** (RECOMMENDED - Minimal Changes)

```
IMigrate Backend
  ↓
HTTP Request to RAG API Service (NEW)
  ↓
RAG Agent generates iFlow
  ↓
Returns ZIP file path
  ↓
IMigrate Backend continues normal flow
```

**Advantages**:
- ✅ Zero modifications to IMigrate's existing code
- ✅ RAG system runs as independent microservice
- ✅ Can test independently
- ✅ Can rollback easily
- ✅ Both systems remain separate and maintainable

**Components to Create**:
1. **RAG API Service** (`rag_api_service.py`) - Flask API wrapping RAG agent
2. **Configuration** - Add RAG_API_URL to IMigrate config
3. **API Bridge Function** - Replace template call with RAG API call

### **Option 2: Direct Integration** (More Coupled)

```
IMigrate Backend
  ↓
Import RAG Agent directly
  ↓
Call RAG Agent methods
  ↓
Continue normal flow
```

**Advantages**:
- ✅ No network calls
- ✅ Faster execution
- ✅ Single deployment

**Disadvantages**:
- ❌ Tight coupling between systems
- ❌ Harder to maintain
- ❌ Dependency conflicts possible
- ❌ Can't test independently

---

## 📝 Detailed Integration Plan (Option 1 - Recommended)

### **Phase 1: Create RAG API Service**

**File**: `rag_api_service.py` (NEW - in root directory)

```python
"""
RAG API Service - Flask API wrapper for RAG agent
This service exposes RAG system's iFlow generation capabilities via REST API
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import os
import logging
from datetime import datetime

from agent.agent import create_sap_iflow_agent
from knowledge_graph.graph_store import GraphStore
import config

app = Flask(__name__)
CORS(app)

# Initialize RAG Agent (once on startup)
graph_store = None
rag_agent = None

@app.before_first_request
def initialize_agent():
    """Initialize RAG agent on first request"""
    global graph_store, rag_agent
    
    # Initialize Neo4j
    graph_store = GraphStore(
        config.NEO4J_URI,
        config.NEO4J_USER,
        config.NEO4J_PASSWORD
    )
    asyncio.run(graph_store.initialize())
    
    # Initialize RAG Agent
    rag_agent = create_sap_iflow_agent(
        graph_store=graph_store,
        openai_api_key=config.OPENAI_API_KEY,
        context_document="SAP iFlow RAG + Knowledge Graph System"
    )
    
    logging.info("RAG Agent initialized successfully")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'RAG API Service',
        'agent_initialized': rag_agent is not None
    })

@app.route('/api/generate-iflow-from-markdown', methods=['POST'])
def generate_iflow_from_markdown():
    """
    Generate iFlow from markdown documentation using RAG system
    
    Expected JSON body:
    {
        "markdown_content": "...",
        "iflow_name": "MyFlow",
        "job_id": "uuid",
        "output_dir": "/path/to/output"
    }
    
    Returns:
    {
        "status": "success",
        "message": "...",
        "files": {
            "zip": "/path/to/package.zip"
        },
        "iflow_name": "MyFlow"
    }
    """
    try:
        data = request.json
        markdown_content = data.get('markdown_content')
        iflow_name = data.get('iflow_name', 'GeneratedIFlow')
        job_id = data.get('job_id')
        output_dir = data.get('output_dir')
        
        if not markdown_content:
            return jsonify({
                'status': 'error',
                'message': 'Missing markdown_content'
            }), 400
        
        # Convert markdown to query for RAG agent
        # The markdown contains the documentation, we need to convert it to a generation request
        query = f"Generate an iFlow named '{iflow_name}' based on this documentation:\n\n{markdown_content}"
        
        # Call RAG agent to generate iFlow package
        result = asyncio.run(
            rag_agent.create_complete_iflow_package(query)
        )
        
        # Format response to match IMigrate's expected format
        if result.get('status') == 'success':
            return jsonify({
                'status': 'success',
                'message': f'Generated iFlow: {result.get("package_path")}',
                'files': {
                    'zip': result.get('package_path'),
                    'debug': {}
                },
                'iflow_name': iflow_name,
                'components': result.get('components', []),
                'metadata': result.get('metadata', {})
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Failed to generate iFlow')
            }), 500
            
    except Exception as e:
        logging.error(f"Error generating iFlow: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('RAG_API_PORT', 5010))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### **Phase 2: Modify IMigrate Backend to Use RAG API**

**File**: `IMigrate/BoomiToIS-API/app.py` (MODIFY)

**Location**: Function `process_iflow_generation()` at line 315

**Current Code** (Line 347-354):
```python
result = generate_iflow_from_markdown(
    markdown_content=markdown_content,
    api_key=ANTHROPIC_API_KEY,
    output_dir=job_result_dir,
    iflow_name=iflow_name,
    job_id=job_id,
    use_converter=False  # Template-based approach
)
```

**NEW CODE** (Replace with):
```python
# Check if RAG API is enabled (via environment variable)
USE_RAG_GENERATION = os.getenv('USE_RAG_GENERATION', 'true').lower() == 'true'
RAG_API_URL = os.getenv('RAG_API_URL', 'http://localhost:5010')

if USE_RAG_GENERATION:
    # Use RAG system for intelligent iFlow generation
    logger.info(f"Using RAG API for iFlow generation: {RAG_API_URL}")
    
    import requests
    
    try:
        # Call RAG API
        response = requests.post(
            f"{RAG_API_URL}/api/generate-iflow-from-markdown",
            json={
                'markdown_content': markdown_content,
                'iflow_name': iflow_name,
                'job_id': job_id,
                'output_dir': job_result_dir
            },
            timeout=300  # 5 minutes timeout for generation
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"RAG API generated iFlow successfully: {result}")
        else:
            logger.error(f"RAG API error: {response.status_code} - {response.text}")
            # Fallback to template-based generation
            logger.warning("Falling back to template-based generation")
            result = generate_iflow_from_markdown(
                markdown_content=markdown_content,
                api_key=ANTHROPIC_API_KEY,
                output_dir=job_result_dir,
                iflow_name=iflow_name,
                job_id=job_id,
                use_converter=False
            )
    except Exception as e:
        logger.error(f"Error calling RAG API: {str(e)}")
        # Fallback to template-based generation
        logger.warning("Falling back to template-based generation")
        result = generate_iflow_from_markdown(
            markdown_content=markdown_content,
            api_key=ANTHROPIC_API_KEY,
            output_dir=job_result_dir,
            iflow_name=iflow_name,
            job_id=job_id,
            use_converter=False
        )
else:
    # Use original template-based generation
    logger.info("Using template-based iFlow generation (RAG disabled)")
    result = generate_iflow_from_markdown(
        markdown_content=markdown_content,
        api_key=ANTHROPIC_API_KEY,
        output_dir=job_result_dir,
        iflow_name=iflow_name,
        job_id=job_id,
        use_converter=False
    )
```

**Same change needed in**: `IMigrate/MuleToIS-API/app.py` (similar function)

### **Phase 3: Configuration Setup**

**File**: `IMigrate/app/.env` (ADD these lines)

```bash
# RAG System Integration
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
RAG_API_TIMEOUT=300
```

**File**: `IMigrate/BoomiToIS-API/.env` (ADD these lines)

```bash
# RAG System Integration
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
```

**File**: `IMigrate/MuleToIS-API/.env` (ADD these lines)

```bash
# RAG System Integration
USE_RAG_GENERATION=true
RAG_API_URL=http://localhost:5010
```

### **Phase 4: Update Root Config** (OPTIONAL - for consistency)

**File**: `config.py` (ADD these lines at the end)

```python
# RAG API Service Configuration (for IMigrate integration)
RAG_API_PORT = int(os.getenv("RAG_API_PORT", "5010"))
RAG_API_HOST = os.getenv("RAG_API_HOST", "0.0.0.0")
USE_RAG_GENERATION = os.getenv("USE_RAG_GENERATION", "true").lower() == "true"
```

---

## 🚀 Deployment Steps

### **Step 1: Start RAG API Service**

```bash
# In root directory
python rag_api_service.py
```

Expected output:
```
RAG Agent initialized successfully
 * Running on http://0.0.0.0:5010
```

### **Step 2: Start IMigrate Main API**

```bash
# In IMigrate/app directory
python app.py
```

Expected output:
```
 * Running on http://localhost:5000
```

### **Step 3: Start BoomiToIS-API**

```bash
# In IMigrate/BoomiToIS-API directory
python app.py
```

Expected output:
```
 * Running on http://localhost:5003
```

### **Step 4: Start MuleToIS-API**

```bash
# In IMigrate/MuleToIS-API directory
python app.py
```

Expected output:
```
 * Running on http://localhost:5001
```

### **Step 5: Start Frontend** (if applicable)

```bash
# In IMigrate/IFA-Project directory
npm start
```

---

## 🧪 Testing Strategy

### **Test 1: RAG API Health Check**

```bash
curl http://localhost:5010/api/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "RAG API Service",
  "agent_initialized": true
}
```

### **Test 2: Direct RAG API Call**

```bash
curl -X POST http://localhost:5010/api/generate-iflow-from-markdown \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "Create an HTTP sender with content modifier and groovy script",
    "iflow_name": "TestFlow",
    "job_id": "test-123"
  }'
```

### **Test 3: End-to-End IMigrate Flow**

1. Open IMigrate frontend
2. Upload a Boomi/MuleSoft XML file
3. Click "Generate Documentation"
4. Wait for documentation to complete
5. Click "Generate iFlow"
6. **Verify**: Check logs to confirm RAG API is called
7. **Verify**: Download generated iFlow and test in SAP Integration Suite

### **Test 4: Fallback Test**

1. Stop RAG API service
2. Upload document in IMigrate
3. Try to generate iFlow
4. **Verify**: System falls back to template-based generation
5. **Verify**: iFlow is still generated successfully

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    IMigrate Frontend (React)                 │
│                       Port: 3000                             │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP Requests
                  ↓
┌─────────────────────────────────────────────────────────────┐
│              IMigrate Main API (Flask)                       │
│                    Port: 5000                                │
│  • Document Upload                                           │
│  • Documentation Generation                                  │
│  • Job Management                                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         ↓                 ↓
┌────────────────┐  ┌────────────────┐
│  BoomiToIS-API │  │  MuleToIS-API  │
│   Port: 5003   │  │   Port: 5001   │
└────────┬───────┘  └────────┬───────┘
         │                   │
         │ HTTP POST         │ HTTP POST
         │ (markdown)        │ (markdown)
         ↓                   ↓
┌─────────────────────────────────────┐
│      RAG API Service (Flask)         │ ← NEW SERVICE
│         Port: 5010                   │
│  • Wraps RAG Agent                   │
│  • Processes Markdown                │
│  • Generates iFlow via RAG           │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│       RAG System (SAPiFlowAgent)     │
│  • Knowledge Graph (Neo4j)           │
│  • Vector Database (Supabase)        │
│  • LLM (OpenAI GPT-4)                │
│  • IFlowPackager                     │
└─────────────────────────────────────┘
```

---

## 🔒 Key Design Principles

1. **Loose Coupling**: RAG API service is completely independent
2. **Fallback Support**: If RAG fails, use template-based generation
3. **Feature Flag**: Can enable/disable RAG via environment variable
4. **No Breaking Changes**: IMigrate continues to work exactly as before
5. **Minimal Modifications**: Only change ~30 lines in two files
6. **Testable**: Each service can be tested independently
7. **Rollback-Friendly**: Can disable RAG instantly via config

---

## 🎯 Benefits of This Approach

### **For IMigrate**:
- ✅ Keep entire UI/UX unchanged
- ✅ Keep all document processing unchanged
- ✅ Keep all job management unchanged
- ✅ Add intelligent iFlow generation
- ✅ Can fallback to templates if needed

### **For RAG System**:
- ✅ No modifications to core agent logic
- ✅ Exposed as reusable API service
- ✅ Can serve multiple clients
- ✅ Independent deployment and scaling

### **For Users**:
- ✅ Same familiar interface
- ✅ Better quality iFlows (RAG-powered)
- ✅ More dynamic generation (not hardcoded)
- ✅ Seamless experience

---

## 📈 Migration Path

### **Phase 1: Development** (Week 1)
- [ ] Create RAG API Service
- [ ] Add integration code to BoomiToIS-API
- [ ] Add integration code to MuleToIS-API
- [ ] Local testing

### **Phase 2: Testing** (Week 2)
- [ ] Test RAG API independently
- [ ] Test IMigrate + RAG integration
- [ ] Compare RAG vs Template output quality
- [ ] Performance testing

### **Phase 3: Gradual Rollout** (Week 3)
- [ ] Deploy with RAG disabled (USE_RAG_GENERATION=false)
- [ ] Enable RAG for test users
- [ ] Monitor logs and performance
- [ ] Collect feedback

### **Phase 4: Full Deployment** (Week 4)
- [ ] Enable RAG for all users (USE_RAG_GENERATION=true)
- [ ] Monitor production
- [ ] Keep template fallback active
- [ ] Document final setup

---

## 🔧 Troubleshooting

### **Issue**: RAG API not responding
**Solution**: 
1. Check if service is running: `curl http://localhost:5010/api/health`
2. Check logs: `tail -f rag_api_service.log`
3. System automatically falls back to templates

### **Issue**: iFlow generation taking too long
**Solution**:
1. Increase timeout in IMigrate config: `RAG_API_TIMEOUT=600`
2. Check RAG system performance
3. Consider async processing

### **Issue**: Generated iFlow not working in SAP
**Solution**:
1. Check generated ZIP structure
2. Compare with template-generated iFlow
3. Use SAP Integration Suite validation

---

## 📝 Files to Create/Modify Summary

### **NEW FILES** (Create these):
1. `rag_api_service.py` - RAG API wrapper service (root directory)

### **MODIFY FILES** (Minimal changes):
1. `IMigrate/BoomiToIS-API/app.py` - Add RAG API call (line ~347)
2. `IMigrate/MuleToIS-API/app.py` - Add RAG API call (similar location)
3. `IMigrate/app/.env` - Add RAG config variables
4. `IMigrate/BoomiToIS-API/.env` - Add RAG config variables
5. `IMigrate/MuleToIS-API/.env` - Add RAG config variables

### **OPTIONAL MODIFY**:
1. `config.py` - Add RAG API configuration

**Total Changes**: 1 new file, 5-6 modified files, ~100 lines of code

---

## ✅ Success Criteria

1. ✅ IMigrate UI works exactly as before
2. ✅ Document upload and processing unchanged
3. ✅ iFlow generation uses RAG system
4. ✅ Generated iFlows are importable to SAP Integration Suite
5. ✅ Fallback to templates works if RAG fails
6. ✅ Can toggle RAG on/off via config
7. ✅ All IMigrate features remain functional
8. ✅ Performance is acceptable (< 5 min for complex flows)

---

## 🚦 Next Steps

1. **Review this plan** - Discuss and approve approach
2. **Create RAG API Service** - Implement the wrapper
3. **Test RAG API independently** - Ensure it works standalone
4. **Integrate with IMigrate** - Minimal code changes
5. **End-to-end testing** - Full workflow validation
6. **Deploy and monitor** - Gradual rollout with monitoring

---

**This integration keeps both systems clean, maintainable, and allows for easy rollback if needed. The key is the API bridge that connects them without tight coupling.**

