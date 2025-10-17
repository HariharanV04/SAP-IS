-- Quick Setup SQL for Supabase
-- Copy and paste this entire script into your Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing tables (in reverse dependency order)
DROP TABLE IF EXISTS user_feedback CASCADE;
DROP TABLE IF EXISTS user_activity CASCADE;
DROP TABLE IF EXISTS job_history CASCADE;
DROP TABLE IF EXISTS iflow_generations CASCADE;
DROP TABLE IF EXISTS system_metrics CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;

-- Create jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    platform TEXT DEFAULT 'mulesoft',
    user_id TEXT,
    file_info JSONB,
    parsed_details JSONB,
    enhance_with_llm BOOLEAN DEFAULT false,
    llm_service TEXT,
    upload_path TEXT,
    results_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Create documents table with vector search
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID,
    filename TEXT NOT NULL,
    document_type TEXT NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create job history table
CREATE TABLE job_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID,
    old_data JSONB,
    new_data JSONB,
    changed_fields TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user activity table
CREATE TABLE user_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    activity_data JSONB,
    job_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user feedback table
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID,
    user_id TEXT,
    feedback_type TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    category TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create system metrics table
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name TEXT NOT NULL,
    metric_value NUMERIC,
    metric_data JSONB,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create iflow generations table
CREATE TABLE iflow_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_job_id UUID,
    markdown_content TEXT,
    generated_iflow TEXT,
    deployment_status TEXT DEFAULT 'not_deployed',
    deployment_url TEXT,
    ai_provider TEXT,
    generation_time_seconds INTEGER,
    token_usage JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deployed_at TIMESTAMPTZ
);

-- Add foreign key constraints
ALTER TABLE documents ADD CONSTRAINT fk_documents_job_id 
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;

ALTER TABLE job_history ADD CONSTRAINT fk_job_history_job_id 
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;

ALTER TABLE user_activity ADD CONSTRAINT fk_user_activity_job_id 
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL;

ALTER TABLE user_feedback ADD CONSTRAINT fk_user_feedback_job_id 
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;

ALTER TABLE iflow_generations ADD CONSTRAINT fk_iflow_generations_original_job_id 
    FOREIGN KEY (original_job_id) REFERENCES jobs(id) ON DELETE CASCADE;

-- Create indexes
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_documents_job_id ON documents(job_id);
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_user_feedback_job_id ON user_feedback(job_id);

-- Create vector search function
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    filename TEXT,
    document_type TEXT,
    content TEXT,
    similarity float,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.filename,
        d.document_type,
        d.content,
        1 - (d.embedding <=> query_embedding) AS similarity,
        d.metadata,
        d.created_at
    FROM documents d
    WHERE d.embedding IS NOT NULL
        AND 1 - (d.embedding <=> query_embedding) > match_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create utility function
CREATE OR REPLACE FUNCTION get_schema_version()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN '1.0.0';
END;
$$;
