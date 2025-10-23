# RAG Similarity Search Integration

**RAG-based semantic search** for finding similar SAP Integration Suite iFlows using vector embeddings and cosine similarity.

---

## 📚 Files Added

```
agentic-rag-IMigrate/
├── unified_semantic_search.py          # Core RAG search system
├── rag_similarity_search.py            # Integration wrapper for agent
└── RAG_SIMILARITY_SEARCH_INTEGRATION.md  # This file
```

**No SQL files needed** - Uses your existing `integration_flows` table and `search_similar_flows()` function!

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install beautifulsoup4
```

### 2. Verify Supabase Table

✅ **No setup needed!** Your existing `integration_flows` table and `search_similar_flows()` function are already configured.

**Existing table structure:**
```sql
integration_flows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Existing function:** `search_similar_flows(query_embedding, match_threshold, match_count)`

### 3. Test the Integration

```bash
cd agentic-rag-IMigrate
python rag_similarity_search.py
```

---

## 📖 Usage

### Option 1: Standalone Search

```python
from rag_similarity_search import search_similar_iflows

# Search for similar iFlows
results = search_similar_iflows(
    documentation="Integration flow that polls SFTP and posts to OData",
    top_k=10
)

for result in results:
    print(f"{result['name']}: {result['similarity_score']*100:.1f}%")
```

### Option 2: In Agent Integration

```python
from rag_similarity_search import RAGSimilaritySearch

# Initialize
rag_search = RAGSimilaritySearch()
rag_search.initialize()

# Process documentation and get similar flows
result = rag_search.process_documentation(documentation_text)

# Get formatted context for LLM
context = rag_search.format_results_for_agent(result['similar_flows'])

# Use context in agent prompt
agent_prompt = f"""
Generate iFlow based on this documentation.

{context}

User Requirements:
{documentation_text}
"""
```

### Option 3: Upload & Search

```python
from unified_semantic_search import UnifiedSemanticSearch

# Initialize
search = UnifiedSemanticSearch()
search.initialize_clients()

# Upload document and get similar flows
result = search.upload_document("documentation.md")

print(f"Found {len(result['similar_flows'])} similar iFlows:")
for flow in result['similar_flows']:
    print(f"  {flow['rank']}. {flow['name']} ({flow['similarity_score']*100:.1f}%)")
```

---

## 🔧 Integration with Agent

### Step 1: Import in agent.py

```python
from rag_similarity_search import get_rag_search

class SAPiFlowAgent:
    def __init__(self):
        # ... existing code ...
        self.rag_search = get_rag_search()
```

### Step 2: Use in Intent Understanding

```python
def _understand_user_intent(self, user_query: str):
    # ... existing intent logic ...
    
    # Search for similar iFlows
    try:
        similar_iflows = self.rag_search.search_similar_flows(user_query, top_k=5)
        
        if similar_iflows:
            print(f"📚 Found {len(similar_iflows)} similar iFlows for reference")
            
            # Add to LLM context
            context = self.rag_search.format_results_for_agent(similar_iflows)
            
            # Include in prompt
            enhanced_prompt = f"""
            {original_prompt}
            
            **Similar Integration Flows in Knowledge Base:**
            {context}
            
            Use these similar flows as reference when appropriate.
            """
    except Exception as e:
        print(f"⚠️  RAG search failed: {e}")
        # Continue without RAG results
```

### Step 3: Use in Strategic Planning

```python
def _create_strategic_plan(self, intent_analysis: Dict):
    # ... existing planning logic ...
    
    # Get similar iFlow patterns
    documentation = self._format_documentation(intent_analysis)
    rag_result = self.rag_search.process_documentation(documentation)
    
    if rag_result['status'] == 'success':
        match_report = rag_result['match_report']
        
        print(f"📊 RAG Match Report:")
        print(f"   High Quality: {match_report['high_quality_matches']}")
        print(f"   Medium Quality: {match_report['medium_quality_matches']}")
        
        # Use best match as reference
        if match_report['best_match']:
            best = match_report['best_match']
            print(f"   Best Match: {best['name']} ({best['similarity_score']*100:.1f}%)")
```

---

## 📊 How It Works

### 1. **Documentation Processing**
```
User Documentation
    ↓
Extract Overview (250 words)
    ↓
Generate OpenAI Embedding (1536 dimensions)
```

### 2. **Vector Search (Uses Your Existing Table)**
```
Query Embedding
    ↓
Supabase RPC: search_similar_flows()
    ↓
Searches: integration_flows table
  - Column: embedding (vector 1536)
    ↓
Cosine Similarity Search
    ↓
Return Top 10 Matches (sorted by similarity)
```

### 3. **Result Ranking**
```
Similarity Score > 0.8  → High Quality
Similarity Score 0.6-0.8 → Medium Quality
Similarity Score < 0.6   → Low Quality
```

---

## 🎯 Benefits

✅ **No Setup Required** - Uses your existing `integration_flows` table and `search_similar_flows()` function
✅ **No GitHub Dependency** - Uses your own Supabase data  
✅ **Semantic Search** - Finds similar patterns, not just keywords  
✅ **Fast** - Vector indexing already exists (ivfflat)  
✅ **Scalable** - Works with thousands of iFlows  
✅ **Quality Scores** - Ranked by relevance  
✅ **Reusable** - Works for documents and metadata  

---

## 📋 Existing Table Structure (Already Configured!)

Your existing `integration_flows` table:

```sql
CREATE TABLE integration_flows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    embedding VECTOR(1536),          ✅ OpenAI embeddings already stored!
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Existing function (already available)
CREATE FUNCTION search_similar_flows(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 10
) RETURNS TABLE (
    id TEXT,
    name TEXT,
    description TEXT,
    similarity FLOAT
);
```

**The RAG search simply calls your existing `search_similar_flows()` function!**

---

## 📈 Example Output

```
🔍 RAG Search: 'Integration flow that polls SFTP and posts to OData'
✅ Found 5 similar iFlows

📚 **Similar Integration Flows Found:**

**1. Employee Data Sync** (Similarity: 92.3%)
   Quality: High
   Description: Polls SFTP directory for employee CSV files, transforms data using GroovyScript, and posts to SAP SuccessFactors OData API...

**2. Invoice Processing** (Similarity: 87.5%)
   Quality: High
   Description: SFTP polling integration that reads invoice XML files, validates against schema, and sends to SAP OData service...

**3. Product Master Upload** (Similarity: 81.2%)
   Quality: High
   Description: Scheduled SFTP integration that fetches product master data and synchronizes with SAP...

**4. Customer Data Sync** (Similarity: 76.8%)
   Quality: Medium
   Description: Integration flow for syncing customer data from external SFTP source...

**5. Order Processing** (Similarity: 68.4%)
   Quality: Medium
   Description: Processes orders from SFTP and updates SAP system...
```

---

## 🧪 Testing

### Test 1: Basic Search
```bash
python rag_similarity_search.py
```

### Test 2: Document Upload
```python
from unified_semantic_search import UnifiedSemanticSearch

search = UnifiedSemanticSearch()
search.initialize_clients()

# Test with sample documentation
result = search.upload_document("path/to/boomi_documentation.md")
print(f"Found {len(result['similar_flows'])} similar flows")
```

### Test 3: Agent Integration
```python
from rag_similarity_search import get_rag_search

rag = get_rag_search()
results = rag.search_similar_flows("Poll SFTP every 5 minutes")

assert len(results) > 0, "Should find similar flows"
assert results[0]['similarity_score'] > 0.5, "Top result should be relevant"
```

---

## 🐛 Troubleshooting

### Error: "No module named 'beautifulsoup4'"
**Fix:** `pip install beautifulsoup4`

### Error: "RAG system not available"
**Fix:** Ensure `unified_semantic_search.py` is in the same directory as `rag_similarity_search.py`

### No Results Found
**Fix:** Verify your `integration_flows` table has data with embeddings:
```sql
SELECT COUNT(*) FROM integration_flows WHERE embedding IS NOT NULL;
```

---

## 📝 Notes

- **Embedding Model:** `text-embedding-ada-002` (1536 dimensions)
- **Similarity Threshold:** 0.3 (30% minimum similarity)
- **Search Limit:** 10 results by default
- **Memory Storage:** Documents stored in memory, not persisted to Supabase

---

**Integration Complete!** 🎉

Your agent can now discover similar iFlows using RAG-based semantic search instead of GitHub search.

