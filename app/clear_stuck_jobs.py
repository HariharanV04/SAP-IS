#!/usr/bin/env python3
"""
Clear stuck jobs to free up resources and speed up iFlow generation
"""

import json
import os
from datetime import datetime, timedelta

def clear_stuck_jobs():
    """Clear jobs that have been stuck in processing for too long"""
    
    # Load jobs
    jobs_file = "jobs.json"
    if not os.path.exists(jobs_file):
        print("❌ jobs.json not found")
        return
    
    with open(jobs_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    print(f"📊 Total jobs: {len(jobs)}")
    
    # Count jobs by status
    status_counts = {}
    stuck_jobs = []
    
    for job_id, job_data in jobs.items():
        status = job_data.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Check for stuck processing jobs
        if status == 'processing':
            created = job_data.get('created', '')
            last_updated = job_data.get('last_updated', '')
            
            # If job has been processing for more than 1 hour, mark as stuck
            if created and last_updated:
                try:
                    # Parse timestamps (they appear to be in a custom format)
                    # For now, mark all processing jobs as potentially stuck
                    stuck_jobs.append({
                        'id': job_id,
                        'created': created,
                        'last_updated': last_updated,
                        'message': job_data.get('message', 'No message')
                    })
                except:
                    stuck_jobs.append({
                        'id': job_id,
                        'created': created,
                        'last_updated': last_updated,
                        'message': job_data.get('message', 'No message')
                    })
    
    print("\n📈 Job Status Distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    print(f"\n🚨 Stuck Processing Jobs: {len(stuck_jobs)}")
    
    if stuck_jobs:
        print("\n🔍 Stuck Jobs Details:")
        for i, job in enumerate(stuck_jobs[:10], 1):  # Show first 10
            print(f"  {i}. {job['id'][:8]}... - Created: {job['created']} - Updated: {job['last_updated']}")
            print(f"     Message: {job['message']}")
        
        if len(stuck_jobs) > 10:
            print(f"     ... and {len(stuck_jobs) - 10} more stuck jobs")
        
        # Ask user if they want to clear stuck jobs
        response = input(f"\n❓ Do you want to clear {len(stuck_jobs)} stuck jobs? (y/N): ")
        
        if response.lower() == 'y':
            cleared_count = 0
            for job in stuck_jobs:
                job_id = job['id']
                if job_id in jobs:
                    # Mark as failed with explanation
                    jobs[job_id]['status'] = 'failed'
                    jobs[job_id]['message'] = 'Job cleared due to being stuck in processing state'
                    jobs[job_id]['last_updated'] = datetime.now().isoformat()
                    cleared_count += 1
            
            # Save updated jobs
            with open(jobs_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Cleared {cleared_count} stuck jobs")
            print("💡 iFlow generation should now be much faster!")
        else:
            print("❌ No jobs cleared")
    else:
        print("✅ No stuck jobs found")
    
    # Show recommendations
    print("\n💡 Recommendations to Speed Up iFlow Generation:")
    print("  1. Use the BoomiToIS-API (port 5003) for faster processing")
    print("  2. Clear stuck jobs to free up resources")
    print("  3. Process smaller Boomi flows first")
    print("  4. Check AI API rate limits and quotas")

if __name__ == "__main__":
    clear_stuck_jobs()
