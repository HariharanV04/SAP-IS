## SAP iFlow Retrieval Playbook (LangChain, KG + RAG, No Ingestion)

Purpose: Orchestrate retrieval-only flows that combine Knowledge Graph (Neo4j) skeletons with RAG (vector DB) artifacts to produce (a) Overview or (b) Equivalent iFlow with complete XML and an optional packaged zip. No ingestion scope.

---

## 🏗️ **System Architecture & Functioning**

### **Overall System Design**
This is a sophisticated **RAG (Retrieval-Augmented Generation) system** that combines multiple data sources and AI capabilities to analyze SAP Integration Flows. The system follows a **hybrid approach** with both hardcoded elements and dynamic RAG agent functionality.

### **Core Components:**
1. **Knowledge Graph (Neo4j)** - Stores structured iFlow topology and relationships
2. **Vector Database (Supabase)** - Stores embeddings and semantic search capabilities  
3. **RAG Agent (GPT-4)** - Orchestrates queries and synthesizes responses
4. **Multiple Tools** - Specialized functions for different query types

### **Data Sources Integration:**

#### **Neo4j Knowledge Graph (2,780 nodes, 11,439 relationships)**
- **Process nodes**: iFlow packages/processes
- **Component nodes**: BPMN elements (events, tasks, gateways)
- **Relationships**: FLOWS_TO, CONNECTS_TO, INVOKES, RECEIVES_FROM
- **Purpose**: Structural analysis, topology understanding

#### **Supabase Vector Database (211 documents)**
- **iflow_assets** (15 items): Groovy scripts, configurations, XML files
- **iflow_components** (102 items): BPMN activities, service tasks, connectors  
- **iflow_flows** (93 items): Sequence flows, message flows, process flows
- **iflow_packages** (1 item): Complete integration flow definitions
- **Purpose**: Semantic search, code retrieval, documentation

### **AI Models Configuration:**

#### **CodeBERT** (for Vector Search)
- **Purpose**: Query encoding for semantic search in the vector database
- **Model**: `microsoft/codebert-base`
- **Function**: Converts user queries into embeddings to search the Supabase vector database
- **Status**: ✅ **Active** - `use_codebert: bool = True` by default

#### **OpenAI GPT-4** (for LLM Responses)
- **Purpose**: Agent reasoning, response generation, and synthesis
- **Model**: `gpt-4`
- **Function**: Combines Knowledge Graph + Vector search results into comprehensive responses
- **Status**: ✅ **Active** - Hardcoded in the agent configuration

### **Query Processing Flow:**
```
User Query → CodeBERT (query encoding) → Vector Search → Neo4j KG Search → GPT-4 (synthesis) → Response
```

1. **CodeBERT** encodes your natural language query into embeddings
2. **Vector Search** finds semantically similar content in Supabase
3. **Neo4j** provides structural/relationship data
4. **GPT-4** synthesizes everything into a comprehensive response

### **Hardcoded vs Dynamic Elements:**

#### **HARDCODED Elements:**
- **Database Credentials**: Supabase URL, Neo4j URI, OpenAI API key (in config.py)
- **Database Schema Structure**: Table names, node types, relationship types
- **Tool Definitions and Execution Order**: Strict sequence (KG → Vector → LLM)
- **Component Types and Patterns**: 20+ predefined SAP iFlow component types
- **Embedding Models**: CodeBERT configuration

#### **DYNAMIC/RAG Elements:**
- **Query Processing**: Semantic search using CodeBERT embeddings
- **Topology Analysis**: Dynamically queries Neo4j for component relationships
- **Multi-Strategy Search**: 8 different search strategies adaptively applied
- **Context-Aware Responses**: LLM synthesizes findings based on query context
- **Code Display**: Automatically formats and displays full code content when requested
- **Error Handling**: Graceful fallbacks when components fail

### **System Intelligence Level:**
This is a **highly intelligent RAG system** that:
- **Understands context** and routes queries appropriately
- **Combines multiple data sources** for comprehensive answers
- **Maintains conversation context** for follow-up questions
- **Provides structured reasoning** with clear data provenance
- **Adapts search strategies** based on query complexity

The system is **primarily RAG-driven** with hardcoded infrastructure (credentials, schema, execution order) but **dynamic intelligence** for query processing, data retrieval, and response generation.

### **RAG Agent Capabilities:**

#### **Core Tools Available:**
1. **GetIflowSkeletonTool** - Retrieves flow topology from Neo4j
2. **ComponentAnalysisTool** - Analyzes specific components and relationships  
3. **VectorSearchTool** - Performs semantic search across Supabase tables
4. **PatternAnalysisTool** - Identifies integration patterns
5. **IFlowComponentQueryTool** - Queries components by type/package
6. **IFlowPackageAnalysisTool** - Analyzes complete packages

#### **Multi-Strategy Search (8 Strategies):**
1. **Package search** (Process nodes)
2. **Component search** (Component nodes) 
3. **Component type filtering**
4. **Component relationship analysis**
5. **Sequence flow analysis**
6. **Integration pattern detection**
7. **Technology search**
8. **General relationship queries**

#### **Key Capabilities:**
- **Semantic Code Search**: Find relevant scripts/configs using natural language
- **Topology Analysis**: Understand flow structure and component relationships
- **Pattern Recognition**: Identify common integration patterns
- **Code Generation**: Create integration scripts and configurations
- **Best Practices**: Provide SAP iFlow development recommendations
- **Multi-Modal Analysis**: Combines structured (KG) + unstructured (Vector) data

#### **Strict Execution Order:**
```
MANDATORY EXECUTION SEQUENCE (NEVER DEVIATE):
1. ALWAYS START WITH KNOWLEDGE GRAPH: Query Neo4j first for topology, components, relationships
2. THEN USE VECTOR DATABASE: Based on KG findings, search for relevant documentation/configs
3. FINALLY SYNTHESIZE: Combine KG + Vector data with LLM reasoning
```

#### **Response Format:**
1) **KG Findings**: "From Neo4j: Found X components/flows with relationships [specific data]"
2) **Vector Findings**: "From Vector DB: Retrieved Y documents based on KG findings [doc names, content]"
3) **Combined Analysis**: "Synthesis of KG topology + Vector documentation: [detailed explanation]"

---

### Drop‑in System Prompt (use as system message)
```
SYSTEM: SAP iFlow Retrieval Orchestrator (KG + RAG)

You MUST answer by combining:
- Knowledge Graph (Neo4j): component topology and relationships (skeleton/blueprint)
- RAG (vector DB): real artifacts (configs and complete XML)

TOOLS (function-calling):
- get_iflow_skeleton(iflow_name) → {nodes:[{id,name,type}], edges:[{from,to,relation}]}
- component_analysis(component_name) → {component, incoming, outgoing, patterns}
- vector_search(query, limit=5, chunk_types=["summary","config","complete_xml"]) → [{document_name, chunk_type, content, confidence, path}]

SELECTION:
- For overview: get_iflow_skeleton first; vector_search with chunk_types=["summary","config"] for evidence.
- For “equivalent iFlow” / “complete XML”: get_iflow_skeleton, then vector_search with chunk_types=["complete_xml"] only (strict), map per KG topology.
- If specific component mentioned: component_analysis(component_name); then focused vector_search by name.

OUTPUT (STRICT):
1) Summary (2–4 bullets)
2) Component Graph: nodes + edges (→ outgoing, ← incoming)
3) Findings
   - KG Evidence: bullets with [KG:label:name] or [KG:id]
   - RAG Evidence: bullets with [DOC:document_name]
4) Complete XML (ONLY if requested)
   ```xml
   ...XML...
   ```
5) Coverage
   - Nodes in skeleton: N
   - Resolved with artifacts: M
   - Missing/low-confidence: list
6) Recommendations (clear next steps)
7) Sources
   - [KG:...]
   - [DOC:...]
8) Confidence: High/Medium/Low (+ why)

RULES:
- Do not invent nodes/edges/XML. If missing, state it and propose top-2 alternatives (with citations).
- Preserve exact component names. Prefer exact XML from RAG.
- Reconcile conflicts explicitly; lower confidence if unresolved.

EXECUTION:
- Parse intent (overview vs equivalent/XML).
- Call KG first for skeleton; call RAG next for artifacts; parallelize when safe.
- Stitch per KG topology; generate coverage; then output with citations.

FALLBACK (Template Synthesis):
- If KG returns no skeleton, synthesize a skeleton using KG-known integration patterns (Request-Reply, Event-Driven, File-Based) and adapter knowledge. Retrieve RAG templates to instantiate real XML. Mark generic placeholders and list gaps.
```

Optional user prompt template:
```
USER:
Context:
- iFlow: {iflow_name}
- Mode: {mode}  # overview | equivalent
- Task: {user_query}

Constraints:
- XML only? {xml_only}
- Top K: {top_k}

Please follow the system policy, query both KG and RAG as needed, and return the formatted answer with citations, coverage, and confidence.
```

---

## LangChain Orchestration (Retrieval Only)

### Components
- LLM: `ChatOpenAI` (or equivalent)
- Tools (LangChain Tools):
  - `GetIflowSkeletonTool` (Neo4j KG via driver)
  - `ComponentAnalysisTool` (Neo4j KG)
  - `VectorSearchTool` (Postgres/pgvector or your vector DB client)
- Stitcher: Python function to map nodes→artifacts, topologically order, compute coverage
- Packager (optional for equivalent mode): Python CLI `packager.py`

### Tool Contracts (Python)
```python
from typing import Optional, List, Dict, Any
from langchain.tools import BaseTool

class GetIflowSkeletonTool(BaseTool):
    name = "get_iflow_skeleton"
    description = "Return iFlow skeleton topology from Neo4j by name."

    def __init__(self, kg_service):
        super().__init__()
        self.kg = kg_service  # must expose .get_iflow_skeleton(iflow_name)

    def _run(self, iflow_name: str) -> Dict[str, Any]:
        return self.kg.get_iflow_skeleton(iflow_name)

    async def _arun(self, iflow_name: str) -> Dict[str, Any]:
        return await self.kg.get_iflow_skeleton_async(iflow_name)


class ComponentAnalysisTool(BaseTool):
    name = "component_analysis"
    description = "Analyze a component: incoming/outgoing edges, patterns."

    def __init__(self, kg_service):
        super().__init__()
        self.kg = kg_service  # must expose .component_analysis(name)

    def _run(self, component_name: str) -> Dict[str, Any]:
        return self.kg.component_analysis(component_name)

    async def _arun(self, component_name: str) -> Dict[str, Any]:
        return await self.kg.component_analysis_async(component_name)


class VectorSearchTool(BaseTool):
    name = "vector_search"
    description = "Semantic retrieval of iFlow artifacts including complete XML."

    def __init__(self, vector_store):
        super().__init__()
        self.vs = vector_store  # must expose .search_similar(query, limit, chunk_types)

    def _run(self, query: str, limit: int = 5, chunk_types: Optional[List[str]] = None):
        return self.vs.search_similar(query=query, limit=limit, chunk_types=chunk_types)

    async def _arun(self, query: str, limit: int = 5, chunk_types: Optional[List[str]] = None):
        return await self.vs.search_similar(query=query, limit=limit, chunk_types=chunk_types)
```

### Agent Setup (LangChain Tools agent)
```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def build_agent(kg_service, vector_store, system_prompt: str) -> AgentExecutor:
    llm = ChatOpenAI(model="gpt-4", temperature=0.1)
    tools = [
        GetIflowSkeletonTool(kg_service),
        ComponentAnalysisTool(kg_service),
        VectorSearchTool(vector_store),
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)
```

### Parallel Retrieval Pattern (optional)
For manual parallelization outside the tools agent (e.g., to prefetch KG & RAG results), use asyncio and then feed results into a Stitcher before the agent formats output.
```python
async def retrieve_parallel(kg_service, vector_store, iflow_name, query, chunk_types, top_k):
    import asyncio
    kg_task = asyncio.create_task(kg_service.get_iflow_skeleton_async(iflow_name))
    rag_task = asyncio.create_task(vector_store.search_similar(query=query, limit=top_k, chunk_types=chunk_types))
    skeleton, artifacts = await asyncio.gather(kg_task, rag_task)
    return skeleton, artifacts
```

### Stitcher (mapping, topology, coverage)
```python
from typing import Tuple

def topological_order(nodes, edges) -> List[Dict[str, Any]]:
    # Simple Kahn's algorithm over ids; assumes edges use ids
    from collections import defaultdict, deque
    id_to_node = {n["id"]: n for n in nodes}
    indeg = defaultdict(int)
    graph = defaultdict(list)
    for e in edges or []:
        if e.get("from") and e.get("to"):
            graph[e["from"]].append(e["to"])
            indeg[e["to"]] += 1
            id_to_node.setdefault(e["from"], {"id": e["from"], "name": e["from"]})
            id_to_node.setdefault(e["to"], {"id": e["to"], "name": e["to"]})
    q = deque([nid for nid in id_to_node if indeg[nid] == 0])
    ordered = []
    while q:
        u = q.popleft()
        ordered.append(id_to_node[u])
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    # fallback: return nodes if graph empty
    return ordered if ordered else nodes

def map_nodes_to_artifacts(nodes, artifacts, confidence_threshold=0.65):
    resolved, missing = [], []
    for n in nodes:
        name = (n.get("name") or "").lower()
        exact = [a for a in artifacts if (a.get("name") or "").lower() == name]
        chosen = None
        if exact:
            chosen = max(exact, key=lambda a: a.get("confidence", 0))
        else:
            # fuzzy: token overlap
            def score(a):
                an = (a.get("name") or a.get("document_name") or "").lower()
                return len(set(name.split()) & set(an.split()))
            if artifacts:
                chosen = max(artifacts, key=score)
        if chosen and chosen.get("confidence", 0) >= confidence_threshold:
            resolved.append({"node": n, "artifact": chosen})
        else:
            missing.append({"node": n, "candidates": (exact[:2] if exact else [])})
    return resolved, missing

def stitch(iflow_name: str, skeleton: Dict[str, Any], artifacts: List[Dict[str, Any]], confidence_threshold=0.65) -> Dict[str, Any]:
    nodes = skeleton.get("nodes", []) if skeleton else []
    edges = skeleton.get("edges", []) if skeleton else []
    ordered_nodes = topological_order(nodes, edges)
    resolved, missing = map_nodes_to_artifacts(ordered_nodes, artifacts, confidence_threshold)
    coverage = {
        "nodes_total": len(nodes),
        "nodes_resolved": len(resolved),
        "missing_or_low_confidence": [m["node"]["name"] for m in missing],
    }
    return {
        "iflow_name": iflow_name,
        "ordered_nodes": ordered_nodes,
        "edges": edges,
        "resolved": resolved,
        "missing": missing,
        "coverage": coverage,
    }
```

### Mode Handling
- overview: allow `chunk_types=["summary","config"]`; return markdown only.
- equivalent: enforce `chunk_types=["complete_xml"]`; build manifest for packager; return markdown + zip.

### Packager (post‑RAG, optional)
CLI:
```powershell
python packager.py `
  --skeleton skeleton.json `
  --artifacts artifacts.json `
  --files-dir ./files `
  --out build/iflow_bundle.zip `
  --iflow-name "MyIFlow" `
  --version "0.1.0" `
  --author "Team"
```

Responsibilities:
- Create `build/{iflow_name}/components/*.xml`, `manifest.json`, `README.md` (topology, coverage, sources); zip to `iflow_bundle.zip`.

---

## Orchestration Patterns (LangChain)

### A) Tools Agent Only
Let the agent decide which tools to call based on the system prompt. Good for quick start.

### B) Hybrid: Manual Retrieval + Tools Agent Formatting
1) Async gather: call KG + RAG in parallel using your own clients.
2) Run `stitch()`.
3) Provide the stitched context as additional input to a tools agent that formats the final markdown per system prompt.

---

## Minimal End‑to‑End Example (pseudo)
```python
async def answer_query(iflow_name: str, user_query: str, mode: str, top_k: int = 5, xml_only: bool = False):
    chunk_types = ["complete_xml"] if (mode == "equivalent" or xml_only) else ["summary","config","complete_xml"]
    skeleton, artifacts = await retrieve_parallel(kg_service, vector_store, iflow_name, user_query or iflow_name, chunk_types, top_k)
    stitched = stitch(iflow_name, skeleton or {"nodes": [], "edges": []}, artifacts or [])

    if mode == "equivalent":
        # write skeleton.json, artifacts.json, files/ from artifacts
        # call packager.py (subprocess) and attach resulting zip
        pass

    agent = build_agent(kg_service, vector_store, system_prompt)
    result = await agent.ainvoke({"input": user_query or f"Provide an {mode} of {iflow_name}."})
    return {
        "agent_output": result["output"],
        "coverage": stitched["coverage"],
        "resolved": stitched["resolved"],
        "missing": stitched["missing"],
    }
```

---

## Config & Thresholds
- `CONFIDENCE_THRESHOLD = 0.65`
- `RAG_CHUNK_TYPES_DEFAULT = ["summary","config","complete_xml"]`
- Enforce `chunk_types=["complete_xml"]` for “equivalent” or `xml_only=true`
- Environment: `NEO4J_*`, vector DB connection, `OPENAI_API_KEY`

---

## Test Scenarios
- Overview mode → returns stitched markdown with citations + coverage
- Equivalent mode → returns stitched markdown + zip (via packager)
- No KG skeleton → pattern synthesis + RAG templates → stitched output with gaps noted
- Ambiguous names → present top candidates, reduce confidence to Medium

---

## Appendix: Sample Cypher (adjust to your schema)
```cypher
// Get iFlow skeleton by name
MATCH (i:IFlow {name:$iflow_name})-[:HAS_COMPONENT]->(c:Component)
OPTIONAL MATCH (c)-[r:FLOWS_TO]->(d:Component)
RETURN collect(DISTINCT {id:id(c), name:c.name, type:head(labels(c))}) AS nodes,
       collect(DISTINCT {from:id(c), to:id(d), relation:type(r)}) AS edges;

// Bridge two systems with shortest component path
MATCH (a:System {name:$source})-[:EMITS|:USES*1..2]->(c1:Component)
MATCH (b:System {name:$target})<-[:CONSUMES|:USES*1..2]-(c2:Component)
MATCH p = shortestPath((c1)-[:FLOWS_TO*..12]->(c2))
RETURN nodes(p) AS nodes, relationships(p) AS edges LIMIT 3;
```


