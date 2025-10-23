-- Intent Training and Feedback System for SAP iFlow Generation
-- Purpose: Collect user feedback and improve intent understanding over time

-- ============================================================================
-- TABLE 1: Intent Training Examples
-- Stores successful intent identifications for few-shot learning
-- ============================================================================
CREATE TABLE IF NOT EXISTS intent_training_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Input
    user_query TEXT NOT NULL,
    markdown_content TEXT,
    
    -- Intent Analysis
    intent_classification TEXT NOT NULL, -- 'complete_iflow_creation', 'component_modification', etc.
    components_identified JSONB NOT NULL, -- Array of components identified by LLM
    
    -- Correctness
    is_correct BOOLEAN DEFAULT NULL, -- User feedback: was this correct?
    missing_components JSONB, -- Components that should have been identified
    extra_components JSONB, -- Components that shouldn't have been identified
    user_corrections JSONB, -- User's manual corrections
    
    -- Metadata
    confidence_score DECIMAL(3,2), -- 0.0-1.0, how confident was the LLM
    model_version TEXT, -- GPT-4, GPT-4-turbo, etc.
    prompt_version TEXT, -- Track prompt iterations
    
    -- Training Status
    approved_for_training BOOLEAN DEFAULT FALSE, -- Manually reviewed and approved
    training_weight DECIMAL(3,2) DEFAULT 1.0, -- Higher weight = more important example
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by TEXT
);

-- Index for fast retrieval during few-shot learning
CREATE INDEX idx_intent_training_approved ON intent_training_examples(approved_for_training, confidence_score DESC);
CREATE INDEX idx_intent_training_classification ON intent_training_examples(intent_classification);


-- ============================================================================
-- TABLE 2: Component Pattern Library
-- Maps phrases/triggers to component types
-- ============================================================================
CREATE TABLE IF NOT EXISTS component_pattern_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Pattern Definition
    trigger_phrase TEXT NOT NULL, -- e.g., "poll sftp", "transform xml to json"
    component_type TEXT NOT NULL, -- e.g., "SFTPAdapter", "GroovyScript"
    pattern_category TEXT NOT NULL, -- 'source_adapter', 'transformation', 'routing', 'target_adapter'
    
    -- Context
    typical_requirements JSONB, -- Common requirements for this pattern
    typical_properties JSONB, -- Common properties/configurations
    
    -- Learning Metrics
    times_matched INTEGER DEFAULT 0, -- How many times this pattern was used
    times_correct INTEGER DEFAULT 0, -- How many times it was correct
    confidence_score DECIMAL(3,2) DEFAULT 0.5, -- Calculated: times_correct / times_matched
    
    -- Aliases and Variations
    aliases TEXT[], -- Alternative phrases: ["sftp polling", "sftp sender", "poll sftp server"]
    
    -- Examples
    example_queries TEXT[], -- Real user queries that matched this pattern
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for pattern matching
CREATE INDEX idx_component_pattern_phrase ON component_pattern_library USING gin(to_tsvector('english', trigger_phrase));
CREATE INDEX idx_component_pattern_type ON component_pattern_library(component_type);
CREATE INDEX idx_component_pattern_confidence ON component_pattern_library(confidence_score DESC);


-- ============================================================================
-- TABLE 3: Generation Feedback
-- Captures user feedback on generated iFlows
-- ============================================================================
CREATE TABLE IF NOT EXISTS generation_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Link to Generation
    job_id TEXT NOT NULL, -- Main app job ID
    iflow_name TEXT,
    package_path TEXT,
    
    -- Original Intent
    original_query TEXT NOT NULL,
    identified_components JSONB NOT NULL, -- What the agent identified
    
    -- User Feedback
    feedback_type TEXT NOT NULL, -- 'correct', 'missing_components', 'extra_components', 'wrong_sequence'
    missing_components JSONB, -- Components that were needed but not generated
    extra_components JSONB, -- Components that were generated but not needed
    wrong_sequence JSONB, -- Components in wrong order
    user_comments TEXT, -- Free-form feedback
    
    -- Quality Metrics
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5), -- 1-5 stars
    was_importable BOOLEAN, -- Could it be imported to SAP Integration Suite?
    worked_correctly BOOLEAN, -- Did it work as expected after import?
    
    -- Learning Priority
    learning_priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    processed_for_training BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Index for feedback processing
CREATE INDEX idx_generation_feedback_job ON generation_feedback(job_id);
CREATE INDEX idx_generation_feedback_unprocessed ON generation_feedback(processed_for_training) WHERE NOT processed_for_training;
CREATE INDEX idx_generation_feedback_priority ON generation_feedback(learning_priority);


-- ============================================================================
-- TABLE 4: Intent Prompt Evolution
-- Track different versions of the intent understanding prompt
-- ============================================================================
CREATE TABLE IF NOT EXISTS intent_prompt_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Prompt Details
    version TEXT NOT NULL UNIQUE, -- e.g., "v1.0", "v1.1", "v2.0"
    prompt_template TEXT NOT NULL, -- The actual prompt
    few_shot_examples JSONB, -- Examples included in prompt
    
    -- Performance Metrics
    total_uses INTEGER DEFAULT 0,
    successful_generations INTEGER DEFAULT 0,
    average_user_rating DECIMAL(3,2),
    accuracy_rate DECIMAL(3,2), -- successful / total
    
    -- Configuration
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 4000,
    
    -- Status
    is_active BOOLEAN DEFAULT FALSE, -- Only one should be active at a time
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    deactivated_at TIMESTAMPTZ
);

CREATE INDEX idx_intent_prompt_active ON intent_prompt_versions(is_active) WHERE is_active = TRUE;


-- ============================================================================
-- TABLE 5: Component Co-occurrence Patterns
-- Learn which components commonly appear together
-- ============================================================================
CREATE TABLE IF NOT EXISTS component_co_occurrence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Component Pair
    component_a TEXT NOT NULL,
    component_b TEXT NOT NULL,
    
    -- Statistics
    times_together INTEGER DEFAULT 1,
    typical_sequence TEXT, -- 'A_before_B', 'B_before_A', 'no_pattern'
    
    -- Context
    typical_use_case TEXT, -- e.g., "SFTP polling with transformation"
    example_iflow_names TEXT[],
    
    -- Confidence
    confidence_score DECIMAL(3,2), -- Based on frequency and user feedback
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint to prevent duplicates
CREATE UNIQUE INDEX idx_component_co_occurrence_unique ON component_co_occurrence(LEAST(component_a, component_b), GREATEST(component_a, component_b));


-- ============================================================================
-- VIEWS for Training and Analysis
-- ============================================================================

-- View: High-Quality Training Examples
CREATE OR REPLACE VIEW v_quality_training_examples AS
SELECT 
    id,
    user_query,
    components_identified,
    confidence_score,
    created_at
FROM intent_training_examples
WHERE approved_for_training = TRUE
  AND is_correct = TRUE
ORDER BY confidence_score DESC, training_weight DESC;


-- View: Common Intent Patterns
CREATE OR REPLACE VIEW v_common_intent_patterns AS
SELECT 
    intent_classification,
    COUNT(*) as occurrence_count,
    AVG(confidence_score) as avg_confidence,
    SUM(CASE WHEN is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as accuracy_rate
FROM intent_training_examples
WHERE is_correct IS NOT NULL
GROUP BY intent_classification
ORDER BY occurrence_count DESC;


-- View: Component Identification Accuracy
CREATE OR REPLACE VIEW v_component_accuracy AS
SELECT 
    jsonb_array_elements_text(components_identified::jsonb) as component_type,
    COUNT(*) as times_identified,
    SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as times_correct,
    (SUM(CASE WHEN is_correct THEN 1 ELSE 0 END)::FLOAT / COUNT(*))::DECIMAL(3,2) as accuracy
FROM intent_training_examples
WHERE is_correct IS NOT NULL
GROUP BY component_type
ORDER BY times_identified DESC;


-- ============================================================================
-- FUNCTIONS for Automated Learning
-- ============================================================================

-- Function: Update component pattern confidence
CREATE OR REPLACE FUNCTION update_pattern_confidence()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE component_pattern_library
    SET 
        confidence_score = (times_correct::DECIMAL / NULLIF(times_matched, 0)),
        updated_at = NOW()
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_pattern_confidence
    AFTER UPDATE OF times_matched, times_correct ON component_pattern_library
    FOR EACH ROW
    EXECUTE FUNCTION update_pattern_confidence();


-- Function: Process feedback for training
CREATE OR REPLACE FUNCTION process_feedback_for_training(feedback_id UUID)
RETURNS VOID AS $$
DECLARE
    feedback_record RECORD;
    missing_comp JSONB;
BEGIN
    -- Get feedback record
    SELECT * INTO feedback_record FROM generation_feedback WHERE id = feedback_id;
    
    IF feedback_record.missing_components IS NOT NULL THEN
        -- Add missing components to pattern library or update confidence
        FOR missing_comp IN SELECT * FROM jsonb_array_elements(feedback_record.missing_components)
        LOOP
            -- Logic to extract patterns from missing components
            -- This would analyze the query to find phrases that should have triggered this component
            -- For example, if "poll sftp" was in query but SFTPAdapter was missing,
            -- strengthen that pattern
            NULL; -- Placeholder - actual implementation would be more complex
        END LOOP;
    END IF;
    
    -- Mark as processed
    UPDATE generation_feedback SET processed_for_training = TRUE, processed_at = NOW() WHERE id = feedback_id;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- SEED DATA: Initial Component Patterns
-- ============================================================================

INSERT INTO component_pattern_library (trigger_phrase, component_type, pattern_category, aliases, typical_requirements) VALUES
-- Source Adapters
('poll sftp', 'SFTPAdapter', 'source_adapter', ARRAY['sftp polling', 'sftp sender', 'poll sftp server', 'retrieve from sftp', 'sftp receiver'], 
 '{"direction": "sender", "polling": true, "typical_interval": "5 minutes"}'::jsonb),

('sftp server', 'SFTPAdapter', 'source_adapter', ARRAY['sftp connection', 'connect to sftp'], 
 '{"authentication": "basic", "port": 22}'::jsonb),

('http endpoint', 'EndpointSender', 'source_adapter', ARRAY['https sender', 'receive http', 'http receiver', 'api endpoint'], 
 '{"protocol": "HTTPS", "method": "POST"}'::jsonb),

('timer', 'Timer', 'source_adapter', ARRAY['schedule', 'polling interval', 'every X minutes', 'cron'], 
 '{"type": "scheduled"}'::jsonb),

-- Transformation
('transform xml to json', 'GroovyScript', 'transformation', ARRAY['xml to json conversion', 'convert xml to json', 'xml json transformation'], 
 '{"input_format": "XML", "output_format": "JSON"}'::jsonb),

('groovy script', 'GroovyScript', 'transformation', ARRAY['custom script', 'data processing', 'script task'], 
 '{"type": "custom_logic"}'::jsonb),

('content modifier', 'ContentModifier', 'transformation', ARRAY['modify content', 'set header', 'set property', 'enrich'], 
 '{"type": "enricher"}'::jsonb),

('message mapping', 'MessageMapping', 'transformation', ARRAY['map fields', 'field mapping', 'data mapping'], 
 '{"type": "graphical_mapping"}'::jsonb),

-- Routing
('router', 'Router', 'routing', ARRAY['routing', 'conditional routing', 'route based on', 'branch'], 
 '{"type": "exclusive_gateway"}'::jsonb),

('splitter', 'Splitter', 'routing', ARRAY['split message', 'divide', 'break apart'], 
 '{"type": "general_splitter"}'::jsonb),

-- Target Adapters
('send to odata', 'RequestReply', 'target_adapter', ARRAY['odata call', 'post to odata', 'odata endpoint', 'call odata service'], 
 '{"adapter_type": "OData", "method": "POST"}'::jsonb),

('http call', 'RequestReply', 'target_adapter', ARRAY['http request', 'call http', 'rest api call', 'post to http'], 
 '{"adapter_type": "HTTP", "method": "POST"}'::jsonb),

('send to sap', 'RequestReply', 'target_adapter', ARRAY['sap call', 'post to sap', 'sap endpoint'], 
 '{"adapter_type": "HTTP", "target_system": "SAP"}'::jsonb)

ON CONFLICT DO NOTHING;


-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE intent_training_examples IS 'Stores user queries and intent analysis results for few-shot learning and model improvement';
COMMENT ON TABLE component_pattern_library IS 'Library of phrase patterns that map to SAP iFlow component types, used for intent understanding';
COMMENT ON TABLE generation_feedback IS 'User feedback on generated iFlows to identify intent understanding gaps';
COMMENT ON TABLE intent_prompt_versions IS 'Tracks different versions of the intent understanding prompt and their performance';
COMMENT ON TABLE component_co_occurrence IS 'Learns which components commonly appear together in successful iFlows';


