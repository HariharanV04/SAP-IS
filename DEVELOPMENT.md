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

