# Supabase Job Tracking Setup Guide

Complete guide for setting up real-time iFlow job tracking with Supabase.

**Date Created**: 2025-01-17
**Status**: ✅ Ready for Deployment

---

## 📋 Overview

This guide will help you:
1. Create the Supabase database schema
2. Verify the schema is working
3. Test backend integration
4. Connect frontend to real-time data

---

## 🚀 Step 1: Apply Database Schema

### 1.1 Access Supabase SQL Editor

1. Go to your Supabase project: https://supabase.com/dashboard/project/jnoobtfelhtjfermohfx
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query"

### 1.2 Run the Schema SQL

1. Open the file: `/IMigrate/supabase_job_tracking_schema.sql`
2. Copy the entire contents (all ~414 lines)
3. Paste into the SQL Editor
4. Click "Run" button

### 1.3 Verify Schema Creation

You should see output like:
```
NOTICE:  IMigrate Job Tracking Schema created successfully!
NOTICE:  Tables: iflow_jobs, iflow_components, rag_retrievals, iflow_generation_logs
NOTICE:  Views: iflow_jobs_summary, recent_jobs_with_details
NOTICE:  Ready to track iFlow generation jobs!
```

### 1.4 Check Tables Were Created

1. Go to "Table Editor" in Supabase dashboard
2. You should see 4 new tables:
   - `iflow_jobs`
   - `iflow_components`
   - `rag_retrievals`
   - `iflow_generation_logs`

---

## 🔍 Step 2: Verify Schema

### 2.1 Check Sample Data

Run this query in SQL Editor:
```sql
SELECT * FROM iflow_jobs ORDER BY created_at DESC LIMIT 5;
```

You should see 1 sample job (created by the schema).

### 2.2 Check Views

Run this query:
```sql
SELECT * FROM iflow_jobs_summary LIMIT 5;
```

You should see job summary with aggregated statistics.

### 2.3 Check Indexes

Run this query:
```sql
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('iflow_jobs', 'iflow_components', 'rag_retrievals', 'iflow_generation_logs')
ORDER BY tablename, indexname;
```

You should see multiple indexes for performance.

---

## 🔐 Step 3: Environment Variables

### 3.1 Add Supabase Credentials to .env Files

The credentials are already in the codebase, but verify they're in these files:

**Main API** (`/IMigrate/app/.env.local`):
```bash
SUPABASE_URL=https://jnoobtfelhtjfermohfx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impub29idGZlbGh0amZlcm1vaGZ4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzE0MTkxNiwiZXhwIjoyMDUyNzE3OTE2fQ.HHDbKhMxnDRe0nZ5v0FkwzLYbsS93U5xVEO76QAkjl4
```

**BoomiToIS-API** (`/IMigrate/BoomiToIS-API/.env.production`):
```bash
SUPABASE_URL=https://jnoobtfelhtjfermohfx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impub29idGZlbGh0amZlcm1vaGZ4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzE0MTkxNiwiZXhwIjoyMDUyNzE3OTE2fQ.HHDbKhMxnDRe0nZ5v0FkwzLYbsS93U5xVEO76QAkjl4
```

**MuleToIS-API** (`/IMigrate/MuleToIS-API/.env.production`):
```bash
SUPABASE_URL=https://jnoobtfelhtjfermohfx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impub29idGZlbGh0amZlcm1vaGZ4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzE0MTkxNiwiZXhwIjoyMDUyNzE3OTE2fQ.HHDbKhMxnDRe0nZ5v0FkwzLYbsS93U5xVEO76QAkjl4
```

**RAG API Service** (`/IMigrate/agentic-rag-IMigrate/config.py`):
Already configured on lines 12-13.

---

## 🧪 Step 4: Test Backend Integration

### 4.1 Install Python Dependencies

If not already installed:
```bash
cd /IMigrate
pip install supabase
```

### 4.2 Test Job Tracker Utility

Create a test script `/IMigrate/test_supabase_job_tracker.py`:
```python
#!/usr/bin/env python3
"""Test Supabase Job Tracker"""

import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from utils.supabase_job_tracker import get_job_tracker
import uuid

print("="*80)
print("Testing Supabase Job Tracker")
print("="*80)

# Initialize tracker
try:
    tracker = get_job_tracker()
    print("✅ Job tracker initialized")
except Exception as e:
    print(f"❌ Failed to initialize job tracker: {e}")
    sys.exit(1)

# Create a test job
try:
    job_id = str(uuid.uuid4())
    print(f"\n📝 Creating test job: {job_id}")

    job = tracker.create_job(
        job_id=job_id,
        platform='mulesoft',
        source_file_name='test_integration.xml',
        source_file_size=1024,
        user_id='test_user',
        llm_provider='anthropic',
        metadata={'test': True}
    )

    print(f"✅ Job created: {job['job_id']}")
    print(f"   Status: {job['status']}")
    print(f"   Progress: {job['progress']}%")
except Exception as e:
    print(f"❌ Failed to create job: {e}")
    sys.exit(1)

# Update job status
try:
    print(f"\n🔄 Updating job status...")

    updated_job = tracker.update_job_status(
        job_id=job_id,
        status='processing',
        progress=50,
        current_step='analyzing'
    )

    print(f"✅ Job updated: {updated_job['status']} - {updated_job['progress']}%")
except Exception as e:
    print(f"❌ Failed to update job: {e}")
    sys.exit(1)

# Add a component
try:
    print(f"\n🧩 Adding test component...")

    component = tracker.add_component(
        job_id=job_id,
        component_type='StartEvent',
        component_name='Start 1',
        component_order=1,
        source='template'
    )

    print(f"✅ Component added: {component['component_name']}")
except Exception as e:
    print(f"❌ Failed to add component: {e}")
    sys.exit(1)

# Get job summary
try:
    print(f"\n📊 Getting job summary...")

    summary = tracker.get_job_summary(job_id)

    print(f"✅ Job Summary:")
    print(f"   Status: {summary['job']['status']}")
    print(f"   Components: {summary['statistics']['total_components']}")
    print(f"   Retrievals: {summary['statistics']['total_retrievals']}")
except Exception as e:
    print(f"❌ Failed to get job summary: {e}")
    sys.exit(1)

# Complete the job
try:
    print(f"\n✅ Completing job...")

    completed_job = tracker.update_job_status(
        job_id=job_id,
        status='completed',
        progress=100,
        current_step='completed'
    )

    print(f"✅ Job completed in {completed_job['duration_seconds']} seconds")
except Exception as e:
    print(f"❌ Failed to complete job: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("✅ All tests passed!")
print("="*80)
```

Run the test:
```bash
cd /IMigrate
python3 test_supabase_job_tracker.py
```

### 4.3 Verify Test Job in Supabase

1. Go to Supabase "Table Editor"
2. Select `iflow_jobs` table
3. You should see the test job with status "completed"

---

## 🌐 Step 5: Start Backend Services

### 5.1 Start Main API

```bash
cd /IMigrate/app
python3 app.py
```

You should see:
```
✅ Supabase job tracking enabled
```

### 5.2 Upload Test Documentation

Using the frontend or curl:
```bash
curl -X POST http://localhost:5000/api/upload-documentation \
  -F "file=@test_doc.md" \
  -F "platform=mulesoft" \
  -F "llm_provider=anthropic"
```

### 5.3 Check Job Was Created

Run in Supabase SQL Editor:
```sql
SELECT
    job_id,
    status,
    progress,
    current_step,
    source_file_name,
    created_at
FROM iflow_jobs
ORDER BY created_at DESC
LIMIT 5;
```

You should see your uploaded documentation job.

---

## 📡 Step 6: Add API Endpoints for Frontend

The Main API needs endpoints for the frontend to query job data. The following endpoints will be added:

### 6.1 Get Job Details
```
GET /api/jobs/:job_id
```

Returns:
- Job status, progress, current step
- Documentation text
- List of components
- RAG retrieval stats
- Generation logs

### 6.2 Get Recent Jobs
```
GET /api/jobs?limit=20
```

Returns list of recent jobs with summaries.

### 6.3 Get Job Logs
```
GET /api/jobs/:job_id/logs?level=ERROR
```

Returns generation logs for a job.

### 6.4 Get Real-Time Updates (WebSocket - Future)
```
ws://localhost:5000/ws/jobs/:job_id
```

Real-time job status updates (future enhancement).

---

## 🎨 Step 7: Update Frontend UI

### 7.1 Modify IFATool View Component

File: `/IMigrate/IFA-Project/frontend/src/pages/IFATool/View.jsx`

Replace the dummy progress screen with real Supabase data:

```javascript
import { useEffect, useState } from 'react';

const [jobData, setJobData] = useState(null);
const [jobLogs, setJobLogs] = useState([]);

// Fetch job data
useEffect(() => {
  if (!jobId) return;

  const fetchJobData = async () => {
    try {
      const response = await fetch(`/api/jobs/${jobId}`);
      const data = await response.json();
      setJobData(data);
    } catch (error) {
      console.error('Failed to fetch job data:', error);
    }
  };

  // Poll every 2 seconds while job is running
  const interval = setInterval(fetchJobData, 2000);
  fetchJobData(); // Initial fetch

  return () => clearInterval(interval);
}, [jobId]);

// Display real-time progress
{jobData && (
  <div className="job-progress">
    <h3>{jobData.status}</h3>
    <progress value={jobData.progress} max="100">{jobData.progress}%</progress>
    <p>Current Step: {jobData.current_step}</p>

    {jobData.components && (
      <div className="components-list">
        <h4>Components ({jobData.total_components})</h4>
        {jobData.components.map(comp => (
          <div key={comp.component_id}>
            {comp.component_type} - {comp.component_name}
            {comp.source === 'rag' && (
              <span>RAG (score: {comp.rag_similarity_score})</span>
            )}
          </div>
        ))}
      </div>
    )}

    {jobData.error_message && (
      <div className="error">
        Error: {jobData.error_message}
      </div>
    )}
  </div>
)}
```

---

## 🎯 Step 8: End-to-End Test

### 8.1 Complete Flow Test

1. **Start all services**:
   ```bash
   # Terminal 1: Main API
   cd /IMigrate/app && python3 app.py

   # Terminal 2: RAG API
   cd /IMigrate/agentic-rag-IMigrate && python3 rag_api_service.py

   # Terminal 3: Frontend
   cd /IMigrate/IFA-Project/frontend && npm run dev
   ```

2. **Upload documentation via UI**:
   - Go to http://localhost:3000
   - Click "IFA Tool"
   - Upload a test documentation file
   - Click "Generate Documentation"

3. **Watch real-time updates**:
   - UI should show progress bar moving
   - Status should update from "pending" → "processing" → "analyzing" → "generating" → "completed"
   - Components list should populate

4. **Verify in Supabase**:
   ```sql
   SELECT * FROM iflow_jobs ORDER BY created_at DESC LIMIT 1;
   SELECT * FROM iflow_components WHERE job_id = '<your-job-id>';
   SELECT * FROM rag_retrievals WHERE job_id = '<your-job-id>';
   ```

---

## 📊 Step 9: Monitor and Debug

### 9.1 Common Queries

**Get all jobs with errors**:
```sql
SELECT job_id, status, error_message, created_at
FROM iflow_jobs
WHERE status = 'failed'
ORDER BY created_at DESC;
```

**Get jobs by platform**:
```sql
SELECT platform, count(*) as total,
       AVG(duration_seconds) as avg_duration
FROM iflow_jobs
WHERE status = 'completed'
GROUP BY platform;
```

**Get RAG retrieval statistics**:
```sql
SELECT
    j.job_id,
    j.iflow_name,
    COUNT(r.retrieval_id) as retrieval_count,
    AVG(r.retrieval_time_ms) as avg_retrieval_time
FROM iflow_jobs j
LEFT JOIN rag_retrievals r ON j.job_id = r.job_id
GROUP BY j.job_id
ORDER BY retrieval_count DESC
LIMIT 10;
```

### 9.2 Enable Real-Time Subscriptions (Optional)

Supabase supports real-time subscriptions. To enable for `iflow_jobs`:

1. Go to Supabase Dashboard → Database → Replication
2. Select `iflow_jobs` table
3. Enable "Real-time"

Then in frontend:
```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Subscribe to job updates
supabase
  .channel('job-updates')
  .on('postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'iflow_jobs', filter: `job_id=eq.${jobId}` },
    (payload) => {
      console.log('Job updated:', payload.new);
      setJobData(payload.new);
    }
  )
  .subscribe();
```

---

## ✅ Success Checklist

- [ ] Supabase schema created successfully
- [ ] Test job tracker script runs without errors
- [ ] Main API shows "✅ Supabase job tracking enabled"
- [ ] Upload documentation creates job in Supabase
- [ ] Job status updates correctly in database
- [ ] Components are tracked in `iflow_components` table
- [ ] Frontend fetches real job data (not dummy)
- [ ] Real-time progress shown in UI
- [ ] End-to-end test completes successfully

---

## 🐛 Troubleshooting

### Issue: "Supabase job tracking not available"

**Solution**: Check environment variables are set:
```bash
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY
```

### Issue: "Permission denied" errors

**Solution**: Check Row Level Security policies in Supabase:
```sql
-- Verify RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('iflow_jobs', 'iflow_components');

-- Check policies
SELECT * FROM pg_policies WHERE tablename = 'iflow_jobs';
```

### Issue: Jobs created but not visible in UI

**Solution**: Check API endpoint is returning data:
```bash
curl http://localhost:5000/api/jobs/<job-id>
```

---

## 📚 Related Documentation

- [supabase_job_tracking_schema.sql](supabase_job_tracking_schema.sql) - Database schema
- [utils/supabase_job_tracker.py](utils/supabase_job_tracker.py) - Python utility
- [RAG_LOGGING_GUIDE.md](RAG_LOGGING_GUIDE.md) - RAG component logging
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - RAG integration overview

---

**Status**: ✅ Ready for Testing
**Next Steps**: Apply schema in Supabase and test backend integration
