# IS-Migration Database Integration Setup Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r database_integration/requirements.txt
```

### 2. Set Up Database Schema

1. **Open your Supabase SQL Editor**
2. **Copy and paste the entire content** of `database_integration/is_migration_schema.sql`
3. **Execute the SQL script**

This will create:
- ✅ `is_migration` schema (isolated from your other projects)
- ✅ All required tables with proper relationships
- ✅ Vector search capabilities with pgvector
- ✅ Indexes for performance
- ✅ Utility functions

### 3. Update Your .env File

Add these Supabase credentials to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# S3 Configuration (optional - will use local storage if not provided)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_bucket_name
AWS_REGION=us-east-1

# Local Storage Fallback
LOCAL_STORAGE_PATH=storage
```

### 4. Test the Setup

Run the test script:
```bash
python database_integration/integration_example.py
```

## 📊 Database Schema Overview

### Tables Created in `is_migration` Schema:

1. **`jobs`** - Main job tracking
   - Job metadata, status, platform, user info
   - File paths and processing details

2. **`documents`** - Document storage with vector search
   - File metadata and content
   - Vector embeddings for similarity search
   - Linked to jobs

3. **`job_history`** - Complete change tracking
   - Tracks all job updates
   - Old vs new data comparison

4. **`user_activity`** - User action tracking
   - Upload, generation, download activities
   - Linked to users and jobs

5. **`user_feedback`** - Feedback and ratings
   - User ratings and comments
   - Categorized feedback

6. **`system_metrics`** - Analytics and monitoring
   - Performance metrics
   - Usage statistics

7. **`iflow_generations`** - iFlow generation tracking
   - Generated content and metadata
   - Deployment status

## 🔍 Vector Search Features

- **Similarity Search**: Find similar documents using vector embeddings
- **Configurable Thresholds**: Adjust similarity matching
- **Metadata Filtering**: Search with additional filters
- **Performance Optimized**: Uses pgvector with proper indexing

## 💾 Storage Integration

### S3 Storage (Production)
- Automatic file upload/download
- Presigned URLs for secure access
- Metadata tracking

### Local Storage (Development)
- Automatic fallback when S3 not configured
- Same API interface
- Perfect for development and testing

## 🔧 Usage Examples

### Basic Job Creation
```python
from database_integration.integrated_manager import integrated_manager

# Create job with file upload
job = integrated_manager.create_job_with_file(
    job_data={
        'filename': 'integration_doc.txt',
        'platform': 'mulesoft',
        'user_id': 'user123'
    },
    file_obj=file_object,
    filename='integration_doc.txt'
)
```

### Vector Search
```python
# Search for similar documents
similar_docs = integrated_manager.search_similar_documents(
    query_text="salesforce integration",
    query_embedding=embedding_vector,
    limit=5
)
```

### Add User Feedback
```python
# Add user feedback
feedback = integrated_manager.db.create_feedback({
    'job_id': job_id,
    'user_id': 'user123',
    'rating': 5,
    'comment': 'Excellent iFlow quality!',
    'category': 'iflow_quality'
})
```

## 🔒 Security Features

- **Row Level Security (RLS)**: Users can only access their own data
- **Schema Isolation**: Your tables are isolated from other projects
- **Proper Permissions**: Configured for anon and authenticated users
- **Foreign Key Constraints**: Data integrity protection

## 📈 Analytics & Monitoring

Get comprehensive usage statistics:
```python
stats = integrated_manager.get_comprehensive_stats(days=30)
print(f"Total jobs: {stats['total_jobs']}")
print(f"Average rating: {stats['average_rating']}")
print(f"Storage usage: {stats['storage']['total_size_mb']} MB")
```

## 🚀 Next Steps

1. **Run the setup** following steps 1-4 above
2. **Test with examples** using `integration_example.py`
3. **Integrate into your existing APIs** by replacing current database calls
4. **Add S3 credentials** when ready for production storage
5. **Configure vector embeddings** for enhanced search capabilities

## 🆘 Troubleshooting

### Common Issues:

1. **"Column does not exist" errors**
   - Make sure you ran the complete SQL schema
   - Check that the `is_migration` schema was created

2. **Connection errors**
   - Verify your Supabase credentials in `.env`
   - Check that your Supabase project is active

3. **Permission errors**
   - Ensure RLS policies are properly configured
   - Check that your API keys have the right permissions

### Getting Help:

- Check the example file: `integration_example.py`
- Review the schema: `is_migration_schema.sql`
- Test connections: Run the test functions

Your IS-Migration project now has enterprise-grade database capabilities with vector search, history tracking, and scalable storage! 🎉
