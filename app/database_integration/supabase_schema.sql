-- Supabase Database Schema for IS-Migration Application
-- Run this in your Supabase SQL Editor

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- DROP EXISTING TABLES (in reverse dependency order)
-- ==========================================
DROP TABLE IF EXISTS user_feedback CASCADE;
DROP TABLE IF EXISTS user_activity CASCADE;
DROP TABLE IF EXISTS job_history CASCADE;
DROP TABLE IF EXISTS iflow_generations CASCADE;
DROP TABLE IF EXISTS system_metrics CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;

-- ==========================================
-- JOBS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    platform TEXT DEFAULT 'mulesoft',
    user_id TEXT,
    
    -- Job metadata
    file_info JSONB,
    parsed_details JSONB,
    
    -- Enhancement settings
    enhance_with_llm BOOLEAN DEFAULT false,
    llm_service TEXT,
    
    -- File paths
    upload_path TEXT,
    results_path TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ==========================================
-- DOCUMENTS TABLE WITH VECTOR SEARCH
-- ==========================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID,

    -- Document metadata
    filename TEXT NOT NULL,
    document_type TEXT NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    content TEXT,

    -- Vector embedding for similarity search
    embedding vector(1536), -- OpenAI embedding dimension

    -- Metadata for search
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- JOB HISTORY TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS job_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID,

    -- Change tracking
    old_data JSONB,
    new_data JSONB,
    changed_fields TEXT[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- USER ACTIVITY TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS user_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,

    -- Activity details
    activity_type TEXT NOT NULL, -- 'upload', 'generate_iflow', 'download', 'feedback'
    activity_data JSONB,

    -- Related entities
    job_id UUID,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- USER FEEDBACK TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID,
    user_id TEXT,

    -- Feedback details
    feedback_type TEXT NOT NULL, -- 'rating', 'comment', 'bug_report'
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    category TEXT, -- 'iflow_quality', 'performance', 'ui_ux'

    -- Metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- SYSTEM METRICS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Metric details
    metric_name TEXT NOT NULL,
    metric_value NUMERIC,
    metric_data JSONB,
    
    -- Timestamps
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- IFLOW GENERATIONS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS iflow_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_job_id UUID,

    -- Generation details
    markdown_content TEXT,
    generated_iflow TEXT,
    deployment_status TEXT DEFAULT 'not_deployed',
    deployment_url TEXT,

    -- AI generation metadata
    ai_provider TEXT, -- 'anthropic', 'gemma3'
    generation_time_seconds INTEGER,
    token_usage JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deployed_at TIMESTAMPTZ
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Job indexes
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform);

-- Document indexes
CREATE INDEX IF NOT EXISTS idx_documents_job_id ON documents(job_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

-- Vector similarity index
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);

-- ==========================================
-- ADD FOREIGN KEY CONSTRAINTS
-- ==========================================

-- Documents foreign keys
ALTER TABLE documents ADD CONSTRAINT fk_documents_job_id
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;

-- Job history foreign keys
ALTER TABLE job_history ADD CONSTRAINT fk_job_history_job_id
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;

-- User activity foreign keys
ALTER TABLE user_activity ADD CONSTRAINT fk_user_activity_job_id
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL;

-- User feedback foreign keys
ALTER TABLE user_feedback ADD CONSTRAINT fk_user_feedback_job_id
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE;

-- iFlow generations foreign keys
ALTER TABLE iflow_generations ADD CONSTRAINT fk_iflow_generations_original_job_id
    FOREIGN KEY (original_job_id) REFERENCES jobs(id) ON DELETE CASCADE;

-- History indexes
CREATE INDEX IF NOT EXISTS idx_job_history_job_id ON job_history(job_id);
CREATE INDEX IF NOT EXISTS idx_job_history_created_at ON job_history(created_at);

-- Activity indexes
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_type ON user_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON user_activity(created_at);

-- Feedback indexes
CREATE INDEX IF NOT EXISTS idx_user_feedback_job_id ON user_feedback(job_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_rating ON user_feedback(rating);

-- Metrics indexes
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_recorded_at ON system_metrics(recorded_at);

-- ==========================================
-- VECTOR SEARCH FUNCTION
-- ==========================================
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

-- ==========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE iflow_generations ENABLE ROW LEVEL SECURITY;

-- Jobs policies (users can only see their own jobs)
CREATE POLICY "Users can view their own jobs" ON jobs
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert their own jobs" ON jobs
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own jobs" ON jobs
    FOR UPDATE USING (auth.uid()::text = user_id);

-- Documents policies (users can only see documents from their jobs)
CREATE POLICY "Users can view documents from their jobs" ON documents
    FOR SELECT USING (
        job_id IN (SELECT id FROM jobs WHERE user_id = auth.uid()::text)
    );

CREATE POLICY "Users can insert documents to their jobs" ON documents
    FOR INSERT WITH CHECK (
        job_id IN (SELECT id FROM jobs WHERE user_id = auth.uid()::text)
    );

-- Similar policies for other tables...
-- (Add more RLS policies as needed for security)

-- ==========================================
-- UTILITY FUNCTIONS
-- ==========================================

-- Function to get schema version
CREATE OR REPLACE FUNCTION get_schema_version()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN '1.0.0';
END;
$$;

-- Function to clean old data
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep int DEFAULT 90)
RETURNS int
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count int;
BEGIN
    -- Delete old completed jobs and related data
    WITH deleted_jobs AS (
        DELETE FROM jobs 
        WHERE status = 'completed' 
            AND created_at < NOW() - INTERVAL '1 day' * days_to_keep
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted_jobs;
    
    RETURN deleted_count;
END;
$$;
