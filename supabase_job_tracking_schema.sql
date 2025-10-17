-- ============================================================================
-- IMigrate Job Tracking Schema for Supabase
-- Purpose: Track iFlow generation jobs and display real-time status in UI
-- Date: 2025-01-17
-- ============================================================================

-- Drop existing tables if they exist (for fresh install)
-- DROP TABLE IF EXISTS iflow_generation_logs CASCADE;
-- DROP TABLE IF EXISTS iflow_components CASCADE;
-- DROP TABLE IF EXISTS rag_retrievals CASCADE;
-- DROP TABLE IF EXISTS iflow_jobs CASCADE;

-- ============================================================================
-- 1. IFLOW_JOBS TABLE
-- Main table tracking each iFlow generation job
-- ============================================================================
CREATE TABLE IF NOT EXISTS iflow_jobs (
    -- Primary identification
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Job metadata
    user_id TEXT,  -- User who initiated the job
    platform TEXT NOT NULL CHECK (platform IN ('boomi', 'mulesoft', 'generic')),
    llm_provider TEXT DEFAULT 'anthropic' CHECK (llm_provider IN ('anthropic', 'openai', 'gemini')),

    -- Job status tracking
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending',
        'processing',
        'documentation_ready',
        'analyzing',
        'generating',
        'completed',
        'failed',
        'cancelled'
    )),

    -- Progress tracking (0-100)
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    current_step TEXT,  -- e.g., 'upload', 'parse', 'analyze', 'generate', 'package'

    -- Input data
    source_file_name TEXT,
    source_file_size BIGINT,
    source_file_url TEXT,  -- URL if stored in Supabase Storage

    -- Documentation
    generated_documentation TEXT,
    documentation_html TEXT,

    -- iFlow generation details
    iflow_name TEXT,
    iflow_description TEXT,
    generation_method TEXT CHECK (generation_method IN ('template', 'rag', 'hybrid')),

    -- Output files
    iflow_zip_url TEXT,
    iflow_xml_url TEXT,

    -- Component statistics
    total_components INTEGER DEFAULT 0,
    components_json JSONB,  -- Array of component details

    -- RAG statistics
    rag_retrievals_count INTEGER DEFAULT 0,
    rag_sources_used INTEGER DEFAULT 0,

    -- Timing information
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,

    -- Error tracking
    error_message TEXT,
    error_stack TEXT,

    -- Metadata
    metadata JSONB,  -- Flexible field for additional data

    -- Timestamps
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_iflow_jobs_status ON iflow_jobs(status);
CREATE INDEX IF NOT EXISTS idx_iflow_jobs_user_id ON iflow_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_iflow_jobs_created_at ON iflow_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_iflow_jobs_platform ON iflow_jobs(platform);

-- ============================================================================
-- 2. IFLOW_COMPONENTS TABLE
-- Detailed tracking of each component in an iFlow
-- ============================================================================
CREATE TABLE IF NOT EXISTS iflow_components (
    -- Primary identification
    component_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES iflow_jobs(job_id) ON DELETE CASCADE,

    -- Component details
    component_type TEXT NOT NULL,  -- e.g., 'StartEvent', 'EndpointSender', 'RequestReply'
    component_name TEXT NOT NULL,
    component_order INTEGER,  -- Order in the iFlow (1, 2, 3, ...)

    -- Component source
    source TEXT CHECK (source IN ('template', 'rag', 'authoritative', 'user_specified')),
    rag_similarity_score DECIMAL(5,4),  -- 0.0000 to 1.0000

    -- RAG retrieval details
    rag_document_id TEXT,
    rag_document_name TEXT,
    rag_chunk_type TEXT,

    -- Component configuration
    configuration JSONB,  -- Component-specific config

    -- XML content
    xml_content TEXT,

    -- Metadata
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_iflow_components_job_id ON iflow_components(job_id);
CREATE INDEX IF NOT EXISTS idx_iflow_components_type ON iflow_components(component_type);
CREATE INDEX IF NOT EXISTS idx_iflow_components_order ON iflow_components(job_id, component_order);

-- ============================================================================
-- 3. RAG_RETRIEVALS TABLE
-- Detailed logging of each RAG retrieval operation
-- ============================================================================
CREATE TABLE IF NOT EXISTS rag_retrievals (
    -- Primary identification
    retrieval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES iflow_jobs(job_id) ON DELETE CASCADE,

    -- Retrieval details
    retrieval_type TEXT CHECK (retrieval_type IN ('vector_search', 'pattern_search', 'graph_query', 'hybrid')),
    search_query TEXT NOT NULL,

    -- Context
    retrieval_location TEXT,  -- e.g., '_retrieve_artifacts_by_node_order'
    component_type_searched TEXT,

    -- Results
    results_count INTEGER DEFAULT 0,
    results JSONB,  -- Array of retrieved documents with metadata

    -- Timing
    retrieval_time_ms INTEGER,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_rag_retrievals_job_id ON rag_retrievals(job_id);
CREATE INDEX IF NOT EXISTS idx_rag_retrievals_type ON rag_retrievals(retrieval_type);
CREATE INDEX IF NOT EXISTS idx_rag_retrievals_created_at ON rag_retrievals(created_at DESC);

-- ============================================================================
-- 4. IFLOW_GENERATION_LOGS TABLE
-- Step-by-step logs for debugging and transparency
-- ============================================================================
CREATE TABLE IF NOT EXISTS iflow_generation_logs (
    -- Primary identification
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES iflow_jobs(job_id) ON DELETE CASCADE,

    -- Log details
    log_level TEXT CHECK (log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    log_message TEXT NOT NULL,
    log_category TEXT,  -- e.g., 'parsing', 'generation', 'rag_retrieval', 'packaging'

    -- Additional context
    step_name TEXT,
    details JSONB,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_iflow_generation_logs_job_id ON iflow_generation_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_iflow_generation_logs_level ON iflow_generation_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_iflow_generation_logs_created_at ON iflow_generation_logs(job_id, created_at);

-- ============================================================================
-- 5. FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for iflow_jobs
DROP TRIGGER IF EXISTS update_iflow_jobs_updated_at ON iflow_jobs;
CREATE TRIGGER update_iflow_jobs_updated_at
    BEFORE UPDATE ON iflow_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically calculate duration when job completes
CREATE OR REPLACE FUNCTION calculate_job_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('completed', 'failed', 'cancelled') AND NEW.started_at IS NOT NULL THEN
        NEW.completed_at = NOW();
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to calculate duration
DROP TRIGGER IF EXISTS calculate_iflow_job_duration ON iflow_jobs;
CREATE TRIGGER calculate_iflow_job_duration
    BEFORE UPDATE ON iflow_jobs
    FOR EACH ROW
    WHEN (NEW.status IN ('completed', 'failed', 'cancelled'))
    EXECUTE FUNCTION calculate_job_duration();

-- ============================================================================
-- 6. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Job Summary with Statistics
CREATE OR REPLACE VIEW iflow_jobs_summary AS
SELECT
    j.job_id,
    j.status,
    j.progress,
    j.current_step,
    j.platform,
    j.iflow_name,
    j.source_file_name,
    j.generation_method,
    j.total_components,
    j.rag_retrievals_count,
    j.duration_seconds,
    j.created_at,
    j.completed_at,
    COUNT(DISTINCT c.component_id) as actual_components_count,
    COUNT(DISTINCT r.retrieval_id) as actual_retrievals_count,
    COUNT(DISTINCT CASE WHEN l.log_level = 'ERROR' THEN l.log_id END) as error_count
FROM iflow_jobs j
LEFT JOIN iflow_components c ON j.job_id = c.job_id
LEFT JOIN rag_retrievals r ON j.job_id = r.job_id
LEFT JOIN iflow_generation_logs l ON j.job_id = l.job_id
GROUP BY j.job_id
ORDER BY j.created_at DESC;

-- View: Recent Jobs with Details
CREATE OR REPLACE VIEW recent_jobs_with_details AS
SELECT
    j.*,
    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'component_id', c.component_id,
                'type', c.component_type,
                'name', c.component_name,
                'order', c.component_order,
                'source', c.source,
                'similarity_score', c.rag_similarity_score
            ) ORDER BY c.component_order
        )
        FROM iflow_components c
        WHERE c.job_id = j.job_id
    ) as components_detail,
    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'retrieval_id', r.retrieval_id,
                'type', r.retrieval_type,
                'query', r.search_query,
                'results_count', r.results_count,
                'time_ms', r.retrieval_time_ms
            ) ORDER BY r.created_at
        )
        FROM rag_retrievals r
        WHERE r.job_id = j.job_id
    ) as retrievals_detail
FROM iflow_jobs j
ORDER BY j.created_at DESC
LIMIT 100;

-- ============================================================================
-- 7. ROW LEVEL SECURITY (RLS) - Optional but recommended
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE iflow_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE iflow_components ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_retrievals ENABLE ROW LEVEL SECURITY;
ALTER TABLE iflow_generation_logs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow all for authenticated users" ON iflow_jobs;
DROP POLICY IF EXISTS "Allow all for authenticated users" ON iflow_components;
DROP POLICY IF EXISTS "Allow all for authenticated users" ON rag_retrievals;
DROP POLICY IF EXISTS "Allow all for authenticated users" ON iflow_generation_logs;

-- Policy: Allow all operations for service role (backend access)
CREATE POLICY "Allow all for service role" ON iflow_jobs
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role" ON iflow_components
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role" ON rag_retrievals
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role" ON iflow_generation_logs
    FOR ALL USING (true);

-- Policy: Allow anonymous read access (for public demo)
-- UNCOMMENT IF YOU WANT PUBLIC READ ACCESS
-- CREATE POLICY "Allow read for anonymous" ON iflow_jobs
--     FOR SELECT USING (true);

-- ============================================================================
-- 8. SAMPLE DATA (for testing)
-- ============================================================================

-- Insert a sample job
INSERT INTO iflow_jobs (
    job_id,
    platform,
    status,
    progress,
    current_step,
    source_file_name,
    iflow_name,
    generation_method,
    total_components,
    rag_retrievals_count
) VALUES (
    gen_random_uuid(),
    'mulesoft',
    'completed',
    100,
    'packaging',
    'stripe_to_salesforce.xml',
    'Stripe_Salesforce_Integration',
    'rag',
    7,
    15
) RETURNING job_id;

-- Note: Save the returned job_id to insert related data

-- ============================================================================
-- 9. USEFUL QUERIES
-- ============================================================================

-- Get all jobs with their component counts
-- SELECT * FROM iflow_jobs_summary;

-- Get recent jobs
-- SELECT * FROM recent_jobs_with_details LIMIT 10;

-- Get job details with all components
-- SELECT
--     j.job_id,
--     j.status,
--     j.iflow_name,
--     jsonb_agg(c.*) as components
-- FROM iflow_jobs j
-- LEFT JOIN iflow_components c ON j.job_id = c.job_id
-- WHERE j.job_id = 'YOUR_JOB_ID'
-- GROUP BY j.job_id;

-- Get RAG retrievals for a job
-- SELECT * FROM rag_retrievals WHERE job_id = 'YOUR_JOB_ID' ORDER BY created_at;

-- Get all logs for a job
-- SELECT * FROM iflow_generation_logs WHERE job_id = 'YOUR_JOB_ID' ORDER BY created_at;

-- Get jobs by status
-- SELECT * FROM iflow_jobs WHERE status = 'processing' ORDER BY created_at DESC;

-- Get average generation time by platform
-- SELECT
--     platform,
--     generation_method,
--     AVG(duration_seconds) as avg_duration_sec,
--     COUNT(*) as total_jobs
-- FROM iflow_jobs
-- WHERE status = 'completed'
-- GROUP BY platform, generation_method;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Grant permissions (adjust based on your setup)
GRANT ALL ON iflow_jobs TO authenticated, service_role;
GRANT ALL ON iflow_components TO authenticated, service_role;
GRANT ALL ON rag_retrievals TO authenticated, service_role;
GRANT ALL ON iflow_generation_logs TO authenticated, service_role;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'IMigrate Job Tracking Schema created successfully!';
    RAISE NOTICE 'Tables: iflow_jobs, iflow_components, rag_retrievals, iflow_generation_logs';
    RAISE NOTICE 'Views: iflow_jobs_summary, recent_jobs_with_details';
    RAISE NOTICE 'Ready to track iFlow generation jobs!';
END $$;
