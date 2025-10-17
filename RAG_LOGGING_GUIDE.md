# RAG Component Retrieval Logging Guide

## Overview

Comprehensive logging system for tracking RAG component retrieval, selection, and iFlow generation across all IMigrate services.

**Date Created**: 2025-01-17
**Status**: ✅ Implemented

---

## 🎯 Purpose

This logging system provides:

1. **Full visibility** into which components are retrieved from RAG
2. **Component metadata** including IDs, types, similarity scores
3. **Retrieval context** (query, location, pattern type)
4. **Component selection** tracking (what was chosen and why)
5. **Generation results** (success/failure, final iFlow details)
6. **Troubleshooting data** for debugging incorrect component selection

---

## 📂 Log File Locations

### Directory Structure

```
/IMigrate/agentic-rag-IMigrate/
├── logs/
│   └── rag_agent/
│       ├── rag_retrieval_YYYYMMDD_HHMMSS.log      # Human-readable text log
│       └── rag_retrieval_YYYYMMDD_HHMMSS.json     # Structured JSON log
│
├── intent_analysis_debug/
│   ├── intent_response_YYYYMMDD_HHMMSS.txt        # Successful intent analysis
│   └── intent_error_YYYYMMDD_HHMMSS.txt           # Failed intent analysis
```

### Log Files Created Per Session

Each time you start the RAG API service and process a request, new log files are created with timestamps.

---

## 📊 Log File Formats

### 1. Text Log Format (`rag_retrieval_*.log`)

Human-readable format for quick troubleshooting:

```
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO - ================================================================================
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO - RAG RETRIEVAL - vector_search
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO - Timestamp: 2025-01-17T14:30:52.123456
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO - Context: {
  "node_id": "comp_123",
  "node_name": "HTTP Sender",
  "node_type": "EndpointSender",
  "iflow_name": "Stripe_Integration",
  "retrieval_location": "_retrieve_artifacts_by_node_order"
}
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO - Query: EndpointSender HTTP Sender Stripe_Integration
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO - Results: 3 components retrieved
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO - --------------------------------------------------------------------------------
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO -   [1] EndpointSender - Stripe_HTTPS_Sender
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO -       ID: chunk_456
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO -       Chunk Type: complete_xml
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO -       Similarity: 0.8765
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO -       iFlow ID: iflow_stripe_001
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO -       Component ID: sender_https_01
2025-01-17 14:30:52 - RAGLogger.RAG_Agent - INFO -       Description: HTTPS sender adapter for Stripe API communication
```

### 2. JSON Log Format (`rag_retrieval_*.json`)

Structured format for programmatic analysis:

```json
{
  "session_id": "20250117_143052",
  "service": "RAG_Agent",
  "started_at": "2025-01-17T14:30:52.123456",
  "retrievals": [
    {
      "timestamp": "2025-01-17T14:30:52.123456",
      "retrieval_type": "vector_search",
      "query": "EndpointSender HTTP Sender Stripe_Integration",
      "context": {
        "node_id": "comp_123",
        "node_name": "HTTP Sender",
        "node_type": "EndpointSender",
        "iflow_name": "Stripe_Integration",
        "retrieval_location": "_retrieve_artifacts_by_node_order"
      },
      "num_results": 3,
      "components": [
        {
          "rank": 1,
          "id": "chunk_456",
          "document_name": "Stripe_HTTPS_Sender",
          "chunk_type": "complete_xml",
          "component_type": "EndpointSender",
          "similarity_score": 0.8765,
          "metadata": {
            "iflow_id": "iflow_stripe_001",
            "component_id": "sender_https_01",
            "artifact_name": "HTTPS_Sender_Stripe",
            "description": "HTTPS sender adapter for Stripe API communication"
          },
          "content_preview": "<?xml version=\"1.0\" encoding=\"UTF-8\"?><bpmn2:participant id=\"Sender\" name=\"Stripe API\"..."
        }
      ]
    },
    {
      "timestamp": "2025-01-17T14:31:15.654321",
      "type": "component_selection",
      "reason": "Strategic plan execution with intelligent intent understanding",
      "context": {
        "user_query": "Create iFlow for Stripe payment processing",
        "query_interpretation": "Build complete Stripe payment integration with HTTP sender, request-reply, and data mapping",
        "user_goal": "Stripe payment processing integration",
        "total_components": 7,
        "has_router": false
      },
      "selected_components": [
        {
          "type": "StartEvent",
          "name": "Start 1",
          "id": "start_evt_1",
          "source": "authoritative_standards"
        },
        {
          "type": "EndpointSender",
          "name": "Stripe API Sender",
          "id": "sender_1",
          "source": "rag_retrieved"
        }
      ]
    },
    {
      "timestamp": "2025-01-17T14:31:45.987654",
      "type": "generation_result",
      "iflow_name": "Stripe_Payment_Processing",
      "success": true,
      "error": null,
      "components_used": [
        {
          "type": "StartEvent",
          "name": "Start 1",
          "id": "start_evt_1"
        },
        {
          "type": "EndpointSender",
          "name": "Stripe API Sender",
          "id": "sender_1"
        }
      ]
    }
  ],
  "completed_at": "2025-01-17T14:31:45.987654"
}
```

---

## 🔍 What Gets Logged

### 1. RAG Vector Search Retrievals

**When**: Every time the agent searches the vector database for components

**Location**: Multiple points in agent.py:
- `_retrieve_artifacts_by_node_order` (line 1091)
- `_rag_search_request_reply_components` (line 4633)

**Logged Information**:
- Search query used
- Number of results returned
- For each retrieved component:
  - Unique ID (`id`)
  - Document name (`document_name`)
  - Chunk type (`chunk_type`: complete_xml, config, summary)
  - Component type (`component_type`: EndpointSender, RequestReply, etc.)
  - Similarity score (0.0 to 1.0)
  - Metadata:
    - iFlow ID
    - Component ID
    - Artifact name
    - Description
  - Content preview (first 300 characters)

### 2. Component Selection

**When**: After all components are identified and selected for iFlow generation

**Location**: `create_complete_iflow_package` method (line 5106)

**Logged Information**:
- List of all selected components
- Reason for selection
- Context:
  - Original user query
  - Query interpretation
  - User goal
  - Total component count
  - Router presence

### 3. Generation Results

**When**: After iFlow package is successfully created

**Location**: `create_complete_iflow_package` method (line 5139)

**Logged Information**:
- iFlow name
- All components used
- Success/failure status
- Error message (if failed)

---

## 🚀 How to Use the Logs

### Starting the System

1. **Start RAG API Service**:
```bash
cd /IMigrate/agentic-rag-IMigrate
python3 rag_api_service.py
```

You'll see:
```
2025-01-17 14:30:00 - RAGLogger.RAG_Agent - INFO - ================================================================================
2025-01-17 14:30:00 - RAGLogger.RAG_Agent - INFO - RAG Logger initialized for RAG_Agent
2025-01-17 14:30:00 - RAGLogger.RAG_Agent - INFO - Log file: /path/to/logs/rag_agent/rag_retrieval_20250117_143000.log
2025-01-17 14:30:00 - RAGLogger.RAG_Agent - INFO - JSON log: /path/to/logs/rag_agent/rag_retrieval_20250117_143000.json
```

2. **Upload documentation** via the IMigrate frontend

3. **Check logs** in real-time:
```bash
# Watch text log
tail -f /IMigrate/agentic-rag-IMigrate/logs/rag_agent/rag_retrieval_*.log

# View JSON log
cat /IMigrate/agentic-rag-IMigrate/logs/rag_agent/rag_retrieval_*.json | jq .
```

### Analyzing Logs

#### Example 1: Check what components were retrieved for a specific query

**Text Log**:
```bash
grep -A 20 "Query: RequestReply" rag_retrieval_*.log
```

**JSON Log**:
```bash
cat rag_retrieval_*.json | jq '.retrievals[] | select(.query | contains("RequestReply"))'
```

#### Example 2: Find components with high similarity scores

**Text Log**:
```bash
grep "Similarity: 0.9" rag_retrieval_*.log
```

**JSON Log**:
```bash
cat rag_retrieval_*.json | jq '.retrievals[].components[] | select(.similarity_score > 0.9)'
```

#### Example 3: Check which components were selected for final iFlow

**Text Log**:
```bash
grep -A 30 "COMPONENT SELECTION" rag_retrieval_*.log
```

**JSON Log**:
```bash
cat rag_retrieval_*.json | jq '.retrievals[] | select(.type == "component_selection")'
```

#### Example 4: View all retrieval locations

**JSON Log**:
```bash
cat rag_retrieval_*.json | jq '.retrievals[].context.retrieval_location' | sort | uniq
```

---

## 🐛 Troubleshooting with Logs

### Problem: Wrong component retrieved

**Steps**:

1. Find the retrieval in the log:
```bash
grep -A 20 "Query: <your-component-type>" rag_retrieval_*.log
```

2. Check:
   - **Similarity scores**: Are they too low? (< 0.7 is concerning)
   - **Component IDs**: Is the correct iFlow ID being retrieved?
   - **Chunk type**: Is it retrieving `complete_xml`, `config`, or just `summary`?
   - **Document name**: Does it match what you expect?

3. If wrong component:
   - Check if the query is correct (context shows the query used)
   - Check if the correct component exists in vector DB
   - Check similarity score threshold

### Problem: Component not found

**Steps**:

1. Check retrieval logs:
```bash
grep "Results: 0 components" rag_retrieval_*.log
```

2. Check the query:
```bash
grep -B 5 "Results: 0 components" rag_retrieval_*.log
```

3. If no results:
   - Verify component exists in vector DB
   - Check if chunk_types filter is too restrictive
   - Try broader search query

### Problem: iFlow generation failed

**Steps**:

1. Check generation result:
```bash
grep -A 10 "IFLOW GENERATION RESULT" rag_retrieval_*.log
```

2. Check for error:
```bash
grep "Status: FAILED" rag_retrieval_*.log
```

3. Review selected components:
```bash
grep -A 30 "COMPONENT SELECTION" rag_retrieval_*.log
```

---

## 📈 Log Analysis Examples

### Example: Track Full Request Flow

**Scenario**: User uploads "Stripe to Salesforce" documentation

**What to look for**:

1. **Intent Analysis**:
```bash
cat intent_analysis_debug/intent_response_*.txt
```
Check: Did it correctly identify HTTP sender, RequestReply, data mapping?

2. **Component Retrieval**:
```bash
grep "Query:" rag_retrieval_*.log | head -20
```
Check: What queries were generated for each component?

3. **Component Selection**:
```bash
grep -A 50 "COMPONENT SELECTION" rag_retrieval_*.log
```
Check: Were all required components selected?

4. **Generation Result**:
```bash
grep -A 20 "GENERATION RESULT" rag_retrieval_*.log
```
Check: Was package created successfully?

---

## 🔧 Advanced Usage

### Comparing Different Runs

```bash
# Get all session IDs
for file in logs/rag_agent/*.json; do
    jq -r '.session_id' "$file"
done

# Compare retrieval counts
for file in logs/rag_agent/*.json; do
    echo "Session: $(jq -r '.session_id' "$file")"
    echo "Retrievals: $(jq '.retrievals | length' "$file")"
    echo "---"
done
```

### Exporting Component Statistics

```bash
# Extract all component types retrieved
cat rag_retrieval_*.json | jq -r '.retrievals[].components[].component_type' | sort | uniq -c | sort -rn

# Calculate average similarity scores
cat rag_retrieval_*.json | jq '.retrievals[].components[].similarity_score' | awk '{sum+=$1; count++} END {print "Average:", sum/count}'

# Find most used iFlow IDs
cat rag_retrieval_*.json | jq -r '.retrievals[].components[].metadata.iflow_id' | sort | uniq -c | sort -rn
```

---

## 📝 Integration with Other Services

### BoomiToIS-API Logs

**Location**: `/IMigrate/BoomiToIS-API/logs/` (if extended)

Future enhancement: Add RAG logger to BoomiToIS-API for tracking which API calls were made to RAG service.

### MuleToIS-API Logs

**Location**: `/IMigrate/MuleToIS-API/logs/` (if extended)

Future enhancement: Add RAG logger to MuleToIS-API for tracking which API calls were made to RAG service.

---

## 🎓 Best Practices

### 1. Regular Log Review

- Check logs after each iFlow generation
- Compare successful vs failed generations
- Track similarity score trends

### 2. Log Retention

- Keep logs for at least 30 days
- Archive old logs to separate directory
- Clean up logs older than 90 days

### 3. Performance Monitoring

- Track number of retrievals per iFlow
- Monitor average similarity scores
- Identify slow queries

### 4. Quality Assurance

- Verify correct components retrieved
- Check component metadata accuracy
- Validate iFlow generation success rate

---

## 🆘 Common Issues

### Issue: No logs being created

**Solution**:
- Check if RAG API service started successfully
- Verify `/logs/rag_agent/` directory exists
- Check file permissions

### Issue: Logs too verbose

**Solution**:
- Use JSON logs for structured queries instead of reading all text
- Filter logs by timestamp or query type
- Use `jq` for targeted JSON queries

### Issue: Can't find specific retrieval

**Solution**:
- Search by query: `grep "Query: <text>" rag_retrieval_*.log`
- Search by component type: `cat *.json | jq '.retrievals[].components[] | select(.component_type == "RequestReply")'`
- Search by timestamp: `grep "2025-01-17T14:30" rag_retrieval_*.log`

---

## 📚 Related Documentation

- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - RAG integration overview
- [PLANNING.md](PLANNING.md) - Project architecture
- [agentic-rag-IMigrate/agent/agent.py](agentic-rag-IMigrate/agent/agent.py) - Agent implementation with logging

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-17 | 1.0 | Initial implementation with comprehensive logging |

---

**Status**: ✅ Ready for Testing
**Next Steps**: Test with real documentation upload and verify log output
