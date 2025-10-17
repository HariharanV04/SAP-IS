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

# Log RAG retrieval
try:
    print(f"\n🔍 Logging RAG retrieval...")

    retrieval = tracker.log_rag_retrieval(
        job_id=job_id,
        retrieval_type='vector_search',
        search_query='StartEvent',
        results=[
            {
                'id': 'chunk_123',
                'document_name': 'Start_Event_Template',
                'similarity_score': 0.95
            }
        ],
        retrieval_location='_retrieve_artifacts_by_node_order'
    )

    print(f"✅ RAG retrieval logged")
except Exception as e:
    print(f"❌ Failed to log RAG retrieval: {e}")
    sys.exit(1)

# Add log entry
try:
    print(f"\n📄 Adding log entry...")

    log_entry = tracker.add_log(
        job_id=job_id,
        log_level='INFO',
        log_message='Test log entry',
        log_category='testing',
        step_name='test_step'
    )

    print(f"✅ Log entry added")
except Exception as e:
    print(f"❌ Failed to add log entry: {e}")
    sys.exit(1)

# Get job summary
try:
    print(f"\n📊 Getting job summary...")

    summary = tracker.get_job_summary(job_id)

    print(f"✅ Job Summary:")
    print(f"   Status: {summary['job']['status']}")
    print(f"   Components: {summary['statistics']['total_components']}")
    print(f"   Retrievals: {summary['statistics']['total_retrievals']}")
    print(f"   Logs: {len(summary['error_logs'])} errors")
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

    print(f"✅ Job completed in {completed_job.get('duration_seconds', 0)} seconds")
except Exception as e:
    print(f"❌ Failed to complete job: {e}")
    sys.exit(1)

# Get recent jobs
try:
    print(f"\n📋 Getting recent jobs...")

    recent_jobs = tracker.get_recent_jobs(limit=5)

    print(f"✅ Found {len(recent_jobs)} recent jobs")
    for job in recent_jobs[:3]:
        print(f"   - {job['job_id']}: {job['status']} ({job['platform']})")
except Exception as e:
    print(f"❌ Failed to get recent jobs: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("✅ All tests passed!")
print("="*80)
print(f"\n💡 Test job ID: {job_id}")
print("   Check Supabase dashboard to verify data was saved")
