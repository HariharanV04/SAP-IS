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

