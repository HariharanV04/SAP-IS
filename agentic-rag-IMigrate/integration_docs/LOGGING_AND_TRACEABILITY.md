# 📝 Logging and Traceability Guide

## Overview
The integrated RAG-IMigrate system has **comprehensive logging and file saving** mechanisms for debugging, traceability, and issue resolution.

---

## 📂 **Saved Files & Directories**

### **1. Query Logs** 🆕
**Location:** `query_logs/query_YYYYMMDD_HHMMSS.json`

**What's Saved:**
```json
{
  "timestamp": "20251016_143022",
  "job_id": "abc123-xyz789",
  "iflow_name": "BoomiFlow_abc123",
  "original_markdown": "# Dell Boomi Process Documentation\n\n## Process: CustomerDataSync...",
  "markdown_length": 5432,
  "constructed_query": "Create a complete SAP iFlow integration package named 'BoomiFlow_abc123'...",
  "query_length": 7654,
  "markdown_truncated_at": 2000,
  "api_endpoint": "/api/generate-iflow-from-markdown",
  "request_time": "2025-10-16T14:30:22.123456"
}
```

**Purpose:**
- ✅ See the **original markdown** IMigrate sent
- ✅ See the **constructed natural language query** sent to RAG Agent
- ✅ Debug query construction issues
- ✅ Trace what documentation was provided
- ✅ Correlate with other files via timestamp

---

### **2. Strategic Plans**
**Location:** `strategic_plans/strategic_plan_YYYYMMDD_HHMMSS.json`

**What's Saved:**
```json
{
  "query": "Create an iflow with HTTP sender, content modifier, and OData request reply",
  "timestamp": "20251010_160047",
  "intent_classification": "complete_iflow_creation",
  "user_goal": "Create SAP iFlow components",
  "query_interpretation": "Heuristic analysis of: Create an iflow with...",
  "total_components": 5,
  "generation_order": ["StartEvent", "EndpointSender", "ContentModifier", "RequestReply", "EndEvent"],
  "integration_approach": "Sequential flow",
  "execution_steps": [
    "1. Understand user intent",
    "2. Identify all required components",
    ...
  ],
  "components": [
    {
      "type": "EndpointSender",
      "name": "H T T P Sender 1",
      "quantity": 1,
      "adapter_type": "OData",
      "source": "explicit",
      "priority": "high"
    }
  ],
  "rag_strategy": {
    "ContentModifier": {
      "search_queries": ["contentmodifier", "content enricher XML", ...],
      "search_limit": 5,
      "chunk_types": ["xml", "groovy", "component"],
      "priority": "high"
    }
  }
}
```

**Purpose:**
- ✅ See **intent analysis** results from LLM
- ✅ See **detected components** with quantities
- ✅ See **generation order** RAG Agent will follow
- ✅ See **RAG search strategy** for each component
- ✅ Debug component detection issues
- ✅ Understand why certain components were added/omitted

---

### **3. Component Metadata**
**Location:** `component_metadata/iflow_components_YYYYMMDD_HHMMSS.json`

**What's Saved:**
```json
{
  "query": "Create an iflow with HTTP sender, content modifier, and OData request reply",
  "timestamp": "20251010_160047",
  "total_components": 5,
  "components": [
    {
      "component_id": 1,
      "component_type": "EndpointSender",
      "component_name": "H T T P Sender 1",
      "xml_element": "participant",
      "keyword_matched": "EndpointSender",
      "instance_number": 1,
      "total_instances": 1,
      "rag_queries": [],
      "description": "EndpointSender component named 'H T T P Sender 1'",
      "source": "explicit",
      "priority": "high",
      "properties": {
        "activityType": "participant",
        "cmdVariantUri": "Unknown",
        "componentVersion": "1.1"
      }
    },
    {
      "component_id": 3,
      "component_type": "RequestReply",
      "xml_element": "serviceTask",
      "adapter_type": "OData",
      "properties": {
        "activityType": "RequestReply",
        "cmdVariantUri": "ctype::FlowstepVariant/cname::RequestReply/version::1.0.0",
        "adapter_type": "OData"
      }
    }
  ]
}
```

**Purpose:**
- ✅ See **detailed component specifications**
- ✅ See **SAP-compliant properties** for each component
- ✅ See **XML element mappings** (participant, serviceTask, etc.)
- ✅ Debug component generation issues
- ✅ Verify adapter types (HTTP/OData)
- ✅ Check component versioning

---

### **4. Generated Packages**
**Location:** `generated_packages/N_Complete_YYYYMMDD_HHMMSS.zip`

**What's Saved:**
- Complete SAP Integration Suite importable iFlow package
- BPMN2 XML files
- MANIFEST.MF
- Component resources (Groovy scripts, message mappings, etc.)

**Purpose:**
- ✅ The final output - deployable to SAP Integration Suite
- ✅ Can be imported and inspected in SAP Web UI
- ✅ Contains all generated XML

---

## 📋 **Console Logging**

### **RAG API Service Logs** (`rag_api_service.py`)

**Startup Logs:**
```
2025-10-16 14:30:15 - INFO - Query logs will be saved to: C:\...\query_logs
2025-10-16 14:30:15 - INFO - Strategic plans will be saved to: C:\...\strategic_plans
2025-10-16 14:30:15 - INFO - Metadata will be saved to: C:\...\component_metadata
2025-10-16 14:30:15 - INFO - Packages will be saved to: C:\...\generated_packages
2025-10-16 14:30:15 - INFO - ================================================================================
2025-10-16 14:30:15 - INFO - INITIALIZING RAG API SERVICE
2025-10-16 14:30:15 - INFO - ================================================================================
2025-10-16 14:30:16 - INFO - ✅ Neo4j Knowledge Graph connected
2025-10-16 14:30:17 - INFO - ✅ RAG Agent initialized successfully
```

**Request Logs:**
```
2025-10-16 14:30:22 - INFO - 🚀 RAG API: Received iFlow generation request
2025-10-16 14:30:22 - INFO - 📝 iFlow Name: BoomiFlow_abc123
2025-10-16 14:30:22 - INFO - 🔑 Job ID: abc123-xyz789
2025-10-16 14:30:22 - INFO - 📄 Markdown length: 5432 characters
2025-10-16 14:30:22 - INFO - 📁 Using default output directory: C:\...\generated_packages
2025-10-16 14:30:22 - INFO - 🔍 Analyzing markdown documentation...
2025-10-16 14:30:22 - INFO - 🤖 Calling RAG Agent to generate iFlow...
2025-10-16 14:30:22 - INFO - 📋 Query length: 7654 characters
2025-10-16 14:30:22 - INFO - 📝 Query log saved to: C:\...\query_logs\query_20251016_143022.json
```

**Completion Logs:**
```
2025-10-16 14:32:45 - INFO - ✅ RAG Agent completed with status: success
2025-10-16 14:32:45 - INFO - 💾 Metadata saved to: C:\...\component_metadata\iflow_components_20251016_143022.json
2025-10-16 14:32:45 - INFO - ================================================================================
2025-10-16 14:32:45 - INFO - ✅ iFlow Generation SUCCESSFUL
2025-10-16 14:32:45 - INFO - 📦 Package: C:\...\generated_packages\N_Complete_20251016_143022.zip
2025-10-16 14:32:45 - INFO - 📊 Metadata: C:\...\component_metadata\iflow_components_20251016_143022.json
2025-10-16 14:32:45 - INFO - 🔧 Components: 5
2025-10-16 14:32:45 - INFO - ================================================================================
```

### **RAG Agent Logs** (`agent/agent.py`)

**Intent Analysis:**
```
🧠 [INTENT_ANALYSIS] Analyzing user intent for: 'Create a complete SAP iFlow...'
🔍 [INTENT_ANALYSIS] Using comprehensive LLM-based intent understanding (user-intent driven)
✅ [INTENT_ANALYSIS] Intent understood: Create SAP iFlow with multiple components
📊 [COMPONENTS] Detected 3 explicit components
🔧 [IMPLICIT] Detected 2 implicit components
```

**Strategic Planning:**
```
📋 [STRATEGIC_PLANNING] Creating strategic plan...
   📊 [GEN_ORDER] Generation order: ['StartEvent', 'EndpointSender', 'ContentModifier', 'RequestReply', 'EndEvent']
📊 [STRATEGIC_PLAN] Plan created:
   🎯 Intent: complete_iflow_creation
   📦 Components: 5
   🔄 Order: StartEvent → EndpointSender → ContentModifier → RequestReply → EndEvent
   🧠 Interpretation: User wants HTTP endpoint with content transformation and external call
```

**Metadata Export:**
```
📄 [STRATEGIC_PLAN_EXPORT] Strategic plan exported to: strategic_plans/strategic_plan_20251016_143022.json
   🎯 Intent: complete_iflow_creation
   📦 Components: 5
   🔄 Order: StartEvent → EndpointSender → ContentModifier → RequestReply → EndEvent
   
📄 [METADATA_EXPORT] Component metadata exported to: component_metadata/iflow_components_20251016_143022.json
   📊 Components: 5
   🔍 Query: 'Create a complete SAP iFlow...'
```

---

## 🔍 **Tracing Issues - Step by Step**

### **Scenario: iFlow generation failed or produced wrong components**

**Step 1: Check Query Log**
```bash
# Open: query_logs/query_20251016_143022.json
```
- ✅ Verify `original_markdown` contains expected documentation
- ✅ Verify `constructed_query` looks correct
- ✅ Check if markdown was truncated properly (first 2000 chars)

**Step 2: Check Strategic Plan**
```bash
# Open: strategic_plans/strategic_plan_20251016_143022.json
```
- ✅ Verify `intent_classification` is correct
- ✅ Check `components` array - are all expected components listed?
- ✅ Check `adapter_type` for RequestReply components
- ✅ Verify `generation_order` matches expected sequence
- ✅ Review `rag_strategy` - are search queries appropriate?

**Step 3: Check Component Metadata**
```bash
# Open: component_metadata/iflow_components_20251016_143022.json
```
- ✅ Verify each component has correct `component_type`
- ✅ Check `xml_element` mappings (participant, serviceTask, callActivity)
- ✅ Verify `properties` contain valid SAP standards
- ✅ Check `adapter_type` for RequestReply

**Step 4: Check Console Logs**
```bash
# In RAG API Service terminal (Port 5010)
# Look for error messages or warnings
```

**Step 5: Inspect Generated Package**
```bash
# Extract: generated_packages/N_Complete_20251016_143022.zip
# Open: src/main/resources/bpmn/Integration Process.bpmn
# Inspect the BPMN2 XML
```

---

## 🎯 **File Correlation via Timestamps**

All files use the **same timestamp format**: `YYYYMMDD_HHMMSS`

For a single iFlow generation, you'll have:
```
query_logs/query_20251016_143022.json
strategic_plans/strategic_plan_20251016_143022.json
component_metadata/iflow_components_20251016_143022.json
generated_packages/N_Complete_20251016_143022.zip
```

**All files with the same timestamp belong to the same generation request!**

---

## 📊 **Summary: What's Logged**

| **Aspect** | **File** | **Purpose** |
|------------|----------|-------------|
| Original Markdown | `query_logs/query_*.json` | IMigrate's generated documentation |
| Constructed Query | `query_logs/query_*.json` | Natural language query sent to RAG Agent |
| Intent Analysis | `strategic_plans/strategic_plan_*.json` | LLM's understanding of user intent |
| Component Detection | `strategic_plans/strategic_plan_*.json` | Which components were identified |
| Generation Order | `strategic_plans/strategic_plan_*.json` | Sequence of component generation |
| RAG Strategy | `strategic_plans/strategic_plan_*.json` | Search queries for each component |
| Component Specs | `component_metadata/iflow_components_*.json` | Detailed SAP-compliant specifications |
| Final Package | `generated_packages/N_Complete_*.zip` | Deployable iFlow ZIP |
| Console Logs | Terminal output | Real-time progress and errors |

---

## ✅ **Benefits of This Logging System**

1. **Full Traceability**: From markdown → query → intent → components → iFlow
2. **Easy Debugging**: Timestamp correlation across all files
3. **Issue Resolution**: Can identify exactly where things went wrong
4. **Audit Trail**: Complete record of all generation requests
5. **Performance Analysis**: Can measure time between steps
6. **Quality Assurance**: Verify correct component detection and SAP compliance
7. **Reproducibility**: Can replay issues with saved queries

---

## 🚀 **Enhancement Added**

The system now saves **query logs** (`query_logs/`) that capture:
- Original markdown from IMigrate
- Constructed natural language query
- Request metadata (job_id, iflow_name, timestamps)

This closes the traceability gap and provides complete end-to-end logging! ✅

