# IMigrate Developer Guide

Developer documentation for contributing to and customizing the SAP Integration Suite migration platform.

---

## Table of Contents

1. [Code Structure](#code-structure)
2. [API Documentation](#api-documentation)
3. [Adding New Features](#adding-new-features)
4. [Testing](#testing)
5. [Common Patterns](#common-patterns)
6. [JSON Blueprint Reference](#json-blueprint-reference)
7. [Contributing Guidelines](#contributing-guidelines)

---

## Code Structure

```
IMigrate/
├── app/                          # Main API (Flask, Port 5000)
│   ├── app.py                    # Main entry point
│   ├── boomi_flow_documentation.py  # Boomi parser
│   ├── mule_flow_documentation.py   # MuleSoft parser
│   └── jobs.json                 # Local job tracking
│
├── BoomiToIS-API/                # iFlow Generation API (Flask, Port 5003)
│   ├── app.py                    # iFlow generation entry
│   ├── sap_btp_integration.py    # SAP BTP deployment
│   ├── direct_iflow_deployment.py  # Direct deploy method
│   ├── feedback_api.py           # Feedback endpoints
│   └── jobs.json                 # iFlow generation jobs
│
├── agentic-rag-IMigrate/         # RAG Agent (Flask, Port 8001)
│   ├── rag_api_service.py        # Flask API wrapper
│   ├── agent/
│   │   ├── agent.py              # SAP iFlow Agent (main logic)
│   │   ├── packager.py           # ZIP package builder
│   │   ├── rag_logger.py         # Query/result logging
│   │   └── iflow_similarity.py   # Neo4j similarity search
│   ├── config.py                 # Centralized config
│   └── generated_packages/       # Output ZIP files
│
├── IFA-Project/frontend/         # React Frontend (Vite, Port 5173)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── common/JobResult.jsx        # Main job page
│   │   │   ├── common/FileUploadForm.jsx   # File upload
│   │   │   └── IFATool/View.jsx            # Job list
│   │   ├── components/
│   │   │   └── FeedbackModal.jsx           # Feedback UI
│   │   └── services/
│   │       └── api.js             # API client
│   └── vite.config.js             # Proxy configuration
│
└── [5 Core Documentation Files]   # ← This is the new structure!
    ├── README.md
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT_GUIDE.md
    ├── FEEDBACK_AND_LEARNING.md
    └── DEVELOPMENT.md
```

---

## API Documentation

### **1. Main API (Port 5000)**

#### **POST /api/upload-documentation**
Upload Boomi/MuleSoft file for documentation generation.

**Request:**
```bash
curl -X POST http://localhost:5000/api/upload-documentation \
  -F "file=@boomi_process.xml" \
  -F "platform=boomi" \
  -F "llm_provider=anthropic"
```

**Response:**
```json
{
  "job_id": "abc-123",
  "status": "queued",
  "message": "Job created successfully"
}
```

#### **GET /api/jobs/:job_id**
Get job status.

**Response:**
```json
{
  "id": "abc-123",
  "status": "documentation_completed",
  "processing_message": "Ready for iFlow generation",
  "files": {
    "markdown": "results/abc-123/boomi_documentation.md"
  },
  "created": "2025-10-23T10:00:00Z"
}
```

**Status Values:**
- `processing` - Generating documentation
- `documentation_completed` - Docs ready, iFlow NOT generated
- `generating_iflow` - iFlow generation in progress
- `completed` - iFlow generated ✅
- `failed` - Error occurred

#### **GET /api/docs/:job_id/markdown**
Retrieve generated markdown documentation.

### **2. BoomiToIS-API (Port 5003)**

#### **POST /api/generate-iflow**
Generate iFlow from markdown documentation.

**Request:**
```bash
curl -X POST http://localhost:5003/api/generate-iflow \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Integration Flow...",
    "iflow_name": "MyIntegration",
    "use_rag": true
  }'
```

**Response:**
```json
{
  "job_id": "def-456",
  "status": "queued",
  "message": "iFlow generation started"
}
```

#### **POST /api/jobs/:job_id/direct-deploy**
Deploy generated iFlow to SAP BTP.

**Request:**
```bash
curl -X POST http://localhost:5003/api/jobs/def-456/direct-deploy \
  -H "Content-Type: application/json" \
  -d '{
    "iflow_name": "MyIntegration",
    "sap_package_id": "IMigrateTest"
  }'
```

**Response:**
```json
{
  "status": "success",
  "iflow_name": "MyIntegration",
  "package_id": "IMigrateTest",
  "deployment_url": "https://..."
}
```

#### **POST /api/feedback/submit**
Submit user feedback.

**Request:**
```json
{
  "job_id": "abc-123",
  "source_platform": "boomi",
  "overall_rating": 5,
  "documentation_quality_rating": 5,
  "iflow_quality_rating": 4,
  "component_mapping_accuracy": 8,
  "config_accuracy": 7,
  "missing_components": [],
  "what_worked_well": ["All components captured"],
  "what_needs_improvement": [],
  "time_to_fix_minutes": 5,
  "deployment_successful": true
}
```

### **3. RAG Agent API (Port 8001)**

#### **POST /api/generate-iflow-from-markdown**
Generate iFlow using RAG agent.

**Request:**
```json
{
  "markdown_content": "# Integration Flow...",
  "iflow_name": "MyIntegration",
  "job_id": "abc-123"
}
```

**Response:**
```json
{
  "status": "success",
  "files": {
    "zip": "generated_packages/MyIntegration_20251023.zip"
  },
  "components": [
    {"type": "Timer", "name": "SchedulePolling"},
    {"type": "SFTP", "name": "PollFiles"},
    {"type": "GroovyScript", "name": "TransformData"}
  ],
  "generation_method": "RAG Agent (Dynamic)"
}
```

---

## Adding New Features

### **1. Add New Platform Support (e.g., Sterling)**

#### **Step 1: Create Parser**
```python
# app/sterling_flow_documentation.py

class SterlingFlowDocumentationGenerator:
    def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Parse Sterling files"""
        # Extract flows, connectors, etc.
        pass
    
    def generate_documentation(self, results: Dict) -> str:
        """Generate markdown"""
        pass
```

#### **Step 2: Add Route in Main API**
```python
# app/app.py

@app.route('/api/upload-documentation', methods=['POST'])
def upload_documentation():
    platform = request.form.get('platform')  # Now includes 'sterling'
    
    if platform == 'sterling':
        return process_sterling_documentation(job_id, input_dir)
```

#### **Step 3: Add Frontend Support**
```javascript
// IFA-Project/frontend/src/pages/common/FileUploadForm.jsx

const platforms = [
  { value: 'boomi', label: 'Dell Boomi' },
  { value: 'mulesoft', label: 'MuleSoft' },
  { value: 'sterling', label: 'IBM Sterling' }  // ← Add this
];
```

### **2. Add New Component Type**

#### **Step 1: Add to Pattern Library**
```sql
INSERT INTO component_pattern_library (
  trigger_phrase,
  component_type,
  pattern_category,
  confidence_score
) VALUES (
  'encrypt.*data',
  'Encryptor',
  'security',
  0.85
);
```

#### **Step 2: Add XML Template**
```python
# agentic-rag-IMigrate/agent/agent.py

async def _generate_component_xml(self, component_type, ...):
    if component_type == 'Encryptor':
        return self._generate_encryptor_xml(...)
    
def _generate_encryptor_xml(self, ...):
    return f"""
    <bpmn2:serviceTask id="{component_id}" name="{name}">
      <bpmn2:extensionElements>
        <ifl:property>
          <key>encryptionAlgorithm</key>
          <value>AES-256</value>
        </key>
      </bpmn2:extensionElements>
    </bpmn2:serviceTask>
    """
```

#### **Step 3: Add to Knowledge Graph** (Optional)
```python
# agentic-rag-IMigrate/agent/iflow_similarity.py

def add_component_to_kg(self, component_xml, component_type='Encryptor'):
    with self.driver.session() as session:
        session.run("""
          CREATE (c:Component {
            id: $id,
            type: $type,
            xml: $xml
          })
        """, id=component_id, type=component_type, xml=component_xml)
```

### **3. Add New LLM Provider (e.g., OpenAI GPT-4)**

#### **Step 1: Add Config**
```python
# agentic-rag-IMigrate/config.py

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'anthropic')  # 'openai', 'anthropic', 'gemma3'
```

#### **Step 2: Add LLM Client**
```python
# agentic-rag-IMigrate/agent/agent.py

def _get_llm_client(self):
    if self.llm_provider == 'openai':
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4", api_key=OPENAI_API_KEY)
    elif self.llm_provider == 'anthropic':
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-3-5-sonnet-20241022")
```

---

## Testing

### **Unit Tests**

```python
# tests/test_agent.py

import pytest
from agent.agent import SAPiFlowAgent

def test_intent_understanding():
    agent = SAPiFlowAgent()
    intent = agent._understand_user_intent(
        "Poll SFTP every 5 minutes and post to OData"
    )
    
    assert 'Timer' in [c['type'] for c in intent['components']]
    assert 'SFTP' in [c['type'] for c in intent['components']]
    assert 'RequestReply' in [c['type'] for c in intent['components']]

def test_component_generation():
    agent = SAPiFlowAgent()
    xml = await agent._generate_component_xml(
        component_type='Timer',
        component_name='SchedulePolling'
    )
    
    assert '<bpmn2:startEvent' in xml
    assert 'ifl:schedule' in xml
```

### **Integration Tests**

```python
# tests/test_integration.py

def test_full_flow():
    # Upload file
    response = client.post('/api/upload-documentation',
        data={'file': open('test.xml'), 'platform': 'boomi'})
    job_id = response.json['job_id']
    
    # Wait for completion
    while True:
        status = client.get(f'/api/jobs/{job_id}').json
        if status['status'] == 'documentation_completed':
            break
    
    # Generate iFlow
    response = client.post('/api/generate-iflow',
        json={'job_id': job_id, 'iflow_name': 'Test'})
    
    assert response.status_code == 200
```

### **Frontend Tests**

```javascript
// IFA-Project/frontend/src/tests/JobResult.test.jsx

import { render, screen, waitFor } from '@testing/library/react';
import JobResult from '../pages/common/JobResult';

test('shows Generate iFlow button after documentation completes', async () => {
  render(<JobResult jobInfo={{status: 'documentation_completed'}} />);
  
  const button = await screen.findByText(/Generate SAP API\/iFlow/i);
  expect(button).toBeInTheDocument();
  expect(button).not.toBeDisabled();
});
```

---

## Common Patterns

### **1. Adding New Status**

**Backend:**
```python
# app/app.py
update_job(job_id, {
    'status': 'new_status_here',
    'processing_message': 'Doing new thing...'
})
```

**Frontend:**
```javascript
// JobResult.jsx
if (jobInfo.status === 'new_status_here') {
  return <div>New status UI</div>;
}
```

### **2. Calling RAG Agent**

```python
# BoomiToIS-API/app.py

import requests

response = requests.post(
    f"{RAG_API_URL}/api/generate-iflow-from-markdown",
    json={
        'markdown_content': markdown,
        'iflow_name': iflow_name,
        'job_id': job_id
    },
    timeout=1200  # 20 minutes
)

if response.status_code == 200:
    result = response.json()
    package_path = result['files']['zip']
```

### **3. Syncing Status Between APIs**

```python
# Main API syncs FROM BoomiToIS-API

boomi_job = requests.get(f"{BOOMI_API_URL}/api/jobs/{boomi_job_id}").json()

if boomi_job['status'] == 'completed':
    update_job(main_job_id, {
        'status': 'completed',
        'boomi_job_data': boomi_job
    })
```

### **4. Logging RAG Queries**

```python
# agentic-rag-IMigrate/agent/rag_logger.py

self.rag_logger.log_query(
    query=user_query,
    query_type="intent_understanding",
    context={"platform": "boomi"}
)

self.rag_logger.log_component_selection(
    selected_components=components,
    reason="Strategic plan execution"
)
```

---

## JSON Blueprint Reference

### **Component Structure**

```json
{
  "type": "RequestReply",
  "name": "FetchEmployeeData",
  "adapter_type": "OData",
  "protocol": "OData V2",
  "target_system": "SAP_SuccessFactors",
  "authentication": "OAuth2",
  "endpoint": "/odata/v2/EmpJob",
  "operation": "Query(GET)",
  "resourcePath": "EmpJob",
  "query_params": {
    "$filter": "userId eq '12345'",
    "$select": "userId,firstName,lastName"
  }
}
```

### **Router Component**

```json
{
  "type": "Router",
  "name": "RouteByStatus",
  "branch_count": 2,
  "routing_criteria": "status field",
  "branch_targets": ["OData", "Mail"],
  "branches": [
    {
      "branch_number": 1,
      "condition": "${property.status} = 'active'",
      "components": ["FetchFromOData"]
    },
    {
      "branch_number": 2,
      "condition": "${property.status} = 'inactive'",
      "components": ["SendNotificationEmail"]
    }
  ]
}
```

### **Timer Component**

```json
{
  "type": "Timer",
  "name": "SchedulePolling",
  "schedule": "*/5 * * * *",  // Every 5 minutes
  "schedule_type": "cron",
  "on_component": "PollSFTP"
}
```

---

## Contributing Guidelines

### **Code Style**

**Python:**
- PEP 8 compliant
- Type hints for function signatures
- Docstrings for all public methods
- Max line length: 120 characters

**JavaScript:**
- ESLint + Prettier
- Functional components with hooks
- PropTypes for all components

### **Git Workflow**

```bash
# Create feature branch
git checkout -b feature/add-sterling-support

# Make changes
git add .
git commit -m "feat: add Sterling platform support"

# Push and create PR
git push origin feature/add-sterling-support
```

### **Commit Messages**

Follow Conventional Commits:
```
feat: add new feature
fix: bug fix
docs: documentation changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

### **Pull Request Template**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex logic
- [ ] Documentation updated
- [ ] No new warnings
```

---

## Debugging

### **Enable Debug Mode**

```python
# app/app.py
app.config['DEBUG'] = True

# agentic-rag-IMigrate/config.py
LOGGING_LEVEL = logging.DEBUG
```

### **Common Debug Patterns**

```python
# Add breakpoints
import pdb; pdb.set_trace()

# Log request/response
logging.debug(f"Request: {request.json}")
logging.debug(f"Response: {response.json()}")

# Profile slow operations
import time
start = time.time()
# ... operation ...
logging.info(f"Operation took {time.time() - start:.2f}s")
```

### **Frontend Debugging**

```javascript
// Enable verbose logging
localStorage.setItem('debug', '*');

// Log all API calls
console.log('API Request:', endpoint, data);
console.log('API Response:', response);

// React DevTools
// Install: https://react.dev/learn/react-developer-tools
```

---

## Performance Optimization

### **Backend Caching**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def query_pattern_library(trigger_phrase: str):
    # Cached for repeated queries
    return supabase.table('component_pattern_library')...
```

### **Frontend Optimization**

```javascript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  // Only re-renders when data changes
});

// Debounce polling
const debouncedPoll = useMemo(
  () => debounce(pollJob, 5000),
  [jobId]
);
```

---

## Useful Commands

```bash
# Find all TODOs in code
grep -r "TODO" --include="*.py" --include="*.jsx"

# Count lines of code
cloc app/ BoomiToIS-API/ agentic-rag-IMigrate/ IFA-Project/frontend/src/

# Find large files
find . -type f -size +1M

# Check Python dependencies
pip list --outdated

# Check npm dependencies
cd IFA-Project/frontend && npm outdated
```

---

## Resources

- **LangChain Docs:** https://python.langchain.com/
- **Anthropic API:** https://docs.anthropic.com/
- **SAP Integration Suite:** https://help.sap.com/docs/integration-suite
- **Neo4j Cypher:** https://neo4j.com/docs/cypher-manual/
- **Supabase:** https://supabase.com/docs
- **React:** https://react.dev/

---

**Happy coding!** 🚀

**See `ARCHITECTURE.md` for system design**  
**See `DEPLOYMENT_GUIDE.md` for setup**  
**See `FEEDBACK_AND_LEARNING.md` for AI learning**



---

# TECHNICAL GUIDE: Job ID Tracking

# Job ID Tracking Across APIs

## TL;DR

**Frontend is polling for STATUS, not just the ID.** It checks: `GET /api/jobs/{mainJobId}` repeatedly to see if `status` changed from `documentation_completed` → `completed`.

**Two separate Job IDs exist:**
1. **Main API Job ID** (`2d838513-613b-4cf0-a6bd-78c95fb91e9d`) - Frontend always uses this
2. **BoomiToIS-API Job ID** (generated internally) - Only used by BoomiToIS-API

**They are tracked via `original_job_id` field in BoomiToIS-API.**

---

## Complete Job ID Flow

### 1. Initial Upload/Documentation (Main API)

```
User uploads file → Main API (port 5000)
     ↓
Creates: job_id = "2d838513-613b-4cf0-a6bd-78c95fb91e9d"
     ↓
Stores in: app/jobs/jobs.json
     ↓
Status: "documentation_completed"
```

**Main API Job Record:**
```json
{
  "id": "2d838513-613b-4cf0-a6bd-78c95fb91e9d",
  "status": "documentation_completed",
  "platform": "boomi",
  "source_type": "uploaded_xml",
  "files": {
    "markdown": "results/2d838513.../boomi_documentation.md",
    "json": "results/2d838513.../boomi_parsed.json"
  }
}
```

---

### 2. User Clicks "Generate iFlow" Button

```
Frontend → POST /api/generate-iflow/2d838513-613b-4cf0-a6bd-78c95fb91e9d
     ↓
Routed to: BoomiToIS-API (port 5003)
     ↓
BoomiToIS-API receives: job_id = "2d838513-613b-4cf0-a6bd-78c95fb91e9d"
     ↓
Creates NEW internal job: iflow_job_id = "a7f8e4c2-1234-5678-abcd-ef9012345678"
     ↓
Stores mapping: original_job_id = "2d838513-613b-4cf0-a6bd-78c95fb91e9d"
```

**BoomiToIS-API Job Record:**
```python
# File: BoomiToIS-API/app.py, Line 309
jobs[iflow_job_id] = {
    'id': 'a7f8e4c2-1234-5678-abcd-ef9012345678',  # NEW BoomiToIS job ID
    'original_job_id': '2d838513-613b-4cf0-a6bd-78c95fb91e9d',  # ← Main API job ID
    'status': 'queued',
    'created': '...',
    'message': 'Job queued. Starting iFlow generation...'
}
```

**Stored in:** `BoomiToIS-API/results/jobs.json`

---

### 3. iFlow Generation (RAG API)

```
BoomiToIS-API → POST /api/generate-iflow-from-markdown
     ↓
Sends: {
  "markdown_content": "...",
  "job_id": "2d838513-613b-4cf0-a6bd-78c95fb91e9d",  ← Passes MAIN job ID!
  "iflow_name": "IFlow_2d838513"
}
     ↓
RAG API (port 5001) generates iFlow
     ↓
Creates: generated_packages/Processing_Integration_Complete_20251023_180637.zip
     ↓
Returns success to BoomiToIS-API
```

**Key Line:** `BoomiToIS-API/app.py:392-404`
```python
# Get the original main job ID (not the BoomiToIS job ID)
main_job_id = jobs[job_id].get('original_job_id', job_id)

# Call RAG API with MAIN job ID
rag_response = requests.post(
    f"{RAG_API_URL}/api/generate-iflow-from-markdown",
    json={
        'markdown_content': markdown_content,
        'iflow_name': iflow_name,
        'job_id': main_job_id,  # ← Pass the MAIN job ID, not BoomiToIS job ID
        'output_dir': job_result_dir
    }
)
```

---

### 4. Status Update After Completion (THE FIX!)

```
RAG API returns success
     ↓
BoomiToIS-API receives success
     ↓
Updates its own job: jobs[iflow_job_id]['status'] = 'completed'
     ↓
ALSO updates Main API: ← NEW! (Lines 526-566)
     ↓
PUT http://localhost:5000/api/jobs/2d838513-613b-4cf0-a6bd-78c95fb91e9d
Body: {
  "status": "completed",
  "processing_message": "iFlow generation completed successfully!",
  "iflow_package_path": "...",
  "package_path": "..."
}
     ↓
Main API updates: jobs["2d838513-613b-4cf0-a6bd-78c95fb91e9d"]["status"] = "completed"
```

**Key Lines:** `BoomiToIS-API/app.py:526-566`
```python
# Update Main API with completion status
try:
    main_job_id = jobs[job_id].get('original_job_id')  # ← Get Main API job ID
    if main_job_id:
        logger.info(f"📡 Updating Main API job {main_job_id} to 'completed' status")
        
        # Get Main API URL
        MAIN_API_URL = os.getenv('MAIN_API_URL', 'http://localhost:5000')
        
        # Update Main API job status
        update_response = requests.put(
            f"{MAIN_API_URL}/api/jobs/{main_job_id}",  # ← Uses Main API job ID!
            json={
                'status': 'completed',
                'processing_message': 'iFlow generation completed successfully!',
                'iflow_package_path': zip_path,
                'package_path': zip_path,
                'iflow_name': iflow_name
            }
        )
```

---

### 5. Frontend Polling (What You're Seeing)

```
Frontend polls every 2 seconds:
     ↓
GET /api/jobs/2d838513-613b-4cf0-a6bd-78c95fb91e9d  ← Always uses Main API job ID
     ↓
Main API returns: {
  "id": "2d838513-613b-4cf0-a6bd-78c95fb91e9d",
  "status": "completed",  ← Changed from "documentation_completed"!
  "iflow_package_path": "...",
  "package_path": "..."
}
     ↓
Frontend detects: status === "completed"
     ↓
Button changes to: "SAP API/iFlow Generated" ✅
     ↓
Stops polling
```

**Frontend Code:** `IFA-Project/frontend/src/services/api.js:161-179`
```javascript
export const getJobStatus = async (jobId, jobInfo = null, platform = 'boomi') => {
    try {
        // For documentation jobs, use the main app API
        console.log(`🔍 getJobStatus using main app API: ${api.defaults.baseURL}`);
        const response = await api.get(`/jobs/${jobId}`);  // ← Always Main API job ID
        return response.data;
    } catch (error) {
        console.error("Error getting job status:", error)
        throw error
    }
}
```

---

## Job ID Mapping Table

| Location | Job ID | Purpose | Stored Where |
|----------|--------|---------|--------------|
| **Main API** | `2d838513-613b-4cf0-a6bd-78c95fb91e9d` | Primary job tracking | `app/jobs/jobs.json` |
| **BoomiToIS-API** | `a7f8e4c2-1234-5678-abcd-ef9012345678` | Internal iFlow generation tracking | `BoomiToIS-API/results/jobs.json` |
| **BoomiToIS-API** | `original_job_id: 2d838513...` | Reference to Main API job | `BoomiToIS-API/results/jobs.json` |
| **Frontend** | `2d838513-613b-4cf0-a6bd-78c95fb91e9d` | Always uses Main API job ID | State/props |

---

## Deployment: How Job ID Mapping Works

When deploying to SAP BTP, the frontend sends the **Main API job ID**, but BoomiToIS-API needs to find the **BoomiToIS job ID** with the actual ZIP file:

**Code:** `BoomiToIS-API/app.py:822-834`
```python
# First, check if this is a documentation job ID that was used to generate an iFlow
iflow_job_id = None
for jid, job_data in jobs.items():
    if job_data.get('original_job_id') == job_id:  # ← Search by Main API job ID
        # Found an iFlow job that was generated from this documentation job
        iflow_job_id = jid  # ← Get BoomiToIS job ID
        logger.info(f"Found iFlow job {iflow_job_id} that was generated from documentation job {job_id}")
        break

# If we found an iFlow job ID, use that instead
if iflow_job_id:
    logger.info(f"Using iFlow job ID {iflow_job_id} instead of documentation job ID {job_id}")
    job_id = iflow_job_id  # ← Switch to BoomiToIS job ID for file access
```

---

## Why Two Job IDs?

### Separation of Concerns

1. **Main API (port 5000)**:
   - Handles file uploads (XML/ZIP/Documentation)
   - Parses and generates documentation
   - Tracks overall job lifecycle
   - **Job ID lives through entire workflow**

2. **BoomiToIS-API (port 5003)**:
   - Only handles iFlow generation
   - Creates temporary job for generation tracking
   - May be called multiple times for same Main API job
   - **Job ID only exists during generation**

### Why Not Use Same ID?

**Scenario:**
```
User uploads Boomi XML → Main API job: "abc123"
   ↓
Documentation generated → Status: "documentation_completed"
   ↓
User clicks "Generate iFlow" → BoomiToIS-API creates: "xyz789"
   ↓
Generation fails, user clicks again → BoomiToIS-API creates: "qwe456"
   ↓
Main API job "abc123" still exists with 2 generation attempts
```

**Benefits:**
- ✅ Multiple generation attempts don't overwrite Main API job
- ✅ Clear audit trail of generation attempts
- ✅ BoomiToIS-API can be restarted without affecting Main API
- ✅ Each service manages its own job lifecycle

---

## How to Track Job IDs

### In Browser Console

**Frontend always shows Main API job ID:**
```javascript
console.log("Checking status for job 2d838513-613b-4cf0-a6bd-78c95fb91e9d...")
// This is the Main API job ID - frontend never sees BoomiToIS job ID
```

### In BoomiToIS-API Logs

**Shows both IDs:**
```
📡 Sending request to RAG API: http://localhost:5001/api/generate-iflow-from-markdown
   Main Job ID: 2d838513-613b-4cf0-a6bd-78c95fb91e9d (BoomiToIS Job ID: a7f8e4c2-1234-5678-abcd-ef9012345678)
```

### In Main API Logs

**Only sees its own job ID:**
```
PUT /api/jobs/2d838513-613b-4cf0-a6bd-78c95fb91e9d HTTP/1.1" 200
```

---

## Polling Behavior

### What Frontend Is Checking

```javascript
// View.jsx:676-691
const response = await fetch(`/api/jobs/${jobId}`);  // Main API job ID
const data = await response.json();

// Check STATUS, not ID
if (data.status === "failed" ||
    (data.status === "completed" &&
     (data.deployment_status === "completed" || data.deployment_status === "failed"))) {
  // Stop polling ✅
} else if (data.status === "documentation_completed") {
  // Keep polling - waiting for iFlow generation ⏳
} else if (data.status === "completed" && !data.deployment_status) {
  // Keep polling - waiting for deployment ⏳
}
```

### Polling is for STATUS changes:
- `documentation_completed` → `completed` (iFlow generation done)
- `completed` → `deployment_status: "completed"` (deployment done)
- Any → `failed` (error occurred)

---

## Summary

| Question | Answer |
|----------|--------|
| **What is frontend polling for?** | **STATUS** of Main API job (not just ID) |
| **Which job ID does frontend use?** | Always **Main API job ID** (`2d838513...`) |
| **Does BoomiToIS-API have different ID?** | **Yes!** Internal ID (`a7f8e4c2...`) |
| **How are they linked?** | Via `original_job_id` field in BoomiToIS job |
| **Who updates Main API status?** | BoomiToIS-API after iFlow generation completes |
| **What if IDs get out of sync?** | Deployment endpoint searches by `original_job_id` |

**Frontend never sees or cares about BoomiToIS job ID - it only polls Main API job ID for status changes!** 🎯




---

# ADDITIONAL DEVELOPMENT NOTES

# IMigrate Developer Guide

Developer documentation for contributing to and customizing the SAP Integration Suite migration platform.

---

## Table of Contents

1. [Code Structure](#code-structure)
2. [API Documentation](#api-documentation)
3. [Adding New Features](#adding-new-features)
4. [Testing](#testing)
5. [Common Patterns](#common-patterns)
6. [JSON Blueprint Reference](#json-blueprint-reference)
7. [Contributing Guidelines](#contributing-guidelines)

---

## Code Structure

```
IMigrate/
├── app/                          # Main API (Flask, Port 5000)
│   ├── app.py                    # Main entry point
│   ├── boomi_flow_documentation.py  # Boomi parser
│   ├── mule_flow_documentation.py   # MuleSoft parser
│   └── jobs.json                 # Local job tracking
│
├── BoomiToIS-API/                # iFlow Generation API (Flask, Port 5003)
│   ├── app.py                    # iFlow generation entry
│   ├── sap_btp_integration.py    # SAP BTP deployment
│   ├── direct_iflow_deployment.py  # Direct deploy method
│   ├── feedback_api.py           # Feedback endpoints
│   └── jobs.json                 # iFlow generation jobs
│
├── agentic-rag-IMigrate/         # RAG Agent (Flask, Port 8001)
│   ├── rag_api_service.py        # Flask API wrapper
│   ├── agent/
│   │   ├── agent.py              # SAP iFlow Agent (main logic)
│   │   ├── packager.py           # ZIP package builder
│   │   ├── rag_logger.py         # Query/result logging
│   │   └── iflow_similarity.py   # Neo4j similarity search
│   ├── config.py                 # Centralized config
│   └── generated_packages/       # Output ZIP files
│
├── IFA-Project/frontend/         # React Frontend (Vite, Port 5173)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── common/JobResult.jsx        # Main job page
│   │   │   ├── common/FileUploadForm.jsx   # File upload
│   │   │   └── IFATool/View.jsx            # Job list
│   │   ├── components/
│   │   │   └── FeedbackModal.jsx           # Feedback UI
│   │   └── services/
│   │       └── api.js             # API client
│   └── vite.config.js             # Proxy configuration
│
└── [5 Core Documentation Files]   # ← This is the new structure!
    ├── README.md
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT_GUIDE.md
    ├── FEEDBACK_AND_LEARNING.md
    └── DEVELOPMENT.md
```

---

## API Documentation

### **1. Main API (Port 5000)**

#### **POST /api/upload-documentation**
Upload Boomi/MuleSoft file for documentation generation.

**Request:**
```bash
curl -X POST http://localhost:5000/api/upload-documentation \
  -F "file=@boomi_process.xml" \
  -F "platform=boomi" \
  -F "llm_provider=anthropic"
```

**Response:**
```json
{
  "job_id": "abc-123",
  "status": "queued",
  "message": "Job created successfully"
}
```

#### **GET /api/jobs/:job_id**
Get job status.

**Response:**
```json
{
  "id": "abc-123",
  "status": "documentation_completed",
  "processing_message": "Ready for iFlow generation",
  "files": {
    "markdown": "results/abc-123/boomi_documentation.md"
  },
  "created": "2025-10-23T10:00:00Z"
}
```

**Status Values:**
- `processing` - Generating documentation
- `documentation_completed` - Docs ready, iFlow NOT generated
- `generating_iflow` - iFlow generation in progress
- `completed` - iFlow generated ✅
- `failed` - Error occurred

#### **GET /api/docs/:job_id/markdown**
Retrieve generated markdown documentation.

### **2. BoomiToIS-API (Port 5003)**

#### **POST /api/generate-iflow**
Generate iFlow from markdown documentation.

**Request:**
```bash
curl -X POST http://localhost:5003/api/generate-iflow \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "# Integration Flow...",
    "iflow_name": "MyIntegration",
    "use_rag": true
  }'
```

**Response:**
```json
{
  "job_id": "def-456",
  "status": "queued",
  "message": "iFlow generation started"
}
```

#### **POST /api/jobs/:job_id/direct-deploy**
Deploy generated iFlow to SAP BTP.

**Request:**
```bash
curl -X POST http://localhost:5003/api/jobs/def-456/direct-deploy \
  -H "Content-Type: application/json" \
  -d '{
    "iflow_name": "MyIntegration",
    "sap_package_id": "IMigrateTest"
  }'
```

**Response:**
```json
{
  "status": "success",
  "iflow_name": "MyIntegration",
  "package_id": "IMigrateTest",
  "deployment_url": "https://..."
}
```

#### **POST /api/feedback/submit**
Submit user feedback.

**Request:**
```json
{
  "job_id": "abc-123",
  "source_platform": "boomi",
  "overall_rating": 5,
  "documentation_quality_rating": 5,
  "iflow_quality_rating": 4,
  "component_mapping_accuracy": 8,
  "config_accuracy": 7,
  "missing_components": [],
  "what_worked_well": ["All components captured"],
  "what_needs_improvement": [],
  "time_to_fix_minutes": 5,
  "deployment_successful": true
}
```

### **3. RAG Agent API (Port 8001)**

#### **POST /api/generate-iflow-from-markdown**
Generate iFlow using RAG agent.

**Request:**
```json
{
  "markdown_content": "# Integration Flow...",
  "iflow_name": "MyIntegration",
  "job_id": "abc-123"
}
```

**Response:**
```json
{
  "status": "success",
  "files": {
    "zip": "generated_packages/MyIntegration_20251023.zip"
  },
  "components": [
    {"type": "Timer", "name": "SchedulePolling"},
    {"type": "SFTP", "name": "PollFiles"},
    {"type": "GroovyScript", "name": "TransformData"}
  ],
  "generation_method": "RAG Agent (Dynamic)"
}
```

---

## Adding New Features

### **1. Add New Platform Support (e.g., Sterling)**

#### **Step 1: Create Parser**
```python
# app/sterling_flow_documentation.py

class SterlingFlowDocumentationGenerator:
    def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Parse Sterling files"""
        # Extract flows, connectors, etc.
        pass
    
    def generate_documentation(self, results: Dict) -> str:
        """Generate markdown"""
        pass
```

#### **Step 2: Add Route in Main API**
```python
# app/app.py

@app.route('/api/upload-documentation', methods=['POST'])
def upload_documentation():
    platform = request.form.get('platform')  # Now includes 'sterling'
    
    if platform == 'sterling':
        return process_sterling_documentation(job_id, input_dir)
```

#### **Step 3: Add Frontend Support**
```javascript
// IFA-Project/frontend/src/pages/common/FileUploadForm.jsx

const platforms = [
  { value: 'boomi', label: 'Dell Boomi' },
  { value: 'mulesoft', label: 'MuleSoft' },
  { value: 'sterling', label: 'IBM Sterling' }  // ← Add this
];
```

### **2. Add New Component Type**

#### **Step 1: Add to Pattern Library**
```sql
INSERT INTO component_pattern_library (
  trigger_phrase,
  component_type,
  pattern_category,
  confidence_score
) VALUES (
  'encrypt.*data',
  'Encryptor',
  'security',
  0.85
);
```

#### **Step 2: Add XML Template**
```python
# agentic-rag-IMigrate/agent/agent.py

async def _generate_component_xml(self, component_type, ...):
    if component_type == 'Encryptor':
        return self._generate_encryptor_xml(...)
    
def _generate_encryptor_xml(self, ...):
    return f"""
    <bpmn2:serviceTask id="{component_id}" name="{name}">
      <bpmn2:extensionElements>
        <ifl:property>
          <key>encryptionAlgorithm</key>
          <value>AES-256</value>
        </key>
      </bpmn2:extensionElements>
    </bpmn2:serviceTask>
    """
```

#### **Step 3: Add to Knowledge Graph** (Optional)
```python
# agentic-rag-IMigrate/agent/iflow_similarity.py

def add_component_to_kg(self, component_xml, component_type='Encryptor'):
    with self.driver.session() as session:
        session.run("""
          CREATE (c:Component {
            id: $id,
            type: $type,
            xml: $xml
          })
        """, id=component_id, type=component_type, xml=component_xml)
```

### **3. Add New LLM Provider (e.g., OpenAI GPT-4)**

#### **Step 1: Add Config**
```python
# agentic-rag-IMigrate/config.py

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'anthropic')  # 'openai', 'anthropic', 'gemma3'
```

#### **Step 2: Add LLM Client**
```python
# agentic-rag-IMigrate/agent/agent.py

def _get_llm_client(self):
    if self.llm_provider == 'openai':
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4", api_key=OPENAI_API_KEY)
    elif self.llm_provider == 'anthropic':
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-3-5-sonnet-20241022")
```

---

## Testing

### **Unit Tests**

```python
# tests/test_agent.py

import pytest
from agent.agent import SAPiFlowAgent

def test_intent_understanding():
    agent = SAPiFlowAgent()
    intent = agent._understand_user_intent(
        "Poll SFTP every 5 minutes and post to OData"
    )
    
    assert 'Timer' in [c['type'] for c in intent['components']]
    assert 'SFTP' in [c['type'] for c in intent['components']]
    assert 'RequestReply' in [c['type'] for c in intent['components']]

def test_component_generation():
    agent = SAPiFlowAgent()
    xml = await agent._generate_component_xml(
        component_type='Timer',
        component_name='SchedulePolling'
    )
    
    assert '<bpmn2:startEvent' in xml
    assert 'ifl:schedule' in xml
```

### **Integration Tests**

```python
# tests/test_integration.py

def test_full_flow():
    # Upload file
    response = client.post('/api/upload-documentation',
        data={'file': open('test.xml'), 'platform': 'boomi'})
    job_id = response.json['job_id']
    
    # Wait for completion
    while True:
        status = client.get(f'/api/jobs/{job_id}').json
        if status['status'] == 'documentation_completed':
            break
    
    # Generate iFlow
    response = client.post('/api/generate-iflow',
        json={'job_id': job_id, 'iflow_name': 'Test'})
    
    assert response.status_code == 200
```

### **Frontend Tests**

```javascript
// IFA-Project/frontend/src/tests/JobResult.test.jsx

import { render, screen, waitFor } from '@testing/library/react';
import JobResult from '../pages/common/JobResult';

test('shows Generate iFlow button after documentation completes', async () => {
  render(<JobResult jobInfo={{status: 'documentation_completed'}} />);
  
  const button = await screen.findByText(/Generate SAP API\/iFlow/i);
  expect(button).toBeInTheDocument();
  expect(button).not.toBeDisabled();
});
```

---

## Common Patterns

### **1. Adding New Status**

**Backend:**
```python
# app/app.py
update_job(job_id, {
    'status': 'new_status_here',
    'processing_message': 'Doing new thing...'
})
```

**Frontend:**
```javascript
// JobResult.jsx
if (jobInfo.status === 'new_status_here') {
  return <div>New status UI</div>;
}
```

### **2. Calling RAG Agent**

```python
# BoomiToIS-API/app.py

import requests

response = requests.post(
    f"{RAG_API_URL}/api/generate-iflow-from-markdown",
    json={
        'markdown_content': markdown,
        'iflow_name': iflow_name,
        'job_id': job_id
    },
    timeout=1200  # 20 minutes
)

if response.status_code == 200:
    result = response.json()
    package_path = result['files']['zip']
```

### **3. Syncing Status Between APIs**

```python
# Main API syncs FROM BoomiToIS-API

boomi_job = requests.get(f"{BOOMI_API_URL}/api/jobs/{boomi_job_id}").json()

if boomi_job['status'] == 'completed':
    update_job(main_job_id, {
        'status': 'completed',
        'boomi_job_data': boomi_job
    })
```

### **4. Logging RAG Queries**

```python
# agentic-rag-IMigrate/agent/rag_logger.py

self.rag_logger.log_query(
    query=user_query,
    query_type="intent_understanding",
    context={"platform": "boomi"}
)

self.rag_logger.log_component_selection(
    selected_components=components,
    reason="Strategic plan execution"
)
```

---

## JSON Blueprint Reference

### **Component Structure**

```json
{
  "type": "RequestReply",
  "name": "FetchEmployeeData",
  "adapter_type": "OData",
  "protocol": "OData V2",
  "target_system": "SAP_SuccessFactors",
  "authentication": "OAuth2",
  "endpoint": "/odata/v2/EmpJob",
  "operation": "Query(GET)",
  "resourcePath": "EmpJob",
  "query_params": {
    "$filter": "userId eq '12345'",
    "$select": "userId,firstName,lastName"
  }
}
```

### **Router Component**

```json
{
  "type": "Router",
  "name": "RouteByStatus",
  "branch_count": 2,
  "routing_criteria": "status field",
  "branch_targets": ["OData", "Mail"],
  "branches": [
    {
      "branch_number": 1,
      "condition": "${property.status} = 'active'",
      "components": ["FetchFromOData"]
    },
    {
      "branch_number": 2,
      "condition": "${property.status} = 'inactive'",
      "components": ["SendNotificationEmail"]
    }
  ]
}
```

### **Timer Component**

```json
{
  "type": "Timer",
  "name": "SchedulePolling",
  "schedule": "*/5 * * * *",  // Every 5 minutes
  "schedule_type": "cron",
  "on_component": "PollSFTP"
}
```

---

## Contributing Guidelines

### **Code Style**

**Python:**
- PEP 8 compliant
- Type hints for function signatures
- Docstrings for all public methods
- Max line length: 120 characters

**JavaScript:**
- ESLint + Prettier
- Functional components with hooks
- PropTypes for all components

### **Git Workflow**

```bash
# Create feature branch
git checkout -b feature/add-sterling-support

# Make changes
git add .
git commit -m "feat: add Sterling platform support"

# Push and create PR
git push origin feature/add-sterling-support
```

### **Commit Messages**

Follow Conventional Commits:
```
feat: add new feature
fix: bug fix
docs: documentation changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

### **Pull Request Template**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex logic
- [ ] Documentation updated
- [ ] No new warnings
```

---

## Debugging

### **Enable Debug Mode**

```python
# app/app.py
app.config['DEBUG'] = True

# agentic-rag-IMigrate/config.py
LOGGING_LEVEL = logging.DEBUG
```

### **Common Debug Patterns**

```python
# Add breakpoints
import pdb; pdb.set_trace()

# Log request/response
logging.debug(f"Request: {request.json}")
logging.debug(f"Response: {response.json()}")

# Profile slow operations
import time
start = time.time()
# ... operation ...
logging.info(f"Operation took {time.time() - start:.2f}s")
```

### **Frontend Debugging**

```javascript
// Enable verbose logging
localStorage.setItem('debug', '*');

// Log all API calls
console.log('API Request:', endpoint, data);
console.log('API Response:', response);

// React DevTools
// Install: https://react.dev/learn/react-developer-tools
```

---

## Performance Optimization

### **Backend Caching**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def query_pattern_library(trigger_phrase: str):
    # Cached for repeated queries
    return supabase.table('component_pattern_library')...
```

### **Frontend Optimization**

```javascript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  // Only re-renders when data changes
});

// Debounce polling
const debouncedPoll = useMemo(
  () => debounce(pollJob, 5000),
  [jobId]
);
```

---

## Useful Commands

```bash
# Find all TODOs in code
grep -r "TODO" --include="*.py" --include="*.jsx"

# Count lines of code
cloc app/ BoomiToIS-API/ agentic-rag-IMigrate/ IFA-Project/frontend/src/

# Find large files
find . -type f -size +1M

# Check Python dependencies
pip list --outdated

# Check npm dependencies
cd IFA-Project/frontend && npm outdated
```

---

## Resources

- **LangChain Docs:** https://python.langchain.com/
- **Anthropic API:** https://docs.anthropic.com/
- **SAP Integration Suite:** https://help.sap.com/docs/integration-suite
- **Neo4j Cypher:** https://neo4j.com/docs/cypher-manual/
- **Supabase:** https://supabase.com/docs
- **React:** https://react.dev/

---

**Happy coding!** 🚀

**See `ARCHITECTURE.md` for system design**  
**See `DEPLOYMENT_GUIDE.md` for setup**  
**See `FEEDBACK_AND_LEARNING.md` for AI learning**


