"""
Integration Example - How to use the new database system in your existing application
"""

from database_integration.integrated_manager import integrated_manager
import uuid
from datetime import datetime
import io

# Example 1: Create a job with file upload
def example_create_job_with_file():
    """Example of creating a job with file upload"""
    
    # Simulate file upload
    file_content = b"Sample document content for processing"
    file_obj = io.BytesIO(file_content)
    
    job_data = {
        'filename': 'sample_document.txt',
        'platform': 'mulesoft',
        'user_id': 'user123',
        'enhance_with_llm': True,
        'llm_service': 'anthropic'
    }
    
    try:
        job = integrated_manager.create_job_with_file(
            job_data=job_data,
            file_obj=file_obj,
            filename='sample_document.txt'
        )
        
        print(f"✅ Job created successfully: {job['id']}")
        return job['id']
        
    except Exception as e:
        print(f"❌ Failed to create job: {str(e)}")
        return None

# Example 2: Update job with results
def example_update_job_with_results(job_id: str):
    """Example of updating a job with result files"""
    
    # Simulate result files
    result_files = {
        'iflow': io.BytesIO(b"Generated iFlow XML content"),
        'documentation': io.BytesIO(b"Generated documentation content"),
        'summary': io.BytesIO(b"Processing summary content")
    }
    
    updates = {
        'status': 'completed',
        'completed_at': datetime.utcnow().isoformat(),
        'message': 'iFlow generation completed successfully'
    }
    
    try:
        success = integrated_manager.update_job_with_results(
            job_id=job_id,
            updates=updates,
            result_files=result_files
        )
        
        if success:
            print(f"✅ Job {job_id} updated with results")
        else:
            print(f"❌ Failed to update job {job_id}")
            
        return success
        
    except Exception as e:
        print(f"❌ Failed to update job: {str(e)}")
        return False

# Example 3: Search similar documents
def example_search_similar_documents():
    """Example of searching for similar documents"""
    
    # In a real application, you would generate embeddings using OpenAI or similar
    # For this example, we'll use a dummy embedding
    query_embedding = [0.1] * 1536  # OpenAI embedding dimension
    
    try:
        similar_docs = integrated_manager.search_similar_documents(
            query_text="integration flow for salesforce",
            query_embedding=query_embedding,
            limit=5
        )
        
        print(f"✅ Found {len(similar_docs)} similar documents")
        for doc in similar_docs:
            print(f"  - {doc['filename']} (similarity: {doc.get('similarity', 0):.2f})")
            
        return similar_docs
        
    except Exception as e:
        print(f"❌ Failed to search documents: {str(e)}")
        return []

# Example 4: Add user feedback
def example_add_feedback(job_id: str):
    """Example of adding user feedback"""
    
    feedback_data = {
        'job_id': job_id,
        'user_id': 'user123',
        'feedback_type': 'rating',
        'rating': 5,
        'comment': 'Excellent iFlow generation quality!',
        'category': 'iflow_quality'
    }
    
    try:
        feedback = integrated_manager.db.create_feedback(feedback_data)
        print(f"✅ Feedback added successfully: {feedback['id']}")
        return feedback
        
    except Exception as e:
        print(f"❌ Failed to add feedback: {str(e)}")
        return None

# Example 5: Get comprehensive job information
def example_get_job_details(job_id: str):
    """Example of getting complete job information"""
    
    try:
        job_details = integrated_manager.get_job_with_files(job_id)
        
        if job_details:
            print(f"✅ Job Details for {job_id}:")
            print(f"  Status: {job_details['status']}")
            print(f"  Platform: {job_details['platform']}")
            print(f"  Documents: {len(job_details.get('documents', []))}")
            print(f"  History entries: {len(job_details.get('history', []))}")
            print(f"  Feedback entries: {len(job_details.get('feedback', []))}")
        else:
            print(f"❌ Job {job_id} not found")
            
        return job_details
        
    except Exception as e:
        print(f"❌ Failed to get job details: {str(e)}")
        return None

# Example 6: Get usage statistics
def example_get_usage_stats():
    """Example of getting usage statistics"""
    
    try:
        stats = integrated_manager.get_comprehensive_stats(days=30)
        
        print("✅ Usage Statistics (Last 30 days):")
        print(f"  Total jobs: {stats.get('total_jobs', 0)}")
        print(f"  Average rating: {stats.get('average_rating', 0):.1f}")
        print(f"  Total feedback: {stats.get('total_feedback', 0)}")
        print(f"  Storage files: {stats.get('storage', {}).get('total_files', 0)}")
        print(f"  Storage size: {stats.get('storage', {}).get('total_size_mb', 0)} MB")
        
        return stats
        
    except Exception as e:
        print(f"❌ Failed to get usage stats: {str(e)}")
        return {}

# Example 7: Test all connections
def example_test_connections():
    """Example of testing all service connections"""
    
    try:
        connections = integrated_manager.test_connections()
        
        print("🔍 Connection Status:")
        print(f"  Database: {'✅ Connected' if connections['database'] else '❌ Failed'}")
        print(f"  Storage: {'✅ Connected' if connections['storage'] else '❌ Failed (using local fallback)'}")
        
        return connections
        
    except Exception as e:
        print(f"❌ Failed to test connections: {str(e)}")
        return {}

def main():
    """Run all examples"""
    print("🚀 Database Integration Examples")
    print("=" * 50)
    
    # Test connections first
    print("\n1. Testing connections...")
    example_test_connections()
    
    # Create a job
    print("\n2. Creating job with file...")
    job_id = example_create_job_with_file()
    
    if job_id:
        # Update job with results
        print("\n3. Updating job with results...")
        example_update_job_with_results(job_id)
        
        # Add feedback
        print("\n4. Adding user feedback...")
        example_add_feedback(job_id)
        
        # Get job details
        print("\n5. Getting job details...")
        example_get_job_details(job_id)
    
    # Search similar documents
    print("\n6. Searching similar documents...")
    example_search_similar_documents()
    
    # Get usage stats
    print("\n7. Getting usage statistics...")
    example_get_usage_stats()
    
    print("\n🎉 Examples completed!")

if __name__ == "__main__":
    main()
