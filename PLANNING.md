# IMigrate + RAG Integration - Planning Document

## 📋 Project Overview

**Project Name**: IMigrate with Agentic RAG Integration
**Version**: 2.0
**Last Updated**: 2025-01-17

**Purpose**: Integrate IMigrate's frontend/backend with RAG system's intelligent iFlow generation, replacing template-based generation with AI-powered dynamic generation.

---

## 🎯 Goals

1. **Keep IMigrate UI/UX intact** - Zero changes to frontend workflows
2. **Replace template-based iFlow generation** - Use RAG's intelligent generation
3. **Maintain backward compatibility** - Fallback to templates if RAG fails
4. **Loose coupling** - Independent services communicating via REST API
5. **Easy rollback** - Toggle RAG on/off via environment variable

---

## 🏗️ Architecture

### **System Overview**

```
IMigrate Frontend (React) → Port 3000
    ↓
IMigrate Main API (Flask) → Port 5000
    ↓
BoomiToIS-API (Flask) → Port 5003
MuleToIS-API (Flask) → Port 5001
    ↓ HTTP POST (markdown)
RAG API Service (Flask) → Port 5010 ← NEW SERVICE
    ↓
Agentic RAG Agent (SAPiFlowAgent)
    ├─→ Neo4j Knowledge Graph
    ├─→ Supabase Vector Database
    └─→ IFlowPackager
```

### **Integration Point**

**Location**: `BoomiToIS-API/app.py` and `MuleToIS-API/app.py`
**Function**: `process_iflow_generation()` at line ~347
**What changes**: Replace `generate_iflow_from_markdown()` call with RAG API call

---

## 📂 File Structure

```
IMigrate/
├── agentic-rag-IMigrate/              # RAG System (KEEP AS-IS)
│   ├── agent/
│   │   └── agent.py                    # Core RAG agent (345 KB)
│   ├── rag/
│   │   └── supabase_vector_store.py
│   ├── knowledge_graph/
│   │   ├── graph_store.py              # Neo4j integration
│   │   └── schema_mapping.py
│   ├── iflow_packaging_system_clean.py # IFlowPackager (76 KB)
│   ├── config.py                       # RAG configuration
│   └── run_agent.py                    # CLI entry point
│
├── rag_api_service.py                 # NEW - RAG API wrapper
│
├── app/                               # Main API (Port 5000)
│   ├── app.py
│   └── .env                           # ADD: RAG config
│
├── BoomiToIS-API/                     # Boomi API (Port 5003)
│   ├── app.py                         # MODIFY: Add RAG integration
│   └── .env                           # ADD: RAG config
│
├── MuleToIS-API/                      # MuleSoft API (Port 5001)
│   ├── app.py                         # MODIFY: Add RAG integration
│   └── .env                           # ADD: RAG config
│
├── IFA-Project/frontend/              # React Frontend (UNCHANGED)
│
├── tests/                             # NEW - Unit tests
│   ├── test_rag_api_service.py
│   ├── test_boomi_integration.py
│   └── test_mule_integration.py
│
├── PLANNING.md                        # This file
└── TASK.md                            # Task tracking
```

---

## 🔧 Technology Stack

### **Existing (IMigrate)**
- Backend: Flask, Python 3.9+, Gunicorn
- Frontend: React 18, Vite, Tailwind CSS
- Database: Supabase PostgreSQL
- AI: Anthropic Claude, OpenAI

### **New (RAG System)**
- Agent: LangChain, OpenAI GPT-4o-mini
- Knowledge Graph: Neo4j Aura
- Vector DB: Supabase (pgvector)
- Packaging: Custom IFlowPackager

---

## 📝 Code Conventions

### **Python Style**
- Follow PEP8
- Use type hints
- Format with `black`
- Docstrings: Google style
- Max file length: 500 lines

### **Module Organization**
For new agent code:
- `agent.py` - Main agent definition
- `tools.py` - Tool functions
- `prompts.py` - System prompts

### **Testing**
- Use pytest
- Tests in `/tests` folder
- Cover: expected use, edge cases, failure cases
- Update tests when logic changes

### **Environment Variables**
- Use `python_dotenv`
- Load with `load_dotenv()`
- Never commit `.env` files

---

## 🔒 Security Considerations

1. **API Keys**: Store in `.env`, never in code
2. **CORS**: Restrict origins in production
3. **Timeouts**: 5-minute timeout for RAG generation
4. **Fallback**: Always fall back to templates if RAG fails
5. **Logging**: Sanitize logs (no credentials)

---

## 🚀 Deployment Strategy

### **Phase 1: Development** (Week 1)
- Create RAG API Service
- Add integration to BoomiToIS-API
- Add integration to MuleToIS-API
- Local testing

### **Phase 2: Testing** (Week 2)
- Unit tests for RAG API
- Integration tests
- Compare RAG vs Template output
- Performance testing

### **Phase 3: Gradual Rollout** (Week 3)
- Deploy with `USE_RAG_GENERATION=false`
- Enable for test users
- Monitor logs and performance
- Collect feedback

### **Phase 4: Full Deployment** (Week 4)
- Enable for all users (`USE_RAG_GENERATION=true`)
- Monitor production
- Keep template fallback active
- Document final setup

---

## 📊 Success Criteria

1. ✅ IMigrate UI works exactly as before
2. ✅ Document upload and processing unchanged
3. ✅ iFlow generation uses RAG system
4. ✅ Generated iFlows are importable to SAP Integration Suite
5. ✅ Fallback to templates works if RAG fails
6. ✅ Can toggle RAG on/off via config
7. ✅ All IMigrate features remain functional
8. ✅ Performance acceptable (< 5 min for complex flows)

---

## 🔍 Known Constraints

1. **Max file size**: 500 lines per file (refactor if larger)
2. **RAG timeout**: 5 minutes max for generation
3. **Fallback required**: Must always have template fallback
4. **No breaking changes**: IMigrate must work as-is
5. **Loose coupling**: Services communicate via HTTP only

---

## 📚 Key Documentation

- [INTEGRATION_PLAN.md](agentic-rag-IMigrate/integration_docs/INTEGRATION_PLAN.md) - Complete integration guide
- [TECHNICAL_DESIGN.md](Complete_Documentation/TECHNICAL_DESIGN.md) - IMigrate architecture
- [HOW_TO_RUN_GUIDE.md](Complete_Documentation/HOW_TO_RUN_GUIDE.md) - Operational guide
- [TASK.md](TASK.md) - Task tracking

---

## 🧠 AI Behavior Rules

- Never assume missing context - Ask questions if uncertain
- Never hallucinate libraries - Only use known packages
- Always confirm file paths exist
- Never delete existing code unless explicitly instructed
- Follow the task list in TASK.md
- Mark completed tasks immediately

---

## 🎨 Naming Conventions

**Services**:
- `rag_api_service.py` - RAG API wrapper
- `test_rag_api_service.py` - Unit tests

**Functions**:
- `generate_iflow_from_markdown()` - Original template-based
- `call_rag_api()` - New RAG API caller
- `create_sap_iflow_agent()` - RAG agent factory

**Environment Variables**:
- `USE_RAG_GENERATION` - Enable/disable RAG
- `RAG_API_URL` - RAG service URL
- `RAG_API_TIMEOUT` - Request timeout

---

## 📈 Performance Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| RAG API Health Check | < 1s | < 2s |
| iFlow Generation (Simple) | < 30s | < 60s |
| iFlow Generation (Complex) | < 2m | < 5m |
| Fallback Activation | < 1s | < 2s |

---

This planning document ensures consistent development practices across the integration project.
