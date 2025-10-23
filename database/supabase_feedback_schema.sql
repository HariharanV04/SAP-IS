-- ============================================================================
-- IMigrate Feedback & Learning System Schema
-- Captures feedback from Boomi, MuleSoft, and Sterling migrations
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. MIGRATION FEEDBACK TABLE (Main feedback collection)
-- ============================================================================
CREATE TABLE IF NOT EXISTS migration_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Job & Source Information
    job_id TEXT NOT NULL,
    source_platform TEXT NOT NULL CHECK (source_platform IN ('boomi', 'mulesoft', 'sterling')),
    source_file_name TEXT,
    source_file_hash TEXT, -- MD5 hash of source file for deduplication
    
    -- User Feedback
    overall_rating INT CHECK (overall_rating >= 1 AND overall_rating <= 5),
    documentation_quality_rating INT CHECK (documentation_quality_rating >= 1 AND documentation_quality_rating <= 5),
    iflow_quality_rating INT CHECK (iflow_quality_rating >= 1 AND iflow_quality_rating <= 5),
    
    -- Detailed Feedback
    what_worked_well TEXT[], -- Array of things that worked
    what_needs_improvement TEXT[], -- Array of issues found
    manual_fixes_required JSONB, -- Structured data of what user had to fix manually
    missing_components TEXT[], -- Components that should have been generated but weren't
    incorrect_components TEXT[], -- Components that were wrong
    
    -- Business Logic Assessment
    business_logic_preserved BOOLEAN,
    business_logic_issues TEXT,
    data_transformation_accurate BOOLEAN,
    data_transformation_issues TEXT,
    
    -- Documentation Feedback
    documentation_completeness_score INT CHECK (documentation_completeness_score >= 1 AND documentation_completeness_score <= 10),
    documentation_missing_sections TEXT[],
    documentation_improvements TEXT,
    
    -- iFlow Generation Feedback
    component_mapping_accuracy INT CHECK (component_mapping_accuracy >= 1 AND component_mapping_accuracy <= 10),
    configuration_accuracy INT CHECK (configuration_accuracy >= 1 AND configuration_accuracy <= 10),
    integration_pattern_correct BOOLEAN,
    integration_pattern_feedback TEXT,
    
    -- User Corrections (Learning Data)
    user_corrections JSONB, -- Before/after corrections made by user
    suggested_mappings JSONB, -- User-suggested component mappings
    
    -- Success Metrics
    deployment_successful BOOLEAN,
    deployment_issues TEXT,
    time_to_fix_minutes INT,
    effort_level TEXT CHECK (effort_level IN ('minimal', 'moderate', 'significant', 'major')),
    
    -- Additional Context
    comments TEXT,
    screenshots_urls TEXT[], -- URLs to screenshots if uploaded
    attachments JSONB, -- Other attachments metadata
    
    -- Metadata
    user_id TEXT, -- Optional user identifier
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_migration_feedback_job_id ON migration_feedback(job_id);
CREATE INDEX idx_migration_feedback_platform ON migration_feedback(source_platform);
CREATE INDEX idx_migration_feedback_rating ON migration_feedback(overall_rating);
CREATE INDEX idx_migration_feedback_created ON migration_feedback(created_at DESC);

-- ============================================================================
-- 2. DOCUMENTATION QUALITY FEEDBACK (Specific to doc generation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS documentation_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Reference
    job_id TEXT NOT NULL,
    source_platform TEXT NOT NULL,
    feedback_id UUID REFERENCES migration_feedback(id),
    
    -- Documentation Structure Feedback
    component_sequence_clear BOOLEAN,
    component_sequence_feedback TEXT,
    business_logic_explanation_clear BOOLEAN,
    business_logic_feedback TEXT,
    data_flow_diagram_helpful BOOLEAN,
    data_flow_feedback TEXT,
    
    -- Missing Information
    missing_connection_details BOOLEAN,
    missing_error_handling_info BOOLEAN,
    missing_data_transformation_details BOOLEAN,
    missing_authentication_info BOOLEAN,
    other_missing_info TEXT[],
    
    -- SAP Conversion Hints Quality
    sap_hints_helpful BOOLEAN,
    sap_hints_accuracy INT CHECK (sap_hints_accuracy >= 1 AND sap_hints_accuracy <= 5),
    sap_hints_feedback TEXT,
    
    -- Specific Improvements
    suggested_documentation_format TEXT,
    suggested_additional_sections TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_doc_feedback_job ON documentation_feedback(job_id);
CREATE INDEX idx_doc_feedback_platform ON documentation_feedback(source_platform);

-- ============================================================================
-- 3. COMPONENT MAPPING FEEDBACK (Learning for component conversion)
-- ============================================================================
CREATE TABLE IF NOT EXISTS component_mapping_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Source Component
    source_platform TEXT NOT NULL,
    source_component_type TEXT NOT NULL,
    source_component_config JSONB,
    
    -- Generated SAP Component
    generated_sap_component TEXT,
    generated_config JSONB,
    
    -- User Assessment
    mapping_correct BOOLEAN NOT NULL,
    mapping_feedback TEXT,
    
    -- User's Correct Mapping (if incorrect)
    correct_sap_component TEXT,
    correct_config JSONB,
    reasoning TEXT, -- Why this mapping is better
    
    -- Context
    business_pattern TEXT, -- e.g., "SFTP_Poll_Transform_Post"
    integration_type TEXT, -- e.g., "batch", "realtime", "hybrid"
    
    -- Metadata
    job_id TEXT,
    feedback_id UUID REFERENCES migration_feedback(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_comp_mapping_source ON component_mapping_feedback(source_platform, source_component_type);
CREATE INDEX idx_comp_mapping_correct ON component_mapping_feedback(mapping_correct);

-- ============================================================================
-- 4. LEARNED PATTERNS (Auto-generated from feedback)
-- ============================================================================
CREATE TABLE IF NOT EXISTS learned_migration_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Pattern Identification
    pattern_name TEXT NOT NULL,
    source_platform TEXT NOT NULL,
    pattern_signature JSONB, -- Unique signature of this pattern
    
    -- Source Pattern
    source_components TEXT[], -- Sequence of source components
    source_configuration_pattern JSONB,
    
    -- SAP Equivalent Pattern
    sap_components TEXT[], -- Sequence of SAP components
    sap_configuration_pattern JSONB,
    conversion_rules JSONB, -- Step-by-step conversion rules
    
    -- Quality Metrics
    confidence_score FLOAT DEFAULT 0.5,
    success_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,
    total_feedback_count INT DEFAULT 0,
    
    -- Learning Source
    learned_from_feedback_ids UUID[], -- Array of feedback IDs this was learned from
    
    -- Status
    status TEXT DEFAULT 'learning' CHECK (status IN ('learning', 'validated', 'production', 'deprecated')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_learned_patterns_platform ON learned_migration_patterns(source_platform);
CREATE INDEX idx_learned_patterns_confidence ON learned_migration_patterns(confidence_score DESC);
CREATE INDEX idx_learned_patterns_status ON learned_migration_patterns(status);

-- ============================================================================
-- 5. PLATFORM-SPECIFIC INTELLIGENCE (Connector mappings, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS platform_connector_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Source Connector
    source_platform TEXT NOT NULL,
    source_connector_type TEXT NOT NULL, -- e.g., "Salesforce", "NetSuite", "SFTP"
    source_connector_version TEXT,
    
    -- SAP Adapter Mapping
    sap_adapter_type TEXT NOT NULL, -- e.g., "SuccessFactors", "OData", "SOAP", "SFTP"
    sap_adapter_version TEXT,
    
    -- Configuration Translation
    connection_property_mappings JSONB, -- How to map connection configs
    authentication_mappings JSONB, -- How to map auth configs
    operation_mappings JSONB, -- How operations map (e.g., Query → GET)
    
    -- Quality
    confidence_score FLOAT DEFAULT 0.5,
    usage_count INT DEFAULT 0,
    success_rate FLOAT DEFAULT 0.5,
    
    -- Learning
    learned_from_feedback_ids UUID[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_connector_mappings_source ON platform_connector_mappings(source_platform, source_connector_type);
CREATE INDEX idx_connector_mappings_confidence ON platform_connector_mappings(confidence_score DESC);

-- ============================================================================
-- 6. FEEDBACK ANALYTICS (Aggregated insights)
-- ============================================================================
CREATE TABLE IF NOT EXISTS feedback_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Time Period
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Platform Stats
    source_platform TEXT NOT NULL,
    
    -- Aggregate Metrics
    total_migrations INT DEFAULT 0,
    avg_overall_rating FLOAT,
    avg_documentation_rating FLOAT,
    avg_iflow_rating FLOAT,
    
    success_rate FLOAT, -- % of successful deployments
    avg_fix_time_minutes FLOAT,
    
    -- Common Issues
    top_issues JSONB, -- Most common issues reported
    top_missing_components TEXT[],
    top_incorrect_mappings JSONB,
    
    -- Improvements Needed
    priority_improvements TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_feedback_analytics_platform ON feedback_analytics(source_platform);
CREATE INDEX idx_feedback_analytics_period ON feedback_analytics(period_start DESC);

-- ============================================================================
-- Functions
-- ============================================================================

-- Function to update confidence score based on feedback
CREATE OR REPLACE FUNCTION update_pattern_confidence()
RETURNS TRIGGER AS $$
BEGIN
    -- Update learned pattern confidence based on new feedback
    -- This is a simplified version - can be enhanced with ML
    UPDATE learned_migration_patterns
    SET 
        success_count = success_count + CASE WHEN NEW.overall_rating >= 4 THEN 1 ELSE 0 END,
        failure_count = failure_count + CASE WHEN NEW.overall_rating <= 2 THEN 1 ELSE 0 END,
        total_feedback_count = total_feedback_count + 1,
        confidence_score = CASE 
            WHEN (success_count + 1.0) / (total_feedback_count + 1.0) > 0.8 THEN 0.9
            WHEN (success_count + 1.0) / (total_feedback_count + 1.0) > 0.6 THEN 0.7
            ELSE 0.5
        END,
        updated_at = NOW()
    WHERE source_platform = NEW.source_platform;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update pattern confidence
CREATE TRIGGER feedback_updates_confidence
AFTER INSERT ON migration_feedback
FOR EACH ROW
EXECUTE FUNCTION update_pattern_confidence();

-- ============================================================================
-- Sample queries for the learning engine
-- ============================================================================

-- Get all high-quality feedback for a specific platform
COMMENT ON TABLE migration_feedback IS 'Query for learning: SELECT * FROM migration_feedback WHERE source_platform = ''boomi'' AND overall_rating >= 4 ORDER BY created_at DESC';

-- Get common issues across platforms
COMMENT ON TABLE feedback_analytics IS 'Query: SELECT source_platform, top_issues FROM feedback_analytics ORDER BY period_start DESC LIMIT 10';

-- Get validated patterns ready for production
COMMENT ON TABLE learned_migration_patterns IS 'Query: SELECT * FROM learned_migration_patterns WHERE status = ''validated'' AND confidence_score > 0.8';


