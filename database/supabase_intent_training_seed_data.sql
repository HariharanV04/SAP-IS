-- ============================================================================
-- SEED DATA: Intent Training Examples & Pattern Library
-- Based on real learnings from iFlow generation sessions
-- ============================================================================
--
-- ⚠️ CRITICAL ARCHITECTURE - RequestReply Pattern:
-- RequestReply is a COMMUNICATION PATTERN that works with adapter types.
-- It is ONE component with an adapter_type property, NOT two separate components!
--
-- Examples:
--   "Send to SAP OData"     → RequestReply (adapter_type: OData)    [1 component]
--   "Call SOAP service"     → RequestReply (adapter_type: SOAP)     [1 component]
--   "POST to REST endpoint" → RequestReply (adapter_type: HTTP)     [1 component]
--   "Query SuccessFactors"  → RequestReply (adapter_type: SuccessFactors) [1 component]
--
-- Supported adapter types: HTTP, OData, SOAP, SFTP, SuccessFactors, ProcessDirect
--
-- Standalone adapters (async/polling) are SEPARATE components:
--   "Poll SFTP every 5 min" → SFTPAdapter + Timer                   [2 components]
-- ============================================================================

-- ============================================================================
-- SECTION 1: Component Pattern Library (Expanded with Learnings)
-- ============================================================================

-- ============================================================================
-- Clear existing seed data if re-running (makes this script idempotent)
-- ============================================================================
-- Delete in correct order to respect foreign keys (children first, parents last)
DELETE FROM generation_feedback WHERE 1=1;
DELETE FROM component_co_occurrence WHERE 1=1;
DELETE FROM intent_training_examples WHERE 1=1;
DELETE FROM intent_prompt_versions WHERE 1=1;
DELETE FROM component_pattern_library WHERE 1=1;

-- SOURCE ADAPTERS (Critical - often missed!)
INSERT INTO component_pattern_library (trigger_phrase, component_type, pattern_category, aliases, typical_requirements, times_matched, times_correct, confidence_score, example_queries) VALUES

-- SFTP Patterns (HIGH PRIORITY - missed in our test case!)
('poll sftp', 'SFTPAdapter', 'source_adapter', 
 ARRAY['sftp polling', 'poll sftp server', 'sftp sender', 'poll from sftp', 'retrieve from sftp', 'sftp receiver', 'sftp inbound'],
 '{"direction": "sender", "polling": true, "typical_interval": "5 minutes", "operation": "GET"}'::jsonb,
 15, 14, 0.93,
 ARRAY['Poll SFTP server for new XML files', 'Retrieve files from SFTP every 5 minutes', 'SFTP polling integration']),

('sftp server', 'SFTPAdapter', 'source_adapter',
 ARRAY['sftp connection', 'connect to sftp', 'sftp endpoint', 'sftp source', 'files from sftp'],
 '{"authentication": "basic", "port": 22, "protocol": "SFTP"}'::jsonb,
 12, 11, 0.92,
 ARRAY['Connect to SFTP server', 'SFTP server at /incoming/orders', 'Files on SFTP server']),

('retrieve.*sftp', 'SFTPAdapter', 'source_adapter',
 ARRAY['get from sftp', 'fetch from sftp', 'download from sftp', 'read from sftp'],
 '{"direction": "sender", "operation": "GET"}'::jsonb,
 8, 7, 0.88,
 ARRAY['Retrieve XML files from SFTP server', 'Get files from SFTP path']),

-- Timer/Scheduler Patterns
('every \d+ (minute|hour|second)', 'Timer', 'source_adapter',
 ARRAY['scheduled', 'polling interval', 'poll every', 'runs every', 'trigger every'],
 '{"type": "scheduled", "unit": "minutes"}'::jsonb,
 10, 9, 0.90,
 ARRAY['Poll every 5 minutes', 'Runs every hour', 'Execute every 30 seconds']),

('poll.*every', 'Timer', 'source_adapter',
 ARRAY['polling schedule', 'periodic polling', 'scheduled polling'],
 '{"polling": true, "scheduled": true}'::jsonb,
 7, 6, 0.86,
 ARRAY['Poll SFTP every 5 minutes', 'Check for files every hour']),

-- HTTP/HTTPS Inbound
('http.*endpoint', 'EndpointSender', 'source_adapter',
 ARRAY['https endpoint', 'rest endpoint', 'api endpoint', 'http receiver', 'receive http', 'http listener'],
 '{"protocol": "HTTPS", "direction": "inbound"}'::jsonb,
 18, 17, 0.94,
 ARRAY['HTTP endpoint receives requests', 'REST API endpoint', 'HTTPS receiver']),

('receive.*http', 'EndpointSender', 'source_adapter',
 ARRAY['accept http', 'http inbound', 'incoming http'],
 '{"protocol": "HTTPS", "direction": "inbound"}'::jsonb,
 9, 8, 0.89,
 ARRAY['Receive HTTP POST requests', 'Accept HTTPS calls']),

-- File Adapter Patterns
('file.*poll', 'FileAdapter', 'source_adapter',
 ARRAY['poll file', 'file polling', 'watch directory', 'monitor folder'],
 '{"operation": "READ", "polling": true}'::jsonb,
 6, 5, 0.83,
 ARRAY['Poll file directory', 'Watch for new files']),

-- TRANSFORMATION COMPONENTS (Usually identified correctly)
('transform.*xml.*json', 'GroovyScript', 'transformation',
 ARRAY['xml to json', 'convert xml to json', 'xml json conversion', 'parse xml to json'],
 '{"input_format": "XML", "output_format": "JSON", "transformation_type": "format_conversion"}'::jsonb,
 25, 24, 0.96,
 ARRAY['Transform XML to JSON format', 'Convert XML files to JSON', 'XML to JSON transformation using Groovy']),

('transform.*json.*xml', 'GroovyScript', 'transformation',
 ARRAY['json to xml', 'convert json to xml', 'json xml conversion'],
 '{"input_format": "JSON", "output_format": "XML", "transformation_type": "format_conversion"}'::jsonb,
 18, 17, 0.94,
 ARRAY['Transform JSON to XML', 'Convert JSON payload to XML']),

('groovy script', 'GroovyScript', 'transformation',
 ARRAY['custom script', 'groovy transformation', 'script task', 'groovy code', 'data processing script'],
 '{"type": "custom_logic", "language": "Groovy"}'::jsonb,
 30, 28, 0.93,
 ARRAY['Add Groovy script for custom logic', 'Use Groovy to process data', 'Script for data transformation']),

('data transformation', 'GroovyScript', 'transformation',
 ARRAY['transform data', 'process data', 'data processing', 'manipulate data'],
 '{"type": "data_processing"}'::jsonb,
 22, 20, 0.91,
 ARRAY['Data transformation logic', 'Process and transform order data']),

('content modifier', 'ContentModifier', 'transformation',
 ARRAY['modify content', 'content enricher', 'set header', 'set property', 'add header', 'modify header', 'enrich message'],
 '{"type": "enricher", "operation": "modify"}'::jsonb,
 35, 34, 0.97,
 ARRAY['Modify content headers', 'Set message properties', 'Add tracking ID to payload']),

('add.*header', 'ContentModifier', 'transformation',
 ARRAY['set header', 'create header', 'modify header', 'header enrichment'],
 '{"type": "enricher", "target": "headers"}'::jsonb,
 16, 15, 0.94,
 ARRAY['Add timestamp header', 'Set custom headers for SAP']),

('message mapping', 'MessageMapping', 'transformation',
 ARRAY['field mapping', 'map fields', 'data mapping', 'graphical mapping'],
 '{"type": "graphical_mapping", "tool": "message_mapping"}'::jsonb,
 14, 13, 0.93,
 ARRAY['Map source fields to target', 'Message mapping between systems']),

('xslt.*transform', 'XSLTMapping', 'transformation',
 ARRAY['xslt mapping', 'xsl transformation', 'xml transformation using xslt'],
 '{"type": "xslt", "input": "XML", "output": "XML"}'::jsonb,
 8, 7, 0.88,
 ARRAY['XSLT transformation for XML', 'Transform XML using XSLT']),

-- ROUTING COMPONENTS
('router', 'Router', 'routing',
 ARRAY['route', 'routing', 'conditional routing', 'route based on', 'branch', 'decision', 'exclusive gateway'],
 '{"type": "exclusive_gateway", "routing_type": "conditional"}'::jsonb,
 28, 27, 0.96,
 ARRAY['Router based on payload', 'Route messages conditionally', 'Branch based on priority']),

('route.*based on', 'Router', 'routing',
 ARRAY['conditional route', 'routing condition', 'route if', 'branch based on'],
 '{"type": "exclusive_gateway", "has_condition": true}'::jsonb,
 15, 14, 0.93,
 ARRAY['Route based on message type', 'Branch based on priority field']),

('splitter', 'Splitter', 'routing',
 ARRAY['split', 'split message', 'divide message', 'break apart', 'split payload'],
 '{"type": "general_splitter", "split_strategy": "xpath"}'::jsonb,
 12, 11, 0.92,
 ARRAY['Split XML into multiple messages', 'Divide order items']),

('multicast', 'Multicast', 'routing',
 ARRAY['broadcast', 'parallel send', 'send to multiple', 'multiple recipients'],
 '{"type": "multicast", "parallel": true}'::jsonb,
 7, 6, 0.86,
 ARRAY['Send to multiple endpoints in parallel', 'Broadcast to all subscribers']),

('aggregator', 'Aggregator', 'routing',
 ARRAY['aggregate', 'combine messages', 'merge', 'collect', 'gather messages'],
 '{"type": "aggregator", "strategy": "collect"}'::jsonb,
 9, 8, 0.89,
 ARRAY['Aggregate responses', 'Combine split messages']),

-- TARGET ADAPTERS - RequestReply Pattern with Different Adapter Types
-- CRITICAL: RequestReply is ONE component with adapter_type property, NOT two separate components!

-- OData RequestReply
('send.*odata', 'RequestReply', 'target_adapter',
 ARRAY['post to odata', 'odata call', 'call odata', 'odata endpoint', 'odata request', 'query odata'],
 '{"adapter_type": "OData", "method": "POST", "direction": "outbound", "pattern": "request_reply"}'::jsonb,
 22, 21, 0.95,
 ARRAY['Send to SAP OData endpoint', 'POST to OData service', 'Call OData API']),

('odata.*endpoint', 'RequestReply', 'target_adapter',
 ARRAY['odata service', 'odata api', 'odata integration', 'odata synchronization'],
 '{"adapter_type": "OData", "protocol": "HTTP", "synchronous": true}'::jsonb,
 18, 17, 0.94,
 ARRAY['OData endpoint /sap/opu/odata', 'Connect to OData service']),

-- SOAP RequestReply
('soap.*call', 'RequestReply', 'target_adapter',
 ARRAY['call soap', 'soap service', 'soap endpoint', 'soap web service', 'soap request'],
 '{"adapter_type": "SOAP", "protocol": "SOAP", "synchronous": true}'::jsonb,
 15, 14, 0.93,
 ARRAY['Call SOAP web service', 'Send SOAP request', 'SOAP service integration']),

('call.*soap.*service', 'RequestReply', 'target_adapter',
 ARRAY['invoke soap', 'soap api', 'soap integration'],
 '{"adapter_type": "SOAP", "wsdl_required": true}'::jsonb,
 12, 11, 0.92,
 ARRAY['Invoke SOAP service with WSDL', 'Call external SOAP API']),

-- HTTP RequestReply (Default)
('post.*sap', 'RequestReply', 'target_adapter',
 ARRAY['send to sap', 'call sap', 'sap call', 'sap endpoint', 'sap integration'],
 '{"adapter_type": "HTTP", "target_system": "SAP", "method": "POST"}'::jsonb,
 25, 24, 0.96,
 ARRAY['POST to SAP S/4HANA', 'Send data to SAP via OData', 'Call SAP backend']),

('http.*call', 'RequestReply', 'target_adapter',
 ARRAY['http request', 'rest call', 'api call', 'http post', 'http get', 'rest api'],
 '{"adapter_type": "HTTP", "protocol": "HTTPS"}'::jsonb,
 30, 28, 0.93,
 ARRAY['Make HTTP call to external API', 'REST API call', 'HTTP POST request']),

('rest.*endpoint', 'RequestReply', 'target_adapter',
 ARRAY['rest service', 'restful api', 'rest integration'],
 '{"adapter_type": "HTTP", "api_type": "REST"}'::jsonb,
 18, 17, 0.91,
 ARRAY['Call REST endpoint', 'REST API integration']),

-- SuccessFactors RequestReply (SAP SF OData V2 Integration)
('successfactors.*query', 'RequestReply', 'target_adapter',
 ARRAY['query successfactors', 'sf call', 'success factors api', 'sf odata', 'query sf'],
 '{"adapter_type": "SuccessFactors", "protocol": "OData V2", "target_system": "SAP_SuccessFactors", "MessageProtocol": "OData V2"}'::jsonb,
 10, 9, 0.90,
 ARRAY['Query SuccessFactors employee data', 'Call SuccessFactors OData API', 'Get employee data from SuccessFactors']),

('employee.*successfactors', 'RequestReply', 'target_adapter',
 ARRAY['sf employee', 'successfactors employee central', 'employee data from sf', 'query employee central'],
 '{"adapter_type": "SuccessFactors", "protocol": "OData V2", "resourcePath": "EmpJob", "operation": "Query(GET)"}'::jsonb,
 8, 7, 0.88,
 ARRAY['Query employee data from SuccessFactors Employee Central', 'Sync employee data from SF']),

('successfactors.*odata', 'RequestReply', 'target_adapter',
 ARRAY['sf odata v2', 'successfactors odata api', 'sf api call'],
 '{"adapter_type": "SuccessFactors", "protocol": "OData V2", "TransportProtocol": "HTTP", "direction": "Receiver"}'::jsonb,
 7, 6, 0.86,
 ARRAY['SuccessFactors OData V2 integration', 'Call SF OData endpoint']),

-- ProcessDirect RequestReply (Internal)
('call.*internal.*iflow', 'RequestReply', 'target_adapter',
 ARRAY['process direct', 'internal call', 'call another iflow', 'processdirect'],
 '{"adapter_type": "ProcessDirect", "internal": true, "synchronous": true}'::jsonb,
 8, 7, 0.89,
 ARRAY['Call another iFlow internally', 'ProcessDirect integration']),

-- Generic RequestReply
('request.*reply', 'RequestReply', 'target_adapter',
 ARRAY['request-reply', 'requestreply', 'synchronous call', 'external call'],
 '{"pattern": "request_reply", "synchronous": true, "adapter_type": "HTTP"}'::jsonb,
 20, 19, 0.95,
 ARRAY['Request-reply pattern', 'Synchronous HTTP call']),

-- ERROR HANDLING
('error.*handling', 'ExceptionHandler', 'error_handling',
 ARRAY['exception handling', 'error management', 'catch errors', 'handle failures'],
 '{"type": "exception_subprocess"}'::jsonb,
 11, 10, 0.91,
 ARRAY['Error handling logic', 'Catch and log errors', 'Exception management']),

('retry', 'RetryHandler', 'error_handling',
 ARRAY['retry logic', 'retry mechanism', 'retry failed', 'retry on error'],
 '{"max_retries": 3, "retry_interval": "1 minute"}'::jsonb,
 8, 7, 0.88,
 ARRAY['Retry failed OData calls 3 times', 'Retry mechanism for errors']),

-- LOGGING & MONITORING
('log.*success', 'Logger', 'monitoring',
 ARRAY['logging', 'log events', 'audit log', 'track execution'],
 '{"log_level": "info", "log_type": "execution"}'::jsonb,
 13, 12, 0.92,
 ARRAY['Log success and failure', 'Track execution events', 'Audit logging']),

-- ADDITIONAL ADAPTERS
('mail.*send', 'MailAdapter', 'target_adapter',
 ARRAY['send email', 'email notification', 'mail adapter'],
 '{"operation": "SEND", "protocol": "SMTP"}'::jsonb,
 6, 5, 0.83,
 ARRAY['Send email notification', 'Email alert on completion']),

('jms.*queue', 'JMSAdapter', 'source_adapter',
 ARRAY['jms message', 'queue listener', 'message queue'],
 '{"protocol": "JMS", "queue_type": "queue"}'::jsonb,
 4, 3, 0.75,
 ARRAY['Listen to JMS queue', 'Receive from message queue'])

ON CONFLICT DO NOTHING;


-- ============================================================================
-- SECTION 2: Intent Training Examples (Real & Synthetic)
-- ============================================================================

-- Example 1: SFTP to SAP OData (From our test case - LEARNING EXAMPLE!)
INSERT INTO intent_training_examples (
    user_query,
    markdown_content,
    intent_classification,
    components_identified,
    is_correct,
    missing_components,
    user_corrections,
    confidence_score,
    model_version,
    prompt_version,
    approved_for_training,
    training_weight
) VALUES (
    'Create a complete SAP iFlow integration package for SFTP to SAP OData Synchronization. Poll SFTP server for XML files every 5 minutes, transform XML to JSON, modify headers, and POST to SAP OData endpoint.',
    
    '# Integration Flow: SFTP to SAP OData Synchronization
## Overview: This integration retrieves XML files from an SFTP server and posts them to SAP via OData.
## Source System: SFTP Server (/incoming/orders), XML files, Polling: Every 5 minutes
## Transformation: Extract order data, Transform XML to JSON, Add timestamp
## Target System: SAP S/4HANA via OData (/sap/opu/odata/sap/API_SALES_ORDER_SRV)',
    
    'complete_iflow_creation',
    
    '[
        {"type": "ContentModifier", "name": "ContentModifier", "quantity": 1},
        {"type": "GroovyScript", "name": "GroovyScript", "quantity": 2},
        {"type": "RequestReply", "name": "RequestReply", "adapter_type": "HTTP", "quantity": 1}
    ]'::jsonb,
    
    FALSE, -- Not correct - missed SFTP and Timer!
    
    '[
        {"type": "SFTPAdapter", "reason": "Poll SFTP server mentioned explicitly"},
        {"type": "Timer", "reason": "Polling every 5 minutes mentioned"}
    ]'::jsonb,
    
    '{"correct_components": ["ContentModifier", "GroovyScript", "RequestReply"], 
      "should_have_identified": ["SFTPAdapter", "Timer"],
      "learnings": "Always check for source system adapters. Poll + SFTP = SFTPAdapter + Timer"}'::jsonb,
    
    0.75,
    'gpt-4',
    'v1.0',
    TRUE,
    2.0 -- High weight - important learning!
);

-- Example 2: Simple HTTP to HTTP (Correct identification)
INSERT INTO intent_training_examples (
    user_query,
    intent_classification,
    components_identified,
    is_correct,
    confidence_score,
    approved_for_training,
    training_weight
) VALUES (
    'Create an iFlow that receives HTTP POST requests, modifies the content, and sends to an external API.',
    'complete_iflow_creation',
    '[
        {"type": "EndpointSender", "name": "HTTPReceiver", "quantity": 1},
        {"type": "ContentModifier", "name": "ModifyPayload", "quantity": 1},
        {"type": "RequestReply", "name": "ExternalAPICall", "adapter_type": "HTTP", "quantity": 1}
    ]'::jsonb,
    TRUE,
    0.95,
    TRUE,
    1.5
);

-- Example 3: File Polling with Transformation
INSERT INTO intent_training_examples (
    user_query,
    intent_classification,
    components_identified,
    is_correct,
    confidence_score,
    approved_for_training,
    training_weight
) VALUES (
    'Poll file directory every 10 minutes, read CSV files, transform to XML using XSLT, and post to SAP.',
    'complete_iflow_creation',
    '[
        {"type": "FileAdapter", "name": "FilePoller", "quantity": 1},
        {"type": "Timer", "name": "ScheduledTimer", "quantity": 1},
        {"type": "XSLTMapping", "name": "CSVtoXML", "quantity": 1},
        {"type": "RequestReply", "name": "SAPCall", "adapter_type": "OData", "quantity": 1}
    ]'::jsonb,
    TRUE,
    0.92,
    TRUE,
    1.5
);

-- Example 4: Router with Multiple Branches
INSERT INTO intent_training_examples (
    user_query,
    intent_classification,
    components_identified,
    is_correct,
    confidence_score,
    approved_for_training
) VALUES (
    'Create an iFlow with content modifier, then router that branches to two groovy scripts based on priority field.',
    'complete_iflow_creation',
    '[
        {"type": "ContentModifier", "name": "SetPriority", "quantity": 1},
        {"type": "Router", "name": "PriorityRouter", "routing_criteria": "priority", "branch_count": 2, "quantity": 1},
        {"type": "GroovyScript", "name": "HighPriorityProcessor", "quantity": 1},
        {"type": "GroovyScript", "name": "LowPriorityProcessor", "quantity": 1}
    ]'::jsonb,
    TRUE,
    0.94,
    TRUE
);

-- Example 5: Splitter-Aggregator Pattern
INSERT INTO intent_training_examples (
    user_query,
    intent_classification,
    components_identified,
    is_correct,
    confidence_score,
    approved_for_training
) VALUES (
    'Split incoming XML into multiple line items, process each with groovy, then aggregate responses.',
    'complete_iflow_creation',
    '[
        {"type": "Splitter", "name": "LineItemSplitter", "quantity": 1},
        {"type": "GroovyScript", "name": "ProcessLineItem", "quantity": 1},
        {"type": "Aggregator", "name": "AggregateResults", "quantity": 1}
    ]'::jsonb,
    TRUE,
    0.91,
    TRUE
);


-- ============================================================================
-- SECTION 3: Component Co-occurrence Patterns
-- ============================================================================

INSERT INTO component_co_occurrence (component_a, component_b, times_together, typical_sequence, typical_use_case, confidence_score) VALUES
('SFTPAdapter', 'Timer', 25, 'together', 'SFTP polling - always need timer for scheduled polling', 0.98),
('SFTPAdapter', 'ContentModifier', 20, 'A_before_B', 'SFTP retrieval followed by content enrichment', 0.92),
('ContentModifier', 'GroovyScript', 35, 'no_pattern', 'Common transformation combo', 0.95),
('GroovyScript', 'RequestReply', 30, 'A_before_B', 'Transform data then send to target', 0.93),
('Splitter', 'Aggregator', 18, 'A_before_B', 'Split-process-aggregate pattern', 0.96),
('Router', 'GroovyScript', 22, 'A_before_B', 'Router branches to processing scripts', 0.91),
('EndpointSender', 'ContentModifier', 28, 'A_before_B', 'Receive HTTP then enrich content', 0.94),
('RequestReply', 'ContentModifier', 15, 'B_before_A', 'Modify content before external call', 0.89)
ON CONFLICT DO NOTHING;


-- ============================================================================
-- SECTION 4: Initial Prompt Version
-- ============================================================================

INSERT INTO intent_prompt_versions (
    version,
    prompt_template,
    few_shot_examples,
    total_uses,
    successful_generations,
    is_active,
    temperature,
    max_tokens
) VALUES (
    'v1.0',
    'Base intent understanding prompt without pattern library',
    '[]'::jsonb,
    100,
    65,
    FALSE, -- Old version
    0.7,
    4000
);

INSERT INTO intent_prompt_versions (
    version,
    prompt_template,
    few_shot_examples,
    total_uses,
    successful_generations,
    is_active,
    temperature,
    max_tokens,
    activated_at
) VALUES (
    'v2.0',
    'Enhanced prompt with pattern library and few-shot examples',
    '[
        {"query": "Poll SFTP every 5 minutes", "components": ["SFTPAdapter", "Timer"]},
        {"query": "Transform XML to JSON", "components": ["GroovyScript"]},
        {"query": "Send to SAP OData", "components": ["RequestReply"]}
    ]'::jsonb,
    0,
    0,
    TRUE, -- Current active version
    0.7,
    4000,
    NOW()
);


-- ============================================================================
-- SECTION 5: Verification Queries
-- ============================================================================

-- Verify patterns were inserted
DO $$
DECLARE
    pattern_count INTEGER;
    example_count INTEGER;
    co_occur_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO pattern_count FROM component_pattern_library;
    SELECT COUNT(*) INTO example_count FROM intent_training_examples;
    SELECT COUNT(*) INTO co_occur_count FROM component_co_occurrence;
    
    RAISE NOTICE '✅ Seed data loaded successfully:';
    RAISE NOTICE '   • Component Patterns: %', pattern_count;
    RAISE NOTICE '   • Training Examples: %', example_count;
    RAISE NOTICE '   • Co-occurrence Patterns: %', co_occur_count;
    
    IF pattern_count < 30 THEN
        RAISE WARNING '⚠️ Expected at least 30 component patterns, found %', pattern_count;
    END IF;
END $$;


-- Show pattern library summary
SELECT 
    pattern_category,
    COUNT(*) as pattern_count,
    AVG(confidence_score)::DECIMAL(3,2) as avg_confidence
FROM component_pattern_library
GROUP BY pattern_category
ORDER BY pattern_count DESC;


-- Show high-priority learnings
SELECT 
    user_query,
    is_correct,
    training_weight,
    CASE 
        WHEN is_correct THEN '✅ Correct'
        ELSE '❌ Learning Example'
    END as status
FROM intent_training_examples
WHERE approved_for_training = TRUE
ORDER BY training_weight DESC, confidence_score DESC;

