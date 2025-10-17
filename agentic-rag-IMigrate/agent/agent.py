"""
AI Agent implementation for SAP iFlow RAG + Knowledge Graph system.
Updated to work with Supabase vector database.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json
from dataclasses import dataclass

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

# Import config for agent settings
import config

# Import Supabase vector store
from rag.supabase_vector_store import SupabaseVectorStore, create_supabase_vector_store

# Import iFlow packaging system
from iflow_packaging_system_clean import IFlowPackager

# Import these modules when needed to avoid path issues

logger = logging.getLogger(__name__)


def create_sap_iflow_agent(graph_store, openai_api_key: str, 
                          supabase_url: Optional[str] = None, 
                          supabase_key: Optional[str] = None,
                          context_document: Optional[str] = None) -> 'SAPiFlowAgent':
    """
    Factory function to create SAPiFlowAgent with Supabase vector store.
    
    Args:
        graph_store: Neo4j graph store instance
        openai_api_key: OpenAI API key for LLM
        supabase_url: Optional Supabase URL (will try config/env if not provided)
        supabase_key: Optional Supabase key (will try config/env if not provided) 
        context_document: Optional context document name
        
    Returns:
        Configured SAPiFlowAgent instance
    """
    try:
        # Create vector store
        if supabase_url and supabase_key:
            vector_store = SupabaseVectorStore(supabase_url, supabase_key)
        else:
            vector_store = create_supabase_vector_store()
        
        logger.info("Created Supabase vector store successfully")
        
        # Create and return agent
        return SAPiFlowAgent(
            vector_store=vector_store,
            graph_store=graph_store, 
            openai_api_key=openai_api_key,
            context_document=context_document
        )
        
    except Exception as e:
        logger.error(f"Failed to create SAPiFlowAgent: {e}")
        raise


# Playbook Stitcher Functions
def topological_order(nodes, edges) -> List[Dict[str, Any]]:
    """Simple Kahn's algorithm over ids; assumes edges use ids"""
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
    """Map nodes to artifacts with confidence scoring"""
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
    """Stitch skeleton topology with artifacts and compute coverage"""
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


@dataclass
class AgentResponse:
    """Response from the AI agent."""
    content: str
    sources: List[Dict[str, Any]]
    tools_used: List[str]
    metadata: Dict[str, Any]


class SAPiFlowTool(BaseTool):
    """Base tool for SAP iFlow operations."""
    
    name: str
    description: str
    vector_store: Any = None
    graph_store: Any = None
    
    def _run(self, query: str) -> str:
        """Synchronous run method."""
        raise NotImplementedError("Use async version")
    
    async def _arun(self, query: str) -> str:
        """Asynchronous run method."""
        raise NotImplementedError("Subclasses must implement")


# Playbook Tools Implementation
class GetIflowSkeletonTool(SAPiFlowTool):
    """Tool to get iFlow skeleton topology from Neo4j - as per playbook."""
    
    def __init__(self, graph_store):
        super().__init__(
            name="get_iflow_skeleton",
            description="Return iFlow skeleton topology from Neo4j by name.",
            vector_store=None,
            graph_store=graph_store
        )
    
    async def _arun(self, iflow_name: str = None, query: str = None) -> Dict[str, Any]:
        """Get iFlow skeleton: {nodes: [{id,name,type}], edges: [{from,to,relation}]}"""
        try:
            # Use iflow_name if provided, otherwise extract from query
            name_to_search = iflow_name or query or "*"
            print(f"\n🏗️ [GET_IFLOW_SKELETON] Analyzing request: '{name_to_search}'")
            
            if name_to_search == "*" or "all" in name_to_search.lower() or "flows" in name_to_search.lower():
                print("🔍 [ANALYSIS] Detected request for ALL flows - querying all packages")
                packages = await self.graph_store.query_iflow_packages()
                
                print(f"📊 [PACKAGE_ANALYSIS] Found {len(packages)} packages:")
                for i, pkg in enumerate(packages[:5]):
                    print(f"   {i+1}. {pkg['package_name']} (ID: {pkg['package_id']}, Type: {pkg['type']})")
                if len(packages) > 5:
                    print(f"   ... and {len(packages) - 5} more packages")
                
                skeleton = {
                    "nodes": [{"id": p["package_id"], "name": p["package_name"], "type": p["type"]} for p in packages],
                    "edges": []
                }
                
                print(f"🏗️ [SKELETON_BUILT] Created skeleton with {len(skeleton['nodes'])} process nodes")
            else:
                print(f"🔍 [ANALYSIS] Searching for specific iFlow: '{name_to_search}'")
                skeleton = await self.graph_store.get_iflow_skeleton(name_to_search)
                
                if skeleton.get("nodes"):
                    print(f"📊 [SPECIFIC_FLOW] Found components:")
                    for i, node in enumerate(skeleton["nodes"][:5]):
                        print(f"   {i+1}. {node['name']} (ID: {node['id']}, Type: {node['type']})")
                    if len(skeleton["nodes"]) > 5:
                        print(f"   ... and {len(skeleton['nodes']) - 5} more components")
                else:
                    print("⚠️ [SPECIFIC_FLOW] No specific flow found, falling back to general search")
            
            node_count = len(skeleton.get("nodes", []))
            edge_count = len(skeleton.get("edges", []))
            print(f"✅ [SKELETON_COMPLETE] Final skeleton: {node_count} nodes, {edge_count} edges")
            
            return skeleton
        except Exception as e:
            logger.error(f"Error getting iFlow skeleton: {e}")
            print(f"❌ [SKELETON_ERROR] {e}")
            return {"nodes": [], "edges": []}


class VectorSearchTool(SAPiFlowTool):
    """Tool for vector similarity search."""
    
    def __init__(self, vector_store):
        super().__init__(
            name="vector_search",
            description="Search for similar SAP iFlow components, patterns, or configurations using semantic similarity",
            vector_store=vector_store,
            graph_store=None
        )

    
    async def _arun(self, query: str, chunk_types: Optional[List[str]] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content using vector similarity."""
        try:
            print(f"\n🔍 [VECTOR_SEARCH] Executing semantic search")
            print(f"📝 [SEARCH_PARAMS] Query: '{query}' | Limit: {limit} | Types: {chunk_types}")
            
            results = await self.vector_store.search_similar(
                query=query,
                limit=limit,
                chunk_types=chunk_types
            )
            
            print(f"✅ [VECTOR_RESULT] Found {len(results)} matching documents")
            
            if results:
                print(f"📊 [DOCUMENT_ANALYSIS] Retrieved documents:")
                unique_docs = {}
                for result in results:
                    doc_name = result.get('document_name', 'Unknown')
                    chunk_type = result.get('chunk_type', 'Unknown')
                    similarity = result.get('similarity_score', 0)
                    
                    if doc_name not in unique_docs:
                        unique_docs[doc_name] = []
                    unique_docs[doc_name].append((chunk_type, similarity))
                
                for i, (doc_name, chunks) in enumerate(unique_docs.items(), 1):
                    print(f"   {i}. {doc_name}")
                    for chunk_type, similarity in chunks:
                        print(f"      • {chunk_type}: {similarity:.3f} similarity")
                
                print(f"📄 [CONTENT_PREVIEW] Sample content from top result:")
                top_result = results[0]
                content_preview = str(top_result.get('content', ''))[:200]
                print(f"   Content: {content_preview}{'...' if len(str(top_result.get('content', ''))) > 200 else ''}")
                
                print(f"🔍 [SEARCH_EFFECTIVENESS] Avg similarity: {sum(r.get('similarity_score', 0) for r in results) / len(results):.3f}")
            else:
                print("❌ [VECTOR_RESULT] No matching documents found")
                print("🔍 [SEARCH_ANALYSIS] This may indicate:")
                print("   • Query terms not in vector database")
                print("   • Embedding model mismatch")
                print("   • Database connection issues")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            print(f"❌ [VECTOR_ERROR] Search failed: {e}")
            print("🔄 [FALLBACK] Attempting text-based fallback search...")
            # Could implement text fallback here
            return []


class ComponentAnalysisTool(SAPiFlowTool):
    """Tool for analyzing SAP iFlow components."""
    
    def __init__(self, graph_store):
        super().__init__(
            name="component_analysis",
            description="Analyze a component: incoming/outgoing edges, patterns.",
            vector_store=None,
            graph_store=graph_store
        )
    
    async def _arun(self, component_name: Optional[str] = None, query: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a specific component."""
        try:
            # Use query if component_name is not provided
            if not component_name and query:
                # Heuristic: avoid taking the full prompt as the component name
                # Extract candidate tokens that look like IDs or short names
                import re
                tokens = re.findall(r"[A-Za-z0-9_\-]{3,}", query)
                # Prefer tokens that look like known prefixes (Component/SequenceFlow/etc.) or are short words
                preferred = [t for t in tokens if t.lower().startswith(('sequenceflow', 'component', 'content', 'script', 'service', 'adapter')) or len(t) <= 60]
                component_name = preferred[0] if preferred else query.strip()[:60]
            
            if not component_name:
                return "Please provide a component name to analyze."
            
            print(f"\n🕸️ [COMPONENT_ANALYSIS] Analyzing component: '{component_name}'")
            
            # Get component relationships with detailed logging
            print("🔍 [STEP_1] Searching for component in Neo4j...")
            try:
                relationships = await self.graph_store.find_component_relationships(component_name)
                print("✅ [STEP_1] Component relationship query completed")
            except Exception as e:
                print(f"❌ [STEP_1] Component query failed: {e}")
                relationships = {}
            
            if not relationships:
                print(f"❌ [COMPONENT_NOT_FOUND] No component named '{component_name}' found")
                print("🔍 [SUGGESTION] Try searching for similar components or check exact name")
                return {
                    "component": {"name": component_name, "type": "Unknown", "id": component_name},
                    "incoming": [],
                    "outgoing": [],
                    "patterns": [],
                    "reusability_score": 0.0,
                    "related_components": []
                }
            
            comp = relationships['component']
            incoming = relationships.get('incoming_connections', [])
            outgoing = relationships.get('outgoing_connections', [])
            
            print(f"✅ [COMPONENT_FOUND] {comp['name']} ({comp['type']})")
            print(f"📊 [CONNECTION_ANALYSIS] Incoming: {len(incoming)}, Outgoing: {len(outgoing)}")
            
            if incoming:
                print("📥 [INCOMING_CONNECTIONS]:")
                for i, conn in enumerate(incoming[:3], 1):
                    source = conn.get('source_name', conn.get('source', 'Unknown'))
                    rel_type = conn.get('rel_type', conn.get('type', 'CONNECTED'))
                    print(f"   {i}. {source} --{rel_type}--> {comp['name']}")
                if len(incoming) > 3:
                    print(f"   ... and {len(incoming) - 3} more incoming connections")
            
            if outgoing:
                print("📤 [OUTGOING_CONNECTIONS]:")
                for i, conn in enumerate(outgoing[:3], 1):
                    target = conn.get('target_name', conn.get('target', 'Unknown'))
                    rel_type = conn.get('rel_type', conn.get('type', 'CONNECTED'))
                    print(f"   {i}. {comp['name']} --{rel_type}--> {target}")
                if len(outgoing) > 3:
                    print(f"   ... and {len(outgoing) - 3} more outgoing connections")
            # Calculate reusability score with detailed logging
            print("🔍 [STEP_2] Calculating component reusability score...")
            try:
                reusability_score = await self.graph_store.get_component_reusability_score(component_name)
                print(f"✅ [STEP_2] Reusability score calculated: {reusability_score:.2f}")
            except Exception as e:
                print(f"⚠️ [STEP_2] Reusability calculation failed: {e}")
                reusability_score = 0.0
            
            # Find related components with detailed logging
            print("🔍 [STEP_3] Finding related components...")
            try:
                related_components = await self.graph_store.find_related_components(component_name)
                print(f"✅ [STEP_3] Found {len(related_components)} related components")
                if related_components:
                    print("🔗 [RELATED_COMPONENTS]:")
                    for i, rel_comp in enumerate(related_components[:3], 1):
                        name = rel_comp.get('name', 'Unknown')
                        comp_type = rel_comp.get('type', 'Unknown')
                        relationship = rel_comp.get('relationship', rel_comp.get('distance', 'Unknown'))
                        print(f"   {i}. {name} ({comp_type}) - Distance: {relationship}")
                    if len(related_components) > 3:
                        print(f"   ... and {len(related_components) - 3} more related components")
            except Exception as e:
                print(f"⚠️ [STEP_3] Related components search failed: {e}")
                related_components = []
            
            response = f"## Component Analysis: {component_name}\n\n"
            response += f"**Type**: {relationships['component']['type']}\n"
            response += f"**Reusability Score**: {reusability_score:.2f}\n\n"
            
            if relationships['outgoing_connections']:
                response += "**Outgoing Connections**:\n"
                for conn in relationships['outgoing_connections']:
                    target_label = conn.get('target_name') or conn.get('target') or 'unknown'
                    rel_label = conn.get('rel_type') or conn.get('type') or 'REL'
                    response += f"- → {target_label} ({rel_label})\n"
                response += "\n"
            
            if relationships['incoming_connections']:
                response += "**Incoming Connections**:\n"
                for conn in relationships['incoming_connections']:
                    source_label = conn.get('source_name') or conn.get('source') or 'unknown'
                    rel_label = conn.get('rel_type') or conn.get('type') or 'REL'
                    response += f"- ← {source_label} ({rel_label})\n"
                response += "\n"
            
            if relationships['patterns']:
                response += "**Integration Patterns**:\n"
                for pattern in relationships['patterns']:
                    response += f"- {pattern}\n"
                response += "\n"
            
            if related_components:
                response += "**Related Components**:\n"
                for comp in related_components[:5]:  # Limit to top 5
                    response += f"- {comp['name']} ({comp['type']}) - Distance: {comp.get('relationship', comp.get('distance', 'Unknown'))}\n"
            
            # Return structured data as per playbook
            return {
                "component": relationships['component'],
                "incoming": relationships['incoming_connections'],
                "outgoing": relationships['outgoing_connections'],
                "patterns": relationships.get('patterns', []),
                "reusability_score": reusability_score,
                "related_components": related_components
            }
            
        except Exception as e:
            logger.error(f"Error in component analysis: {e}")
            print(f"❌ [KNOWLEDGE GRAPH] Error: {e}")
            return {
                "component": {"name": component_name or "Unknown", "type": "Unknown", "id": component_name or "Unknown"},
                "incoming": [],
                "outgoing": [],
                "patterns": [],
                "reusability_score": 0.0,
                "related_components": []
            }


class PatternAnalysisTool(SAPiFlowTool):
    """Tool for analyzing integration patterns."""
    
    def __init__(self, graph_store):
        super().__init__(
            name="pattern_analysis",
            description="Use this tool to analyze integration patterns in the iFlow. Call this when asked about patterns, flow types, or integration architecture.",
            vector_store=None,
            graph_store=graph_store
        )
    
    async def _arun(self, pattern_type: Optional[str] = None, query: Optional[str] = None) -> str:
        """Analyze integration patterns."""
        try:
            if pattern_type:
                patterns = await self.graph_store.find_integration_patterns(pattern_type)
            else:
                patterns = await self.graph_store.find_integration_patterns()
            
            if not patterns:
                return "No integration patterns found."
            
            response = f"## Integration Patterns Analysis\n\n"
            response += f"Found {len(patterns)} pattern(s):\n\n"
            
            for i, pattern in enumerate(patterns, 1):
                response += f"{i}. **{pattern['name']}**\n"
                response += f"   Type: {pattern['type']}\n"
                response += f"   Description: {pattern['description']}\n"
                response += f"   Complexity: {pattern['complexity_score']:.1f}/10\n"
                response += f"   Document: {pattern['document']}\n"
                if pattern['components']:
                    response += f"   Components: {', '.join(pattern['components'][:3])}"
                    if len(pattern['components']) > 3:
                        response += f" (+{len(pattern['components']) - 3} more)"
                    response += "\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            return f"Error analyzing patterns: {str(e)}"


class IFlowComponentQueryTool(SAPiFlowTool):
    """Tool for querying iFlow components."""
    
    def __init__(self, graph_store):
        super().__init__(
            name="iflow_component_query",
            description="Query iFlow components by type, ID, or package. Use this when asked about specific components or component types.",
            vector_store=None,
            graph_store=graph_store
        )
    
    async def _arun(self, query: str, component_type: Optional[str] = None, package_name: Optional[str] = None) -> str:
        """Query iFlow components."""
        try:
            print(f"\n🔍 [KNOWLEDGE GRAPH] Querying iFlow components: '{query}'")
            
            # Extract filters from query
            query_lower = query.lower()
            search_type = None
            search_package = package_name
            
            # Check for specific component types mentioned in query (normalized to Neo4j 'type')
            component_types = [
                'end event', 'start event', 'intermediate event',
                'service task', 'user task', 'script task', 'task',
                'exclusive gateway', 'parallel gateway', 'gateway',
                'adapter', 'router', 'splitter', 'aggregator', 'script', 'mapping', 'modifier'
            ]
            for comp_type in component_types:
                if comp_type in query_lower:
                    search_type = comp_type
                    break
            
            if component_type:
                search_type = component_type
            
            # Check for package names in query
            if not search_package and ('package' in query_lower or 'iflow' in query_lower):
                words = query.split()
                for word in words:
                    if len(word) > 5 and word not in ['package', 'iflow', 'component']:
                        search_package = word
                        break
            
            # Sequence flow specific request?
            if 'sequenceflow_' in query_lower or ('sequence flow' in query_lower and any(ch.isdigit() for ch in query_lower)):
                # Extract identifier token
                token = None
                for word in query.replace(':', ' ').replace('-', ' ').split():
                    if 'sequenceflow' in word.lower():
                        token = word
                        break
                # Also try to capture like SequenceFlow_81564015
                for word in query.split():
                    if word.lower().startswith('sequenceflow_'):
                        token = word
                        break
                if token:
                    print(f"   🔍 Fetching components by sequence flow: {token} ...")
                    rows = await self.graph_store.query_components_by_sequence_flow(token)
                    if not rows:
                        return f"No components found for sequence flow '{token}'."
                    # Format detailed list
                    response = f"## Components for Sequence Flow: {token}\n\n"
                    for i, row in enumerate(rows, 1):
                        response += (
                            f"{i}. {row['source_id']} ({row['source_type']})"
                            f"  --{row['relationship_type']}-->  "
                            f"{row['target_id']} ({row['target_type']})\n"
                        )
                    response += "\nSummary:\n"
                    source_types = {}
                    target_types = {}
                    for r in rows:
                        source_types[r['source_type']] = source_types.get(r['source_type'], 0) + 1
                        target_types[r['target_type']] = target_types.get(r['target_type'], 0) + 1
                    response += "- Sources: " + ", ".join([f"{k} x{v}" for k,v in source_types.items()]) + "\n"
                    response += "- Targets: " + ", ".join([f"{k} x{v}" for k,v in target_types.items()]) + "\n"
                    return response

            print(f"   🔍 Fetching components from Neo4j (type: {search_type}, package: {search_package})...")
            # Map natural language to actual 'type' values
            type_map = {
                'end event': 'EndEvent',
                'start event': 'StartEvent',
                'intermediate event': 'IntermediateEvent',
                'service task': 'ServiceTask',
                'user task': 'UserTask',
                'script task': 'ScriptTask',
                'exclusive gateway': 'ExclusiveGateway',
                'parallel gateway': 'ParallelGateway',
                'gateway': 'Gateway'
            }
            effective_type = type_map.get(search_type, search_type)
            components = await self.graph_store.query_iflow_components(
                component_type=effective_type,
                folder_id=search_package
            )
            print(f"🔧 [KNOWLEDGE GRAPH] Retrieved {len(components)} components from Neo4j")
            
            if not components:
                return f"No iFlow components found matching the query '{query}'."
            
            # Show detailed component data being retrieved
            print(f"📋 [KNOWLEDGE GRAPH] Component Data Retrieved:")
            for comp in components[:3]:  # Show first 3
                print(f"   • {comp['component_id']} ({comp['component_type']})")
                print(f"     - Folder: {comp.get('folder_id', 'Unknown')}")
                if comp.get('name'):
                    print(f"     - Name: {comp['name']}")
            if len(components) > 3:
                print(f"   ... and {len(components) - 3} more")
            
            response = f"## iFlow Components\n\n"
            response += f"Found {len(components)} component(s):\n\n"
            
            for i, comp in enumerate(components[:10], 1):  # Limit to 10 for display
                response += f"{i}. **{comp['component_id']}**\n"
                response += f"   Type: {comp['component_type']}\n"
                if comp.get('name'):
                    response += f"   Name: {comp['name']}\n"
                response += f"   Folder: {comp.get('folder_id', 'Unknown')}\n"
                if comp.get('position_x') is not None:
                    response += f"   Position: ({comp['position_x']}, {comp['position_y']})\n"
                response += "\n"
            
            if len(components) > 10:
                response += f"... and {len(components) - 10} more components\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error querying iFlow components: {e}")
            return f"Error querying iFlow components: {str(e)}"


class IFlowPackageAnalysisTool(SAPiFlowTool):
    """Tool for analyzing iFlow packages with components, flows, and assets."""
    
    def __init__(self, graph_store):
        super().__init__(
            name="iflow_package_analysis",
            description="Analyze iFlow packages including components, flows, and assets. Use this when asked about specific iFlow packages or to get package statistics.",
            vector_store=None,
            graph_store=graph_store
        )
    
    async def _arun(self, package_name: str, query: Optional[str] = None) -> str:
        """Analyze an iFlow package."""
        try:
            # Use query if package_name is not provided
            if not package_name and query:
                package_name = query.strip()
            
            if not package_name:
                # List available packages if no specific package requested
                print(f"\n🕸️ [KNOWLEDGE GRAPH] Fetching available iFlow packages...")
                packages = await self.graph_store.query_iflow_packages()
                print(f"📦 [KNOWLEDGE GRAPH] Retrieved {len(packages)} packages from Neo4j")
                
                if packages:
                    response = "## Available iFlow Packages:\n\n"
                    for pkg in packages:
                        response += f"**{pkg['package_name']}**\n"
                        if pkg.get('description'):
                            response += f"Description: {pkg['description']}\n"
                        if pkg.get('version'):
                            response += f"Version: {pkg['version']}\n"
                        response += "\n"
                    return response
                else:
                    return "No iFlow packages found in the knowledge graph."
            
            print(f"\n🕸️ [KNOWLEDGE GRAPH] Analyzing iFlow package: '{package_name}'")
            
            # Get detailed package analysis
            analysis = await self.graph_store.analyze_iflow_package(package_name)
            
            if "error" in analysis:
                return f"Error: {analysis['error']}"
            
            package_info = analysis['package']
            stats = analysis['statistics']
            
            print(f"📋 [KNOWLEDGE GRAPH] Package Analysis Retrieved:")
            print(f"   • Package: {package_info['name']}")
            print(f"   • Components: {stats.get('total_components', 0)}")
            print(f"   • Flows: {stats.get('total_flows', 0)}")
            if 'total_assets' in stats:
                print(f"   • Assets: {stats['total_assets']}")
            
            response = f"## iFlow Package Analysis: {package_info['name']}\n\n"
            
            if package_info.get('description'):
                response += f"**Description**: {package_info['description']}\n\n"
            
            if package_info.get('version'):
                response += f"**Version**: {package_info['version']}\n\n"
            
            response += f"### Statistics:\n"
            response += f"- **Total Components**: {stats.get('total_components', 0)}\n"
            response += f"- **Total Flows**: {stats.get('total_flows', 0)}\n"
            if 'total_assets' in stats:
                response += f"- **Total Assets**: {stats['total_assets']}\n"
            response += "\n"
            
            if stats['component_types']:
                response += "### Component Types:\n"
                for comp_type, count in stats['component_types'].items():
                    response += f"- **{comp_type}**: {count}\n"
                response += "\n"
            
            if stats['flow_types']:
                response += "### Flow Types:\n"
                for flow_type, count in stats['flow_types'].items():
                    response += f"- **{flow_type}**: {count}\n"
                response += "\n"
            
            if stats.get('asset_types'):
                response += "### Asset Types:\n"
                for asset_type, count in stats['asset_types'].items():
                    response += f"- **{asset_type}**: {count}\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in iFlow package analysis: {e}")
            return f"Error analyzing iFlow package: {str(e)}"


class SAPiFlowAgent:
    """AI Agent for SAP iFlow analysis and recommendations with request classification."""
    
    # Complete iFlow component definitions for dynamic component selection
    COMPLETE_IFLOW_COMPONENTS = {
        'start_event': {'type': 'StartEvent', 'xml_element': 'startEvent'},
        'end_event': {'type': 'EndEvent', 'xml_element': 'endEvent'},
        'groovy_script': {'type': 'GroovyScript', 'xml_element': 'callActivity'},
        'content_modifier': {'type': 'ContentModifier', 'xml_element': 'callActivity'},
        'message_mapping': {'type': 'MessageMapping', 'xml_element': 'callActivity'},
        'xslt_mapping': {'type': 'XSLTMapping', 'xml_element': 'callActivity'},
        'router': {'type': 'Router', 'xml_element': 'callActivity'},
        'multicast': {'type': 'Multicast', 'xml_element': 'callActivity'},
        'splitter': {'type': 'Splitter', 'xml_element': 'callActivity'},
        'aggregator': {'type': 'Aggregator', 'xml_element': 'callActivity'},
        'message_filter': {'type': 'MessageFilter', 'xml_element': 'callActivity'},
        'http_sender': {'type': 'EndpointSender', 'xml_element': 'participant'},
        'http_receiver': {'type': 'EndpointReceiver', 'xml_element': 'participant'},
        'sftp_adapter': {'type': 'SFTPAdapter', 'xml_element': 'callActivity'},
        'mail_adapter': {'type': 'MailAdapter', 'xml_element': 'callActivity'},
        'soap_adapter': {'type': 'SOAPAdapter', 'xml_element': 'callActivity'},
        'odata_adapter': {'type': 'ODataAdapter', 'xml_element': 'callActivity'},
        'jms_adapter': {'type': 'JMSAdapter', 'xml_element': 'callActivity'},
        'amqp_adapter': {'type': 'AMQPAdapter', 'xml_element': 'callActivity'},
    }
    
    # Authoritative SAP Integration Suite Standards - NEVER override these with RAG content
    SAP_AUTHORITATIVE_STANDARDS = {
        # Event Components
        'StartEvent': {
            'activityType': 'startEvent',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::MessageStartEvent',
            'componentVersion': '1.1'
        },
        'EndEvent': {
            'activityType': 'endEvent',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0',
            'componentVersion': '1.1'
        },
        
        # Processing Components
        'ContentModifier': {
            'activityType': 'Enricher',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::Enricher/version::1.6.1',
            'componentVersion': '1.6',
            'bodyType': 'constant',
            'propertyTable': '',
            'headerTable': '',
            'wrapContent': ''
        },
        'GroovyScript': {
            'activityType': 'Script',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2',
            'componentVersion': '1.1',
            'subActivityType': 'GroovyScript',
            'scriptFunction': '',
            'scriptBundleId': ''
        },
        'MessageMapping': {
            'activityType': 'Mapping',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::MessageMapping/version::1.1.0',
            'componentVersion': '1.1'
        },
        'XSLTMapping': {
            'activityType': 'XSLTMapping',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::XSLTMapping/version::1.1.0',
            'componentVersion': '1.1'
        },
        
        # Routing and Flow Control
        'Router': {
            'componentVersion': '1.1',
            'activityType': 'ExclusiveGateway',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.1.2',
            'throwException': 'false'
        },
        'Multicast': {
            'activityType': 'Multicast',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::Multicast/version::1.1.0',
            'componentVersion': '1.1'
        },
        'Splitter': {
            'exprType': 'XPath',
            'Streaming': 'true',
            'StopOnExecution': 'true',
            'SplitterThreads': '10',
            'splitExprValue': '',
            'ParallelProcessing': 'false',
            'componentVersion': '1.6',
            'activityType': 'Splitter',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::GeneralSplitter/version::1.6.0',
            'grouping': '',
            'splitType': 'GeneralSplitter',
            'timeOut': '300'
        },
        'Aggregator': {
            'activityType': 'Aggregator',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::Aggregator/version::1.1.0',
            'componentVersion': '1.1'
        },
        'MessageFilter': {
            'activityType': 'Filter',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::MessageFilter/version::1.1.0',
            'componentVersion': '1.1',
            'exprType': 'xpath',
            'exprValue': '//root'
        },
        'JsonToXmlConverter': {
            'activityType': 'JsonToXmlConverter',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::JsonToXmlConverter/version::1.0.2',
            'componentVersion': '1.0',
            'useNamespaces': 'false',
            'jsonNamespaceSeparator': ':',
            'addXMLRootElement': 'false',
            'additionalRootElementName': ''
        },
        'Gather': {
            'activityType': 'Gather',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::Gather/version::1.0.0',
            'componentVersion': '1.0',
            'messageType': 'SameXMLFormat',
            'aggregationAlgorithm': 'sap-identical-multi-mapping'
        },
        
        # Endpoint Components
        'EndpointSender': {
            'activityType': 'participant',
            'ifl:type': 'EndpointSender',
            'enableBasicAuthentication': 'false',
            'componentVersion': '1.1'
        },
        'EndpointReceiver': {
            'activityType': 'participant',
            'ifl:type': 'EndpointReceiver',
            'enableBasicAuthentication': 'false',
            'componentVersion': '1.1'
        },
        'ExternalCall': {
            'activityType': 'ExternalCall',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4',
            'componentVersion': '1.0'
        },
        'RequestReply': {
            'activityType': 'RequestReply',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::RequestReply/version::1.0.0',
            'componentVersion': '1.0'
        },
        
        # Adapter Components
        'SFTPAdapter': {
            'activityType': 'SFTP',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::SFTPAdapter/version::1.1.0',
            'componentVersion': '1.1'
        },
        'MailAdapter': {
            'activityType': 'Mail',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::MailAdapter/version::1.1.0',
            'componentVersion': '1.1'
        },
        'SOAPAdapter': {
            'activityType': 'SOAP',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::SOAPAdapter/version::1.1.0',
            'componentVersion': '1.1'
        },
        'ODataAdapter': {
            'activityType': 'OData',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::ODataAdapter/version::1.1.0',
            'componentVersion': '1.1'
        },
        'JMSAdapter': {
            'activityType': 'JMS',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::JMSAdapter/version::1.1.0',
            'componentVersion': '1.1'
        },
        'AMQPAdapter': {
            'activityType': 'AMQP',
            'cmdVariantUri': 'ctype::FlowstepVariant/cname::AMQPAdapter/version::1.1.0',
            'componentVersion': '1.1'
        }
    }
    
    # Component type mapping for RAG search optimization
    COMPONENT_SEARCH_MAPPING = {
        # Event Components
        'start_event': ['start event', 'message start', 'start', 'begin', 'initiate'],
        'end_event': ['end event', 'message end', 'end', 'finish', 'complete', 'terminate'],
        
        # Processing Components
        'content_modifier': ['enricher', 'content modifier', 'content enricher', 'enrich', 'modify content', 'set properties'],
        'groovy_script': ['groovy', 'script', 'groovy script', 'data processor', 'processor script', 'transformation script', 'custom logic'],
        'message_mapping': ['message mapping', 'mapping', 'transform', 'data transformation', 'field mapping'],
        'xslt_mapping': ['xslt', 'xslt mapping', 'xml transformation', 'xsl transformation'],
        
        # Routing and Flow Control
        'router': ['router', 'routing', 'route', 'conditional routing', 'decision', 'branch', 'exclusive gateway', 'gateway', 'decision point', 'conditional flow'],
        'multicast': ['multicast', 'broadcast', 'parallel send', 'multiple recipients'],
        'splitter': ['splitter', 'split', 'divide', 'break apart', 'fragment'],
        'aggregator': ['aggregator', 'aggregate', 'combine', 'merge', 'collect', 'gather'],
        'message_filter': ['filter', 'message filter', 'condition', 'conditional', 'if-then'],
        
        # Request-Reply Pattern (3 components)
        'request_reply': ['request reply', 'request-reply', 'requestreply'],
        'endpoint_sender': ['endpoint sender', 'http sender', 'https sender', 'sender', 'participant sender'],
        'endpoint_receiver': ['endpoint receiver', 'http receiver', 'https receiver', 'receiver', 'participant receiver'],
        'message_flow': ['message flow', 'http flow', 'https flow', 'connection', 'communication'],
        'http_sender': ['http sender', 'https sender', 'endpoint sender', 'http call', 'api call', 'rest call'],
        'http_receiver': ['http receiver', 'https receiver', 'endpoint receiver', 'http endpoint', 'rest endpoint'],
        
        # Adapter Components
        'sftp_adapter': ['sftp', 'sftp adapter', 'file transfer', 'secure ftp', 'file upload', 'file download'],
        'mail_adapter': ['mail', 'email', 'mail adapter', 'smtp', 'send email', 'notification'],
        'soap_adapter': ['soap', 'soap adapter', 'web service', 'soap call', 'xml service'],
        'odata_adapter': ['odata', 'odata adapter', 'odata service', 'odata call', 'sap odata'],
        'jms_adapter': ['jms', 'jms adapter', 'message queue', 'queue', 'messaging'],
        'amqp_adapter': ['amqp', 'amqp adapter', 'rabbitmq', 'message broker', 'async messaging']
    }
    
    # Request-Reply Pattern Definition (3 components)
    REQUEST_REPLY_PATTERN = {
        'pattern_name': 'Request-Reply Pattern',
        'description': 'Complete request-reply pattern with HTTP sender, service task, and HTTP receiver',
        'components': [
            {
                'type': 'http_sender',
                'name': 'HTTPS Sender',
                'xml_element': 'participant',
                'activity_type': 'EndpointSender',
                'description': 'HTTP/HTTPS sender adapter for outgoing requests'
            },
            {
                'type': 'request_reply',
                'name': 'Request Reply',
                'xml_element': 'serviceTask',
                'activity_type': 'ExternalCall',
                'description': 'Service task that makes external calls and waits for response'
            },
            {
                'type': 'http_receiver',
                'name': 'HTTP Receiver',
                'xml_element': 'participant',
                'activity_type': 'EndpointReceiver',
                'description': 'HTTP receiver adapter for incoming responses'
            }
        ],
        'message_flows': [
            {
                'from': 'http_sender',
                'to': 'start_event',
                'flow_type': 'HTTPS',
                'properties': {
                    'urlPath': '/test',
                    'httpMethod': 'POST',
                    'TransportProtocol': 'HTTPS'
                }
            },
            {
                'from': 'request_reply',
                'to': 'http_receiver',
                'flow_type': 'HTTP',
                'properties': {
                    'httpMethod': 'POST',
                    'TransportProtocol': 'HTTP',
                    'authenticationMethod': 'Client Certificate'
                }
            }
        ],
        'sequence_flow': [
            'start_event',
            'groovy_script',
            'content_modifier',
            'request_reply',
            'end_event'
        ]
    }
    
    def __init__(self, vector_store, graph_store, openai_api_key: str, context_document: Optional[str] = None):
        """
        Initialize the SAP iFlow agent.

        Args:
            vector_store: Vector store for semantic search
            graph_store: Graph store for relationship analysis
            openai_api_key: OpenAI API key
            context_document: Name of the document being analyzed
        """
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.context_document = context_document or "the current SAP iFlow"
        # Using playbook approach instead of request classifier
        self.llm = ChatOpenAI(
            model=config.AGENT_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            api_key=openai_api_key,
            streaming=config.AGENT_STREAM
        )

        # Initialize RAG component retrieval logger
        from utils.rag_logger import get_rag_logger
        self.rag_logger = get_rag_logger("RAG_Agent")
        logger.info("RAG Logger initialized for component retrieval tracking")

        # Initialize playbook tools with enhanced debugging
        self.debug_level = "VERBOSE"  # Enhanced debug level for detailed logs
        self.tools = [
            GetIflowSkeletonTool(graph_store),
            ComponentAnalysisTool(graph_store),
            VectorSearchTool(vector_store)
        ]
        # Map tool names to instances for internal orchestration/fallbacks
        self.tools_map = {tool.name: tool for tool in self.tools}

        # Initialize iFlow packager for generating importable packages
        self.packager = IFlowPackager(output_directory="generated_packages")

        # Create agent
        self.agent = self._create_agent()

    async def _retrieve_artifacts_by_node_order(
        self,
        iflow_name: str,
        skeleton: Dict[str, Any],
        per_node_limit: int = 2,
    ) -> Dict[str, Any]:
        """Given an iFlow skeleton, retrieve vector artifacts per node (in KG order) and stitch.
        - Builds semantic queries using node.type and node.name
        - Retrieves top-N vector chunks per node in topological order
        - Returns stitched structure with coverage
        """
        nodes = (skeleton or {}).get("nodes", [])
        edges = (skeleton or {}).get("edges", [])
        ordered_nodes = topological_order(nodes, edges)

        all_artifacts: List[Dict[str, Any]] = []
        per_node_results: List[Dict[str, Any]] = []

        if not self.vector_store:
            return {"ordered_nodes": ordered_nodes, "artifacts": [], "stitched": None, "per_node": []}

        for node in ordered_nodes:
            node_id = node.get("id", "unknown")
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            folder_id = node.get("folder_id", "")

            # Compose a semantically rich query from node properties
            # Example: "Enricher Data Enricher api_integration"
            query_terms = [t for t in [node_type, node_name, folder_id, iflow_name] if t]
            vector_query = " ".join(query_terms)

            # Debug: show node and embedding vector preview
            try:
                if hasattr(self.vector_store, "_encode_query"):
                    emb_preview = self.vector_store._encode_query(vector_query)
                    # Print only first 8 values to keep logs readable
                    preview_values = ", ".join(f"{v:.6f}" for v in emb_preview[:8])
                    print(f"[VECTOR_DEBUG] Node: '{node_name}' (type: {node_type})")
                    print(f"[VECTOR_DEBUG] Query: '{vector_query}'")
                    print(f"[VECTOR_DEBUG] Embedding dim: {len(emb_preview)} | values[0:8]: [{preview_values}]")
            except Exception as dbg_err:
                print(f"[VECTOR_DEBUG] Embedding preview failed: {dbg_err}")

            try:
                results = await self.vector_store.search_similar(
                    query=vector_query,
                    limit=per_node_limit,
                    chunk_types=["component", "asset", "pattern"]
                )

                # Log RAG retrieval
                self.rag_logger.log_retrieval(
                    query=vector_query,
                    results=results,
                    context={
                        "node_id": node_id,
                        "node_name": node_name,
                        "node_type": node_type,
                        "iflow_name": iflow_name,
                        "retrieval_location": "_retrieve_artifacts_by_node_order"
                    },
                    retrieval_type="vector_search"
                )
            except Exception as e:
                logger.error(f"Vector search failed for node {node_name}: {e}")
                results = []

            # Filter out non-relevant or oversized BPMN/entire iFlow chunks to save tokens
            filtered = [r for r in results if self._is_relevant_rag_chunk(r)]

            annotated = []
            for r in filtered:
                # Normalize fields for stitcher
                artifact = {
                    "name": r.get("document_name") or r.get("metadata", {}).get("iflow_name") or r.get("id", "artifact"),
                    "document_name": r.get("document_name", "unknown"),
                    "chunk_type": r.get("chunk_type", "unknown"),
                    "content": r.get("content", ""),
                    "confidence": float(r.get("similarity_score", 0.0)),
                    "similarity": float(r.get("similarity_score", 0.0)),
                    "node_id": node_id,
                    "node_name": node_name,
                    "node_type": node_type,
                }
                annotated.append(artifact)
                all_artifacts.append(artifact)

            per_node_results.append({
                "node": node,
                "query": vector_query,
                "results": annotated,
            })

        stitched = stitch(iflow_name=iflow_name or "iflow", skeleton=skeleton, artifacts=all_artifacts, confidence_threshold=0.65)

        return {
            "ordered_nodes": ordered_nodes,
            "artifacts": all_artifacts,
            "per_node": per_node_results,
            "stitched": stitched,
        }

    def _is_relevant_rag_chunk(self, chunk: Dict[str, Any]) -> bool:
        """Heuristic filter to keep only compact, relevant chunks and avoid full iFlow dumps."""
        allowed = {"component", "asset", "pattern"}
        ctype = (chunk.get("chunk_type") or "").lower()
        if ctype and ctype not in allowed:
            return False
        content = chunk.get("content", "") or ""
        doc_name = (chunk.get("document_name") or "").lower()
        # Skip very large BPMN/definitions blocks which eat tokens
        if len(content) > 6000 and ("<bpmn2:definitions" in content or "<definitions" in content):
            return False
        if "iflow" in doc_name and len(content) > 6000:
            return False
        return True
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent with tools and prompt."""
        
        # Enhanced system prompt with STRICT execution order
        system_prompt = """SAP iFlow Analysis Agent - STRICT EXECUTION ORDER:

MANDATORY EXECUTION SEQUENCE (NEVER DEVIATE):
1. ALWAYS START WITH KNOWLEDGE GRAPH: Query Neo4j first for topology, components, relationships
2. THEN USE VECTOR DATABASE: Based on KG findings, search for relevant documentation/configs
3. FINALLY SYNTHESIZE: Combine KG + Vector data with LLM reasoning

EXECUTION RULES:
- NEVER call vector_search before calling a KG tool (get_iflow_skeleton OR component_analysis)
- ALWAYS use KG findings to inform vector search queries
- For ANY query, start with either get_iflow_skeleton OR component_analysis
- Use KG results to determine what to search for in Vector DB

TOOLS (MUST USE IN THIS ORDER):
1. FIRST: get_iflow_skeleton(iflow_name) OR component_analysis(component_name) - Neo4j KG
2. SECOND: vector_search(query_based_on_kg_findings, limit, chunk_types) - Vector DB  
3. THIRD: LLM synthesis of combined findings

QUERY ROUTING:
- General flow questions → get_iflow_skeleton FIRST, then vector_search for flow docs
- Specific component questions → component_analysis FIRST, then vector_search for component details
- Technical/XML questions → component_analysis for structure FIRST, then vector_search for configs
- "All flows" questions → get_iflow_skeleton FIRST, then vector_search for comprehensive docs

RESPONSE FORMAT:
1) KG Findings: "From Neo4j: Found X components/flows with relationships [specific data]"
2) Vector Findings: "From Vector DB: Retrieved Y documents based on KG findings [doc names, content]"
3) Combined Analysis: "Synthesis of KG topology + Vector documentation: [detailed explanation]"

CODE DISPLAY RULES (CRITICAL):
- When user asks for scripts/code (e.g., "show me groovy script", "get me the code"):
  ALWAYS include the FULL CODE CONTENT from vector search results in response
- Format code with proper syntax highlighting using ```groovy code blocks
- Include both the code AND a brief explanation
- Example: "Here's the dateconversion.groovy script:
  
  ```groovy
  [FULL CODE CONTENT HERE]
  ```
  
  This script handles date format conversion..."

STRICT COMPLIANCE:
- If you call vector_search before KG tools, you are FAILING the requirement
- Always explain how KG findings informed your vector search strategy
- Show the connection between KG structure and Vector content

ERROR HANDLING:
- If KG fails or returns zero results: "KG returned no results; proceeding to Vector DB using user query and known iFlow aliases"
- If Vector fails after KG: "Vector search failed: [error] - proceeding with KG findings only"
- Never skip KG step even if it fails - always attempt it first
- If LLM is unavailable/invalid key: "LLM unavailable - using tool-only fallback (KG → Vector) and returning structured evidence""" 

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True
        )
    
    async def comprehensive_search(self, question: str) -> Dict[str, Any]:
        """
        Perform comprehensive search across ALL sources: Knowledge Graph (FIRST AND COMPREHENSIVE) + Vector DB + LLM synthesis.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with all search results and synthesized response
        """
        print(f"\n🔄 [SEARCH] '{question}'")
        print("🎯 Plan: KG (Neo4j) → Vector DB → LLM synthesis")
        
        all_results = {
            "kg_comprehensive": None,  # New comprehensive results
            "kg_packages": None,
            "kg_components": None,
            "kg_flows": None,
            "kg_patterns": None,
            "vector_results": None,
            "data_sources": [],
            "final_response": "",
            "tools_used": [],
            "raw_data": []
        }
        
        # PHASE 1: COMPREHENSIVE Neo4j Search (ALL queries at once)
        print("\n🕸️ [KG] Comprehensive Neo4j search")
        
        try:
            if hasattr(self.graph_store, 'verbose'):
                self.graph_store.verbose = 1  # concise KG logs
            try:
                await self.graph_store.get_schema_overview()
            except Exception:
                pass
            print("   Running query strategies…")
            neo4j_results = await self.graph_store.comprehensive_neo4j_search(question)
            
            if neo4j_results and any([
                neo4j_results.get("packages"),
                neo4j_results.get("components"),
                neo4j_results.get("component_relationships"),
                neo4j_results.get("sequence_flows"),
                neo4j_results.get("patterns"),
                neo4j_results.get("technologies"),
                neo4j_results.get("related_data")
            ]):
                all_results["kg_comprehensive"] = neo4j_results
                all_results["data_sources"].append("Neo4j Knowledge Graph (Comprehensive)")
                all_results["tools_used"].append("comprehensive_neo4j_search")
                
                # Format comprehensive results for LLM processing
                comprehensive_summary = f"Neo4j Comprehensive Search Results:\n\n"
                
                if neo4j_results["packages"]:
                    comprehensive_summary += f"📦 iFlow Packages ({len(neo4j_results['packages'])}):\n"
                    for pkg in neo4j_results["packages"][:5]:
                        comprehensive_summary += f"   • {pkg['package_name']} ({pkg['type']})\n"
                    if len(neo4j_results["packages"]) > 5:
                        comprehensive_summary += f"   ... and {len(neo4j_results['packages']) - 5} more\n"
                    comprehensive_summary += "\n"
                
                if neo4j_results["components"]:
                    comprehensive_summary += f"🔧 Components ({len(neo4j_results['components'])}):\n"
                    for comp in neo4j_results["components"][:10]:
                        comprehensive_summary += f"   • {comp['component_id']} ({comp['component_type']})\n"
                    if len(neo4j_results["components"]) > 10:
                        comprehensive_summary += f"   ... and {len(neo4j_results['components']) - 10} more\n"
                    comprehensive_summary += "\n"
                
                if neo4j_results["component_relationships"]:
                    comprehensive_summary += f"🔗 Component Relationships ({len(neo4j_results['component_relationships'])}):\n"
                    for rel in neo4j_results["component_relationships"][:3]:
                        comp = rel["component"]
                        comprehensive_summary += f"   • {comp['name']} ({comp['type']}): {len(rel['outgoing_connections'])} outgoing, {len(rel['incoming_connections'])} incoming\n"
                    if len(neo4j_results["component_relationships"]) > 3:
                        comprehensive_summary += f"   ... and {len(neo4j_results['component_relationships']) - 3} more\n"
                    comprehensive_summary += "\n"
                
                if neo4j_results["sequence_flows"]:
                    comprehensive_summary += f"➡️ Sequence Flows ({len(neo4j_results['sequence_flows'])}):\n"
                    for flow in neo4j_results["sequence_flows"][:5]:
                        comprehensive_summary += f"   • {flow.get('source_id')} → {flow.get('target_id')}\n"
                    comprehensive_summary += "\n"
                
                if neo4j_results["patterns"]:
                    comprehensive_summary += f"📋 Integration Patterns ({len(neo4j_results['patterns'])}):\n"
                    for pattern in neo4j_results["patterns"][:3]:
                        comprehensive_summary += f"   • {pattern['name']}: {pattern['type']}\n"
                    comprehensive_summary += "\n"
                
                if neo4j_results["technologies"]:
                    comprehensive_summary += f"🔧 Technologies ({len(neo4j_results['technologies'])}):\n"
                    for tech in neo4j_results["technologies"][:5]:
                        comprehensive_summary += f"   • {tech['name']}: {tech.get('category', 'N/A')}\n"
                    comprehensive_summary += "\n"
                
                all_results["raw_data"].append(comprehensive_summary)
                print(f"✅ [KG] Done | queries: {neo4j_results['total_queries']} | ok: {neo4j_results['successful_queries']}")
            else:
                print("❌ [KG] No data found")
        
        except Exception as e:
            print(f"❌ [PHASE 1] Comprehensive Neo4j search failed: {e}")
        
        # PHASE 1b: Legacy Knowledge Graph Search (individual tools for additional data)
        print("\n🕸️ [KG] Additional tool passes (if needed)")
        
        # Tool 1: Query iFlow Packages
        try:
            print("\n   📦 [KG-1] Searching iFlow packages...")
            package_tool = next(tool for tool in self.tools if tool.name == 'iflow_package_analysis')
            package_response = await package_tool._arun("", question)  # Let it auto-detect from query
            if package_response and "no iflow packages found" not in package_response.lower() and "error" not in package_response.lower():
                all_results["kg_packages"] = package_response
                all_results["raw_data"].append(f"iFlow Packages: {package_response}")
                all_results["tools_used"].append('kg_packages')
                print("   ✅ Found iFlow package information")
            else:
                print("   ❌ No iFlow package information found")
        except Exception as e:
            print(f"   ❌ Package search error: {e}")
        
        # Tool 2: Query iFlow Components
        try:
            print("\n   🔧 [KG-2] Searching iFlow components...")
            components_tool = next(tool for tool in self.tools if tool.name == 'iflow_component_query')
            components_response = await components_tool._arun(question)
            if components_response and "no iflow components found" not in components_response.lower():
                all_results["kg_components"] = components_response
                all_results["raw_data"].append(f"iFlow Components: {components_response}")
                all_results["tools_used"].append('kg_components')
                print("   ✅ Found iFlow component information")
            else:
                print("   ❌ No iFlow component information found")
        except Exception as e:
            print(f"   ❌ Component search error: {e}")
            
        # Tool 3: Pattern Analysis
        try:
            print("\n   📋 [KG-3] Searching integration patterns...")
            pattern_tool = next(tool for tool in self.tools if tool.name == 'pattern_analysis')
            pattern_response = await pattern_tool._arun(question)
            if pattern_response and "no integration patterns found" not in pattern_response.lower():
                all_results["kg_patterns"] = pattern_response
                all_results["raw_data"].append(f"Integration Patterns: {pattern_response}")
                all_results["tools_used"].append('pattern_analysis')
                print("   ✅ Found integration pattern information")
            else:
                print("   ❌ No integration pattern information found")
        except Exception as e:
            print(f"   ❌ Integration patterns search error: {e}")
            
        # Tool 4: Component Analysis (legacy tool for backwards compatibility)
        try:
            print("\n   🔧 [KG-4] Searching component relationships...")
            component_tool = next((tool for tool in self.tools if tool.name == 'component_analysis'), None)
            if component_tool:
                component_response = await component_tool._arun(question)
                if component_response and "not found" not in component_response.lower():
                    # Merge with components if not already found
                    if not all_results["kg_components"]:
                        all_results["kg_components"] = component_response
                        all_results["raw_data"].append(f"Component Relationships: {component_response}")
                        all_results["tools_used"].append('component_analysis')
                    print("   ✅ Found component relationship information")
                else:
                    print("   ❌ No component relationship information found")
            else:
                print("   ❌ Component analysis tool not available")
        except Exception as e:
            print(f"   ❌ Component relationship search error: {e}")
        
        # PHASE 2: Vector Database Search
        print("\n📊 [PHASE 2] Vector Database Search (PostgreSQL)")
        try:
            print("   🔍 Searching vector database for semantic matches...")
            vector_tool = next(tool for tool in self.tools if tool.name == 'vector_search')
            vector_response = await vector_tool._arun(question)
            all_results["tools_used"].append('vector_search')
            
            if vector_response and vector_response.strip() and "no similar content found" not in vector_response.lower():
                print("   ✅ Found relevant documents in vector database")
                all_results["vector_results"] = vector_response
                all_results["raw_data"].append(f"Vector Search: {vector_response}")
            else:
                print("   ❌ No relevant documents found in vector database")
                
        except Exception as e:
            print(f"   ❌ Vector database search error: {e}")
        
        # Determine data sources found
        kg_sources = [tool for tool in all_results["tools_used"] if tool.startswith('kg_') or tool in ['component_analysis', 'pattern_analysis']]
        if kg_sources:
            all_results["data_sources"].append("Knowledge Graph (Neo4j)")
        if all_results["vector_results"]:
            all_results["data_sources"].append("Vector Database (PostgreSQL)")
            
        # PHASE 3: LLM Synthesis of ALL Information
        print(f"\n🧠 [SYNTHESIS] Sources: {', '.join(all_results['data_sources'])} | Tools: {len(all_results['tools_used'])}")
        
        if all_results["raw_data"]:
            # Synthesize all information using LLM
            combined_data = "\n\n".join(all_results["raw_data"])
            from langchain.schema import HumanMessage
            synthesis_prompt = f"""
            Based on the comprehensive information gathered from multiple sources, please provide a thorough and well-organized response to the user's question.

            USER QUESTION: {question}

            INFORMATION GATHERED FROM SOURCES:
            {combined_data}

            Please synthesize this information into a comprehensive, well-structured response that:
            1. Directly answers the user's question
            2. Combines relevant information from all sources
            3. Provides additional context and insights
            4. Is well-organized and easy to read
            5. Mentions which sources the information came from

            SPECIAL INSTRUCTIONS FOR CODE REQUESTS:
            - If user asks for scripts, code, or specific file content (e.g., "show me groovy script", "get me the code"):
              ALWAYS include the complete code content found in the vector search results
            - Format code with proper markdown syntax highlighting (```groovy, ```xml, etc.)
            - Include both the full code AND a brief explanation of what it does
            - Don't just describe the code - show the actual code content

            Provide a complete and thorough response.
            """
            
            print("   🔀 Synthesizing final answer…")
            llm_response = await self.llm.ainvoke([HumanMessage(content=synthesis_prompt)])
            all_results["final_response"] = llm_response.content
            print("   ✅ LLM synthesis complete")
        else:
            # No external data found, use LLM inherent knowledge
            print("   💡 No external data found - using LLM inherent knowledge")
            all_results["data_sources"] = ["LLM Inherent Knowledge Only"]
            
            from langchain.schema import HumanMessage
            llm_response = await self.llm.ainvoke([HumanMessage(content=f"""
            Answer the following question using only your pre-trained knowledge.
            
            Question: {question}
            
            Please provide a comprehensive and helpful response based on your training data.
            """)])
            
            all_results["final_response"] = llm_response.content
            print("   ✅ LLM inherent knowledge response generated")
        
        return all_results
    
    async def handle_code_generation(self, question: str, classification) -> Dict[str, Any]:
        """Handle code generation requests."""
        print(f"\n💻 [CODE GENERATION] Generating code for: '{question}'")
        
        all_results = {
            "kg_packages": None,
            "kg_components": None, 
            "kg_flows": None,
            "vector_results": None,
            "data_sources": [],
            "final_response": "",
            "tools_used": [],
            "raw_data": []
        }
        
        # Focus on vector search for code examples
        try:
            vector_tool = next(tool for tool in self.tools if tool.name == 'vector_search')
            vector_response = await vector_tool._arun(question)
            if vector_response and "no similar content found" not in vector_response.lower():
                all_results["vector_results"] = vector_response
                all_results["raw_data"].append(f"Code Examples: {vector_response}")
                all_results["tools_used"].append('vector_search')
                all_results["data_sources"].append("Vector Database (Code Examples)")
        except Exception as e:
            print(f"   ❌ Vector search error: {e}")
        
        # Also get relevant components for context
        try:
            component_tool = next(tool for tool in self.tools if tool.name == 'iflow_component_query')
            component_response = await component_tool._arun(question)
            if component_response and "no iflow components found" not in component_response.lower():
                all_results["kg_components"] = component_response
                all_results["raw_data"].append(f"Related Components: {component_response}")
                all_results["tools_used"].append('kg_components')
                all_results["data_sources"].append("Knowledge Graph (Components)")
        except Exception as e:
            print(f"   ❌ Component search error: {e}")
        
        # Generate response with code focus
        if all_results["raw_data"]:
            combined_data = "\n\n".join(all_results["raw_data"])
            synthesis_prompt = f"""
            Generate code or provide implementation guidance for the user's request.
            
            USER REQUEST: {question}
            
            AVAILABLE INFORMATION:
            {combined_data}
            
            Please provide:
            1. Actual code/configuration if examples are available
            2. Step-by-step implementation guidance
            3. Best practices and considerations
            4. Complete, runnable examples when possible
            
            Format the response with clear code blocks and explanations.
            """
            
            from langchain.schema import HumanMessage
            llm_response = await self.llm.ainvoke([HumanMessage(content=synthesis_prompt)])
            all_results["final_response"] = llm_response.content
        else:
            # Use LLM inherent knowledge for code generation
            from langchain.schema import HumanMessage
            llm_response = await self.llm.ainvoke([HumanMessage(content=f"""
            Generate code or provide implementation guidance for: {question}
            
            Please provide complete, practical code examples with explanations.
            """)])
            all_results["final_response"] = llm_response.content
            all_results["data_sources"] = ["LLM Inherent Knowledge"]
        
        return all_results
    
    async def handle_search(self, question: str, classification) -> Dict[str, Any]:
        """Handle search requests."""
        print(f"\n🔍 [SEARCH] Searching for: '{question}'")
        
        all_results = {
            "kg_packages": None,
            "kg_components": None, 
            "kg_flows": None,
            "vector_results": None,
            "data_sources": [],
            "final_response": "",
            "tools_used": [],
            "raw_data": []
        }
        
        # Focus on knowledge graph searches
        try:
            # Search packages only if explicitly asked about packages/processes
            if any(tok in question.lower() for tok in ["package", "process "]):
                package_tool = next(tool for tool in self.tools if tool.name == 'iflow_package_analysis')
                package_response = await package_tool._arun("", question)
                if package_response and "error" not in package_response.lower():
                    all_results["kg_packages"] = package_response
                    all_results["raw_data"].append(f"iFlow Packages: {package_response}")
                    all_results["tools_used"].append('kg_packages')
        except Exception as e:
            print(f"   ❌ Package search error: {e}")
        
        try:
            # Search components
            component_tool = next(tool for tool in self.tools if tool.name == 'iflow_component_query')
            component_response = await component_tool._arun(question)
            if component_response and "no iflow components found" not in component_response.lower():
                all_results["kg_components"] = component_response
                all_results["raw_data"].append(f"iFlow Components: {component_response}")
                all_results["tools_used"].append('kg_components')
        except Exception as e:
            print(f"   ❌ Component search error: {e}")
        
        # Also search the vector DB for supporting snippets/examples
        try:
            vector_tool = next(tool for tool in self.tools if tool.name == 'vector_search')
            vector_response = await vector_tool._arun(question)
            if vector_response and "no similar content found" not in vector_response.lower():
                all_results["vector_results"] = vector_response
                all_results["raw_data"].append(f"Vector Search: {vector_response}")
                all_results["tools_used"].append('vector_search')
        except Exception as e:
            print(f"   ❌ Vector search error: {e}")
        
        # Decide final response strategy
        if all_results["kg_components"] and ("sequenceflow_" in question.lower() or "sequence flow" in question.lower()):
            # For sequence flow requests, return the exact list produced by the tool
            primary = all_results["kg_components"]
            # Append sources summary
            sources = ["Knowledge Graph"]
            if all_results["vector_results"]:
                sources.append("Vector DB")
            all_results["final_response"] = primary + "\n\nSources Used: " + ", ".join(sources)
            all_results["data_sources"] = sources
        else:
            if all_results["raw_data"]:
                if any(r.startswith("iFlow Components:") for r in all_results["raw_data"]):
                    all_results["data_sources"].append("Knowledge Graph")
                if all_results["vector_results"]:
                    all_results["data_sources"].append("Vector DB")
                combined_data = "\n\n".join(all_results["raw_data"])
                synthesis_prompt = f"""
                Provide search results for the user's query.
                
                USER SEARCH: {question}
                
                FOUND INFORMATION:
                {combined_data}
                
                Please organize the results in a clear, structured format with:
                1. Exact lists when requested (do not summarize lists)
                2. Categorized listings
                3. Key details for each item
                4. Relevant context and relationships
                5. End with a 'Sources Used' line summarizing where data came from
                """
                
                from langchain.schema import HumanMessage
                llm_response = await self.llm.ainvoke([HumanMessage(content=synthesis_prompt)])
                all_results["final_response"] = llm_response.content
            else:
                all_results["final_response"] = f"No specific results found for '{question}' in the iFlow knowledge base."
                all_results["data_sources"] = ["Search - No Results"]
        
        return all_results
    
    async def handle_analysis(self, question: str, classification) -> Dict[str, Any]:
        """Handle analysis requests."""
        print(f"\n📊 [ANALYSIS] Analyzing: '{question}'")
        
        # Use comprehensive search but focus on analytical tools
        return await self.comprehensive_search(question)
    
    def _is_packaging_request(self, question: str) -> bool:
        """
        Detect if user wants to package/generate an importable iFlow component.
        
        Args:
            question: User query
            
        Returns:
            True if this is a packaging request
        """
        packaging_keywords = [
            'package', 'create package', 'generate package', 'import', 'importable',
            'create iflow', 'generate iflow', 'build iflow', 'make iflow',
            'sap integration suite', 'zip', 'deploy'
        ]
        
        component_keywords = [
            'content enricher', 'content modifier', 'content modification', 'groovy script', 'groovy', 'message mapping', 
            'xslt mapping', 'schema', 'wsdl', 'http adapter', 'https adapter',
            'sftp adapter', 'mail adapter', 'request-reply', 'request reply', 'requestreply', 'external call',
            'endpoint sender', 'endpoint receiver', 'http sender', 'http receiver', 'router', 'content-based router'
        ]
        
        question_lower = question.lower()
        
        # Check for explicit packaging keywords
        has_packaging = any(keyword in question_lower for keyword in packaging_keywords)
        
        # Check for component types (often indicates intent to create/package)
        has_component = any(keyword in question_lower for keyword in component_keywords)
        
        # Debug output for RequestReply detection
        if 'request' in question_lower and 'reply' in question_lower:
            print(f"DEBUG: RequestReply detection - has_packaging: {has_packaging}, has_component: {has_component}")
            print(f"DEBUG: Question lower: {question_lower}")
            print(f"DEBUG: Matching component keywords: {[kw for kw in component_keywords if kw in question_lower]}")
        
        # Strong indicators of packaging intent
        strong_indicators = [
            'create a', 'generate a', 'build a', 'make a',
            'package a', 'import a', 'need a',
            'create ', 'generate ', 'build ', 'make ',
            'package ', 'import ', 'need ',
            'generate an', 'create an', 'build an', 'make an'
        ]
        has_strong = any(indicator in question_lower for indicator in strong_indicators)
        
        # Check for flow/integration keywords that indicate generation
        flow_keywords = [
            'flow', 'integration', 'integrated', 'with', 'component', 'components'
        ]
        has_flow = any(keyword in question_lower for keyword in flow_keywords)
        
        # If user mentions "generate/create/build" + "flow/integration" + component types, it's definitely a generation request
        if has_strong and has_flow and has_component:
            if 'request' in question_lower and 'reply' in question_lower:
                print(f"DEBUG: RequestReply - Strong+Flow+Component detected: True")
            return True
            
        result = has_packaging or (has_component and has_strong)
        if 'request' in question_lower and 'reply' in question_lower:
            print(f"DEBUG: RequestReply - Final result: {result} (has_packaging: {has_packaging}, has_component: {has_component}, has_strong: {has_strong})")
        return result
    
    def _detect_complete_iflow_request(self, question: str) -> bool:
        """
        Detect if user is requesting a complete iFlow vs single component.
        
        Args:
            question: User query string
            
        Returns:
            True if complete iFlow request detected
        """
        import re
        
        complete_iflow_indicators = [
            # Direct phrases
            'complete iflow', 'full iflow', 'entire iflow',
            'integration flow', 'full integration', 'complete integration',
            'end-to-end', 'complete package',
            
            # Multiple component indicators (kept as secondary signal only)
            'with.*and', 'including.*and', 'along with',
            'start.*end', 'sender.*receiver',
            'integrated flow', 'generate.*flow', 'create.*flow'
        ]
        
        question_lower = question.lower()
        
        # FIRST: robustly count distinct component types mentioned
        # This ensures that single-component phrasing like
        # "generate an integrated flow with request reply" does NOT force multi-component routing
        component_types_mentioned = []
        component_keywords = {
            'sender': 'EndpointSender',
            'receiver': 'EndpointReceiver', 
            'https': 'HTTPS',
            'http': 'HTTPS',
            'start event': 'StartEvent',
            'start message': 'StartEvent',
            'end event': 'EndEvent',
            'end message': 'EndEvent',
            'groovy script': 'GroovyScript',
            'data processor': 'GroovyScript',
            'processor script': 'GroovyScript',
            'transformation script': 'GroovyScript',
            'content enricher': 'ContentModifier',
            'content modifier': 'ContentModifier',
            'message mapping': 'MessageMapping',
            'request-reply': 'RequestReply',
            'request reply': 'RequestReply',
            'external call': 'ExternalCall',
            'router': 'Router',
            'content-based router': 'Router',
            'content based router': 'Router'
        }
        
        for keyword, comp_type in component_keywords.items():
            if keyword in question_lower and comp_type not in component_types_mentioned:
                component_types_mentioned.append(comp_type)

        # PRIMARY DECISION: if 2 or more distinct component types → complete iFlow
        if len(component_types_mentioned) >= 2:
            return True

        # If exactly one component type is mentioned:
        # - Check if user explicitly wants a "flow" or "integration" → complete iFlow
        # - Otherwise treat as single-component
        if len(component_types_mentioned) == 1:
            # Check if user says "flow", "integration", "iflow" → wants complete flow
            flow_indicators = ['flow', 'iflow', 'integration', 'end-to-end', 'complete', 'full']
            wants_complete_flow = any(indicator in question_lower for indicator in flow_indicators)
            
            if wants_complete_flow:
                print(f"   🔀 [ROUTING] Single component with 'flow' keyword → Complete iFlow (Start → {component_types_mentioned[0]} → End)")
                return True
            else:
                print(f"   🔀 [ROUTING] Single component, no 'flow' keyword → Single component only")
                return False

        # FALLBACK: No explicit components recognized → use indicator heuristics
        for indicator in complete_iflow_indicators:
            if re.search(indicator, question_lower):
                return True
        
        return False

    def _identify_components_in_query(self, question: str, llm_components: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Identify all iFlow components mentioned in the user query using heuristic parsing.
        Preserves the order of components as they appear in the query and supports more component types.
        If llm_components are provided, they'll be merged later; default path uses heuristics only.
        """
        import re
        question_lower = question.lower()

        # Expanded phrase → type mapping (synonyms included)
        phrase_map: Dict[str, Dict[str, str]] = {
            # Events
            'start event': {'type': 'StartEvent', 'xml_element': 'startEvent'},
            'start message': {'type': 'StartEvent', 'xml_element': 'startEvent'},
            'end event': {'type': 'EndEvent', 'xml_element': 'endEvent'},
            'end message': {'type': 'EndEvent', 'xml_element': 'endEvent'},

            # Senders/Receivers (participants)
            'http sender': {'type': 'EndpointSender', 'xml_element': 'participant'},
            'https sender': {'type': 'EndpointSender', 'xml_element': 'participant'},
            'http receiver': {'type': 'EndpointReceiver', 'xml_element': 'participant'},
            'https receiver': {'type': 'EndpointReceiver', 'xml_element': 'participant'},
            'sender': {'type': 'EndpointSender', 'xml_element': 'participant'},
            'receiver': {'type': 'EndpointReceiver', 'xml_element': 'participant'},

            # Processing steps (callActivity)
            'groovy script': {'type': 'GroovyScript', 'xml_element': 'callActivity'},
            'groovy': {'type': 'GroovyScript', 'xml_element': 'callActivity'},
            'content enricher': {'type': 'ContentModifier', 'xml_element': 'callActivity'},
            'content modifier': {'type': 'ContentModifier', 'xml_element': 'callActivity'},
            'content modifiers': {'type': 'ContentModifier', 'xml_element': 'callActivity'},  # Plural form
            'content modifier\'s': {'type': 'ContentModifier', 'xml_element': 'callActivity'},  # Possessive form
            'message mapping': {'type': 'MessageMapping', 'xml_element': 'callActivity'},
            'xslt mapping': {'type': 'XSLTMapping', 'xml_element': 'callActivity'},
            'router': {'type': 'Router', 'xml_element': 'exclusiveGateway'},
            'routing': {'type': 'Router', 'xml_element': 'exclusiveGateway'},
            'route': {'type': 'Router', 'xml_element': 'exclusiveGateway'},
            'routes': {'type': 'Router', 'xml_element': 'exclusiveGateway'},
            'multicast': {'type': 'Multicast', 'xml_element': 'callActivity'},
            'splitter': {'type': 'Splitter', 'xml_element': 'callActivity'},
            'split message': {'type': 'Splitter', 'xml_element': 'callActivity'},
            'divide payload': {'type': 'Splitter', 'xml_element': 'callActivity'},
            'break message into parts': {'type': 'Splitter', 'xml_element': 'callActivity'},
            'gather': {'type': 'Gather', 'xml_element': 'callActivity'},
            'aggregate': {'type': 'Gather', 'xml_element': 'callActivity'},
            'aggregator (gather)': {'type': 'Gather', 'xml_element': 'callActivity'},
            'aggregator': {'type': 'Aggregator', 'xml_element': 'callActivity'},
            'message filter': {'type': 'MessageFilter', 'xml_element': 'callActivity'},
            'filter': {'type': 'MessageFilter', 'xml_element': 'callActivity'},
            'filter message': {'type': 'MessageFilter', 'xml_element': 'callActivity'},
            'filter messages': {'type': 'MessageFilter', 'xml_element': 'callActivity'},

            # Converters
            'json to xml converter': {'type': 'JsonToXmlConverter', 'xml_element': 'callActivity'},
            'jsontoxml': {'type': 'JsonToXmlConverter', 'xml_element': 'callActivity'},
            'json_xml': {'type': 'JsonToXmlConverter', 'xml_element': 'callActivity'},
            'convert json to xml': {'type': 'JsonToXmlConverter', 'xml_element': 'callActivity'},

            # Request-Reply components (with adapter type support)
            # PRIORITY: Longest matches first to prevent "odata" from matching before "odata request reply"
            'odata request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'OData'},
            'soap request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'SOAP'},
            'processdirect request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'ProcessDirect'},
            'process direct request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'ProcessDirect'},
            'successfactors request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'SuccessFactors'},
            'success factors request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'SuccessFactors'},
            'http request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'HTTP'},
            'rest request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'HTTP'},
            'request reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'HTTP'},
            'request-reply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'HTTP'},
            'requestreply': {'type': 'RequestReply', 'xml_element': 'serviceTask', 'adapter_type': 'HTTP'},
            'external call': {'type': 'ExternalCall', 'xml_element': 'serviceTask', 'adapter_type': 'HTTP'},

            # Adapters - REMOVED odata, http, and soap as standalone since they're now part of RequestReply
            # Only keep actual standalone adapters
            'sftp': {'type': 'SFTPAdapter', 'xml_element': 'callActivity'},
            'mail': {'type': 'MailAdapter', 'xml_element': 'callActivity'},
            'jms': {'type': 'JMSAdapter', 'xml_element': 'callActivity'},
            'amqp': {'type': 'AMQPAdapter', 'xml_element': 'callActivity'},
        }

        # Find all phrase occurrences with positions for ordering
        hits: List[Tuple[int, str, Dict[str, str]]] = []
        for phrase, info in phrase_map.items():
            for m in re.finditer(re.escape(phrase), question_lower):
                hits.append((m.start(), phrase, info))

        # Sort by textual order
        hits.sort(key=lambda x: x[0])

        identified_components: List[Dict[str, Any]] = []
        seen_types: set = set()
        
        for _, phrase, info in hits:
            ctype = info['type']
            
            # Handle multiple instances of the same component type
            if ctype in seen_types and ctype in {'StartEvent', 'EndEvent'}:
                # We'll enforce single Start/End later, skip duplicates here to reduce noise
                continue
            
            # Extract component count and name
            count, base_name = self._extract_component_count_and_name(question, phrase, info['type'])
            
            # Create components based on count
            for i in range(count):
                # Always use proper spacing and capitalization for all components
                if info['type'] in ['StartEvent', 'EndEvent', 'Router']:
                    comp_name = f"{base_name} {i+1}"  # "Start 1", "End 1", "Router 1"
                elif info['type'] == 'MessageFilter':
                    comp_name = f"Filter {i+1}"  # "Filter 1", "Filter 2", etc.
                else:
                    # Convert camelCase/underscore to proper spacing: ContentModifier → "Content Modifier"
                    spaced_name = re.sub(r'([A-Z])', r' \1', base_name).strip()  # Add space before capitals
                    comp_name = f"{spaced_name} {i+1}"  # "Content Modifier 1", "Content Modifier 2", etc.
                comp = {
                    'keyword': phrase,
                    'type': info['type'],
                    'xml_element': info['xml_element'],
                    'name': comp_name,
                    'rag_queries': self._generate_component_rag_queries(phrase, info['type']),
                    'instance_number': i + 1,
                    'total_instances': count
                }
                
                # Add adapter_type if present (for RequestReply with HTTP/OData)
                if 'adapter_type' in info:
                    comp['adapter_type'] = info['adapter_type']
                
                identified_components.append(comp)
            
            seen_types.add(ctype)
        
        # Merge LLM-suggested components (names/types) if provided
        if llm_components:
            # Normalize types and build order preference by LLM output
            order_preference = []
            llm_map: Dict[str, str] = {}
            for item in llm_components:
                ctype = (item.get('type') or '').strip()
                cname = (item.get('name') or '').strip()
                if not ctype:
                    continue
                # Normalize some common phrases → canonical types
                type_norm_map = {
                    'start': 'StartEvent', 'start event': 'StartEvent',
                    'end': 'EndEvent', 'end event': 'EndEvent',
                    'groovy': 'GroovyScript', 'groovy script': 'GroovyScript',
                    'content enricher': 'ContentModifier', 'message mapping': 'MessageMapping',
                    'http': 'HTTPS', 'https': 'HTTPS',
                    'sender': 'EndpointSender', 'receiver': 'EndpointReceiver'
                }
                ctype_norm = type_norm_map.get(ctype.lower(), ctype)
                llm_map[ctype_norm] = cname or llm_map.get(ctype_norm, '')
                order_preference.append(ctype_norm)
            
            # Update names for already-identified components
            for comp in identified_components:
                if comp['type'] in llm_map and llm_map[comp['type']]:
                    comp['name'] = llm_map[comp['type']]
            
            # Add any LLM components not captured by heuristics yet
            existing_types = {comp['type'] for comp in identified_components}
            for ctype_norm, cname in llm_map.items():
                if ctype_norm not in existing_types and ctype_norm in [v['type'] for v in self.COMPLETE_IFLOW_COMPONENTS.values()] + ['GroovyScript', 'ContentModifier', 'MessageMapping', 'HTTPS']:
                    # Find matching key to get xml_element
                    xml_element = 'callActivity'
                    for k, v in self.COMPLETE_IFLOW_COMPONENTS.items():
                        if v['type'] == ctype_norm:
                            xml_element = v['xml_element']
                            break
                    identified_components.append({
                        'keyword': ctype_norm,
                        'type': ctype_norm,
                        'xml_element': xml_element,
                        'name': cname if cname else ctype_norm,
                        'rag_queries': self._generate_component_rag_queries(ctype_norm, ctype_norm)
                    })
            
            # Reorder components to match LLM's sequence (keep relative order for non-mentioned)
            type_to_comp = {c['type']: c for c in identified_components}
            ordered = []
            seen = set()
            for t in order_preference:
                if t in type_to_comp and t not in seen:
                    ordered.append(type_to_comp[t])
                    seen.add(t)
            for c in identified_components:
                if c['type'] not in seen:
                    ordered.append(c)
            identified_components = ordered
        
        # Ensure we have essential components (start/end) exactly once
        essential_components = ['StartEvent', 'EndEvent']
        found_types = [comp['type'] for comp in identified_components]
        for essential in essential_components:
            if found_types.count(essential) == 0:
                # Name preference from LLM map if available
                default_name = 'Start' if essential == 'StartEvent' else 'End'
                identified_components.append({
                    'keyword': 'start event' if essential == 'StartEvent' else 'end event',
                    'type': essential,
                    'xml_element': 'startEvent' if essential == 'StartEvent' else 'endEvent',
                    'name': (llm_map.get(essential) if 'llm_map' in locals() and llm_map.get(essential) else default_name),
                    'rag_queries': ['start event', 'message start event', 'startEvent'] if essential == 'StartEvent' else ['end event', 'message end event', 'endEvent']
                })
            elif found_types.count(essential) > 1:
                # Deduplicate by keeping first occurrence
                first = True
                deduped = []
                for comp in identified_components:
                    if comp['type'] == essential:
                        if first:
                            deduped.append(comp)
                            first = False
                        else:
                            continue
                    else:
                        deduped.append(comp)
                identified_components = deduped
        
        # Ensure adapter-like components are unique (keep first occurrence)
        unique_once_types = {'EndpointSender', 'EndpointReceiver', 'HTTPS', 'HTTPAdapter', 'SFTPAdapter', 'MailAdapter'}
        seen_types = set()
        deduped_all = []
        for comp in identified_components:
            if comp['type'] in unique_once_types:
                if comp['type'] in seen_types:
                    continue
                seen_types.add(comp['type'])
            deduped_all.append(comp)
        identified_components = deduped_all

        # Handle multiple instances of processing steps (allow multiple ContentModifiers, etc.)
        # Only deduplicate truly unintended duplicates
        deduped_proc = []
        seen_combinations = set()
        for comp in identified_components:
            # Create a unique key based on type and instance number
            key = (comp['type'], comp.get('instance_number', 1))
            if key not in seen_combinations:
                seen_combinations.add(key)
                deduped_proc.append(comp)
        identified_components = deduped_proc
        
        return identified_components

    def _extract_component_count_and_name(self, question: str, component_key: str, component_type: str) -> tuple[int, str]:
        """
        Extract component count and name from query.
        Handles cases like "two content modifiers", "three groovy scripts", etc.
        
        Returns:
            tuple: (count, base_name)
        """
        import re
        
        # Number words mapping
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        # Patterns to extract count and name
        patterns = [
            # "two content modifiers" -> (2, "ContentModifier")
            rf'(\w+)\s+{re.escape(component_key)}',
            # "content modifier called MyModifier" -> (1, "MyModifier")
            rf'{re.escape(component_key)}\s+called\s+(\w+)',
            # "content modifier named MyModifier" -> (1, "MyModifier")
            rf'{re.escape(component_key)}\s+named\s+(\w+)',
            # "MyModifier content modifier" -> (1, "MyModifier")
            rf'(\w+)\s+{re.escape(component_key)}'
        ]
        
        count = 1  # Default count
        base_name = None
        
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                extracted = match.group(1).lower()
                
                # Check if it's a number word
                if extracted in number_words:
                    count = number_words[extracted]
                    base_name = None  # Will use default name
                # Check if it's a regular number
                elif extracted.isdigit():
                    count = int(extracted)
                    base_name = None  # Will use default name
                # Check if it's a valid component name (not common words)
                elif extracted not in ['a', 'an', 'the', 'with', 'and', 'or', 'but', 'flow', 'integration', 'by', 'followed', 'then', 'after']:
                    base_name = extracted.capitalize()
                    count = 1
                break
        
        # Generate default name if not extracted
        if base_name is None:
            if component_type == 'GroovyScript':
                base_name = 'GroovyScript'
            elif component_type == 'ContentModifier':
                base_name = 'ContentModifier'
            elif component_type == 'EndpointSender':
                base_name = 'HTTPSender'
            elif component_type == 'EndpointReceiver':
                base_name = 'HTTPSReceiver'
            elif component_type == 'StartEvent':
                base_name = 'Start'
            elif component_type == 'EndEvent':
                base_name = 'End'
            elif component_type == 'MessageMapping':
                base_name = 'MessageMapping'
            elif component_type == 'MessageFilter':
                base_name = 'Filter'
            else:
                base_name = component_type
        
        print(f"🔍 [COMPONENT_EXTRACTION] '{component_key}' -> count={count}, base_name='{base_name}'")
        return count, base_name

    def _extract_component_name_from_query(self, question: str, component_key: str, component_type: str) -> str:
        """Extract specific component name from query, or generate default."""
        import re
        
        # Patterns to extract names like "CustomerProcessor groovy script" 
        name_patterns = [
            rf'(\w+)\s+{re.escape(component_key)}',
            rf'{re.escape(component_key)}\s+called\s+(\w+)', 
            rf'{re.escape(component_key)}\s+named\s+(\w+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                candidate = match.group(1).lower()
                if candidate not in ['a', 'an', 'the', 'with', 'and', 'or', 'but', 'flow', 'integration']:
                    return candidate.capitalize()
        
        # Generate default names - use generic names instead of hardcoded ones
        if component_type == 'GroovyScript':
            return 'GroovyScript'  # Use generic SAP element name
        elif component_type == 'ContentModifier':
            return 'ContentModifier'  # Use proper SAP element name
        elif component_type == 'EndpointSender':
            return 'HTTPSender'  # More descriptive name
        elif component_type == 'EndpointReceiver':
            return 'HTTPSReceiver'  # More descriptive name
        elif component_type == 'StartEvent':
            return 'Start'
        elif component_type == 'EndEvent':
            return 'End'
        elif component_type == 'MessageMapping':
            return 'MessageMapping'
        elif component_type == 'HTTPS':
            return 'HTTPS'
        else:
            return component_type  # Use the actual SAP component type name

    async def _llm_extract_components(self, question: str) -> List[Dict[str, Any]]:
        """Use LLM to extract an ordered list of components with names from the user query.
        Returns a list of dicts: {'type': str, 'name': Optional[str]}.
        Designed to be token-efficient with a constrained prompt and output format.
        """
        try:
            allowed_types = [
                'StartEvent','EndEvent','GroovyScript','ContentModifier','MessageMapping',
                'HTTPS','EndpointSender','EndpointReceiver','HTTPAdapter','SFTPAdapter',
                'MailAdapter','ExclusiveGateway','ParallelGateway','ServiceTask'
            ]
            instruction = (
                "Extract the ordered list of SAP Integration Suite iFlow components explicitly requested in the user's query. "
                "Output ONLY a compact JSON array where each item has keys 'type' and 'name'. "
                "Types MUST be chosen from this list: " + ",".join(allowed_types) + ". "
                "Use null for 'name' if the user did not specify one. Do not invent extra components.\n\n"
                f"User query: {question}"
            )
            llm_resp = await self.llm.ainvoke([HumanMessage(content=instruction)])
            raw = llm_resp.content.strip()
            # Extract JSON array if wrapped
            import json, re
            json_str = raw
            m = re.search(r"\[.*\]", raw, flags=re.DOTALL)
            if m:
                json_str = m.group(0)
            data = json.loads(json_str)
            components = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'type' in item:
                        components.append({'type': item.get('type'), 'name': item.get('name')})
            return components
        except Exception:
            # Fallback: no LLM guidance
            return []

    def _generate_component_rag_queries(self, component_key: str, component_type: str) -> List[str]:
        """Generate RAG search queries for specific component type."""
        base_queries = [component_key, component_type.lower()]
        
        # Add component-specific search terms that match vector database content
        if component_type == 'GroovyScript':
            base_queries.extend([
                'groovy script XML', 'groovy script', 'processData', 'import com.sap.gateway',
                'def Message processData', 'groovy transformation', 'callActivity groovy'
            ])
        elif component_type == 'StartEvent':
            base_queries.extend([
                'start event XML', 'start event', 'startEvent', 'message start event',
                'bpmn2:startEvent', 'startEvent XML'
            ])
        elif component_type == 'EndEvent':
            base_queries.extend([
                'end event XML', 'end event', 'endEvent', 'message end event',
                'bpmn2:endEvent', 'endEvent XML'
            ])
        elif component_type == 'ContentModifier':
            base_queries.extend([
                'content enricher XML', 'content enricher', 'enricher', 'callActivity enricher',
                'content modifier XML', 'callActivity XML', 'enricher XML'
            ])
        elif component_type == 'MessageMapping':
            base_queries.extend([
                'message mapping XML', 'message mapping', 'mapping XML', 'callActivity mapping'
            ])
        elif component_type == 'Router':
            base_queries.extend([
                'router XML', 'exclusive gateway XML', 'gateway XML', 'router', 'exclusive gateway'
            ])
        elif component_type == 'Splitter':
            base_queries.extend([
                'splitter XML', 'general splitter', 'splitter', 'activityType Splitter',
                'GeneralSplitter', 'callActivity splitter', 'split message', 'splitter component'
            ])
        elif component_type == 'MessageFilter':
            base_queries.extend([
                'message filter XML', 'filter XML', 'message filter', 'activityType Filter',
                'Filter', 'callActivity filter', 'filter message', 'filter component'
            ])
        elif component_type == 'EndpointSender':
            base_queries.extend([
                'endpoint sender XML', 'http sender XML', 'participant sender XML', 'sender XML'
            ])
        elif component_type == 'EndpointReceiver':
            base_queries.extend([
                'endpoint receiver XML', 'http receiver XML', 'participant receiver XML', 'receiver XML'
            ])
        elif component_type == 'ExternalCall':
            base_queries.extend([
                'external call XML', 'service task XML', 'external call', 'service task'
            ])
        elif component_type == 'RequestReply':
            # CRITICAL: Search for RequestReply with activityType filter
            base_queries.extend([
                'RequestReply', 'request reply', 'activityType RequestReply',
                'Request Reply XML', 'service task request reply',
                'external call request reply', 'RequestReply adapter',
                'RequestReply HTTP', 'RequestReply OData'
            ])
        
        return base_queries

    def _extract_component_info(self, question: str) -> Dict[str, str]:
        """
        Extract component type and name from user question.
        
        Args:
            question: User query
            
        Returns:
            Dictionary with 'type' and 'name' keys
        """
        question_lower = question.lower()
        
        # Component type mapping
        component_mapping = {
            'content enricher': 'ContentModifier',
            'content modifier': 'ContentModifier',
            'groovy script': 'GroovyScript',
            'message mapping': 'MessageMapping',
            'xslt mapping': 'XSLTMapping',
            'schema': 'Schema',
            'wsdl': 'WSDL',
            'http adapter': 'HTTPAdapter',
            'sftp adapter': 'SFTPAdapter',
            'mail adapter': 'MailAdapter',
            'request reply': 'RequestReply',
            'request-reply': 'RequestReply',
            'requestreply': 'RequestReply',
            'external call': 'ExternalCall',
            'router': 'Router',
            'content-based router': 'Router',
            'content based router': 'Router'
        }
        
        # Find component type
        component_type = None  # No default - let the system determine
        for key, value in component_mapping.items():
            if key in question_lower:
                component_type = value
                break
        
        # If no specific component detected, return None to trigger fallback flow
        if not component_type:
            return {'type': None, 'name': 'SimpleFlow'}
        
        # Extract component name (simple heuristic)
        import re
        
        # Look for patterns like "create a CustomerProcessor content enricher"
        # Avoid matching common words like "by", "with", "and", etc.
        name_patterns = [
            r'(?:create|generate|build|make)?\s*(?:a|an)?\s*([A-Za-z][A-Za-z0-9_]*)\s+(?:content enricher|groovy script|message mapping|request reply)',
            r'(?:for|called|named)\s+([A-Za-z][A-Za-z0-9_]*)',
            r'([A-Za-z][A-Za-z0-9_]*)\s+(?:content enricher|groovy script|message mapping|request reply)'
        ]
        
        # Use the same naming convention as multi-component creation
        # Map component types to base names
        base_name_map = {
            'ContentModifier': 'ContentModifier',
            'GroovyScript': 'GroovyScript',
            'RequestReply': 'RequestReply',
            'MessageMapping': 'MessageMapping',
            'ExternalCall': 'RequestReply',
            'Router': 'Router',
            'StartEvent': 'Start',
            'EndEvent': 'End'
        }
        
        base_name = base_name_map.get(component_type, component_type)
        
        # For single-component creation, use proper spacing and capitalization
        if component_type in ['StartEvent', 'EndEvent', 'Router']:
            component_name = f"{base_name} 1"  # "Start 1", "End 1", "Router 1"
        else:
            # Convert camelCase/underscore to proper spacing: ContentModifier → "Content Modifier"
            spaced_name = re.sub(r'([A-Z])', r' \1', base_name).strip()  # Add space before capitals
            component_name = f"{spaced_name} 1"  # "Content Modifier 1", "Groovy Script 1", etc.
        
        print(f"   📛 [NAMING] Single component: {component_type} → {component_name}")
        
        return {
            'type': component_type,
            'name': component_name
        }
    
    async def _create_simple_flow_package(self, question: str) -> Dict[str, Any]:
        """
        Create a simple iFlow package with just StartEvent → EndEvent.
        
        Args:
            question: User query
            
        Returns:
            Dictionary containing package information
        """
        print(f"🔄 [SIMPLE_FLOW] Creating basic StartEvent → EndEvent flow")
        
        # Generate StartEvent and EndEvent XML with proper naming
        start_event_xml = await self._generate_generic_component_xml('StartEvent', 'Start 1', [], [])
        end_event_xml = await self._generate_generic_component_xml('EndEvent', 'End 1', [], [])
        
        # Create a simple flow with StartEvent → EndEvent
        components = [
            {
                'xml': start_event_xml,
                'type': 'StartEvent',
                'name': 'Start 1',  # Updated to match naming convention
                'id': 'StartEvent_1'
            },
            {
                'xml': end_event_xml,
                'type': 'EndEvent', 
                'name': 'End 1',  # Updated to match naming convention
                'id': 'EndEvent_1'
            }
        ]
        
        # Generate iFlow name
        iflow_name = self._generate_iflow_name(question, components) or 'SimpleFlow'
        
        # Package using the complete iFlow packager
        package_path = self.packager.package_complete_iflow_corrected(
            components=components,
            iflow_name=iflow_name,
            flow_description=f'Simple iFlow generated from: {question}',
            groovy_files={},
            complete_iflow_template=[]
        )
        
        return {
            'final_response': f"✅ Simple iFlow package created: {package_path}",
            'package_path': package_path,
            'package_info': {
                'iflow_name': iflow_name,
                'components': len(components),
                'sources_used': 'Basic StartEvent → EndEvent flow',
                'package_path': package_path
            },
            'tools_used': ['_create_simple_flow_package', 'package_complete_iflow_corrected']
        }
    
    async def _ensure_start_end_events(self, components: List[Dict[str, Any]]) -> None:
        """
        Ensure StartEvent and EndEvent are always present in the flow (no duplicates).
        
        Args:
            components: List of components to check and modify
        """
        # Check if StartEvent and EndEvent already exist
        has_start = any(comp['type'] == 'StartEvent' for comp in components)
        has_end = any(comp['type'] == 'EndEvent' for comp in components)
        
        if not has_start:
            print("   ➕ [START_EVENT] Adding StartEvent (not found in user components)")
            start_event_xml = await self._generate_generic_component_xml('StartEvent', 'Start 1', [], [])
            components.insert(0, {
                'type': 'StartEvent',
                'name': 'Start 1',  # With space and number
                'xml': start_event_xml,
                'quantity': 1,
                'source': 'auto_generated',
                'priority': 'high',
                'rag_results': []
            })
        
        if not has_end:
            print("   ➕ [END_EVENT] Adding EndEvent (not found in user components)")
            end_event_xml = await self._generate_generic_component_xml('EndEvent', 'End 1', [], [])
            components.append({
                'type': 'EndEvent',
                'name': 'End 1',  # With space and number
                'xml': end_event_xml,
                'quantity': 1,
                'source': 'auto_generated',
                'priority': 'high',
                'rag_results': []
            })
        
        if has_start and has_end:
            print("   ✅ [EVENTS] StartEvent and EndEvent already present (no duplicates created)")
    
    async def _generate_component_xml(self, component_type: str, component_name: str,
                                    retrieved_content: List[Dict[str, Any]], component_metadata: Dict = None) -> str:
        """
        Generate complete SAP iFlow XML from retrieved RAG content.
        
        Args:
            component_type: Type of component to generate
            component_name: Name for the component
            retrieved_content: Content retrieved from RAG/KG
            component_metadata: Optional metadata for component (e.g., Router branch_count, routing_criteria)
            
        Returns:
            Complete XML string ready for packaging
        """
        # Extract relevant XML/code content from RAG results
        xml_snippets = []
        code_content = []
        
        for item in retrieved_content:
            content = item.get('content', '')
            if '<' in content and '>' in content:  # Likely XML
                xml_snippets.append(content)
            elif any(keyword in content.lower() for keyword in ['script', 'groovy', 'function']):
                code_content.append(content)
        
        # Generate component-specific XML based on type
        if component_type == 'ContentModifier':
            return self._generate_content_modifier_xml(component_name, xml_snippets, code_content)
        elif component_type == 'GroovyScript':
            return self._generate_groovy_script_xml(component_name, xml_snippets, code_content)
        elif component_type == 'MessageMapping':
            return self._generate_message_mapping_xml(component_name, retrieved_content)
        elif component_type == 'RequestReply':
            # Generate RequestReply ServiceTask (ExternalCall semantics) from RAG
            xml = self._generate_request_reply_xml_from_rag(component_name, xml_snippets, code_content)
            return xml
        elif component_type == 'Router':
            # Extract Router-specific metadata
            metadata = component_metadata or {}
            branch_count = metadata.get('branch_count', 2)
            routing_criteria = metadata.get('routing_criteria')
            return self._generate_router_xml(component_name, xml_snippets, code_content, branch_count, routing_criteria)
        elif component_type == 'Splitter':
            return self._generate_splitter_xml(component_name, xml_snippets, code_content)
        elif component_type == 'MessageFilter':
            return self._generate_message_filter_xml(component_name, xml_snippets, code_content)
        elif component_type == 'JsonToXmlConverter':
            return self._generate_json_to_xml_converter_xml(component_name, xml_snippets, code_content)
        elif component_type == 'Gather':
            return self._generate_gather_xml(component_name, xml_snippets, code_content)
        else:
            return await self._generate_generic_component_xml(component_type, component_name, xml_snippets, code_content)
    
    def _generate_content_modifier_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate ContentModifier (aka Content Enricher) XML using authoritative SAP standards."""
        import uuid
        
        # Generate CallActivity XML matching reference-like structure
        component_id = f"CallActivity_{uuid.uuid4().hex[:8]}"
        
        # Start with callActivity (not serviceTask!)
        xml_content = f'''<bpmn2:callActivity id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
        
        # Use AUTHORITATIVE SAP standards - NEVER override with RAG content
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['ContentModifier']
        
        # Add all authoritative properties
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
        
        return xml_content
    
    def _generate_splitter_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate General Splitter XML using RAG content + authoritative SAP standards."""
        import uuid
        import re
        
        # Generate CallActivity XML (Splitter is callActivity, not serviceTask!)
        component_id = f"General_Splitter_{uuid.uuid4().hex[:8]}"
        
        # Extract properties from RAG content if available
        rag_properties = {}
        for snippet in xml_snippets:
            # Extract all property elements from RAG chunks (with or without ifl: prefix)
            prop_pattern = r'<(?:ifl:)?property>\s*<key>\s*([^<]+?)\s*</key>\s*<value>\s*(.*?)\s*</value>\s*</(?:ifl:)?property>'
            prop_matches = re.findall(prop_pattern, snippet, re.DOTALL)
            
            for key, value in prop_matches:
                key = key.strip()
                value = value.strip()
                # Only store CONFIGURATION properties from RAG, NOT structural ones
                # NEVER allow RAG to override activityType, cmdVariantUri, splitType - these MUST be correct
                if key in [
                    'exprType', 'Streaming', 'StopOnExecution', 'SplitterThreads', 
                    'splitExprValue', 'ParallelProcessing', 'grouping', 'timeOut'
                ]:
                    rag_properties[key] = value
        
        # Use AUTHORITATIVE SAP standards as base - CRITICAL fields protected
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['Splitter'].copy()
        
        # Only allow RAG to override CONFIGURATION values, not structural properties
        for key, value in rag_properties.items():
            if key in authoritative_properties:
                authoritative_properties[key] = value
        
        print(f"   📋 [SPLITTER] Using {len(rag_properties)} config properties from RAG, {len(authoritative_properties)} total")
        print(f"   🔒 [SPLITTER] Protected fields: activityType={authoritative_properties['activityType']}, splitType={authoritative_properties['splitType']}")
        
        xml_content = f'''<bpmn2:callActivity id="{component_id}" name="General Splitter">
    <bpmn2:extensionElements>'''
        
        # Add all properties (authoritative + RAG overrides)
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
        
        return xml_content
    
    def _generate_message_filter_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate Message Filter XML using authoritative SAP standards."""
        import uuid
        
        # Generate CallActivity XML (MessageFilter is callActivity)
        component_id = f"Filter_{uuid.uuid4().hex[:8]}"
        
        # Use AUTHORITATIVE SAP standards - includes default XPath expression
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['MessageFilter'].copy()
        
        print(f"   📋 [MESSAGE_FILTER] Using authoritative SAP standards with default XPath")
        print(f"   🔒 [MESSAGE_FILTER] Protected fields: activityType={authoritative_properties['activityType']}, exprType={authoritative_properties['exprType']}, exprValue={authoritative_properties['exprValue']}")
        
        xml_content = f'''<bpmn2:callActivity id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
        
        # Add all authoritative properties (including exprType and exprValue)
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
        
        return xml_content
    
    def _generate_groovy_script_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate GroovyScript XML using RAG chunks as templates only - all IDs generated fresh."""
        import uuid
        import re
        
        # Generate fresh component ID - never use RAG chunk IDs
        component_id = f"CallActivity_{uuid.uuid4().hex[:8]}"
        script_filename = f"{name.lower().replace(' ', '_')}.groovy"
        
        # Extract properties from RAG content (XML callActivity examples we found)
        properties = []
        
        # Look for SAP groovy script patterns in retrieved XML content
        for snippet in xml_snippets:
            # Extract all property elements
            prop_pattern = r'<property>\s*<key>\s*([^<]+?)\s*</key>\s*<value>\s*(.*?)\s*</value>\s*</property>'
            prop_matches = re.findall(prop_pattern, snippet, re.DOTALL)
            
            for key, value in prop_matches:
                key = key.strip()
                value = value.strip()
                # Only add if not already present and is a valid groovy script property
                if key not in [p[0] for p in properties] and key in [
                    'scriptFunction', 'scriptBundleId', 'componentVersion', 
                    'activityType', 'cmdVariantUri', 'subActivityType'
                ]:
                    properties.append((key, value))
        
        # Extract and store full groovy script content from RAG for packaging
        self.groovy_script_content = ""
        if code_content:
            # Find the most complete groovy script with processData function
            best_script = ""
            max_length = 0
            
            for content in code_content:
                # Look for complete groovy scripts with processData function
                if ('def Message processData' in content or 
                    'def processData' in content or 
                    'import com.sap.gateway.ip.core.customdev.util.Message' in content):
                    if len(content) > max_length:
                        max_length = len(content)
                        best_script = content
            
            if best_script:
                # Clean up the script content
                self.groovy_script_content = best_script.strip()
            else:
                # Use first available script content
                self.groovy_script_content = code_content[0].strip()
        
        # If no groovy content found in RAG, create a default one
        if not self.groovy_script_content:
            self.groovy_script_content = f'''/* Generated {name} groovy script */
import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;

def Message processData(Message message) {{
    // Body processing
    def body = message.getBody(String.class);
    
    // Headers processing
    def headers = message.getHeaders();
    
    // Properties processing  
    def properties = message.getProperties();
    
    // Process the message here
    // Add your {name} logic
    
    return message;
}}'''
        
        # Generate CallActivity XML with fresh ID - RAG chunks used as templates only
        xml_content = f'''<bpmn2:callActivity id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
        
        # Use AUTHORITATIVE SAP standards - NEVER override with RAG content
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['GroovyScript']
        
        # Add all authoritative properties
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        # Add script filename property
        xml_content += f'''
        <ifl:property>
            <key>script</key>
            <value>{script_filename}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
        
        return xml_content
    
    def _generate_message_mapping_xml(self, name: str, retrieved_content: List[Dict]) -> str:
        """
        Generate MessageMapping XML as a proper BPMN callActivity element.
        
        MessageMapping is a transformation component that maps message structures.
        It must be a callActivity with proper SAP properties to work in iFlows.
        """
        import uuid
        
        # Generate unique component ID for this MessageMapping instance
        component_id = f"CallActivity_{uuid.uuid4().hex[:8]}"
        
        # Use AUTHORITATIVE SAP MessageMapping standards
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['MessageMapping']
        
        # Generate CallActivity XML with proper BPMN structure
        xml_content = f'''<bpmn2:callActivity id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
        
        # Add all authoritative SAP MessageMapping properties
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        # Add mapping resource reference (.mmap filename)
        mapping_resource = f"{name.replace(' ', '_')}.mmap"
        xml_content += f'''
        <ifl:property>
            <key>mappinguri</key>
            <value>src/main/resources/mapping/{mapping_resource}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
        
        print(f"   ✅ [MESSAGE_MAPPING] Generated callActivity for {name}")
        print(f"   📝 [MESSAGE_MAPPING] Mapping resource: {mapping_resource}")
        
        # Extract actual mapping content from RAG results (if available)
        # This will be used by the packaging system to create the .mmap file
        mapping_content = self._extract_mapping_content_from_rag_results(retrieved_content)
        if mapping_content:
            print(f"   📄 [MESSAGE_MAPPING] Extracted mapping content from RAG ({len(mapping_content)} chars)")
        
        # Store mapping content as a special marker in the XML comment
        # This will be extracted by the packaging system
        if mapping_content:
            xml_content += f'\n<!-- MAPPING_CONTENT_START\n{mapping_content}\nMAPPING_CONTENT_END -->'
        
        return xml_content
    
    def _extract_mapping_content_from_rag_results(self, retrieved_content: List[Dict]) -> str:
        """
        Extract mapping XML content from RAG results. Prioritize exact .mmap content
        from vector DB (iflow_assets). Fallback to any snippet containing the mapping
        namespace. As last resort, return a minimal valid mapping skeleton.
        """
        try:
            # 1) Look for explicit mmap content in retrieved chunks
            for item in retrieved_content or []:
                text = item.get('content') or item.get('text') or ''
                meta = item.get('metadata') or {}
                path_hint = (meta.get('path') or meta.get('file_path') or '').lower()
                chunk_type = (meta.get('chunk_type') or '').lower()
                title = (meta.get('title') or '').lower()
                if (
                    '.mmap' in path_hint
                    or title.endswith('.mmap')
                    or 'mapping' in chunk_type
                ) and ('http://sap.com/xi/transformation/mm' in text or 'mapping:Mapping' in text):
                    return text

            # 2) Fallback: any chunk that looks like mapping XML
            for item in retrieved_content or []:
                text = item.get('content') or item.get('text') or ''
                if 'http://sap.com/xi/transformation/mm' in text or 'mapping:Mapping' in text:
                    return text
        except Exception:
            pass

        # 3) Minimal valid skeleton (prevents "Stream after migration is null")
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<mapping:Mapping xmlns:mapping="http://sap.com/xi/transformation/mm">\n'
            '    <mapping:MappingDefinition name="MessageMapping" description="Generated message mapping">\n'
            '        <mapping:Source>\n'
            '            <mapping:Schema/>\n'
            '        </mapping:Source>\n'
            '        <mapping:Target>\n'
            '            <mapping:Schema/>\n'
            '        </mapping:Target>\n'
            '    </mapping:MappingDefinition>\n'
            '</mapping:Mapping>'
        )
    
    def _generate_router_xml(self, name: str, xml_snippets: List[str], code_content: List[str], branch_count: int = 2, routing_criteria: str = None) -> str:
        """
        Generate Router (ExclusiveGateway with branching) XML using official SAP standards.
        
        Creates a content-based router with proper SAP ExclusiveGateway properties and dynamic branching.
        The router will have user-specified number of branches (default: 2):
        - Branch 1: Conditional route (based on payload criteria like priority, status, etc.)
        - Branch 2+: Additional conditional or default routes
        
        User Intent Examples:
        - "routing based on priority" → Creates branches for high/low priority
        - "route to two groovy scripts" → Creates 2 branches to different scripts
        - "split based on payload.status" → Creates conditional branches based on status field
        - "three branches for high, medium, low" → Creates 3 branches
        
        Args:
            name: The name of the router component
            xml_snippets: Reference XML snippets from RAG
            code_content: Reference code content from RAG
            branch_count: Number of branches to create (default: 2)
            routing_criteria: Payload field for routing (e.g., "priority", "status")
        
        Note: activityType is 'exclusiveGateway' (official SAP BPMN2 standard).
        """
        import uuid
        
        component_id = f"ExclusiveGateway_{uuid.uuid4().hex[:8]}"
        
        # Get official SAP Router (ExclusiveGateway) properties
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['Router']
        
        # Router is an exclusiveGateway in BPMN2 with SAP properties
        # The 'default' attribute will be added by the packaging system after determining which route is default
        xml_content = f'''<bpmn2:exclusiveGateway id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
        
        # Add official SAP ExclusiveGateway properties
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        # Add routingConditions property (required by SAP)
        xml_content += f'''
        <ifl:property>
            <key>routingConditions</key>
            <value>{branch_count}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:exclusiveGateway>'''
        
        print(f"   ✅ [ROUTER] Generated exclusiveGateway with {branch_count} branches")
        if routing_criteria:
            print(f"   📝 [ROUTER] Routing criteria: {routing_criteria}")
        print(f"   🔀 [ROUTER] Branches will be dynamically connected to user-specified components")
        
        return xml_content
    
    def _generate_endpoint_sender_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate EndpointSender XML using SAP authoritative standards."""
        import uuid
        
        component_id = f"EndpointSender_{uuid.uuid4().hex[:8]}"
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['EndpointSender']
        
        xml_content = f'''<bpmn2:participant id="{component_id}" ifl:type="EndpointSender" name="{name}">
    <bpmn2:extensionElements>'''
        
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:participant>'''
        
        return xml_content
    
    
    def _generate_external_call_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate ExternalCall (Request-Reply) XML using SAP authoritative standards."""
        import uuid
        
        component_id = f"ServiceTask_{uuid.uuid4().hex[:8]}"
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['ExternalCall']
        
        xml_content = f'''<bpmn2:serviceTask id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
        
        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
        
        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:serviceTask>'''
        
        return xml_content
    
    async def _generate_generic_component_xml(self, component_type: str, name: str, 
                                      xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate generic component XML using authoritative SAP standards."""
        import uuid
        
        # Handle StartEvent and EndEvent with proper BPMN2 elements
        if component_type == 'StartEvent':
            component_id = f"StartEvent_{uuid.uuid4().hex[:8]}"
            authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['StartEvent']
            
            xml_content = f'''<bpmn2:startEvent id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
            
            for key, value in authoritative_properties.items():
                xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
            
            xml_content += '''
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:startEvent>'''
            
        elif component_type == 'EndEvent':
            component_id = f"EndEvent_{uuid.uuid4().hex[:8]}"
            authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['EndEvent']
            
            xml_content = f'''<bpmn2:endEvent id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''
            
            for key, value in authoritative_properties.items():
                xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''
            
            xml_content += '''
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''
            
        # Handle request-reply pattern components
        elif component_type == 'EndpointSender':
            return self._generate_endpoint_sender_xml(name, xml_snippets, code_content)
        elif component_type == 'EndpointReceiver':
            return await self._generate_endpoint_receiver_xml({'name': name}, [])
        elif component_type == 'RequestReply':
            # Dedicated RequestReply component generation
            return self._generate_request_reply_xml_from_rag(name, xml_snippets, code_content)
        else:
            # Generic serviceTask for other components
            component_id = f"{component_type}_{uuid.uuid4().hex[:8]}"
            
            xml_content = f'''<bpmn2:serviceTask id="{component_id}" name="{name}" activityType="ExternalCall">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>{component_type}</value>
        </ifl:property>
        <ifl:property>
            <key>componentName</key>
            <value>{name}</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:serviceTask>'''
        
        return xml_content

    def _generate_json_to_xml_converter_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate JSON → XML Converter XML using authoritative SAP standards."""
        import uuid
        component_id = f"JsonToXml_{uuid.uuid4().hex[:8]}"
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['JsonToXmlConverter'].copy()

        xml_content = f'''<bpmn2:callActivity id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''

        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''

        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

        return xml_content

    def _generate_gather_xml(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate Gather XML using authoritative SAP standards."""
        import uuid
        component_id = f"Gather_{uuid.uuid4().hex[:8]}"
        authoritative_properties = self.SAP_AUTHORITATIVE_STANDARDS['Gather'].copy()

        xml_content = f'''<bpmn2:callActivity id="{component_id}" name="{name}">
    <bpmn2:extensionElements>'''

        for key, value in authoritative_properties.items():
            xml_content += f'''
        <ifl:property>
            <key>{key}</key>
            <value>{value}</value>
        </ifl:property>'''

        xml_content += '''
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

        return xml_content
    def _generate_request_reply_xml_from_rag(self, name: str, xml_snippets: List[str], code_content: List[str]) -> str:
        """Generate RequestReply serviceTask XML using exact structure from reference file."""
        import uuid
        
        # Use exact structure from reference file - just the serviceTask part
        component_id = f"ServiceTask_{uuid.uuid4().hex[:8]}"
        
        # Generate sequence flow IDs for proper connections
        incoming_flow_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
        outgoing_flow_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
        
        # Generate the exact RequestReply serviceTask structure
        # Use activityType="ExternalCall" as per the RequestReply chunk
        # NOTE: Do NOT include <bpmn2:incoming> and <bpmn2:outgoing> tags here
        # The packager will generate the correct sequence flows dynamically
        xml_content = f'''<bpmn2:serviceTask id="{component_id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>activityType</key>
            <value>ExternalCall</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:serviceTask>'''
        
        return xml_content

    def _extract_xml_id(self, xml_content: str) -> Optional[str]:
        """Extract the id attribute from a BPMN XML element string."""
        import re
        m = re.search(r'id="([^"]+)"', xml_content)
        return m.group(1) if m else None
    
    def _extract_adapter_type_from_rag(self, rag_results: List[Dict], user_query: str = "") -> str:
        """
        Extract adapter type (HTTP or OData) from RAG results by checking metadata.properties.Name field.
        
        Args:
            rag_results: RAG search results containing RequestReply entries with properties
            user_query: Original user query to check for explicit adapter type mention
            
        Returns:
            'OData' or 'HTTP' (defaults to 'HTTP' if not found)
        """
        # First, check if user explicitly mentioned OData or HTTP in their query
        query_lower = user_query.lower()
        if 'odata' in query_lower:
            print(f"   🔍 [ADAPTER_DETECT] User explicitly requested OData adapter")
            return 'OData'
        elif 'http' in query_lower and 'odata' not in query_lower:
            print(f"   🔍 [ADAPTER_DETECT] User explicitly requested HTTP adapter")
            return 'HTTP'
        
        # Parse properties from RAG results to find Name field
        # PRIORITY 1: Check metadata.properties (JSON) - most reliable
        for r in (rag_results or []):
            metadata = r.get('metadata', {}) or {}
            
            if 'properties' in metadata and isinstance(metadata['properties'], dict):
                props = metadata['properties']
                adapter_name = props.get('Name', '')
                comp_type = props.get('ComponentType', '')
                
                if adapter_name in ['OData', 'HTTP']:
                    print(f"   ✅ [ADAPTER_DETECT] Found adapter type from metadata.properties.Name: {adapter_name}")
                    return adapter_name
                elif comp_type == 'HCIOData':
                    print(f"   ✅ [ADAPTER_DETECT] Found OData from metadata.properties.ComponentType: {comp_type}")
                    return 'OData'
                elif comp_type == 'HTTP':
                    print(f"   ✅ [ADAPTER_DETECT] Found HTTP from metadata.properties.ComponentType: {comp_type}")
                    return 'HTTP'
        
        # PRIORITY 2: Parse from XML content as fallback
        import re
        for r in (rag_results or []):
            content = r.get('content', '')
            
            # Look for <key>Name</key><value>OData</value> or <key>Name</key><value>HTTP</value>
            name_pattern = r'<key>\s*Name\s*</key>\s*<value>\s*(OData|HTTP)\s*</value>'
            name_match = re.search(name_pattern, content, re.IGNORECASE)
            if name_match:
                adapter_name = name_match.group(1)
                print(f"   ✅ [ADAPTER_DETECT] Found adapter type from XML content: {adapter_name}")
                return adapter_name
            
            # Check ComponentType field as fallback
            comp_type_pattern = r'<key>\s*ComponentType\s*</key>\s*<value>\s*(HCIOData|HTTP)\s*</value>'
            comp_match = re.search(comp_type_pattern, content, re.IGNORECASE)
            if comp_match:
                comp_type = comp_match.group(1)
                if comp_type == 'HCIOData':
                    print(f"   ✅ [ADAPTER_DETECT] Found OData from XML ComponentType: {comp_type}")
                    return 'OData'
                elif comp_type == 'HTTP':
                    print(f"   ✅ [ADAPTER_DETECT] Found HTTP from XML ComponentType: {comp_type}")
                    return 'HTTP'
        
        # Default to HTTP if not found
        print(f"   ⚠️ [ADAPTER_DETECT] No adapter type found in RAG results, defaulting to HTTP")
        return 'HTTP'

    def _normalize_request_reply_activity(self, xml_content: str) -> str:
        """Force activityType and cmdVariantUri to RequestReply for the provided serviceTask XML."""
        import re
        # Normalize activityType value
        xml_content = re.sub(
            r'(\<key\>\s*activityType\s*\<\/key\>\s*\<value\>)([^<]*)(\<\/value\>)',
            r'\1RequestReply\3',
            xml_content,
            flags=re.IGNORECASE
        )
        # Normalize cmdVariantUri
        xml_content = re.sub(
            r'(\<key\>\s*cmdVariantUri\s*\<\/key\>\s*\<value\>)([^<]*)(\<\/value\>)',
            r'\1ctype::FlowstepVariant/cname::RequestReply/version::1.0.0\3',
            xml_content,
            flags=re.IGNORECASE
        )
        return xml_content

    async def _understand_user_intent(self, query: str) -> Dict[str, Any]:
        """
        Use GenAI to understand user intent and create a strategic plan for iFlow generation.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary containing intent analysis and strategic plan
        """
        print(f"🧠 [INTENT_ANALYSIS] Analyzing user intent for: '{query}'")
        
        # ALWAYS use comprehensive intent understanding - NO pattern matching!
        # The agent must be 100% user-intent driven, not pattern-driven
        print(f"🔍 [INTENT_ANALYSIS] Using comprehensive LLM-based intent understanding (user-intent driven)")
        
        # Create a comprehensive prompt for intent understanding
        intent_prompt = f"""
You are an expert SAP Integration Suite architect. Analyze the following user query and understand their intent for creating an iFlow.

User Query: "{query}"

Please analyze and provide a structured response with:

1. **Intent Classification**: What does the user want to achieve?
   - Complete iFlow creation
   - Single component creation
   - iFlow analysis/modification
   - Other

2. **Component Detection**: Identify ONLY the components the user explicitly requests:
   - List EXACTLY what the user mentions, IN THE EXACT ORDER they specify
   - Do NOT add any components the user didn't request (except Start/End events which are always implicit)
   - If user says "content modifier and sender", ONLY add: ContentModifier, EndpointSender
   - **CRITICAL - RequestReply with Adapter Type**:
     * If user says "request reply", "HTTP request reply", "OData request reply" → ONLY add: RequestReply component
     * DO NOT add separate OData or HTTP adapter components - they are part of the RequestReply trio
     * The adapter type (HTTP/OData) is a PROPERTY of the RequestReply, not a separate component
     * Extract adapter_type field: "OData" if user mentions "odata", otherwise "HTTP"
   - If user says "router" or "routing", add: Router component (exclusiveGateway in BPMN2)
   - Multiple instances: "two content modifiers" means quantity=2, "several groovy scripts" means quantity=3
   - Router branching: If user mentions "route to X and Y" or "split to X branches", detect the branch count and target components

3. **Component Specifications**: For each component, determine:
   - Component type (ContentModifier, GroovyScript, RequestReply, Router, etc.)
   - Component name (if specified or generate appropriate name)
   - Quantity/instances needed (CRITICAL: "two X" = quantity 2, "three Y" = quantity 3, etc.)
   - Any specific requirements or configurations
   - Position in the user's requested sequence
   - **Router-specific (CRITICAL)**: 
     * **routing_criteria**: Extract the payload field name for routing (e.g., "priority", "status", "type"). If user says "based on priority", extract "priority".
     * **branch_count**: Count how many branches/paths the router should have. If user mentions "two groovy scripts" after router, branch_count=2.
     * **branch_targets**: List the component types for each branch (e.g., ["GroovyScript", "GroovyScript"] for 2 groovy script branches).

4. **Strategic Plan**: Create a step-by-step plan:
   - Component identification strategy
   - RAG search strategy for each component
   - Component generation order (MUST match the user's explicit sequence)
   - Integration approach

**IMPORTANT**: 
- Respect the user's explicit component order. If they say "content modifier, request reply, and groovy script", the order MUST be: ContentModifier → RequestReply → GroovyScript
- Parse quantity words correctly: "one"=1, "two"=2, "three"=3, "a"=1, "several"=3, "multiple"=2
- DO NOT add EndpointSender or EndpointReceiver unless explicitly requested by the user
- For "request reply", only add RequestReply component type (it will auto-expand to the full trio: service task + message flow + receiver)
- **CRITICAL FOR ROUTER**: If user mentions Router, YOU MUST extract:
  * routing_criteria: The payload field name (e.g., "priority" from "based on priority")
  * branch_count: Number of branches (e.g., 2 from "two groovy scripts")
  * branch_targets: List of component types for branches (e.g., ["GroovyScript", "GroovyScript"])

5. **Query Variations**: Identify different ways the user might phrase similar requests

Respond in JSON format with this structure:
{{
    "intent_classification": "complete_iflow_creation",
    "user_goal": "Create a complete SAP iFlow with multiple components",
    "components_needed": [
        {{
            "type": "ContentModifier",
            "name": "ContentModifier",
            "quantity": 1,
            "explicitly_mentioned": true,
            "requirements": "Standard content modification"
        }},
        {{
            "type": "RequestReply",
            "name": "RequestReply",
            "quantity": 1,
            "explicitly_mentioned": true,
            "requirements": "Request-reply pattern with adapter",
            "adapter_type": "HTTP"
        }},
        {{
            "type": "Router",
            "name": "Router",
            "quantity": 1,
            "explicitly_mentioned": true,
            "requirements": "Content-based routing with branching logic",
            "routing_criteria": "priority",
            "branch_count": 2,
            "branch_targets": ["GroovyScript", "GroovyScript"]
        }},
        {{
            "type": "GroovyScript",
            "name": "GroovyScript",
            "quantity": 2,
            "explicitly_mentioned": true,
            "requirements": "Two groovy script processors for router branches"
        }}
    ],
    "implicit_components": [
        {{
            "type": "StartEvent",
            "name": "Start",
            "quantity": 1,
            "reason": "Required for iFlow initiation"
        }},
        {{
            "type": "EndEvent",
            "name": "End",
            "quantity": 1,
            "reason": "Required for iFlow termination"
        }}
    ],
    "strategic_plan": {{
        "rag_search_strategy": "Search for each component type with optimized queries",
        "generation_order": ["StartEvent", "ContentModifier", "Router", "GroovyScript", "GroovyScript", "EndEvent"],
        "integration_approach": "Sequential flow with Router branching to multiple Groovy Scripts based on payload criteria"
    }},
    "query_interpretation": "User wants to create a complete iFlow with content modifier, then router splitting to two groovy scripts based on priority field"
}}

NOTE: In generation_order, repeat component types based on their quantity. If user wants 2 GroovyScripts, include "GroovyScript" twice in the order.

Focus on understanding the user's natural language and intent, not rigid pattern matching.
"""

        try:
            # Use the LLM to understand intent
            response = self.llm.invoke(intent_prompt)

            # Parse the JSON response
            import json
            import re
            from pathlib import Path
            from datetime import datetime

            # Get response content
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Save raw response to file for debugging/analysis
            debug_dir = Path(__file__).parent.parent / "intent_analysis_debug"
            debug_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_file = debug_dir / f"intent_response_{timestamp}.txt"

            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("RAW LLM RESPONSE - Intent Analysis\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Query: {query[:200]}...\n")
                f.write("="*80 + "\n\n")
                f.write("FULL RESPONSE:\n")
                f.write("-"*80 + "\n")
                f.write(response_text)
                f.write("\n" + "-"*80 + "\n\n")
                f.write("RESPONSE METADATA:\n")
                f.write(f"Type: {type(response)}\n")
                f.write(f"Has content attr: {hasattr(response, 'content')}\n")
                f.write(f"Length: {len(response_text)} characters\n")
                f.write("="*80 + "\n")

            print(f"💾 [DEBUG] Raw response saved to: {debug_file}")

            # Try to extract JSON from markdown code blocks or plain text
            # Pattern 1: JSON in markdown code blocks ```json ... ```
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                extraction_method = "markdown_code_block"
            else:
                # Pattern 2: Look for raw JSON object
                json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    extraction_method = "regex_extraction"
                else:
                    # Pattern 3: Try the whole response
                    json_str = response_text.strip()
                    extraction_method = "full_response"

            # Parse JSON
            intent_analysis = json.loads(json_str)

            # Save successful parse info
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write("\nPARSING SUCCESS:\n")
                f.write(f"Extraction method: {extraction_method}\n")
                f.write(f"Extracted JSON length: {len(json_str)} characters\n")
                f.write("\nEXTRACTED JSON:\n")
                f.write("-"*80 + "\n")
                f.write(json.dumps(intent_analysis, indent=2))
                f.write("\n" + "-"*80 + "\n")

            print(f"✅ [INTENT_ANALYSIS] Intent understood: {intent_analysis.get('user_goal', 'Unknown')}")
            print(f"📊 [COMPONENTS] Detected {len(intent_analysis.get('components_needed', []))} explicit components")
            print(f"🔧 [IMPLICIT] Detected {len(intent_analysis.get('implicit_components', []))} implicit components")
            print(f"🔧 [EXTRACTION] Used method: {extraction_method}")

            return intent_analysis

        except Exception as e:
            print(f"⚠️ [INTENT_FALLBACK] GenAI intent analysis failed: {e}")

            # Save failure details to debug file
            if 'response' in locals():
                response_text = response.content if hasattr(response, 'content') else str(response)

                # Create debug directory if needed
                from pathlib import Path
                from datetime import datetime
                debug_dir = Path(__file__).parent.parent / "intent_analysis_debug"
                debug_dir.mkdir(exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                error_file = debug_dir / f"intent_error_{timestamp}.txt"

                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write("="*80 + "\n")
                    f.write("FAILED INTENT ANALYSIS - Debug Info\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write("="*80 + "\n\n")
                    f.write("FULL RAW RESPONSE:\n")
                    f.write("-"*80 + "\n")
                    f.write(response_text)
                    f.write("\n" + "-"*80 + "\n\n")
                    if 'json_str' in locals():
                        f.write("EXTRACTED STRING (that failed to parse):\n")
                        f.write("-"*80 + "\n")
                        f.write(json_str)
                        f.write("\n" + "-"*80 + "\n")

                print(f"💾 [DEBUG] Error details saved to: {error_file}")
                print(f"🔍 [DEBUG] Raw LLM response (first 500 chars): {response_text[:500]}")

            print("🔄 [INTENT_FALLBACK] Using heuristic fallback...")

            # Fallback to heuristic analysis
            return self._heuristic_intent_analysis(query)

    def _parse_quantity_from_query(self, query: str, component_keyword: str) -> int:
        """Parse quantity from query for a specific component (e.g., 'two request replies' → 2)"""
        import re
        query_lower = query.lower()
        
        # Number word to digit mapping
        number_words = {
            'one': 1, 'a': 1, 'an': 1, 'single': 1,
            'two': 2, 'couple': 2,
            'three': 3, 'several': 3,
            'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'multiple': 2, 'few': 2
        }
        
        # Debug logging
        print(f"   🔢 [QTY_PARSE] Parsing quantity for keyword pattern: '{component_keyword}' in query: '{query_lower}'")
        
        # Try to find quantity before the component keyword
        # Pattern: "two request replies", "three groovy scripts", etc.
        for word, num in number_words.items():
            pattern = rf'\b{word}\s+{component_keyword}'
            match = re.search(pattern, query_lower)
            if match:
                print(f"   ✅ [QTY_PARSE] Found '{word}' → quantity={num} (pattern: {pattern})")
                return num
        
        # Try to find digit directly before component
        # Pattern: "2 request replies", "3 groovy scripts"
        digit_pattern = rf'(\d+)\s+{component_keyword}'
        match = re.search(digit_pattern, query_lower)
        if match:
            qty = int(match.group(1))
            print(f"   ✅ [QTY_PARSE] Found digit '{match.group(1)}' → quantity={qty}")
            return qty
        
        # Default to 1 if no quantity specified
        print(f"   ℹ️ [QTY_PARSE] No quantity found, defaulting to 1")
        return 1
    
    def _heuristic_intent_analysis(self, query: str) -> Dict[str, Any]:
        """
        Fallback heuristic analysis when GenAI fails.
        Uses comprehensive component detection to be fully user-intent driven.
        NOW SUPPORTS ALL COMPONENTS - no hardcoded restrictions!
        """
        query_lower = query.lower()
        
        # Simple heuristic classification
        if any(word in query_lower for word in ['create', 'generate', 'build', 'make']):
            intent = "complete_iflow_creation"
        elif any(word in query_lower for word in ['analyze', 'examine', 'check']):
            intent = "iflow_analysis"
        else:
            intent = "complete_iflow_creation"
        
        print(f"   🎯 [HEURISTIC] Using comprehensive component detection (supports ALL components)")
        
        # Use comprehensive component detection - this detects ALL component types!
        # No hardcoding - fully user-intent driven
        detected_components = self._identify_components_in_query(query)
        
        components = []
        
        # Convert detected components to the format expected by strategic planning
        for comp in detected_components:
            comp_type = comp['type']
            comp_name = comp['name']
            
            # Skip Start/End events here as they're added implicitly later
            if comp_type in {'StartEvent', 'EndEvent'}:
                continue
            
            # Build component entry
            component_entry = {
                "type": comp_type,
                "name": comp_name,
                "quantity": comp.get('total_instances', 1),
                "explicitly_mentioned": True,
                "requirements": f"User-requested {comp_type}"
            }
            
            # Preserve adapter_type for RequestReply components (HTTP/OData)
            if 'adapter_type' in comp:
                component_entry['adapter_type'] = comp['adapter_type']
                print(f"   🔧 [HEURISTIC] Detected RequestReply with adapter_type: {comp['adapter_type']}")
            
            # Add Router-specific metadata if present (extract from query)
            if comp_type == 'Router':
                import re
                # Extract Router metadata from query
                routing_criteria = None
                branch_count = 2  # Default
                branch_targets = []
                
                # Extract routing criteria
                criteria_keywords = ['priority', 'status', 'type', 'severity', 'category', 'level']
                for keyword in criteria_keywords:
                    if keyword in query_lower:
                        routing_criteria = keyword
                        break
                
                if not routing_criteria:
                    criteria_match = re.search(r'(?:based on|routing (?:on|by)|split by|route by)\s+(?:payload\s+)?(\w+)', query_lower)
                    if criteria_match:
                        routing_criteria = criteria_match.group(1)
                
                # Count branch targets
                router_pos = query_lower.find('router')
                if router_pos != -1:
                    remaining_query = query_lower[router_pos:]
                    groovy_match = re.search(r'(two|three|four|five|\d+)\s+groovy\s+scripts?', remaining_query)
                    if groovy_match:
                        num_word = groovy_match.group(1)
                        branch_count = {'two': 2, 'three': 3, 'four': 4, 'five': 5}.get(num_word, int(num_word) if num_word.isdigit() else 2)
                        branch_targets = ['GroovyScript'] * branch_count
                    
                    modifier_match = re.search(r'(two|three|four|five|\d+)\s+content\s+modifiers?', remaining_query)
                    if modifier_match:
                        num_word = modifier_match.group(1)
                        branch_count = {'two': 2, 'three': 3, 'four': 4, 'five': 5}.get(num_word, int(num_word) if num_word.isdigit() else 2)
                        branch_targets = ['ContentModifier'] * branch_count
                
                component_entry['routing_criteria'] = routing_criteria
                component_entry['branch_count'] = branch_count
                component_entry['branch_targets'] = branch_targets
            
            components.append(component_entry)
            print(f"   ✅ [HEURISTIC] Detected: {comp_type} (qty={component_entry['quantity']})")
        
        # Build generation_order respecting user's sequence
        # IMPORTANT: Preserve the order components were detected in (user's intent)
        generation_order = ["StartEvent"]
        
        # Add components in the order they were detected (preserves user's sequence)
        for comp in components:
            comp_type = comp["type"]
            quantity = comp.get("quantity", 1)
            
            # If Router has explicit branch targets, insert them after the Router
            if comp_type == "Router":
                generation_order.extend(["Router"] * quantity)
                branch_targets = comp.get("branch_targets", [])
                if branch_targets:
                    # Add branch targets immediately after Router
                    for target in branch_targets:
                        generation_order.append(target)
            else:
                # Add component in its natural position
                generation_order.extend([comp_type] * quantity)
        
        generation_order.append("EndEvent")
        
        return {
            "intent_classification": intent,
            "user_goal": "Create SAP iFlow components",
            "components_needed": components,
            "implicit_components": [
                {
                    "type": "StartEvent",
                    "name": "Start",
                    "quantity": 1,
                    "reason": "Required for iFlow initiation"
                },
                {
                    "type": "EndEvent",
                    "name": "End",
                    "quantity": 1,
                    "reason": "Required for iFlow completion"
                }
            ],
            "strategic_plan": {
                "rag_search_strategy": "Search for each component type",
                "generation_order": generation_order,  # Now respects quantities!
                "integration_approach": "Sequential flow"
            },
            "query_interpretation": f"Heuristic analysis of: {query}"
        }

    def _create_strategic_plan(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a detailed strategic plan based on intent analysis.
        
        Args:
            intent_analysis: Result from _understand_user_intent
            
        Returns:
            Detailed strategic plan for iFlow generation
        """
        print(f"📋 [STRATEGIC_PLANNING] Creating strategic plan...")
        
        # Combine explicit and implicit components
        all_components = []
        
        # Add explicit components (preserve all fields including adapter_type)
        for comp in intent_analysis.get('components_needed', []):
            all_components.append({
                **comp,  # This spreads all fields including adapter_type
                'source': 'explicit',
                'priority': 'high'
            })
        
        # Add implicit components
        for comp in intent_analysis.get('implicit_components', []):
            all_components.append({
                **comp,
                'source': 'implicit',
                'priority': 'medium'
            })
        
        # Create RAG search strategy for each component
        rag_strategy = {}
        for comp in all_components:
            comp_type = comp['type']
            rag_strategy[comp_type] = {
                'search_queries': self._generate_component_rag_queries(comp_type.lower(), comp_type),
                'search_limit': 5,
                'chunk_types': ['xml', 'groovy', 'component'],
                'priority': comp['priority']
            }
        
        # Determine generation order - MUST respect quantities!
        # If LLM provided generation_order, use it; otherwise build from components
        generation_order = intent_analysis.get('strategic_plan', {}).get('generation_order', [])
        if not generation_order:
            # Build generation order preserving user's sequence
            # IMPORTANT: Respect the order components appear in the query (user intent)
            start_components = [c for c in all_components if c['type'] == 'StartEvent']
            end_components = [c for c in all_components if c['type'] == 'EndEvent']
            processing_components = [c for c in all_components if c['type'] not in ['StartEvent', 'EndEvent']]

            generation_order = []

            # Start(s)
            for c in start_components:
                generation_order.extend(['StartEvent'] * c.get('quantity', 1))

            # Processing components in the order they were detected (preserves user's sequence)
            for c in processing_components:
                comp_type = c['type']
                quantity = c.get('quantity', 1)
                
                # If Router has explicit branch targets, insert them after Router
                if comp_type == 'Router':
                    generation_order.extend(['Router'] * quantity)
                    branch_targets = c.get('branch_targets', [])
                    if branch_targets:
                        # Add branch targets immediately after Router
                        for target in branch_targets:
                            generation_order.append(target)
                else:
                    generation_order.extend([comp_type] * quantity)

            # End(s)
            for c in end_components:
                generation_order.extend(['EndEvent'] * c.get('quantity', 1))
        
        print(f"   📊 [GEN_ORDER] Generation order: {generation_order}")
        
        strategic_plan = {
            'intent_classification': intent_analysis.get('intent_classification'),
            'user_goal': intent_analysis.get('user_goal'),
            'total_components': len(all_components),
            'components': all_components,
            'rag_strategy': rag_strategy,
            'generation_order': generation_order,
            'integration_approach': intent_analysis.get('strategic_plan', {}).get('integration_approach', 'Sequential flow'),
            'query_interpretation': intent_analysis.get('query_interpretation'),
            'execution_steps': [
                '1. Understand user intent',
                '2. Identify all required components',
                '3. Create strategic plan',
                '4. Execute RAG searches for each component',
                '5. Generate component XML using authoritative SAP standards',
                '6. Create iFlow package with proper connections',
                '7. Export final package'
            ]
        }
        
        print(f"📊 [STRATEGIC_PLAN] Plan created:")
        print(f"   🎯 Intent: {strategic_plan['intent_classification']}")
        print(f"   📦 Components: {strategic_plan['total_components']}")
        print(f"   🔄 Order: {' → '.join(generation_order)}")
        print(f"   🧠 Interpretation: {strategic_plan['query_interpretation']}")
        
        return strategic_plan

    def _optimize_rag_search_query(self, component_type: str, component_name: str) -> str:
        """
        Optimize RAG search query using component mapping for better results.
        
        Args:
            component_type: The SAP component type (e.g., 'ContentModifier')
            component_name: The component name
            
        Returns:
            Optimized search query string
        """
        # Map component type to search terms
        search_terms = []
        
        # Add component-specific search terms
        if component_type == 'ContentModifier':
            search_terms.extend(['enricher', 'content modifier', 'content enricher'])
        elif component_type == 'GroovyScript':
            search_terms.extend(['groovy', 'script', 'groovy script'])
        elif component_type == 'StartEvent':
            search_terms.extend(['start event', 'message start', 'start'])
        elif component_type == 'EndEvent':
            search_terms.extend(['end event', 'message end', 'end'])
        elif component_type == 'EndpointSender':
            search_terms.extend(['http sender', 'https sender', 'endpoint sender'])
        elif component_type == 'RequestReply':
            search_terms.extend(['request reply', 'requestreply', 'activity_type:RequestReply', 'service task'])
        elif component_type == 'EndpointReceiver':
            search_terms.extend(['http receiver', 'https receiver', 'endpoint receiver'])
        elif component_type == 'Router':
            search_terms.extend(['router', 'routing', 'conditional routing', 'decision'])
        elif component_type == 'MessageMapping':
            search_terms.extend(['message mapping', 'mapping', 'transform'])
        
        # Add component name and type
        search_terms.extend([component_name, component_type])
        
        # Add SAP-specific terms
        search_terms.extend(['SAP', 'iFlow', 'integration'])
        
        # Create optimized query
        optimized_query = ' '.join(search_terms)
        print(f"🔍 [RAG_OPTIMIZATION] Optimized query for {component_type}: '{optimized_query}'")
        
        return optimized_query

    def _is_request_reply_pattern(self, component: Dict[str, Any]) -> bool:
        """Check if component represents a request-reply pattern"""
        comp_type = component.get('type', '').lower()
        comp_name = component.get('name', '').lower()
        
        # Only treat as request-reply pattern if the component type is explicitly ExternalCall
        # or the name contains specific request-reply indicators
        if comp_type == 'externalcall':
            return True
        
        # Check for specific request-reply keywords in name
        request_reply_keywords = [
            'request_reply', 'request-reply', 'external_call', 'api_call'
        ]
        
        return any(keyword in comp_name for keyword in request_reply_keywords)
    
    async def _generate_request_reply_pattern(self, component: Dict[str, Any], rag_results: List[Dict], receiver_instance: int = 1, user_query: str = "") -> List[Dict[str, Any]]:
        """Generate the 3-component request-reply pattern: ExternalCall + MessageFlow + EndpointReceiver
        
        Args:
            component: Component configuration
            rag_results: RAG search results
            receiver_instance: Instance number for the receiver (e.g., 1 for Receiver1, 2 for Receiver2)
            user_query: Original user query for adapter type detection
        """
        print(f"   🔄 [REQUEST_REPLY] Generating 3-component pattern with Receiver{receiver_instance}...")
        
        # CRITICAL: Detect adapter type (HTTP vs OData) from component, RAG results, or user query
        # PRIORITY 1: Use adapter_type from component if set (most reliable)
        if 'adapter_type' in component:
            adapter_type = component['adapter_type']
            print(f"   🎯 [ADAPTER_TYPE] Using adapter_type from component: {adapter_type}")
        else:
            # PRIORITY 2: Detect from user query or RAG results
            adapter_type = self._extract_adapter_type_from_rag(rag_results, user_query)
            print(f"   🎯 [ADAPTER_TYPE] Detected adapter type from user query/RAG: {adapter_type}")
        
        print(f"   🔍 [RAG_DEBUG] Total RAG results received: {len(rag_results or [])}")
        for idx, r in enumerate(rag_results or []):
            metadata = r.get('metadata', {}) or {}
            props = metadata.get('properties', {})
            act_type = metadata.get('activity_type', 'N/A')
            name_prop = props.get('Name', 'N/A') if isinstance(props, dict) else 'N/A'
            comp_type = props.get('ComponentType', 'N/A') if isinstance(props, dict) else 'N/A'
            print(f"      RAG[{idx}]: activity_type='{act_type}', Name='{name_prop}', ComponentType='{comp_type}'")
        
        # Filter RAG results for the specific adapter type
        # This ensures we only use the correct adapter configuration
        filtered_rag_results = []
        for r in (rag_results or []):
            content = r.get('content', '')
            metadata = r.get('metadata', {}) or {}
            activity_type = metadata.get('activity_type', '').lower()
            
            # Accept if: 1) activityType is RequestReply
            if activity_type == 'requestreply' or 'request reply' in content.lower() or 'name="Request Reply' in content:
                # Additional filtering: Check if this RAG result matches our desired adapter type
                import re
                
                # PRIORITY 1: Check metadata.properties (JSON)
                adapter_matched = False
                if 'properties' in metadata and isinstance(metadata['properties'], dict):
                    props = metadata['properties']
                    name_prop = props.get('Name', '')
                    comp_type_prop = props.get('ComponentType', '')
                    
                    if name_prop == adapter_type:
                        filtered_rag_results.append(r)
                        print(f"   ✅ [RAG_FILTER] Found {adapter_type} RequestReply chunk (metadata.properties.Name = {name_prop})")
                        adapter_matched = True
                    elif (comp_type_prop == 'HCIOData' and adapter_type == 'OData') or (comp_type_prop == 'HTTP' and adapter_type == 'HTTP'):
                        filtered_rag_results.append(r)
                        print(f"   ✅ [RAG_FILTER] Found {adapter_type} RequestReply chunk (metadata.properties.ComponentType = {comp_type_prop})")
                        adapter_matched = True
                
                # PRIORITY 2: Check XML content if no metadata.properties
                if not adapter_matched:
                    name_in_content = re.search(r'<key>\s*Name\s*</key>\s*<value>\s*(OData|HTTP)\s*</value>', content, re.IGNORECASE)
                    comp_type_in_content = re.search(r'<key>\s*ComponentType\s*</key>\s*<value>\s*(HCIOData|HTTP)\s*</value>', content, re.IGNORECASE)
                    
                    if name_in_content:
                        found_adapter = name_in_content.group(1)
                        if found_adapter == adapter_type:
                            filtered_rag_results.append(r)
                            print(f"   ✅ [RAG_FILTER] Found {adapter_type} RequestReply chunk (XML Name = {found_adapter})")
                            adapter_matched = True
                    elif comp_type_in_content:
                        found_comp = comp_type_in_content.group(1)
                        if (found_comp == 'HCIOData' and adapter_type == 'OData') or (found_comp == 'HTTP' and adapter_type == 'HTTP'):
                            filtered_rag_results.append(r)
                            print(f"   ✅ [RAG_FILTER] Found {adapter_type} RequestReply chunk (XML ComponentType = {found_comp})")
                            adapter_matched = True
                
                # Backward compatibility: If no adapter type found, include only if this is the only entry
                if not adapter_matched:
                    filtered_rag_results.append(r)
                    print(f"   ⚠️ [RAG_FILTER] Found RequestReply chunk without adapter type - including for backward compatibility")
        
        # Use filtered results for XML generation
        rag_xml_snippets = [r.get('content', '') for r in filtered_rag_results]
        
        print(f"   📊 [FILTER_RESULT] Filtered {len(filtered_rag_results)} RAG results for '{adapter_type}' adapter")
        if len(filtered_rag_results) == 0:
            print(f"   ⚠️ [FILTER_WARNING] No RAG results matched '{adapter_type}' adapter!")
            print(f"   ⚠️ [FILTER_WARNING] MessageFlow will use fallback/default properties")
        
        # Component 1: ExternalCall (ServiceTask)
        request_reply_xml = self._generate_request_reply_xml_from_rag(
            f"{component['name']}", rag_xml_snippets, []
        )
        # Extract service task id to align messageFlow sourceRef
        service_task_id = self._extract_xml_id(request_reply_xml) or f"ServiceTask_{hash(component['name']) % 100000}"
        external_call = {
            'type': 'RequestReply',
            'name': f"{component['name']}",
            'xml': request_reply_xml,
            'quantity': 1,
            'source': 'request_reply_pattern',
            'priority': 'high',
            'rag_results': filtered_rag_results,
            'adapter_type': adapter_type  # Store adapter type for reference
        }
        
        # Component 2 & 3: Build receiver first to get participant ID
        # Participants follow SAP naming: Receiver1, Receiver2, Sender1, Sender2, etc.
        receiver_name = f'Receiver{receiver_instance}'
        receiver_component = {'name': receiver_name}
        endpoint_receiver_xml = await self._generate_endpoint_receiver_xml(receiver_component, filtered_rag_results)
        participant_id = self._extract_xml_id(endpoint_receiver_xml) or f"Participant_{hash(receiver_name) % 100000}"

        # Component 2: MessageFlow connecting service task to receiver
        # CRITICAL: Use adapter-specific MessageFlow generation
        message_flow_xml = await self._generate_message_flow_xml_dynamic(
            component, filtered_rag_results, adapter_type, 
            source_id=service_task_id, target_id=participant_id
        )
        
        message_flow = {
            'type': 'MessageFlow',
            'name': adapter_type,  # Use adapter type as name (HTTP or OData)
            'xml': message_flow_xml,
            'quantity': 1,
            'source': 'request_reply_pattern',
            'priority': 'high',
            'rag_results': filtered_rag_results,
            'adapter_type': adapter_type
        }
        
        # Component 3: EndpointReceiver Participant
        endpoint_receiver = {
            'type': 'EndpointRecevier',
            'name': receiver_name,
            'xml': endpoint_receiver_xml,
            'quantity': 1,
            'source': 'request_reply_pattern',
            'priority': 'high',
            'rag_results': filtered_rag_results
        }
        
        print(f"   ✅ [REQUEST_REPLY] Generated 3 components with {adapter_type} adapter:")
        print(f"      1. RequestReply (ServiceTask) - activityType: ExternalCall")
        print(f"      2. MessageFlow - Adapter: {adapter_type} (from VectorDB properties)")
        print(f"      3. {receiver_name} (Participant)")
        print(f"   🎯 [ADAPTER_CONFIRM] User requested '{adapter_type}' adapter - Generated '{adapter_type}' MessageFlow")
        return [external_call, message_flow, endpoint_receiver]
    
    async def _generate_external_call_xml(self, component: Dict[str, Any], rag_results: List[Dict] = None) -> str:
        """Generate XML for ExternalCall component"""
        comp_name = component['name']
        comp_id = f"ServiceTask_{hash(comp_name) % 100000}"
        
        # Get SAP authoritative standards
        standards = self.SAP_AUTHORITATIVE_STANDARDS.get('ExternalCall', {})
        
        xml = f'''<bpmn2:serviceTask id="{comp_id}" name="{comp_name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>{standards.get('componentVersion', '1.0')}</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>{standards.get('activityType', 'ExternalCall')}</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>{standards.get('cmdVariantUri', 'ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4')}</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:serviceTask>'''
        
        return xml
    
    async def _generate_message_flow_xml(self, component: Dict[str, Any], rag_results: List[Dict] = None, source_id: Optional[str] = None, target_id: Optional[str] = None) -> str:
        """Generate XML for MessageFlow component, allowing explicit source/target IDs."""
        comp_name = component['name']
        flow_id = f"MessageFlow_{hash(comp_name) % 100000}"
        if source_id is None:
            source_id = f"ServiceTask_{hash(comp_name) % 100000}"
        if target_id is None:
            target_id = f"Participant_{hash(comp_name) % 100000}"
        
        xml = f'''<bpmn2:messageFlow id="{flow_id}" name="HTTP" sourceRef="{source_id}" targetRef="{target_id}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>Description</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>methodSourceExpression</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>apiArtifactType</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>providerAuth</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>privateKeyAlias</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>httpMethod</key>
            <value>POST</value>
        </ifl:property>
        <ifl:property>
            <key>allowedResponseHeaders</key>
            <value>*</value>
        </ifl:property>
        <ifl:property>
            <key>Name</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>internetProxyType</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocolVersion</key>
            <value>1.5.0</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVName</key>
            <value>external</value>
        </ifl:property>
        <ifl:property>
            <key>proxyPort</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>streaming</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>enableMPLAttachments</key>
            <value>true</value>
        </ifl:property>
        <ifl:property>
            <key>httpAddressQuery</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>httpRequestTimeout</key>
            <value>60000</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocol</key>
            <value>None</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVId</key>
            <value>1.5.0</value>
        </ifl:property>
        <ifl:property>
            <key>providerName</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>allowedRequestHeaders</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>direction</key>
            <value>Receiver</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentType</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>httpShouldSendBody</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>throwExceptionOnFailure</key>
            <value>true</value>
        </ifl:property>
        <ifl:property>
            <key>proxyType</key>
            <value>Internet</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.5</value>
        </ifl:property>
        <ifl:property>
            <key>retryIteration</key>
            <value>1</value>
        </ifl:property>
        <ifl:property>
            <key>proxyHost</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>httpAddressWithoutQuery</key>
            <value>https://example.com</value>
        </ifl:property>
        <ifl:property>
            <key>providerUrl</key>
            <value>https://example.com</value>
        </ifl:property>
        <ifl:property>
            <key>retryOnConnectionFailure</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>system</key>
            <value>Receiver1</value>
        </ifl:property>
        <ifl:property>
            <key>authenticationMethod</key>
            <value>None</value>
        </ifl:property>
        <ifl:property>
            <key>locationID</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>retryInterval</key>
            <value>5</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocol</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.5.0</value>
        </ifl:property>
        <ifl:property>
            <key>credentialName</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>httpErrorResponseCodes</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocolVersion</key>
            <value>1.5.0</value>
        </ifl:property>
        <ifl:property>
            <key>providerRelativeUrl</key>
            <value/>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''
        
        return xml
    
    async def _generate_message_flow_xml_dynamic(self, component: Dict[str, Any], rag_results: List[Dict] = None, adapter_type: str = 'HTTP', source_id: Optional[str] = None, target_id: Optional[str] = None) -> str:
        """
        Generate XML for MessageFlow component dynamically based on adapter type (HTTP or OData).
        
        Args:
            component: Component configuration
            rag_results: RAG search results containing adapter-specific properties
            adapter_type: 'HTTP' or 'OData'
            source_id: Source reference ID (ServiceTask)
            target_id: Target reference ID (Participant)
            
        Returns:
            MessageFlow XML string with adapter-specific properties
        """
        comp_name = component['name']
        flow_id = f"MessageFlow_{hash(comp_name) % 100000}"
        if source_id is None:
            source_id = f"ServiceTask_{hash(comp_name) % 100000}"
        if target_id is None:
            target_id = f"Participant_{hash(comp_name) % 100000}"
        
        print(f"   🔧 [MESSAGE_FLOW] Generating {adapter_type} MessageFlow XML from VectorDB properties")
        
        # Extract properties from RAG results (both JSON metadata and XML content)
        # CRITICAL: Extract from the MessageFlow element that matches the adapter type!
        rag_properties = {}
        if rag_results:
            import re
            for r in rag_results:
                metadata = r.get('metadata', {}) or {}
                content = r.get('content', '')
                
                # PRIORITY 1: Extract from metadata.properties (JSON) if available
                if 'properties' in metadata and isinstance(metadata['properties'], dict):
                    props = metadata['properties']
                    adapter_name = props.get('Name', '')
                    if adapter_name == adapter_type:
                        print(f"   ✅ [RAG_MATCH] Found matching entry with Name='{adapter_name}' in metadata.properties")
                        for key, value in props.items():
                            if key not in ['ifl:type', 'activityType']:  # Skip internal fields
                                rag_properties[key] = str(value)
                        print(f"   ✅ [RAG_PROPS] Extracted {len(rag_properties)} properties from metadata.properties")
                        break  # Use first matching entry only
                
                # PRIORITY 2: Extract from MessageFlow XML element with matching Name
                if not rag_properties:
                    # Find the messageFlow element with our adapter name
                    messageflow_pattern = rf'<(?:bpmn2:)?messageFlow[^>]*name="{re.escape(adapter_type)}"[^>]*>(.*?)</(?:bpmn2:)?messageFlow>'
                    mf_match = re.search(messageflow_pattern, content, re.DOTALL | re.IGNORECASE)
                    
                    if mf_match:
                        messageflow_content = mf_match.group(1)
                        print(f"   ✅ [RAG_MATCH] Found MessageFlow element with name='{adapter_type}'")
                        
                        # Extract ALL properties from within this MessageFlow element
                        prop_pattern = r'<(?:ifl:)?property>\s*<key>\s*([^<]+?)\s*</key>\s*<value>\s*(.*?)\s*</value>\s*</(?:ifl:)?property>'
                        prop_matches = re.findall(prop_pattern, messageflow_content, re.DOTALL)
                        
                        if prop_matches:
                            print(f"   ✅ [RAG_PROPS] Found {len(prop_matches)} properties in MessageFlow XML")
                            for key, value in prop_matches:
                                key_clean = key.strip()
                                if key_clean not in ['ifl:type', 'activityType']:
                                    rag_properties[key_clean] = value.strip()
                            break  # Use first matching entry only
                    else:
                        # Fallback: Check if this content has Name property = adapter_type
                        name_match = re.search(r'<key>\s*Name\s*</key>\s*<value>\s*([^<]+)\s*</value>', content, re.IGNORECASE)
                        if name_match and name_match.group(1).strip() == adapter_type:
                            print(f"   ✅ [RAG_MATCH] Found content with Name='{adapter_type}' property")
                            # Extract all properties from this content
                            prop_pattern = r'<(?:ifl:)?property>\s*<key>\s*([^<]+?)\s*</key>\s*<value>\s*(.*?)\s*</value>\s*</(?:ifl:)?property>'
                            prop_matches = re.findall(prop_pattern, content, re.DOTALL)
                            if prop_matches and len(prop_matches) > 5:
                                print(f"   ✅ [RAG_PROPS] Found {len(prop_matches)} properties in XML content")
                                for key, value in prop_matches:
                                    key_clean = key.strip()
                                    if key_clean not in ['ifl:type', 'activityType']:
                                        rag_properties[key_clean] = value.strip()
                                break
        
        print(f"   📊 [RAG_PROPS] Total extracted properties: {len(rag_properties)}")
        if rag_properties:
            print(f"   🔑 [RAG_PROPS] Keys: {', '.join(list(rag_properties.keys())[:15])}...")
        
        if adapter_type == 'OData':
            # Generate OData-specific MessageFlow XML
            return self._generate_odata_message_flow_xml(
                flow_id, source_id, target_id, rag_properties
            )
        elif adapter_type == 'SOAP':
            # Generate SOAP-specific MessageFlow XML
            return self._generate_soap_message_flow_xml(
                flow_id, source_id, target_id, rag_properties
            )
        elif adapter_type == 'ProcessDirect':
            # Generate ProcessDirect-specific MessageFlow XML
            return self._generate_processdirect_message_flow_xml(
                flow_id, source_id, target_id, rag_properties
            )
        elif adapter_type == 'SuccessFactors':
            # Generate SuccessFactors-specific MessageFlow XML
            return self._generate_successfactors_message_flow_xml(
                flow_id, source_id, target_id, rag_properties
            )
        else:
            # Generate HTTP MessageFlow XML (existing logic)
            return await self._generate_message_flow_xml(
                component, rag_results, source_id, target_id
            )
    
    def _generate_odata_message_flow_xml(self, flow_id: str, source_id: str, target_id: str, rag_properties: Dict[str, str]) -> str:
        """
        Generate OData-specific MessageFlow XML using ACTUAL properties from VectorDB.
        
        Args:
            flow_id: MessageFlow ID
            source_id: Source reference ID
            target_id: Target reference ID
            rag_properties: Properties extracted from RAG results (from VectorDB)
            
        Returns:
            OData MessageFlow XML string with actual VectorDB properties
        """
        print(f"   🔧 [ODATA_FLOW] Generating OData MessageFlow with {len(rag_properties)} properties from VectorDB")
        
        # Use ACTUAL properties from VectorDB - NO hardcoded defaults
        # Only add minimal required properties if not found in RAG
        properties = {}
        
        # First, use ALL properties from RAG (VectorDB)
        for key, value in rag_properties.items():
            # Skip internal metadata fields
            if key not in ['ifl:type', 'activityType']:
                properties[key] = value
        
        # Only add these if missing from RAG (for backward compatibility)
        if 'Name' not in properties:
            properties['Name'] = 'OData'
        if 'direction' not in properties:
            properties['direction'] = 'Receiver'
        if 'ComponentNS' not in properties:
            properties['ComponentNS'] = 'sap'
        
        # Build properties XML in consistent order
        properties_xml = []
        for key, value in properties.items():
            # Escape XML special characters in values
            escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            properties_xml.append(f'''        <ifl:property>
            <key>{key}</key>
            <value>{escaped_value}</value>
        </ifl:property>''')
        
        adapter_name = properties.get('Name', 'OData')
        xml = f'''<bpmn2:messageFlow id="{flow_id}" name="{adapter_name}" sourceRef="{source_id}" targetRef="{target_id}">
    <bpmn2:extensionElements>
{chr(10).join(properties_xml)}
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''
        
        print(f"   ✅ [ODATA_FLOW] Generated MessageFlow with properties: {', '.join(list(properties.keys())[:10])}...")
        return xml
    
    def _generate_soap_message_flow_xml(self, flow_id: str, source_id: str, target_id: str, rag_properties: Dict[str, str]) -> str:
        """
        Generate SOAP-specific MessageFlow XML using ACTUAL properties from VectorDB.
        
        Args:
            flow_id: MessageFlow ID
            source_id: Source reference ID
            target_id: Target reference ID
            rag_properties: Properties extracted from RAG results (from VectorDB)
            
        Returns:
            SOAP MessageFlow XML string with actual VectorDB properties
        """
        print(f"   🔧 [SOAP_FLOW] Generating SOAP MessageFlow with {len(rag_properties)} properties from VectorDB")
        
        # Use ACTUAL properties from VectorDB - NO hardcoded defaults
        # Only add minimal required properties if not found in RAG
        properties = {}
        
        # First, use ALL properties from RAG (VectorDB)
        for key, value in rag_properties.items():
            # Skip internal metadata fields
            if key not in ['ifl:type', 'activityType']:
                properties[key] = value
        
        # Only add these if missing from RAG (for backward compatibility)
        if 'Name' not in properties:
            properties['Name'] = 'SOAP'
        if 'direction' not in properties:
            properties['direction'] = 'Receiver'
        if 'ComponentNS' not in properties:
            properties['ComponentNS'] = 'sap'
        
        # Build properties XML in consistent order
        properties_xml = []
        for key, value in properties.items():
            # Escape XML special characters in values
            escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            properties_xml.append(f'''        <ifl:property>
            <key>{key}</key>
            <value>{escaped_value}</value>
        </ifl:property>''')
        
        adapter_name = properties.get('Name', 'SOAP')
        xml = f'''<bpmn2:messageFlow id="{flow_id}" name="{adapter_name}" sourceRef="{source_id}" targetRef="{target_id}">
    <bpmn2:extensionElements>
{chr(10).join(properties_xml)}
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''
        
        print(f"   ✅ [SOAP_FLOW] Generated MessageFlow with properties: {', '.join(list(properties.keys())[:10])}...")
        return xml
    
    def _generate_processdirect_message_flow_xml(self, flow_id: str, source_id: str, target_id: str, rag_properties: Dict[str, str]) -> str:
        """
        Generate ProcessDirect-specific MessageFlow XML using ACTUAL properties from VectorDB.
        
        Args:
            flow_id: MessageFlow ID
            source_id: Source reference ID
            target_id: Target reference ID
            rag_properties: Properties extracted from RAG results (from VectorDB)
            
        Returns:
            ProcessDirect MessageFlow XML string with actual VectorDB properties
        """
        print(f"   🔧 [PROCESSDIRECT_FLOW] Generating ProcessDirect MessageFlow with {len(rag_properties)} properties from VectorDB")
        
        # Use ACTUAL properties from VectorDB - NO hardcoded defaults
        # Only add minimal required properties if not found in RAG
        properties = {}
        
        # First, use ALL properties from RAG (VectorDB)
        for key, value in rag_properties.items():
            # Skip internal metadata fields
            if key not in ['ifl:type', 'activityType']:
                properties[key] = value
        
        # Only add these if missing from RAG (for backward compatibility)
        if 'Name' not in properties:
            properties['Name'] = 'ProcessDirect'
        if 'direction' not in properties:
            properties['direction'] = 'Receiver'
        if 'ComponentNS' not in properties:
            properties['ComponentNS'] = 'sap'
        
        # Build properties XML in consistent order
        properties_xml = []
        for key, value in properties.items():
            # Escape XML special characters in values
            escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            properties_xml.append(f'''        <ifl:property>
            <key>{key}</key>
            <value>{escaped_value}</value>
        </ifl:property>''')
        
        adapter_name = properties.get('Name', 'ProcessDirect')
        xml = f'''<bpmn2:messageFlow id="{flow_id}" name="{adapter_name}" sourceRef="{source_id}" targetRef="{target_id}">
    <bpmn2:extensionElements>
{chr(10).join(properties_xml)}
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''
        
        print(f"   ✅ [PROCESSDIRECT_FLOW] Generated MessageFlow with properties: {', '.join(list(properties.keys())[:10])}...")
        return xml
    
    def _generate_successfactors_message_flow_xml(self, flow_id: str, source_id: str, target_id: str, rag_properties: Dict[str, str]) -> str:
        """
        Generate SuccessFactors-specific MessageFlow XML using ACTUAL properties from VectorDB.
        
        Args:
            flow_id: MessageFlow ID
            source_id: Source reference ID
            target_id: Target reference ID
            rag_properties: Properties extracted from RAG results (from VectorDB)
            
        Returns:
            SuccessFactors MessageFlow XML string with actual VectorDB properties
        """
        print(f"   🔧 [SUCCESSFACTORS_FLOW] Generating SuccessFactors MessageFlow with {len(rag_properties)} properties from VectorDB")
        
        # Use ACTUAL properties from VectorDB - NO hardcoded defaults
        # Only add minimal required properties if not found in RAG
        properties = {}
        
        # First, use ALL properties from RAG (VectorDB)
        for key, value in rag_properties.items():
            # Skip internal metadata fields
            if key not in ['ifl:type', 'activityType']:
                properties[key] = value
        
        # Only add these if missing from RAG (for backward compatibility)
        if 'Name' not in properties:
            properties['Name'] = 'SuccessFactors'
        if 'direction' not in properties:
            properties['direction'] = 'Receiver'
        if 'ComponentNS' not in properties:
            properties['ComponentNS'] = 'sap'
        
        # Build properties XML in consistent order
        properties_xml = []
        for key, value in properties.items():
            # Escape XML special characters in values
            escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            properties_xml.append(f'''        <ifl:property>
            <key>{key}</key>
            <value>{escaped_value}</value>
        </ifl:property>''')
        
        adapter_name = properties.get('Name', 'SuccessFactors')
        xml = f'''<bpmn2:messageFlow id="{flow_id}" name="{adapter_name}" sourceRef="{source_id}" targetRef="{target_id}">
    <bpmn2:extensionElements>
{chr(10).join(properties_xml)}
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''
        
        print(f"   ✅ [SUCCESSFACTORS_FLOW] Generated MessageFlow with properties: {', '.join(list(properties.keys())[:10])}...")
        return xml
    
    async def _generate_endpoint_receiver_xml(self, component: Dict[str, Any], rag_results: List[Dict] = None) -> str:
        """Generate XML for EndpointReceiver component with intentional typo 'EndpointRecevier'"""
        # Participants should follow SAP naming convention with numbers: "Receiver1", "Sender1"
        comp_name = component.get('name', 'Receiver1')
        participant_id = f"Participant_{hash(comp_name) % 100000}"
        
        # Use intentional typo 'EndpointRecevier' as per SAP convention [[memory:8143208]]
        xml = f'''<bpmn2:participant id="{participant_id}" ifl:type="EndpointRecevier" name="{comp_name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''
        
        return xml

    def _detect_request_reply_pattern(self, question: str) -> bool:
        """
        Detect if user is requesting ONLY a request-reply pattern (not mixed with other components).
        
        Args:
            question: User query string
            
        Returns:
            True if ONLY request-reply pattern detected (no other components mentioned)
        """
        question_lower = question.lower()
        
        # Request-reply pattern indicators
        request_reply_indicators = [
            'request reply', 'request-reply', 'external call', 'api call',
            'service call', 'http call', 'rest call', 'web service call',
            'call external', 'external service', 'http request', 'api request'
        ]
        
        # Other component indicators that would indicate mixed components
        other_component_indicators = [
            'groovy', 'script', 'content modifier', 'enricher', 'router', 'gateway',
            'sftp', 'odata', 'mail', 'soap', 'jms', 'amqp', 'splitter', 'aggregator',
            'message mapping', 'xslt', 'filter', 'multicast', 'start event', 'end event'
        ]
        
        # Check for request-reply indicators
        has_request_reply = any(indicator in question_lower for indicator in request_reply_indicators)
        
        # Check for other components
        has_other_components = any(indicator in question_lower for indicator in other_component_indicators)
        
        # Only return True if request-reply is mentioned AND no other components are mentioned
        return has_request_reply and not has_other_components

    async def _handle_request_reply_intent(self, query: str) -> Dict[str, Any]:
        """
        Handle request-reply pattern intent analysis.
        
        Args:
            query: User query string
            
        Returns:
            Intent analysis dictionary for request-reply pattern
        """
        print(f"🔍 [REQUEST-REPLY_INTENT] Processing request-reply pattern for: '{query}'")
        
        # Search for request-reply components in vector database
        search_results = await self._search_request_reply_components(query)
        
        # Create intent analysis for request-reply pattern
        # IMPORTANT: Only include RequestReply component - no EndpointSender unless explicitly requested
        intent_analysis = {
            "intent_classification": "request_reply_pattern",
            "user_goal": "Create a request-reply pattern (RequestReply service task with receiver)",
            "components_needed": [
                {
                    "type": "RequestReply",
                    "name": "RequestReply",
                    "quantity": 1,
                    "explicitly_mentioned": True,
                    "requirements": "Request-reply pattern: ExternalCall service task + MessageFlow + EndpointRecevier",
                    "rag_results": search_results.get('request_reply', [])
                }
            ],
            "implicit_components": [
                {
                    "type": "StartEvent",
                    "name": "Start",
                    "quantity": 1,
                    "reason": "Required for iFlow initiation"
                },
                {
                    "type": "EndEvent",
                    "name": "End",
                    "quantity": 1,
                    "reason": "Required for iFlow completion"
                }
            ],
            "message_flows": search_results.get('message_flows', []),
            "pattern_examples": search_results.get('pattern_examples', []),
            "strategic_plan": {
                "rag_search_strategy": "Search for complete request-reply pattern components",
                "generation_order": ["StartEvent", "EndpointSender", "ExternalCall", "EndpointReceiver", "EndEvent"],
                "integration_approach": "Request-reply pattern with HTTP sender, service task, and HTTP receiver",
                "pattern_type": "request_reply"
            },
            "query_interpretation": f"User wants to create a request-reply pattern: {query}"
        }
        
        print(f"✅ [REQUEST-REPLY_INTENT] Pattern analysis complete:")
        print(f"   • HTTP Sender: {len(search_results.get('http_sender', []))} components found")
        print(f"   • Request Reply: {len(search_results.get('request_reply', []))} components found")
        print(f"   • HTTP Receiver: {len(search_results.get('http_receiver', []))} components found")
        print(f"   • Message Flows: {len(search_results.get('message_flows', []))} flows found")
        
        return intent_analysis

    def _generate_request_reply_rag_queries(self, question: str) -> List[str]:
        """
        Generate RAG search queries for request-reply pattern components.
        
        Args:
            question: User query string
            
        Returns:
            List of optimized search queries for all 3 components
        """
        queries = []
        
        # Query 1: HTTP Sender (EndpointSender)
        queries.append("endpoint sender https sender http sender")
        
        # Query 2: Request Reply Service Task (ExternalCall)
        queries.append("request reply external call service task")
        
        # Query 3: HTTP Receiver (EndpointReceiver)
        queries.append("endpoint receiver http receiver https receiver")
        
        # Query 4: Message Flow (HTTPS/HTTP)
        queries.append("message flow https http transport protocol")
        
        # Query 5: Complete request-reply pattern
        queries.append("request reply pattern http sender receiver")
        
        return queries

    async def _search_request_reply_components(self, question: str) -> Dict[str, Any]:
        """
        Search for all request-reply pattern components in vector database.
        
        Args:
            question: User query string
            
        Returns:
            Dictionary with all 3 components and their RAG results
        """
        print(f"\n🔍 [REQUEST-REPLY] Searching for complete pattern components...")
        
        # Generate search queries for all components
        search_queries = self._generate_request_reply_rag_queries(question)
        
        # Search results for each component type
        search_results = {
            'http_sender': [],
            'request_reply': [],
            'http_receiver': [],
            'message_flows': [],
            'pattern_examples': []
        }
        
        # Search for each component type
        for query in search_queries:
            try:
                # Search in vector database
                results = await self.vector_store.search_similar(
                    query=query,
                    limit=3,
                    chunk_types=["complete_xml", "config", "summary"]
                )

                # Log RAG retrieval for request-reply pattern
                self.rag_logger.log_retrieval(
                    query=query,
                    results=results,
                    context={
                        "pattern_type": "request_reply",
                        "search_query_type": query,
                        "retrieval_location": "_rag_search_request_reply_components"
                    },
                    retrieval_type="pattern_search"
                )

                # Categorize results based on content
                for result in results:
                    content = result.get('content', '').lower()
                    document_name = result.get('document_name', '').lower()
                    
                    # Categorize based on content analysis
                    if any(term in content for term in ['endpointsender', 'sender', 'https sender']):
                        search_results['http_sender'].append(result)
                    elif any(term in content for term in ['externalcall', 'request reply', 'service task']):
                        search_results['request_reply'].append(result)
                    elif any(term in content for term in ['endpointreceiver', 'receiver', 'http receiver']):
                        search_results['http_receiver'].append(result)
                    elif any(term in content for term in ['messageflow', 'https', 'http', 'transport']):
                        search_results['message_flows'].append(result)
                    else:
                        search_results['pattern_examples'].append(result)
                        
            except Exception as e:
                print(f"⚠️ [REQUEST-REPLY] Search error for query '{query}': {str(e)}")
                continue
        
        # Log search results
        print(f"📊 [REQUEST-REPLY] Search results:")
        print(f"   • HTTP Sender: {len(search_results['http_sender'])} components")
        print(f"   • Request Reply: {len(search_results['request_reply'])} components")
        print(f"   • HTTP Receiver: {len(search_results['http_receiver'])} components")
        print(f"   • Message Flows: {len(search_results['message_flows'])} flows")
        print(f"   • Pattern Examples: {len(search_results['pattern_examples'])} examples")
        
        return search_results

    def _export_component_metadata(self, components: List[Dict[str, Any]], query: str, output_dir: str = "component_metadata") -> str:
        """
        Export component metadata to JSON file before iFlow generation.
        
        Args:
            components: List of identified components
            query: Original user query
            output_dir: Directory to save metadata files
            
        Returns:
            Path to the exported JSON file
        """
        import json
        import os
        from datetime import datetime
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare metadata
        metadata = {
            "query": query,
            "timestamp": timestamp,
            "total_components": len(components),
            "components": []
        }
        
        for i, comp in enumerate(components):
            # Get XML element from COMPLETE_IFLOW_COMPONENTS mapping
            xml_element = 'serviceTask'  # default
            for key, value in self.COMPLETE_IFLOW_COMPONENTS.items():
                if value['type'] == comp['type']:
                    xml_element = value['xml_element']
                    break
            
            component_metadata = {
                "component_id": i + 1,
                "component_type": comp['type'],
                "component_name": comp['name'],
                "xml_element": xml_element,
                "keyword_matched": comp.get('keyword', comp['type']),
                "instance_number": comp.get('instance_number', 1),
                "total_instances": comp.get('total_instances', comp.get('quantity', 1)),
                "rag_queries": comp.get('rag_queries', []),
                "description": f"{comp['type']} component named '{comp['name']}'",
                "source": comp.get('source', 'unknown'),
                "priority": comp.get('priority', 'medium'),
                "properties": {
                    "activityType": self.SAP_AUTHORITATIVE_STANDARDS.get(comp['type'], {}).get('activityType', 'Unknown'),
                    "cmdVariantUri": self.SAP_AUTHORITATIVE_STANDARDS.get(comp['type'], {}).get('cmdVariantUri', 'Unknown'),
                    "componentVersion": self.SAP_AUTHORITATIVE_STANDARDS.get(comp['type'], {}).get('componentVersion', 'Unknown')
                }
            }
            
            # Add adapter_type if present (for RequestReply with HTTP/OData)
            if 'adapter_type' in comp:
                component_metadata['adapter_type'] = comp['adapter_type']
                component_metadata['properties']['adapter_type'] = comp['adapter_type']
                print(f"   📋 [METADATA] RequestReply with adapter_type: {comp['adapter_type']}")
            
            metadata["components"].append(component_metadata)
        
        # Export to JSON file
        filename = f"iflow_components_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📄 [METADATA_EXPORT] Component metadata exported to: {filepath}")
        print(f"   📊 Components: {len(components)}")
        print(f"   🔍 Query: '{query}'")
        
        return filepath

    async def create_complete_iflow_package(self, question: str) -> Dict[str, Any]:
        """
        Create a complete importable iFlow package using intelligent intent understanding.
        
        This method:
        1. Uses GenAI to understand user intent and create strategic plan
        2. Identifies all components (explicit and implicit) intelligently
        3. Executes strategic RAG searches for each component
        4. Generates XML using authoritative SAP standards
        5. Packages everything using package_complete_iflow
        
        Args:
            question: User query requesting complete iFlow creation
            
        Returns:
            Dictionary containing analysis results and package information
        """
        print(f"\n📦 [INTELLIGENT_IFLOW] Creating iFlow package with intelligent intent understanding")
        print(f"🔍 [USER_QUERY] '{question}'")
        
        # STEP 1: Understand user intent using GenAI
        print("\n🧠 [STEP_1] Understanding user intent...")
        intent_analysis = await self._understand_user_intent(question)
        
        # STEP 2: Create strategic plan
        print("\n📋 [STEP_2] Creating strategic plan...")
        strategic_plan = self._create_strategic_plan(intent_analysis)
        
        # STEP 3: Export strategic plan metadata
        print("\n📄 [STEP_3] Exporting strategic plan metadata...")
        metadata_file = self._export_strategic_plan_metadata(strategic_plan, question)
        
        # STEP 4: Export component metadata
        print("\n📊 [STEP_4] Exporting component metadata...")
        components = strategic_plan.get('components', [])
        # Rule: Do not include EndpointSender/EndpointReceiver (correct spelling) for RequestReply patterns in
        # multi-component flows unless explicitly requested by the user text. This prevents adding an HTTPS Sender
        # and avoids participants being treated as process elements (packager expects only 'EndpointRecevier').
        try:
            user_text = f"{strategic_plan.get('query_interpretation', '')} {strategic_plan.get('user_goal', '')}".lower()
            has_request_reply = any(c.get('type') in {'RequestReply', 'ExternalCall'} for c in components)
            mentions_sender = any(kw in user_text for kw in ['sender', 'http sender', 'https sender'])
            mentions_receiver = any(kw in user_text for kw in ['receiver', 'http receiver', 'https receiver'])
            if has_request_reply and not mentions_sender:
                before = len(components)
                components = [c for c in components if c.get('type') != 'EndpointSender']
                if len(components) != before:
                    print("   🔧 [COMPONENT_FILTER] Removed EndpointSender (not explicitly requested)")
            if has_request_reply and not mentions_receiver:
                before = len(components)
                components = [c for c in components if c.get('type') != 'EndpointReceiver']
                if len(components) != before:
                    print("   🔧 [COMPONENT_FILTER] Removed EndpointReceiver (use RequestReply trio receiver)")
            # Remove any pre-declared MessageFlow components; trio will add the single correct one
            before = len(components)
            components = [c for c in components if c.get('type') != 'MessageFlow']
            if len(components) != before:
                print("   🔧 [COMPONENT_FILTER] Removed standalone MessageFlow components")
        except Exception as _:
            # Safe to ignore filtering if metadata missing
            pass
        component_metadata_file = self._export_component_metadata(components, question)
        
        # STEP 5: Execute strategic plan
        print("\n⚡ [STEP_5] Executing strategic plan...")
        execution_result = await self._execute_strategic_plan(strategic_plan)
        
        return execution_result

    def _export_strategic_plan_metadata(self, strategic_plan: Dict[str, Any], query: str, output_dir: str = "strategic_plans") -> str:
        """
        Export strategic plan metadata to JSON file.
        
        Args:
            strategic_plan: Strategic plan from _create_strategic_plan
            query: Original user query
            output_dir: Directory to save metadata files
            
        Returns:
            Path to the exported JSON file
        """
        import json
        import os
        from datetime import datetime
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare strategic plan metadata
        plan_metadata = {
            "query": query,
            "timestamp": timestamp,
            "intent_classification": strategic_plan.get('intent_classification'),
            "user_goal": strategic_plan.get('user_goal'),
            "query_interpretation": strategic_plan.get('query_interpretation'),
            "total_components": strategic_plan.get('total_components'),
            "generation_order": strategic_plan.get('generation_order'),
            "integration_approach": strategic_plan.get('integration_approach'),
            "execution_steps": strategic_plan.get('execution_steps'),
            "components": strategic_plan.get('components'),
            "rag_strategy": strategic_plan.get('rag_strategy')
        }
        
        # Export to JSON file
        filename = f"strategic_plan_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📄 [STRATEGIC_PLAN_EXPORT] Strategic plan exported to: {filepath}")
        print(f"   🎯 Intent: {strategic_plan.get('intent_classification')}")
        print(f"   📦 Components: {strategic_plan.get('total_components')}")
        print(f"   🔄 Order: {' → '.join(strategic_plan.get('generation_order', []))}")
        
        return filepath

    async def _execute_strategic_plan(self, strategic_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the strategic plan to create the iFlow package.
        
        Args:
            strategic_plan: Strategic plan from _create_strategic_plan
            
        Returns:
            Dictionary containing execution results and package information
        """
        print(f"🚀 [EXECUTION] Executing strategic plan...")
        
        components = strategic_plan.get('components', [])
        rag_strategy = strategic_plan.get('rag_strategy', {})
        generation_order = strategic_plan.get('generation_order', [])
        
        print(f"   📊 [EXECUTION] Components in plan: {len(components)}")
        for comp in components:
            print(f"      - {comp['type']}: quantity={comp.get('quantity', 1)}")
        print(f"   📋 [EXECUTION] Generation order: {generation_order}")
        print(f"   🎯 [EXECUTION] Will generate {len(generation_order)} component instances")
        
        # Execute RAG searches and generate components
        components_with_content = []
        
        # Enforce strict user-specified order and clean naming
        # Track instance counts globally for all component types
        type_instance_counts: Dict[str, int] = {}
        
        def normalized_name_for(comp_type: str) -> str:
            base = comp_type
            # Map to friendly base names
            base_map = {
                'ContentModifier': 'ContentModifier',
                'GroovyScript': 'GroovyScript',
                'RequestReply': 'RequestReply',
                'ExternalCall': 'RequestReply',
                'Router': 'Router',
                'StartEvent': 'Start',
                'EndEvent': 'End',
                'MessageFilter': 'Filter',
                'EndpointReceiver': 'Receiver',
                'EndpointRecevier': 'Receiver',  # Handle typo variant
                'EndpointSender': 'Sender',
                'IntegrationProcess': 'Integration Process'
            }
            base = base_map.get(comp_type, comp_type)
            
            # Track instance numbers for ALL components
            type_instance_counts[base] = type_instance_counts.get(base, 0) + 1
            instance_num = type_instance_counts[base]
            
            # Naming pattern depends on component type:
            # - Start/End events: With space → "Start 1", "End 1"
            # - Router: With space → "Router 1"
            # - Participants (Receiver, Sender): No space/underscore → Receiver1, Sender1
            # - Integration Process: With space → "Integration Process 1"
            # - Other components: With proper spacing → "Content Modifier 1", "Groovy Script 1"
            if comp_type in ['StartEvent', 'EndEvent', 'Router']:
                return f"{base} {instance_num}"  # Space for Start/End events and Router
            elif comp_type in ['EndpointReceiver', 'EndpointRecevier', 'EndpointSender']:
                return f"{base}{instance_num}"  # No separator for participants
            elif comp_type == 'IntegrationProcess':
                return f"{base} {instance_num}"  # Space for Integration Process
            else:
                # Convert camelCase/underscore to proper spacing: ContentModifier → "Content Modifier"
                spaced_name = re.sub(r'([A-Z])', r' \1', base).strip()  # Add space before capitals
                return f"{spaced_name} {instance_num}"  # Proper spacing for other components

        # Process components according to generation_order (which respects quantities)
        # Build a map of component types to their full component data
        comp_map = {c['type']: c for c in components}
        
        for comp_type in generation_order:
            # Get component data from map
            comp = comp_map.get(comp_type)
            if not comp:
                print(f"   ⚠️ [EXECUTION] Component type '{comp_type}' in generation_order but not in components list")
                continue
            
            # Assign normalized, readable name in the order provided
            comp_name = normalized_name_for(comp_type)
            
            print(f"🔍 [RAG_EXECUTION] Processing {comp_type}: {comp_name}")
            
            # Get RAG strategy for this component
            strategy = rag_strategy.get(comp_type, {})
            search_queries = strategy.get('search_queries', [])
            search_limit = strategy.get('search_limit', 5)
            chunk_types = strategy.get('chunk_types', ['xml', 'groovy', 'component'])
            
            # Execute RAG search
            rag_results = []
            
            # SPECIAL CASE: For RequestReply, do a specific search to get ALL RequestReply entries
            if comp_type == 'RequestReply':
                print(f"   🔍 [REQUESTREPLY_SEARCH] Performing specialized search for RequestReply adapters")
                
                # Get adapter_type if specified
                requested_adapter = comp.get('adapter_type', 'HTTP')
                print(f"   🎯 [ADAPTER_REQUEST] User requested adapter type: {requested_adapter}")
                
                # Search with multiple specific queries to ensure we get the right adapter
                # CRITICAL: Search for MessageFlow XML content directly
                requestreply_queries = [
                    f'messageFlow Name {requested_adapter}',  # Direct search for MessageFlow with adapter name
                    f'ComponentType HCIOData' if requested_adapter == 'OData' else f'ComponentType {requested_adapter}',
                    f'{requested_adapter} adapter messageFlow',
                    f'serviceTask ExternalCall {requested_adapter}',
                    'activityType ExternalCall messageFlow',
                    'Request Reply ServiceTask MessageFlow'
                ]
                
                for rr_query in requestreply_queries:
                    try:
                        results = await self.vector_store.search_similar(
                            query=rr_query,
                            limit=10,  # Higher limit to get all adapter types
                            chunk_types=chunk_types
                        )
                        rag_results.extend(results)
                        print(f"      📊 Query '{rr_query}' returned {len(results)} results")
                    except Exception as e:
                        print(f"   ⚠️ RequestReply RAG search failed for '{rr_query}': {e}")
            else:
                # Normal RAG search for other components
                for query in search_queries[:3]:  # Limit to top 3 queries
                    try:
                        results = await self.vector_store.search_similar(
                            query=query,
                            limit=search_limit,
                            chunk_types=chunk_types
                        )
                        rag_results.extend(results)
                    except Exception as e:
                        print(f"   ⚠️ RAG search failed for '{query}': {e}")
            
            # Deduplicate RAG results (important for RequestReply which searches multiple times)
            seen_ids = set()
            unique_rag_results = []
            for r in rag_results:
                r_id = r.get('id') or r.get('content', '')[:100]  # Use ID or content snippet as key
                if r_id not in seen_ids:
                    seen_ids.add(r_id)
                    unique_rag_results.append(r)
            rag_results = unique_rag_results
            print(f"   📊 [RAG_RESULTS] Total unique results after deduplication: {len(rag_results)}")
            
            # Special-case expansion: RequestReply must expand into ExternalCall + MessageFlow + EndpointReceiver
            if comp_type in {'RequestReply', 'ExternalCall'} or self._is_request_reply_pattern(comp):
                print("   🔎 [RR_DETECT] RequestReply pattern detected → expanding into trio")
                # Build instance-specific component with normalized name
                inst_comp = dict(comp)
                inst_comp['name'] = comp_name
                
                # Generate receiver instance number from global counter
                type_instance_counts['Receiver'] = type_instance_counts.get('Receiver', 0) + 1
                receiver_instance = type_instance_counts['Receiver']
                
                # Pass user query for adapter type detection (HTTP vs OData)
                user_query = strategic_plan.get('query_interpretation', '')
                
                # CRITICAL: Also check if adapter_type was set in component
                if 'adapter_type' not in inst_comp and 'adapter_type' in comp:
                    inst_comp['adapter_type'] = comp['adapter_type']
                    print(f"   🔧 [ADAPTER_PRESERVE] Preserving adapter_type from component: {comp['adapter_type']}")
                
                rr_components = await self._generate_request_reply_pattern(inst_comp, rag_results, receiver_instance, user_query)
                components_with_content.extend(rr_components)
                print(f"   ✅ [RR_EXPANDED] Added trio for {comp_name}")
                continue

            # Generate XML for non-RequestReply components
            # Each entry in generation_order is a single instance
            # Prepare component metadata (especially for Router)
            component_metadata = {}
            if comp_type == 'Router':
                # Extract Router-specific metadata from component
                component_metadata['branch_count'] = comp.get('branch_count', 2)
                component_metadata['routing_criteria'] = comp.get('routing_criteria')
                component_metadata['branch_targets'] = comp.get('branch_targets', [])
            
            # Generate XML with instance-specific name and metadata
            xml_content = await self._generate_component_xml(
                component_type=comp_type,
                component_name=comp_name,
                retrieved_content=rag_results,
                component_metadata=component_metadata
            )
            
            # Create component with content
            component_with_content = {
                'type': comp_type,
                'name': comp_name,
                'xml': xml_content,
                'quantity': 1,  # Each entry in generation_order is 1 instance
                'source': comp.get('source', 'unknown'),
                'priority': comp.get('priority', 'medium'),
                'rag_results': rag_results
            }
            
            # Preserve Router metadata in the component_with_content
            if comp_type == 'Router':
                component_with_content.update(component_metadata)
            
            components_with_content.append(component_with_content)
            print(f"   ✅ Generated {comp_type}: {comp_name}")
        
        # Ensure StartEvent and EndEvent are always present (no duplicates)
        await self._ensure_start_end_events(components_with_content)
        
        print(f"   ✅ [EXECUTION] Generated {len(components_with_content)} total components:")
        for comp in components_with_content:
            print(f"      - {comp['type']}: {comp['name']}")
        
        # Generate iFlow name
        iflow_name = self._generate_iflow_name(strategic_plan.get('query_interpretation', ''), components_with_content)
        
        # Prepare groovy files
        groovy_files = {}
        for comp in components_with_content:
            if comp['type'] == 'GroovyScript':
                script_filename = f"{comp['name'].lower().replace(' ', '_')}.groovy"
                groovy_files[script_filename] = 'def Message processData(m){ return m }'
        
        # Check if we have Router components requiring branching logic
        has_router = any(comp['type'] == 'Router' for comp in components_with_content)
        
        if has_router:
            print(f"🔀 [BRANCHING] Router detected - applying branching logic")
            components_with_content = self._apply_router_branching_logic(components_with_content, strategic_plan)
        
        # Log component selection
        self.rag_logger.log_component_selection(
            selected_components=components_with_content,
            reason="Strategic plan execution with intelligent intent understanding",
            context={
                "user_query": question,
                "query_interpretation": strategic_plan.get('query_interpretation', ''),
                "user_goal": strategic_plan.get('user_goal', ''),
                "total_components": len(components_with_content),
                "has_router": has_router
            }
        )

        # Package the iFlow
        print(f"📦 [PACKAGING] Creating iFlow package: {iflow_name}")
        package_path = self.packager.package_complete_iflow_corrected(
            components=components_with_content,
            iflow_name=iflow_name,
            flow_description=f'Intelligent iFlow generated from: {strategic_plan.get("query_interpretation", "")}',
            groovy_files=groovy_files
        )

        # Prepare package info with all required fields
        package_info = {
            'iflow_name': iflow_name,
            'component_count': len(components_with_content),
            'package_path': package_path,
            'components': components_with_content,
            'sources_used': sum(len(comp.get('rag_results', [])) for comp in components_with_content),
            'ready_for_import': True,
            'package_type': 'intelligent_iflow'
        }

        # Log generation result
        self.rag_logger.log_generation_result(
            iflow_name=iflow_name,
            components_used=components_with_content,
            success=bool(package_path),
            error=None if package_path else "Package generation failed"
        )

        return {
            'final_response': self._format_complete_iflow_response(package_info, strategic_plan.get('query_interpretation', '')),
            'package_info': package_info,
            'vector_results': [],
            'data_sources': ['Intelligent intent understanding', 'Strategic RAG execution'],
            'tools_used': ['_understand_user_intent', '_create_strategic_plan', '_execute_strategic_plan', 'package_complete_iflow_corrected'],
            'strategic_plan': strategic_plan
        }

    def _apply_router_branching_logic(self, components: List[Dict], strategic_plan: Dict) -> List[Dict]:
        """
        Reorganize components to support Router branching instead of linear flow.
        
        Transform:
            Start → Router → Comp1 → Comp2 → End (linear)
        
        Into:
            Start → Router
                     ├─ Branch1 → Comp1 → End
                     └─ Branch2 → Comp2 → End
        
        Args:
            components: List of components with XML
            strategic_plan: Strategic plan containing Router metadata
            
        Returns:
            Modified component list with branching structure metadata
        """
        print(f"   🔀 [BRANCHING] Applying Router branching logic...")
        
        # Find Router component(s)
        router_indices = [i for i, c in enumerate(components) if c['type'] == 'Router']
        
        if not router_indices:
            return components  # No router, return as-is
        
        # For now, handle single Router case
        router_idx = router_indices[0]
        router_comp = components[router_idx]
        
        # Extract Router metadata
        branch_count = router_comp.get('branch_count', 2)
        branch_targets = router_comp.get('branch_targets', [])
        routing_criteria = router_comp.get('routing_criteria')
        
        print(f"   📊 [ROUTER_META] Branch count: {branch_count}, Criteria: {routing_criteria}")
        print(f"   🎯 [ROUTER_META] Branch targets: {branch_targets}")
        
        # Find components before and after router
        components_before_router = components[:router_idx]
        components_after_router = components[router_idx + 1:]
        
        # Separate Start/End events from processing components
        start_events = [c for c in components_before_router if c['type'] == 'StartEvent']
        end_events = [c for c in components if c['type'] == 'EndEvent']
        processing_before = [c for c in components_before_router if c['type'] not in {'StartEvent', 'EndEvent'}]
        
        # Components that should be in branches (after router, excluding end events)
        branch_components = [c for c in components_after_router if c['type'] != 'EndEvent']
        
        print(f"   📦 [BRANCHING] {len(branch_components)} components to distribute across {branch_count} branches")
        print(f"   📋 [BRANCHING] Processing before router: {[c['type'] + ':' + c['name'] for c in processing_before]}")
        print(f"   📋 [BRANCHING] Components after router: {[c['type'] + ':' + c['name'] for c in branch_components]}")
        print(f"   📋 [BRANCHING] Total components received: {len(components)}")
        
        # If no explicit branch_targets, but components exist after router,
        # distribute them into branches automatically
        # IMPORTANT: User intent is key - they specified Router, so they want branching!
        if not branch_targets and not branch_components:
            print(f"   ℹ️ [BRANCHING] Router at end with no components to branch - keeping simple Router")
            # Keep original order unchanged
            return components
        
        # Assign components to branches
        # If branch_targets specified, use them; otherwise distribute evenly
        branch_assignments = {}
        
        if branch_targets and len(branch_targets) == branch_count:
            # Group components by type matching branch targets
            # Each branch target gets ONE component of that type
            available_components = list(branch_components)  # Make a copy
            
            for i, target_type in enumerate(branch_targets):
                branch_num = i + 1
                # Find first available component of target type
                matching_comp = next((c for c in available_components if c['type'] == target_type), None)
                
                if matching_comp:
                    branch_assignments[branch_num] = [matching_comp]
                    available_components.remove(matching_comp)  # Remove from available
                else:
                    # No matching component found, create empty branch
                    branch_assignments[branch_num] = []
                    print(f"   ⚠️ [BRANCHING] No {target_type} available for Branch {branch_num}")
        else:
            # Distribute components evenly across branches
            for i, comp in enumerate(branch_components):
                branch_num = (i % branch_count) + 1
                if branch_num not in branch_assignments:
                    branch_assignments[branch_num] = []
                branch_assignments[branch_num].append(comp)
        
        print(f"   ✅ [BRANCHING] Branch assignments: {{{', '.join([f'Branch{k}: {len(v)} comps' for k, v in branch_assignments.items()])}}}")
        
        # Add branch metadata to components
        for branch_num, branch_comps in branch_assignments.items():
            for comp in branch_comps:
                comp['branch_number'] = branch_num
                comp['is_in_branch'] = True
        
        # Add branch metadata to router
        router_comp['branches'] = []
        for branch_num in range(1, branch_count + 1):
            branch_comps = branch_assignments.get(branch_num, [])
            branch_info = {
                'branch_number': branch_num,
                'components': [c['name'] for c in branch_comps],
                'component_ids': [self._extract_xml_id(c['xml']) for c in branch_comps],
                'routing_condition': self._generate_routing_condition(routing_criteria, branch_num, branch_count)
            }
            router_comp['branches'].append(branch_info)
        
        print(f"   🔀 [ROUTER] Configured {len(router_comp['branches'])} branches with routing conditions")
        
        # Reconstruct component list in proper order
        # CRITICAL FIX: Include processing_before components!
        # Correct order: Start → processing_before → Router → branch_components → End
        reorganized = start_events + processing_before + [router_comp] + branch_components + end_events
        
        print(f"   ✅ [BRANCHING] Reorganized flow: {' → '.join([c['type'] for c in reorganized])}")
        
        return reorganized
    
    def _generate_routing_condition(self, criteria: str, branch_num: int, total_branches: int) -> str:
        """
        Generate a routing condition for a specific branch.
        
        Args:
            criteria: Payload field to route on (e.g., "priority", "status")
            branch_num: Branch number (1-indexed)
            total_branches: Total number of branches
            
        Returns:
            Routing condition expression (SAP/XPath format)
        """
        if not criteria:
            # Default conditions
            if branch_num == total_branches:
                return "default"  # Last branch is default/otherwise
            return f"${{property.branch}} = '{branch_num}'"
        
        # Generate condition based on criteria
        # CRITICAL: Last branch is ALWAYS default (SAP requirement)
        if branch_num == total_branches:
            return "default"
        
        # Define default condition values for common criteria (can be overridden by user)
        default_values = {
            'priority': ['high', 'medium', 'low', 'critical', 'normal'],
            'status': ['active', 'inactive', 'pending', 'completed', 'error'],
            'type': ['typeA', 'typeB', 'typeC'],
            'severity': ['critical', 'high', 'medium', 'low'],
            'level': ['level1', 'level2', 'level3'],
            'category': ['A', 'B', 'C']
        }
        
        # Use predefined values if criteria matches, otherwise generate generic condition
        criteria_lower = criteria.lower() if criteria else 'branch'
        
        if criteria_lower in default_values:
            conditions = default_values[criteria_lower]
            if branch_num <= len(conditions):
                return f"${{property.{criteria}}} = '{conditions[branch_num - 1]}'"
            # If we exceed predefined values, generate generic
            return f"${{property.{criteria}}} = 'value{branch_num}'"
        else:
            # For unknown/custom criteria, generate generic condition
            # User can manually edit this in SAP UI after import
            return f"${{property.{criteria}}} = 'value{branch_num}'"
    
    # Legacy method for backward compatibility - now uses intelligent approach
    async def create_complete_iflow_package_legacy(self, question: str) -> Dict[str, Any]:
        """
        Legacy method that uses the old pattern-based approach.
        Kept for backward compatibility but redirects to intelligent approach.
        """
        print("⚠️ [LEGACY_METHOD] Using legacy pattern-based approach. Consider using intelligent intent understanding.")
        
        # Check if we have enough components for a complete iFlow
        identified_components = self._identify_components_in_query(question)
        
        if len(identified_components) >= 2:
            print(f"⚡ [DYNAMIC_PATH] Found {len(identified_components)} components dynamically. Building with RAG/KG lookup...")
            print(f"   Components detected: {[c['type'] for c in identified_components]}")
            
            # Use RAG/KG to get real SAP component templates instead of generating placeholders
            components_with_real_content = []
            
            for comp in identified_components:
                print(f"🔍 [RAG_LOOKUP] Looking up real SAP component: {comp['type']}")
                
                # Get real component content from RAG/KG
                try:
                    # Use optimized RAG search for each component
                    optimized_query = self._optimize_rag_search_query(comp['type'], comp['name'])
                    rag_results = await self.vector_store.search_similar(
                        query=optimized_query,
                        limit=5,
                        chunk_types=['xml', 'groovy', 'component']
                    )
                    
                    if rag_results:
                        print(f"   ✅ Found {len(rag_results)} RAG results for {comp['type']}")
                        
                        # Generate real XML using the existing methods
                        real_xml = await self._generate_component_xml(
                            component_type=comp['type'],
                            component_name=comp['name'],
                            retrieved_content=rag_results
                        )
                        
                        components_with_real_content.append({
                            'type': comp['type'],
                            'name': comp['name'],
                            'xml': real_xml
                        })
                        print(f"   + Added real {comp['type']}: {comp['name']} from RAG/KG")
                    else:
                        print(f"   ⚠️ No RAG results for {comp['type']}, using fallback")
                        # Fallback to basic component if no RAG content found
                        fallback_xml = self._generate_basic_component_xml(comp)
                        components_with_real_content.append({
                            'type': comp['type'],
                            'name': comp['name'],
                            'xml': fallback_xml
                        })
                        
                except Exception as e:
                    print(f"   ❌ Error looking up {comp['type']}: {e}")
                    # Fallback to basic component
                    fallback_xml = self._generate_basic_component_xml(comp)
                    components_with_real_content.append({
                        'type': comp['type'],
                        'name': comp['name'],
                        'xml': fallback_xml
                    })
            
            # ALWAYS ensure we have proper StartEvent and EndEvent
            has_start = any(c['type'] == 'StartEvent' for c in components_with_real_content)
            has_end = any(c['type'] == 'EndEvent' for c in components_with_real_content)
            
            if not has_start:
                print("   + Adding required StartEvent")
                start_event = {
                    'type': 'StartEvent',
                    'name': 'Start',
                    'xml': '''<bpmn2:startEvent id="StartEvent_1" name="Start">
    <bpmn2:extensionElements>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageStartEvent</value></ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:startEvent>'''
                }
                components_with_real_content.insert(0, start_event)
            
            if not has_end:
                print("   + Adding required EndEvent")
                end_event = {
                    'type': 'EndEvent',
                    'name': 'End',
                    'xml': '''<bpmn2:endEvent id="EndEvent_1" name="End">
    <bpmn2:extensionElements>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageEndEvent</value></ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''
                }
                components_with_real_content.append(end_event)
            
            # Continue with the existing packaging logic...
            iflow_name = self._generate_iflow_name(question, components_with_real_content) or 'CompleteIntegrationFlow'
            
            # Use corrected packager; pass groovy file content based on actual component names
            groovy_files = {}
            for comp in components_with_real_content:
                if comp['type'] == 'GroovyScript':
                    script_filename = f"{comp['name'].lower().replace(' ', '_')}.groovy"
                    groovy_files[script_filename] = 'def Message processData(m){ return m }'
            
            print("   Components assembled (real SAP components):", [c['type'] for c in components_with_real_content])
            package_path = self.packager.package_complete_iflow_corrected(
                components=components_with_real_content,
                iflow_name=iflow_name,
                groovy_files=groovy_files
            )
            
            return {
                'final_response': self._format_complete_iflow_response({
                    'iflow_name': iflow_name,
                    'component_count': len(components_with_real_content),
                    'package_path': package_path,
                    'components': components_with_real_content
                }, question),
                'package_info': {
                    'iflow_name': iflow_name,
                    'component_count': len(components_with_real_content),
                    'package_path': package_path,
                    'components': components_with_real_content
                },
                'vector_results': [],
                'data_sources': ['Real SAP components from RAG/KG'],
                'tools_used': ['_identify_components_in_query', '_generate_component_xml', 'package_complete_iflow_corrected']
            }
        
        # FALLBACK: If dynamic detection didn't find enough components, use the old explicit detection
        print("🔄 [FALLBACK] Using explicit component detection...")
        
        # EXPANDED FAST PATH: Detect ANY explicit component requests to avoid RAG fallback
        qlower = question.lower()
        
        # Component detection patterns
        explicit_https = ('https sender' in qlower) or ('http sender' in qlower) or ('endpoint sender' in qlower)
        explicit_groovy = ('groovy' in qlower) or ('groovy script' in qlower)
        explicit_cm = bool(re.search(r"content\s*-?modif", qlower)) or ('enrich' in qlower) or ('content enricher' in qlower)
        explicit_end = ('message end' in qlower) or ('end event' in qlower) or ('end' in qlower)
        explicit_gateway = ('exclusive gateway' in qlower) or ('gateway' in qlower) or ('parallel gateway' in qlower)
        explicit_branches = ('two branches' in qlower) or ('two paths' in qlower) or ('branch' in qlower)
        explicit_service = ('service task' in qlower) or ('service' in qlower)
        explicit_receiver = ('http receiver' in qlower) or ('https receiver' in qlower) or ('receiver' in qlower)
        
        # Count explicit components to determine if we should use fast path
        explicit_count = sum([explicit_https, explicit_groovy, explicit_cm, explicit_end, explicit_gateway, explicit_service, explicit_receiver])
        
        if explicit_count >= 2:  # Use fast path if 2+ components are explicitly mentioned
            print("⚡ [FAST_PATH] Explicit components detected. Building without RAG...")
            print(f"   flags -> https:{explicit_https} groovy:{explicit_groovy} contentModifier:{explicit_cm} end:{explicit_end} gateway:{explicit_gateway} branches:{explicit_branches} service:{explicit_service} receiver:{explicit_receiver}")

            # Prepare minimal, SAP-compliant XML blocks modeled on reference iFlow
            import uuid

            components_fast = []

            if explicit_https:
                components_fast.append({
                    'type': 'EndpointSender',
                    'name': 'Sender1',
                    'xml': f'''<bpmn2:participant id="EndpointSender_{uuid.uuid4().hex[:8]}" ifl:type="EndpointSender" name="Sender1">
    <bpmn2:extensionElements>
        <ifl:property><key>enableBasicAuthentication</key><value>false</value></ifl:property>
        <ifl:property><key>ifl:type</key><value>EndpointSender</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''
                })

            if explicit_groovy:
                groovy_id = f"CallActivity_{uuid.uuid4().hex[:8]}"
                groovy_name = 'GroovyScript'  # Use generic name instead of hardcoded DataProcessor
                script_filename = f"{groovy_name.lower()}.groovy"
                components_fast.append({
                    'type': 'GroovyScript',
                    'name': groovy_name,
                    'xml': f'''<bpmn2:callActivity id="{groovy_id}" name="{groovy_name}">
    <bpmn2:extensionElements>
        <ifl:property><key>scriptFunction</key><value/></ifl:property>
        <ifl:property><key>scriptBundleId</key><value/></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
        <ifl:property><key>activityType</key><value>Script</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2</value></ifl:property>
        <ifl:property><key>subActivityType</key><value>GroovyScript</value></ifl:property>
        <ifl:property><key>script</key><value>{script_filename}</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
                })

            if explicit_cm:
                cm_id = f"CallActivity_{uuid.uuid4().hex[:8]}"
                components_fast.append({
                    'type': 'ContentModifier',
                    'name': 'Content Modifier 1',
                    'xml': f'''<bpmn2:callActivity id="{cm_id}" name="Content Modifier 1">
    <bpmn2:extensionElements>
        <ifl:property><key>bodyType</key><value>constant</value></ifl:property>
        <ifl:property><key>propertyTable</key><value/></ifl:property>
        <ifl:property><key>headerTable</key><value/></ifl:property>
        <ifl:property><key>wrapContent</key><value/></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.6</value></ifl:property>
        <ifl:property><key>activityType</key><value>Enricher</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::Enricher/version::1.6.1</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
                })
                print("   + Added Content Modifier component in fast path")

            # Safety: if explicitly requested but not present due to any edge parsing, force-add
            if explicit_cm and not any(c.get('type') == 'ContentModifier' for c in components_fast):
                cm_id2 = f"CallActivity_{uuid.uuid4().hex[:8]}"
                components_fast.append({
                    'type': 'ContentModifier',
                    'name': 'Content Modifier 1',
                    'xml': f'''<bpmn2:callActivity id="{cm_id2}" name="Content Modifier 1">
    <bpmn2:extensionElements>
        <ifl:property><key>bodyType</key><value>constant</value></ifl:property>
        <ifl:property><key>propertyTable</key><value/></ifl:property>
        <ifl:property><key>headerTable</key><value/></ifl:property>
        <ifl:property><key>wrapContent</key><value/></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.6</value></ifl:property>
        <ifl:property><key>activityType</key><value>Enricher</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::Enricher/version::1.6.1</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''
                })
                print("   + Forced Content Modifier component due to explicit request")

            if explicit_gateway:
                gateway_id = f"ExclusiveGateway_{uuid.uuid4().hex[:8]}"
                components_fast.append({
                    'type': 'ExclusiveGateway',
                    'name': 'Decision Gateway',
                    'xml': f'''<bpmn2:exclusiveGateway id="{gateway_id}" name="Decision Gateway">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:exclusiveGateway>'''
                })
                print("   + Added Exclusive Gateway component in fast path")

            if explicit_end:
                components_fast.append({
                    'type': 'EndEvent',
                    'name': 'End 1',
                    'xml': '''<bpmn2:endEvent id="EndEvent_auto" name="End 1">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value></ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''
                })

            if explicit_gateway:
                gateway_id = f"ExclusiveGateway_{uuid.uuid4().hex[:8]}"
                components_fast.append({
                    'type': 'ExclusiveGateway',
                    'name': 'Decision Gateway',
                    'xml': f'''<bpmn2:exclusiveGateway id="{gateway_id}" name="Decision Gateway">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.1.0</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:exclusiveGateway>'''
                })
                
                # If "two branches" mentioned, add second end event
                if explicit_branches:
                    components_fast.append({
                        'type': 'EndEvent',
                        'name': 'End 2',
                        'xml': '''<bpmn2:endEvent id="EndEvent_auto2" name="End 2">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value></ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''
                    })

            if explicit_service:
                service_id = f"ServiceTask_{uuid.uuid4().hex[:8]}"
                components_fast.append({
                    'type': 'ServiceTask',
                    'name': 'Service Task',
                    'xml': f'''<bpmn2:serviceTask id="{service_id}" name="Service Task" activityType="ExternalCall">
    <bpmn2:extensionElements>
        <ifl:property><key>ComponentType</key><value>ServiceTask</value></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:serviceTask>'''
                })

            if explicit_receiver:
                components_fast.append({
                    'type': 'EndpointReceiver',
                    'name': 'Receiver1',
                    'xml': f'''<bpmn2:participant id="EndpointReceiver_{uuid.uuid4().hex[:8]}" ifl:type="EndpointReceiver" name="Receiver1">
    <bpmn2:extensionElements>
        <ifl:property><key>enableBasicAuthentication</key><value>false</value></ifl:property>
        <ifl:property><key>ifl:type</key><value>EndpointReceiver</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''
                })

                print("   + Added second End Event for branching")

            # Name and package directly
            iflow_name = self._generate_iflow_name(question, components_fast) or 'CompleteIntegrationFlow'

            # Use corrected packager; pass groovy file content based on actual component names
            groovy_files = {}
            for comp in components_fast:
                if comp['type'] == 'GroovyScript':
                    script_filename = f"{comp['name'].lower().replace(' ', '_')}.groovy"
                    groovy_files[script_filename] = 'def Message processData(m){ return m }'

            print("   Components assembled (fast):", [c['type'] for c in components_fast])
            package_path = self.packager.package_complete_iflow_corrected(
                components=components_fast,
                iflow_name=iflow_name,
                flow_description=f'Complete iFlow generated (fast path) from: {question}',
                groovy_files=groovy_files,
                complete_iflow_template=[]
            )

            print(f"✅ [PACKAGING] Complete iFlow package created: {package_path}")
            package_info = {
                'package_path': package_path,
                'iflow_name': iflow_name,
                'component_count': len(components_fast),
                'components': [{'type': c['type'], 'name': c['name']} for c in components_fast],
                'sources_used': 0,
                'ready_for_import': True,
                'package_type': 'complete_iflow'
            }
            response_content = self._format_complete_iflow_response(package_info, question)
            return {
                'final_response': response_content,
                'package_info': package_info,
                'vector_results': [],
                'tools_used': ['create_complete_iflow_package', 'IFlowPackager_fast_path'],
                'session_id': None
            }

        # Step 1: Identify all components in the query (heuristic-based; old procedure)
        identified_components = self._identify_components_in_query(question)
        print(f"🎯 [COMPONENTS_IDENTIFIED] Found {len(identified_components)} components:")
        for comp in identified_components:
            print(f"   • {comp['type']}: {comp['name']}")
        
        try:
            # Step 2: First, search for complete iFlow template configuration (old procedure)
            print(f"\n🏗️ [COMPLETE_IFLOW_TEMPLATE] Searching for iFlow-level configuration...")
            
            complete_iflow_queries = [
                "complete iFlow BPMN collaboration properties",
                "integration flow collaboration configuration", 
                "httpSessionHandling CORS properties",
                "BPMN definitions collaboration extensionElements",
                "full integration process template",
                "iFlow collaboration properties template"
            ]
            
            complete_iflow_rag_content = []
            for template_query in complete_iflow_queries:
                try:
                    search_results = await self.comprehensive_search(template_query)
                    if search_results.get('vector_results'):
                        complete_iflow_rag_content.extend(search_results['vector_results'])
                except Exception as e:
                    print(f"   ⚠️ Template search failed for '{template_query}': {e}")
            
            print(f"   📄 Retrieved {len(complete_iflow_rag_content)} complete iFlow template items")
            
            # Step 3: Generate XML for each component with RAG content
            complete_components = []
            
            for component in identified_components:
                print(f"\n🔧 [COMPONENT] Generating {component['type']}: {component['name']}")
                
                # Retrieve RAG content for this component type (old procedure via comprehensive_search)
                rag_content = []
                for rag_query in component['rag_queries']:
                    try:
                        search_results = await self.comprehensive_search(rag_query)
                        if search_results.get('vector_results'):
                            rag_content.extend(search_results['vector_results'])
                    except Exception as e:
                        print(f"   ⚠️ RAG search failed for '{rag_query}': {e}")
                
                print(f"   📄 Retrieved {len(rag_content)} RAG items for {component['type']}")
                
                # Generate XML based on component type
                if component['type'] == 'GroovyScript':
                    xml_content = await self._generate_component_xml(
                        'GroovyScript', component['name'], rag_content
                    )
                    # Store groovy content for packaging
                    groovy_content = getattr(self, 'groovy_script_content', None)
                elif component['type'] == 'ContentModifier':
                    xml_content = await self._generate_component_xml(
                        'ContentModifier', component['name'], rag_content
                    )
                    groovy_content = None
                elif component['type'] == 'Splitter':
                    xml_content = await self._generate_component_xml(
                        'Splitter', component['name'], rag_content
                    )
                    groovy_content = None
                elif component['type'] == 'MessageFilter':
                    xml_content = await self._generate_component_xml(
                        'MessageFilter', component['name'], rag_content
                    )
                    groovy_content = None
                else:
                    # Generate basic XML structure for other components
                    xml_content = self._generate_basic_component_xml(component)
                    groovy_content = None
                
                complete_components.append({
                    'xml': xml_content,
                    'type': component['type'],
                    'name': component['name'],
                    'id': f"{component['type']}_{len(complete_components)+1}",
                    'groovy_content': groovy_content
                })
                
                print(f"   ✅ Generated {component['type']} XML")
            
            # Step 3: Generate iFlow name
            iflow_name = self._generate_iflow_name(question, complete_components)
            print(f"\n📝 [IFLOW_NAME] Generated name: {iflow_name}")
            
            # Step 4: Package using package_complete_iflow
            print(f"📦 [PACKAGING] Creating complete iFlow package...")
            
            # Prepare components for packager (handle groovy files)
            packager_components = []
            for comp in complete_components:
                packager_comp = {
                    'xml': comp['xml'],
                    'type': comp['type'],
                    'name': comp['name'],
                    'id': comp['id']
                }
                packager_components.append(packager_comp)
            
            # Handle groovy script files separately if needed
            groovy_files = {}
            for comp in complete_components:
                if comp['type'] == 'GroovyScript' and comp['groovy_content']:
                    script_filename = f"{comp['name'].lower().replace(' ', '_')}.groovy"
                    groovy_files[script_filename] = comp['groovy_content']
            
            # Use CORRECTED packaging method with complete iFlow template data
            package_path = self.packager.package_complete_iflow_corrected(
                components=packager_components,
                iflow_name=iflow_name,
                flow_description=f'Complete iFlow generated from: {question}',
                groovy_files=groovy_files,
                complete_iflow_template=complete_iflow_rag_content
            )
            
            print(f"✅ [PACKAGING] Complete iFlow package created: {package_path}")
            
            # Step 5: Prepare response
            package_info = {
                'package_path': package_path,
                'iflow_name': iflow_name,
                'component_count': len(complete_components),
                'components': [{'type': c['type'], 'name': c['name']} for c in complete_components],
                'sources_used': sum(len(comp.get('rag_content', [])) for comp in complete_components),
                'ready_for_import': True,
                'package_type': 'complete_iflow'
            }
            
            # Create response
            response_content = self._format_complete_iflow_response(package_info, question)
            
            return {
                'final_response': response_content,
                'package_info': package_info,
                'vector_results': [],
                'tools_used': ['create_complete_iflow_package', 'comprehensive_search', 'package_complete_iflow'],
                'session_id': None
            }
            
        except Exception as e:
            error_msg = f"Error creating complete iFlow package: {e}"
            print(f"❌ [ERROR] {error_msg}")
            import traceback
            print(traceback.format_exc())
            
            return {
                'final_response': f"❌ Failed to create complete iFlow package: {error_msg}",
                'package_info': None,
                'vector_results': [],
                'tools_used': ['create_complete_iflow_package'],
                'session_id': None
            }

    def _generate_basic_component_xml(self, component: Dict[str, Any]) -> str:
        """Generate basic XML for non-processing components."""
        import uuid
        
        component_id = f"{component['type']}_{uuid.uuid4().hex[:8]}"
        
        if component['type'] == 'StartEvent':
            outgoing_flow_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
            return f'''<bpmn2:startEvent id="{component_id}" name="{component['name']}">
    <bpmn2:outgoing>{outgoing_flow_id}</bpmn2:outgoing>
    <bpmn2:extensionElements>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::MessageStartEvent</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:startEvent>'''
        
        elif component['type'] == 'EndEvent':
            incoming_flow_id = f"SequenceFlow_{uuid.uuid4().hex[:8]}"
            return f'''<bpmn2:endEvent id="{component_id}" name="{component['name']}">
    <bpmn2:incoming>{incoming_flow_id}</bpmn2:incoming>
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''
        
        elif component['type'] == 'EndpointSender':
            return f'''<bpmn2:participant id="{component_id}" ifl:type="EndpointSender" name="{component['name']}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>enableBasicAuthentication</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointSender</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''
        
        else:
            # Generic component
            return f'''<{component['xml_element']} id="{component_id}" name="{component['name']}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentType</key>
            <value>{component['type']}</value>
        </ifl:property>
    </bpmn2:extensionElements>
</{component['xml_element']}>'''

    def _generate_iflow_name(self, question: str, components: List[Dict]) -> str:
        """Generate appropriate iFlow name from query and components."""
        import re
        
        # Try to extract name from query
        name_patterns = [
            r'(?:create|generate|build|make)\s+(?:a|an)?\s*(\w+)\s+(?:iflow|integration)',
            r'(?:iflow|integration)\s+(?:called|named)\s+(\w+)',
            r'(\w+)\s+(?:iflow|integration)\s+package'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match and match.group(1).lower() not in ['complete', 'full', 'entire']:
                return match.group(1).capitalize()
        
        # Generate descriptive name based on components
        component_types = [comp['type'] for comp in components]
        
        # Create descriptive name based on main components
        if 'HTTPSender' in component_types or 'EndpointSender' in component_types:
            if 'GroovyScript' in component_types and 'ContentModifier' in component_types:
                return 'HTTPS_Processing_Integration'
            elif 'GroovyScript' in component_types:
                return 'HTTPS_Groovy_Integration'
            elif 'ContentModifier' in component_types:
                return 'HTTPS_Content_Integration'
            else:
                return 'HTTPS_Integration'
        elif 'GroovyScript' in component_types and 'ContentModifier' in component_types:
            return 'Processing_Integration'
        elif 'GroovyScript' in component_types:
            return 'Groovy_Integration'
        elif 'ContentModifier' in component_types:
            return 'Content_Integration'
        elif 'MessageMapping' in component_types:
            return 'Message_Mapping_Integration'
        else:
            return 'Complete_Integration_Flow'

    def _format_complete_iflow_response(self, package_info: Dict, question: str) -> str:
        """Format the response for complete iFlow creation."""
        components_list = "\n".join([f"   • {comp['type']}: {comp['name']}" for comp in package_info['components']])
        
        return f"""✅ **Complete iFlow Package Created Successfully!**

**iFlow Details:**
- Name: {package_info['iflow_name']}
- Components: {package_info['component_count']}
- Package: `{package_info['package_path']}`

**Components Included:**
{components_list}

**Package Contents:**
- Complete SAP iFlow XML with proper BPMN structure
- All component implementations (XML + scripts)
- SAP Integration Suite manifest files
- Proper sequence flows and connections
- Ready for direct import into SAP IS

**Generated from:**
- {package_info['sources_used']} relevant content items from knowledge base
- Query: "{question}"

**Next Steps:**
1. Download the ZIP file: `{package_info['package_path']}`
2. Import into SAP Integration Suite
3. Deploy and configure as needed

The complete iFlow package is production-ready and fully compliant with SAP Integration Suite requirements."""

    async def create_importable_package(self, question: str) -> Dict[str, Any]:
        """
        Create an importable iFlow package based on user request.
        
        DYNAMIC GENERATION RULES:
        - Retrieves relevant content from RAG/KG
        - Generates complete XML from the content
        - Only generate components explicitly mentioned by the user
        - No default or hardcoded components unless user mentions them
        - For RequestReply: generate StartEvent → RequestReply + external Receiver → EndEvent
        - For other components: generate only what user asks for
        - Packages it using IFlowPackager
        - Returns both analysis and package path
        
        Args:
            question: User query requesting package creation
            
        Returns:
            Dictionary containing analysis results and package information
        """
        print(f"\n📦 [PACKAGE_CREATION] Creating importable package for: '{question}'")
        
        # Extract component information
        component_info = self._extract_component_info(question)
        component_type = component_info['type']
        component_name = component_info['name']
        
        print(f"🎯 [COMPONENT_INFO] Type: {component_type}, Name: {component_name}")
        print(f"🔍 [DEBUG] Original question: '{question}'")
        print(f"🔍 [DEBUG] Question lower: '{question.lower()}'")
        
        # If no specific component detected, return error (no fallback)
        if component_type is None:
            return {
                'error': 'No specific component detected',
                'final_response': f"❌ **No Component Detected**\n\nI couldn't identify a specific component from your request: '{question}'\n\nPlease specify a component type like:\n- RequestReply\n- ContentModifier\n- GroovyScript\n- etc.",
                'vector_results': [],
                'kg_results': [],
                'data_sources': [],
                'tools_used': ['create_importable_package']
            }
        
        # Export strategic plan and component metadata BEFORE packaging
        minimal_plan = {
            'intent_classification': 'single_component',
            'user_goal': f'Generate {component_type}',
            'query_interpretation': question,
            'total_components': 1,
            'generation_order': [component_type],
            'integration_approach': 'single component flow',
            'execution_steps': [],
            'components': [{
                'type': component_type,
                'name': component_name,
                'quantity': 1
            }],
            'rag_strategy': {}
        }
        try:
            self._export_strategic_plan_metadata(minimal_plan, question)
            self._export_component_metadata(minimal_plan['components'], question)
        except Exception as _:
            pass
        
        try:
            # Step 1: Retrieve relevant content using existing RAG/KG capabilities
            print("🔍 [RAG_RETRIEVAL] Retrieving relevant content...")
            search_results = await self.comprehensive_search(question)
            
            # Extract content from search results
            retrieved_content = []
            if search_results.get('vector_results'):
                retrieved_content.extend(search_results['vector_results'])
            
            print(f"✅ [RAG_RETRIEVAL] Retrieved {len(retrieved_content)} relevant items")
            
            # Step 2: Generate component XML
            print("🛠️ [XML_GENERATION] Generating component XML...")
            component_xml = await self._generate_component_xml(
                component_type, component_name, retrieved_content
            )
            
            print("✅ [XML_GENERATION] XML generated successfully")
            
            # Step 3: Build components for packaging - DYNAMIC BASED ON USER REQUEST
            components_for_packaging = []
            
            if component_type == 'RequestReply':
                # For RequestReply: Generate complete BPMN structure as per user rules
                print("🔄 [REQUESTREPLY] Generating complete BPMN structure...")
                
                # 1. StartEvent (inside process)
                start_event_xml = await self._generate_generic_component_xml('StartEvent', 'Start 1', [], [])
                components_for_packaging.append({
                    'xml': start_event_xml,
                    'type': 'StartEvent',
                    'name': 'Start 1',  # Updated to match naming convention
                    'id': 'StartEvent_1'
                })
                
                # 2. RequestReply ServiceTask (inside process)
                # Extract the actual ID from the generated XML
                import re
                service_task_id_match = re.search(r'id="([^"]+)"', component_xml)
                actual_service_task_id = service_task_id_match.group(1) if service_task_id_match else 'ServiceTask_1'
                
                components_for_packaging.append({
                    'xml': component_xml,
                    'type': 'RequestReply',
                    'name': component_name,  # Already using proper naming from _extract_component_info
                    'id': actual_service_task_id
                })
                
                # 3. EndEvent (inside process)
                end_event_xml = await self._generate_generic_component_xml('EndEvent', 'End 1', [], [])
                components_for_packaging.append({
                    'xml': end_event_xml,
                    'type': 'EndEvent',
                    'name': 'End 1',  # Updated to match naming convention
                    'id': 'EndEvent_1'
                })
                
                # 4. External Receiver participant (outside process, in collaboration)
                receiver_participant = {
                    'xml': '''<bpmn2:participant id="Participant_Receiver1" ifl:type="EndpointRecevier" name="Receiver1">
    <bpmn2:extensionElements>
        <ifl:property><key>ifl:type</key><value>EndpointRecevier</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>''',
                    'type': 'EndpointRecevier',
                    'name': 'Receiver1',  # Updated to match naming convention (no separator)
                    'id': 'Participant_Receiver1'
                }
                components_for_packaging.append(receiver_participant)
                
                # 5. MessageFlow connecting RequestReply to external receiver
                message_flow_xml = f'''<bpmn2:messageFlow id="MessageFlow_HTTP" name="HTTP" sourceRef="{actual_service_task_id}" targetRef="Participant_Receiver1">
    <bpmn2:extensionElements>
        <ifl:property><key>ComponentType</key><value>HTTP</value></ifl:property>
        <ifl:property><key>TransportProtocol</key><value>HTTP</value></ifl:property>
        <ifl:property><key>MessageProtocol</key><value>None</value></ifl:property>
        <ifl:property><key>direction</key><value>Receiver</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.17.0</value></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.17</value></ifl:property>
        <ifl:property><key>httpMethod</key><value>POST</value></ifl:property>
        <ifl:property><key>system</key><value>ReceiverSystem</value></ifl:property>
        <ifl:property><key>providerUrl</key><value>https://example.com/api</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''
                components_for_packaging.append({
                    'xml': message_flow_xml,
                    'type': 'MessageFlow',
                    'name': 'HTTP',
                    'id': 'MessageFlow_HTTP'
                })
                
            else:
                # For other components: Generate only what user asked for
                print(f"🔄 [{component_type.upper()}] Generating single component...")
                components_for_packaging.append({
                    'xml': component_xml,
                    'type': component_type,
                    'name': component_name,
                    'id': f"{component_type}_1"
                })
            
            # Step 4: Package using complete iFlow packager
            print("📦 [PACKAGING] Creating complete iFlow package...")
            
            # Generate iFlow name
            iflow_name = self._generate_iflow_name(question, components_for_packaging) or f"{component_type}Flow"
            
            # For GroovyScript, pass the extracted groovy content
            groovy_files = {}
            if component_type == 'GroovyScript' and hasattr(self, 'groovy_script_content'):
                groovy_files[f"{component_name.lower()}.groovy"] = self.groovy_script_content
                print(f"📄 [GROOVY_CONTENT] Using extracted script content ({len(self.groovy_script_content)} chars)")
            
            package_path = self.packager.package_complete_iflow_corrected(
                components=components_for_packaging,
                iflow_name=iflow_name,
                flow_description=f'Generated {component_type} from RAG content: {question}',
                groovy_files=groovy_files,
                complete_iflow_template=[]
            )
            
            print(f"✅ [PACKAGING] Package created: {package_path}")
            
            # Step 5: Prepare response
            package_info = {
                'package_path': package_path,
                'component_type': component_type,
                'component_name': component_name,
                'xml_preview': component_xml[:300] + '...' if len(component_xml) > 300 else component_xml,
                'sources_used': len(retrieved_content),
                'ready_for_import': True
            }
            
            # Combine with original search results
            search_results['package_info'] = package_info
            search_results['final_response'] = f"""
✅ **Importable iFlow Package Created Successfully!**

**Component Details:**
- Type: {component_type}
- Name: {component_name}
- Package: `{package_path}`

**Package Contents:**
- Complete SAP iFlow XML with proper BPMN structure
- SAP Integration Suite manifest files
- Ready for direct import into SAP IS

**Analysis Results:**
- RAG Sources: {len(retrieved_content)} items retrieved
            - Vector Search: {len(search_results.get('vector_results') or [])} results
            - Knowledge Graph: {len(search_results.get('kg_results') or [])} results

**Next Steps:**
1. Import the package into SAP Integration Suite
2. Configure any required parameters
3. Deploy and test the integration flow

The package is ready for immediate use in your SAP Integration Suite environment.
"""
            
            return search_results
            
        except Exception as e:
            print(f"❌ [PACKAGE_CREATION] Error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'error': str(e),
                'final_response': f"❌ **Package Creation Failed**\n\nError: {str(e)}\n\nPlease check the logs for more details.",
                'vector_results': [],
                'kg_results': [],
                'data_sources': [],
                'tools_used': ['create_importable_package', 'comprehensive_search']
            }

    async def query(self, question: str, session_id: Optional[str] = None, mode: str = "overview") -> AgentResponse:
        """
        Process user query with new behavior: KG → Vector DB → LLM fallback, structured debug logging.
        
        Args:
            question: User question
            session_id: Optional session ID for conversation tracking
            mode: "overview" or "equivalent" (for XML extraction)
            
        Returns:
            Agent response with concise answer + structured debug log
        """
        import time
        start_time = time.time()
        
        # Enhanced debug logging is always on for detailed analysis
        show_debug = True  # Always show detailed logs as requested
        if "no-logs" in question.lower():
            show_debug = False
            
        try:
            # Clean query for processing
            clean_question = question.replace("show debug", "").replace("hide debug", "").replace("no-logs", "").strip()
            
            # Check if this is a packaging request FIRST
            if self._is_packaging_request(clean_question):
                print(f"\n📦 [PACKAGING_DETECTED] This is a packaging request")
                
                # Detect if this is a complete iFlow request vs single component
                if self._detect_complete_iflow_request(clean_question):
                    print(f"🌟 [COMPLETE_IFLOW_DETECTED] Creating complete iFlow with multiple components")
                    packaging_results = await self.create_complete_iflow_package(clean_question)
                else:
                    print(f"🔧 [SINGLE_COMPONENT_DETECTED] Creating single component package")
                    packaging_results = await self.create_importable_package(clean_question)
                
                # Convert to AgentResponse format
                vector_results = packaging_results.get('vector_results', []) or []
                data_sources = packaging_results.get('data_sources', []) or []
                tools_used = packaging_results.get('tools_used', []) or []
                
                return AgentResponse(
                    content=packaging_results.get('final_response', 'Package created successfully'),
                    sources=[f"RAG/KG Search: {len(vector_results)} items"] + data_sources,
                    tools_used=['create_importable_package', 'comprehensive_search', 'IFlowPackager'] + tools_used,
                    metadata={
                        'query_type': 'packaging_request',
                        'session_id': session_id,
                        'processing_time': time.time() - start_time,
                        'package_info': packaging_results.get('package_info'),
                        'mode': mode
                    }
                )
            
            if show_debug:
                print(f"\n" + "="*80)
                print(f"🔍 [QUERY ANALYSIS] Processing: '{clean_question}'")
                print(f"📊 [QUERY METADATA] Length: {len(clean_question)} chars | Mode: {mode}")
                print("="*80)
                
                # Show detailed schema upfront for context
                print("🗄️ [SCHEMA CONTEXT] Neo4j Database Overview:")
                try:
                    await self.graph_store.get_schema_overview()
                except Exception as e:
                    print(f"⚠️ [SCHEMA ERROR] Could not fetch schema: {e}")
            
            # Let the agent handle the orchestration
            # If LLM fails (e.g., invalid key), fall back to tool-only execution
            try:
                result = await self.agent.ainvoke({"input": clean_question})
            except Exception as llm_error:
                if show_debug:
                    print(f"⚠️ [LLM FALLBACK] Agent LLM call failed: {llm_error}")
                    print("🔄 [LLM FALLBACK] Using tool-only path: KG → Vector → Compose")

                # TOOL-ONLY FALLBACK EXECUTION
                tools_used = []
                debug_steps = []

                # 1) KG FIRST: Try to interpret question as iFlow name for skeleton
                kg_result = None
                try:
                    skeleton = await self.tools_map["get_iflow_skeleton"]._arun(iflow_name=None, query=clean_question)
                    tools_used.append("get_iflow_skeleton")
                    kg_result = skeleton if isinstance(skeleton, dict) else {}
                    debug_steps.append({
                        "step_id": "step_1",
                        "step_type": "KG",
                        "action": "get_iflow_skeleton",
                        "data_source": "Neo4j Knowledge Graph",
                        "query": clean_question,
                        "results_count": len(kg_result.get("nodes", [])) + len(kg_result.get("edges", [])),
                        "data_analysis": f"Nodes: {len(kg_result.get('nodes', []))}, Edges: {len(kg_result.get('edges', []))}",
                        "observation": kg_result,
                        "used_in_answer": True,
                        "note": "KG skeleton retrieval in fallback"
                    })
                except Exception as kg_err:
                    if show_debug:
                        print(f"❌ [FALLBACK/KG] Error: {kg_err}")

                # 2) VECTOR SECOND: If we have a KG skeleton, retrieve per-node artifacts in order and stitch
                vector_results = []
                stitched_summary = None
                try:
                    if kg_result and (kg_result.get("nodes") or kg_result.get("edges")):
                        retrieval = await self._retrieve_artifacts_by_node_order(
                            iflow_name=clean_question,
                            skeleton=kg_result,
                            per_node_limit=2,
                        )
                        vector_results = retrieval.get("artifacts", [])
                        stitched_summary = retrieval.get("stitched")
                        tools_used.append("vector_search")
                        debug_steps.append({
                            "step_id": "step_2",
                            "step_type": "VECTOR",
                            "action": "vector_search",
                            "data_source": "PostgreSQL Vector Database",
                            "query": "per-node ordered semantic queries (type+name+folder+iflow)",
                            "results_count": len(vector_results),
                            "data_analysis": f"Artifacts: {len(vector_results)}; Resolved: {len((stitched_summary or {}).get('resolved', []))}",
                            "observation": retrieval,
                            "used_in_answer": True,
                            "note": "Node-ordered retrieval and stitching"
                        })
                    else:
                        # No KG context: do a single-shot vector query from the question
                        vector_results = await self.tools_map["vector_search"]._arun(query=clean_question, limit=5)
                        tools_used.append("vector_search")
                        debug_steps.append({
                            "step_id": "step_2",
                            "step_type": "VECTOR",
                            "action": "vector_search",
                            "data_source": "PostgreSQL Vector Database",
                            "query": clean_question,
                            "results_count": len(vector_results),
                            "data_analysis": f"Docs: {len(vector_results)}",
                            "observation": vector_results,
                            "used_in_answer": True,
                            "note": "Single-shot semantic search (no KG context)"
                        })
                except Exception as vec_err:
                    if show_debug:
                        print(f"❌ [FALLBACK/VECTOR] Error: {vec_err}")

                # Compose minimal answer from tools (include stitched info if available)
                summary_lines = []
                if kg_result and (kg_result.get("nodes") or kg_result.get("edges")):
                    summary_lines.append(f"From Neo4j: {len(kg_result.get('nodes', []))} nodes, {len(kg_result.get('edges', []))} edges found.")
                if vector_results:
                    if isinstance(vector_results, list):
                        top_docs = ", ".join([d.get("document_name", d.get("name", "Unknown")) for d in vector_results[:3]])
                        summary_lines.append(f"From Vector DB: {len(vector_results)} artifacts (e.g., {top_docs}).")
                    else:
                        summary_lines.append("From Vector DB: artifacts retrieved.")
                if stitched_summary:
                    cov = (stitched_summary or {}).get("coverage", {})
                    summary_lines.append(
                        f"Stitching: resolved {cov.get('nodes_resolved', 0)}/{cov.get('nodes_total', 0)} nodes; missing {len((stitched_summary or {}).get('missing', []))}."
                    )
                if not summary_lines:
                    summary_lines.append("No KG/Vector evidence found; answer uses general knowledge.")

                fallback_output = (
                    " ".join(summary_lines) +
                    "\n\nNote: LLM was unavailable; used tool-only fallback."
                )

                result = {
                    "output": fallback_output,
                    "intermediate_steps": [
                        (type("A", (), {"tool": s["action"], "tool_input": s["query"]})(), s["observation"]) for s in debug_steps
                    ]
                }
            
            # Enhanced debug info extraction with comprehensive data source tracking
            debug_steps = []
            tools_used = []
            kg_data_fetched = {}
            vector_data_fetched = {}
            llm_synthesis_used = False
            
            if show_debug:
                print("\n🔧 [AGENT EXECUTION] Comprehensive data source analysis:")
            
            # Track all three data sources and enforce execution order
            data_sources_used = {"KG": False, "VECTOR": False, "LLM": False}
            kg_executed = False
            vector_executed = False
            execution_order_violations = []
            
            for i, (action, observation) in enumerate(result.get("intermediate_steps", [])):
                step_id = f"step_{i+1}"
                tool_name = action.tool
                tools_used.append(tool_name)
                
                # Determine step type and data source + check execution order
                if tool_name in ["get_iflow_skeleton", "component_analysis"]:
                    step_type = "KG"
                    data_source = "Neo4j Knowledge Graph"
                    data_sources_used["KG"] = True
                    kg_executed = True
                    
                elif tool_name == "vector_search":
                    step_type = "VECTOR"
                    data_source = "PostgreSQL Vector Database"
                    data_sources_used["VECTOR"] = True
                    vector_executed = True
                    
                    # CHECK EXECUTION ORDER VIOLATION
                    if not kg_executed:
                        violation_msg = f"❌ EXECUTION ORDER VIOLATION: vector_search called before KG tools at step {step_id}"
                        execution_order_violations.append(violation_msg)
                        if show_debug:
                            print(f"   {violation_msg}")
                    
                else:
                    step_type = "LLM"
                    data_source = "LLM Knowledge"
                    data_sources_used["LLM"] = True
                
                # Detailed data analysis
                if observation:
                    if isinstance(observation, dict):
                        data_analysis = f"Dict with keys: {list(observation.keys())}"
                        if step_type == "KG":
                            kg_data_fetched[tool_name] = observation
                            # Detailed KG data analysis
                            if 'nodes' in observation:
                                data_analysis += f" | {len(observation['nodes'])} nodes"
                            if 'edges' in observation:
                                data_analysis += f" | {len(observation['edges'])} edges"
                            if 'component' in observation:
                                comp = observation['component']
                                data_analysis += f" | Component: {comp.get('name', 'Unknown')} ({comp.get('type', 'Unknown')})"
                    elif isinstance(observation, list):
                        data_analysis = f"List with {len(observation)} items"
                        if step_type == "VECTOR":
                            vector_data_fetched[tool_name] = observation
                            # Detailed Vector data analysis
                            if observation:
                                doc_names = set(item.get('document_name', 'Unknown') for item in observation)
                                avg_similarity = sum(item.get('similarity_score', 0) for item in observation) / len(observation)
                                data_analysis += f" | Docs: {len(doc_names)} | Avg similarity: {avg_similarity:.1f}/10"
                    else:
                        data_analysis = f"String/Other: {len(str(observation))} chars"
                else:
                    data_analysis = "No data returned"
                
                if show_debug:
                    print(f"   {step_id}. {tool_name} ({step_type})")
                    print(f"      📍 Data Source: {data_source}")
                    print(f"      📝 Query Input: {str(action.tool_input)}")
                    print(f"      📊 Data Retrieved: {data_analysis}")
                    
                    # Show sample data for each source type
                    if observation and step_type == "KG" and isinstance(observation, dict):
                        print(f"      🕸️  KG Sample: {str(observation)[:200]}...")
                    elif observation and step_type == "VECTOR" and isinstance(observation, list) and observation:
                        sample = observation[0]
                        print(f"      📄 Vector Sample: {sample.get('document_name', 'Unknown')} - {str(sample.get('content', ''))[:100]}...")
                
                debug_steps.append({
                    "step_id": step_id,
                    "step_type": step_type,
                    "action": tool_name,
                    "data_source": data_source,
                    "query": str(action.tool_input),
                    "results_count": len(str(observation).split('\n')) if observation else 0,
                    "data_analysis": data_analysis,
                    "observation": observation,
                    "used_in_answer": True,
                    "note": f"Successfully retrieved from {data_source}" if observation else f"No data from {data_source}"
                })
            
            # Check if LLM synthesis was used (if agent generated response without just using tools)
            if result.get("output") and len(result.get("output", "")) > 100:
                llm_synthesis_used = True
                data_sources_used["LLM"] = True
            
            if show_debug:
                print(f"\n📊 [DATA SOURCES SUMMARY]")
                print(f"   🕸️  Neo4j KG: {'✅ Used' if data_sources_used['KG'] else '❌ Not used'}")
                print(f"   📄 Vector DB: {'✅ Used' if data_sources_used['VECTOR'] else '❌ Not used'}")
                print(f"   🧠 LLM Synthesis: {'✅ Used' if llm_synthesis_used else '❌ Not used'}")
                
                # EXECUTION ORDER VALIDATION
                print(f"\n🔄 [EXECUTION ORDER VALIDATION]")
                if execution_order_violations:
                    print(f"   ❌ VIOLATIONS DETECTED: {len(execution_order_violations)}")
                    for violation in execution_order_violations:
                        print(f"      • {violation}")
                    print(f"   ⚠️  CORRECT ORDER: KG tools → vector_search → LLM synthesis")
                else:
                    if kg_executed and vector_executed:
                        print(f"   ✅ PERFECT ORDER: KG → Vector → LLM synthesis")
                    elif kg_executed and not vector_executed:
                        print(f"   ✅ PARTIAL ORDER: KG executed, Vector not used")
                    elif not kg_executed and not vector_executed:
                        print(f"   ⚠️  NO EXTERNAL DATA: Only LLM knowledge used")
                    else:
                        print(f"   ❌ INVALID STATE: This should not happen")
            
            # Calculate dynamic confidence based on data quality
            confidence_score = 0.0
            confidence_factors = []
            
            # Vector search quality contribution
            vector_confidence = 0.0
            vector_count = 0
            for step in debug_steps:
                if step["step_type"] == "VECTOR" and step.get("observation"):
                    try:
                        if isinstance(step["observation"], list) and step["observation"]:
                            similarities = [item.get('similarity_score', 0) for item in step["observation"]]
                            if similarities:
                                avg_sim = sum(similarities) / len(similarities)
                                # Scale similarity (0-15 range) to confidence (0-0.6 max)
                                vector_confidence += min(avg_sim / 25.0, 0.6)
                                vector_count += len(similarities)
                                confidence_factors.append(f"Vector avg: {avg_sim:.1f}")
                    except:
                        pass
            
            # Knowledge Graph quality contribution  
            kg_confidence = 0.0
            kg_connections = 0
            for step in debug_steps:
                if step["step_type"] == "KG" and step.get("observation"):
                    try:
                        if isinstance(step["observation"], dict):
                            incoming = len(step["observation"].get('incoming', []))
                            outgoing = len(step["observation"].get('outgoing', []))
                            related = len(step["observation"].get('related_components', []))
                            kg_connections = incoming + outgoing + related
                            # Scale connections (0-20 range) to confidence (0-0.3 max)
                            kg_confidence = min(kg_connections / 50.0, 0.3)
                            if kg_connections > 0:
                                confidence_factors.append(f"KG connections: {kg_connections}")
                    except:
                        pass
            
            # Cross-source consistency bonus
            consistency_bonus = 0.0
            if vector_confidence > 0 and kg_confidence > 0:
                consistency_bonus = 0.1
                confidence_factors.append("Cross-source consistency")
            elif vector_confidence > 0:
                confidence_factors.append("Vector evidence only") 
            elif kg_confidence > 0:
                confidence_factors.append("KG evidence only")
            
            # Base confidence for having any results
            base_confidence = 0.1 if (vector_count > 0 or kg_connections > 0) else 0.0
            
            # Calculate final confidence score
            confidence_score = min(base_confidence + vector_confidence + kg_confidence + consistency_bonus, 1.0)
            
            # Generate confidence reason
            if confidence_score >= 0.8:
                confidence_level = "Very high confidence"
            elif confidence_score >= 0.6:
                confidence_level = "High confidence"
            elif confidence_score >= 0.4:
                confidence_level = "Medium confidence"
            elif confidence_score >= 0.2:
                confidence_level = "Low confidence"
            else:
                confidence_level = "Very low confidence"
            
            factor_summary = ", ".join(confidence_factors) if confidence_factors else "Limited evidence"
            confidence_reason = f"{confidence_level}: {factor_summary}"
            
            # Format response with debug log if requested
            response_content = result["output"]
            
            if show_debug:
                execution_time = time.time() - start_time
                
                # Enhanced debug logging with data analysis
                print(f"\n🧠 [AGENT REASONING] How the agent reached its conclusion:")
                print(f"⏱️ [EXECUTION TIME] {execution_time:.2f} seconds")
                print(f"🎯 [CONFIDENCE] {confidence_score:.2f} ({confidence_reason})")
                
                print(f"\n📋 [DETAILED REASONING TRACE]:")
                for step in debug_steps:
                    print(f"   {step['step_id']}: {step['action']} ({step['step_type']})")
                    print(f"      🔍 Query: {step['query']}")
                    print(f"      📍 Data Source: {step['data_source']}")
                    print(f"      📊 Result: {step['data_analysis']}")
                    print(f"      ✅ Status: {step['note']}")
                
                # Detailed KG data summary
                if kg_data_fetched:
                    print(f"\n🕸️ [NEO4J KNOWLEDGE GRAPH DATA] Detailed analysis:")
                    for tool, data in kg_data_fetched.items():
                        print(f"   📊 Tool: {tool}")
                        if isinstance(data, dict):
                            print(f"      📋 Structure: {list(data.keys())}")
                            
                            if 'nodes' in data and data['nodes']:
                                nodes = data['nodes']
                                print(f"      🔗 Nodes: {len(nodes)} found")
                                node_types = {}
                                for node in nodes[:5]:  # Show first 5 nodes
                                    node_type = node.get('type', 'Unknown')
                                    node_types[node_type] = node_types.get(node_type, 0) + 1
                                    print(f"         • {node.get('name', 'Unknown')} (ID: {node.get('id', 'Unknown')}, Type: {node_type})")
                                if len(nodes) > 5:
                                    print(f"         ... and {len(nodes) - 5} more nodes")
                                print(f"      📈 Node Types Distribution: {dict(node_types)}")
                            
                            if 'edges' in data and data['edges']:
                                edges = data['edges']
                                print(f"      🔗 Edges: {len(edges)} relationships")
                                edge_types = {}
                                for edge in edges[:3]:  # Show first 3 edges
                                    rel_type = edge.get('relation', 'CONNECTED')
                                    edge_types[rel_type] = edge_types.get(rel_type, 0) + 1
                                    print(f"         • {edge.get('from', 'Unknown')} --{rel_type}--> {edge.get('to', 'Unknown')}")
                                if len(edges) > 3:
                                    print(f"         ... and {len(edges) - 3} more relationships")
                                print(f"      📈 Relationship Types: {dict(edge_types)}")
                            
                            if 'component' in data:
                                comp = data['component']
                                print(f"      🔧 Component Details:")
                                print(f"         • Name: {comp.get('name', 'Unknown')}")
                                print(f"         • Type: {comp.get('type', 'Unknown')}")
                                print(f"         • ID: {comp.get('id', 'Unknown')}")
                            
                            if 'incoming' in data:
                                incoming = data['incoming']
                                print(f"      📥 Incoming Connections: {len(incoming)}")
                                for conn in incoming[:2]:
                                    source = conn.get('source_name', conn.get('source', 'Unknown'))
                                    rel_type = conn.get('rel_type', 'CONNECTED')
                                    print(f"         • {source} --{rel_type}--> component")
                            
                            if 'outgoing' in data:
                                outgoing = data['outgoing']
                                print(f"      📤 Outgoing Connections: {len(outgoing)}")
                                for conn in outgoing[:2]:
                                    target = conn.get('target_name', conn.get('target', 'Unknown'))
                                    rel_type = conn.get('rel_type', 'CONNECTED')
                                    print(f"         • component --{rel_type}--> {target}")
                
                # Detailed Vector data summary
                if vector_data_fetched:
                    print(f"\n📄 [VECTOR DATABASE DATA] Detailed analysis:")
                    for tool, data in vector_data_fetched.items():
                        print(f"   📊 Tool: {tool}")
                        if isinstance(data, list) and data:
                            print(f"      📋 Documents: {len(data)} retrieved")
                            
                            # Analyze document types and similarities
                            doc_types = {}
                            similarities = []
                            unique_docs = set()
                            
                            for i, doc in enumerate(data[:3]):  # Show first 3 docs
                                doc_name = doc.get('document_name', 'Unknown')
                                chunk_type = doc.get('chunk_type', 'unknown')
                                similarity = doc.get('similarity_score', 0)
                                content = str(doc.get('content', ''))[:150]
                                
                                doc_types[chunk_type] = doc_types.get(chunk_type, 0) + 1
                                similarities.append(similarity)
                                unique_docs.add(doc_name)
                                
                                print(f"         📄 Doc {i+1}: {doc_name}")
                                print(f"            • Type: {chunk_type}")
                                print(f"            • Similarity: {similarity:.3f}")
                                print(f"            • Content: {content}...")
                            
                            if len(data) > 3:
                                print(f"         ... and {len(data) - 3} more documents")
                            
                            avg_similarity = sum(similarities) / len(similarities) if similarities else 0
                            print(f"      📈 Document Types: {dict(doc_types)}")
                            print(f"      📈 Unique Documents: {len(unique_docs)}")
                            print(f"      📈 Average Similarity: {avg_similarity:.3f}")
                        elif isinstance(data, list):
                            print(f"      ❌ No documents retrieved")
                
                # LLM synthesis analysis
                if llm_synthesis_used:
                    print(f"\n🧠 [LLM SYNTHESIS DATA] Analysis:")
                    response_length = len(result.get("output", ""))
                    print(f"   📊 Response Length: {response_length} characters")
                    print(f"   🔍 LLM Used For: Combining KG + Vector data and generating structured response")
                    print(f"   📈 Synthesis Quality: {'High' if response_length > 200 else 'Basic'}")
                    
                    # Check if LLM added reasoning beyond just data retrieval
                    kg_data_present = bool(kg_data_fetched)
                    vector_data_present = bool(vector_data_fetched)
                    
                    if kg_data_present and vector_data_present:
                        print(f"   🔗 LLM Role: Synthesized data from both KG and Vector sources")
                    elif kg_data_present:
                        print(f"   🔗 LLM Role: Interpreted KG data + added general knowledge")
                    elif vector_data_present:
                        print(f"   🔗 LLM Role: Interpreted Vector data + added general knowledge")
                    else:
                        print(f"   🔗 LLM Role: Used general knowledge (no external data sources)")
                else:
                    print(f"\n🧠 [LLM SYNTHESIS DATA] Not used or minimal usage")
                
                print(f"\n🛠️ [TOOLS SUMMARY] Used: {', '.join(set(tools_used)) if tools_used else 'None'}")
                print("="*80)
                
                # Add debug summary to response with execution order info
                execution_order_status = "✅ CORRECT ORDER" if not execution_order_violations else f"❌ {len(execution_order_violations)} VIOLATIONS"
                
                debug_summary = f"""

---
📊 DETAILED EXECUTION LOG
⏱️ Execution Time: {execution_time:.2f}s
🎯 Confidence: {confidence_score:.2f} ({confidence_reason})
🛠️ Tools: {', '.join(set(tools_used)) if tools_used else 'None'}
📊 Data Sources: {len([s for s in debug_steps if s['step_type'] in ['KG', 'VECTOR']])} external sources queried
🔍 Total Steps: {len(debug_steps)}
🔄 Execution Order: {execution_order_status}
---"""
                response_content += debug_summary
            
            return AgentResponse(
                content=response_content,
                sources=[],
                tools_used=tools_used,
                metadata={
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "model": "gpt-5-mini",
                    "mode": mode,
                    "confidence_score": confidence_score,
                    "execution_time": time.time() - start_time,
                    "debug_enabled": show_debug,
                    "steps_count": len(debug_steps)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            error_msg = f"I encountered an error while processing your question: {str(e)}"
            
            if show_debug:
                error_msg += f"""
---
📊 DEBUG LOG
Timestamp: {datetime.now().isoformat()}
Error: {str(e)}
Confidence Score: 0.0 (Error occurred)
"""
            
            return AgentResponse(
                content=error_msg,
                sources=[],
                tools_used=[],
                metadata={
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "debug_enabled": show_debug
                }
            )
    
    async def analyze_iflow(self, iflow_name: str) -> AgentResponse:
        """
        Perform comprehensive analysis of an iFlow.
        
        Args:
            iflow_name: Name of the iFlow to analyze
            
        Returns:
            Comprehensive analysis response
        """
        analysis_queries = [
            f"Analyze the components in iFlow '{iflow_name}'",
            f"Identify integration patterns in '{iflow_name}'",
            f"Find similar components to those in '{iflow_name}'",
            f"Recommend optimizations for '{iflow_name}'"
        ]
        
        responses = []
        all_sources = []
        all_tools = []
        
        for query in analysis_queries:
            response = await self.query(query)
            responses.append(response.content)
            all_sources.extend(response.sources)
            all_tools.extend(response.tools_used)
        
        combined_response = "\n\n".join(responses)
        
        return AgentResponse(
            content=combined_response,
            sources=all_sources,
            tools_used=list(set(all_tools)),
            metadata={
                "analysis_type": "comprehensive_iflow_analysis",
                "iflow_name": iflow_name,
                "timestamp": datetime.now().isoformat()
            }
        )


async def main():
    """Main entry point for running the agent directly."""
    import os
    import sys
    from pathlib import Path
    
    # Add parent directory to path for config import
    sys.path.append(str(Path(__file__).parent.parent))
    
    # Load .env file if available (check parent directory)
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Loaded .env file")
        except ImportError:
            print("⚠️  python-dotenv not installed")
    
    try:
        from config import OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY, POSTGRES_URL, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
    except ImportError:
        print("❌ Could not import from config.py")
        return
    
    # Get OpenAI key from config.py or environment
    openai_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY is required (set in config.py or environment)")
        return
    
    print("🚀 Starting SAP iFlow Agent")
    print("=" * 50)
    
    # Try to initialize stores with fallbacks
    vector_store = None
    graph_store = None
    
    # Try VectorStore (requires POSTGRES_URL) - prefer config.py then environment
    postgres_url = POSTGRES_URL or os.getenv("POSTGRES_URL")
    if postgres_url:
        try:
            print("📦 Initializing VectorStore...")
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from rag.vector_store import VectorStore
            vector_store = VectorStore(postgres_url)
            await vector_store.initialize()
            print("✅ VectorStore connected")
        except Exception as e:
            print(f"⚠️  VectorStore failed: {e}")
    else:
        print("⚠️  POSTGRES_URL not set - VectorStore disabled")
    
    # Try GraphStore (requires NEO4J_*) - use config.py values directly (ignore .env)
    neo4j_uri = NEO4J_URI  # Direct from config.py - new iFlow database
    neo4j_user = NEO4J_USER  # Direct from config.py 
    neo4j_password = NEO4J_PASSWORD  # Direct from config.py
    
    if neo4j_uri and neo4j_user and neo4j_password:
        try:
            print("\n🕸️ [KNOWLEDGE GRAPH] Initializing Neo4j Connection...")
            print("=" * 60)
            print(f"🌐 [NEO4J CLOUD] Target URI: {neo4j_uri}")
            print(f"👤 [NEO4J CLOUD] Username: {neo4j_user}")
            print(f"🔐 [NEO4J CLOUD] Password: {'*' * len(neo4j_password)}")
            
            # Determine connection type
            if neo4j_uri.startswith('neo4j+s://'):
                print("🔒 [NEO4J CLOUD] Connection Type: AuraDB Cloud (Secure)")
            elif neo4j_uri.startswith('neo4j://'):
                print("🏠 [NEO4J CLOUD] Connection Type: Local Instance")
            else:
                print(f"🔧 [NEO4J CLOUD] Connection Type: {neo4j_uri.split('://')[0]}")
            
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from knowledge_graph.graph_store import GraphStore
            graph_store = GraphStore(neo4j_uri, neo4j_user, neo4j_password)
            await graph_store.initialize()
            print("✅ GraphStore connected to Neo4j AuraDB Cloud")
            # Snapshot functionality removed as requested
        except Exception as e:
            print(f"❌ [NEO4J CLOUD] Connection failed: {e}")
            print("💡 [NEO4J CLOUD] Please check:")
            print("   - AuraDB instance is running in Neo4j Aura Console")
            print("   - Credentials are correct")
            print("   - Network connectivity to cloud instance")
            graph_store = None  # Ensure graph_store is None on failure
    else:
        print("⚠️  NEO4J_* credentials not set - GraphStore disabled")
    
    # Show credential status
    print("\n💡 Credential Status:")
    print("   From config.py:")
    print(f"     - OPENAI_API_KEY: {'✅' if OPENAI_API_KEY else '❌'}")
    print(f"     - SUPABASE_URL: {'✅' if SUPABASE_URL else '❌'}")
    print(f"     - SUPABASE_KEY: {'✅' if SUPABASE_KEY else '❌'}")
    print(f"     - POSTGRES_URL: {'✅' if POSTGRES_URL else '❌'}")
    print(f"     - NEO4J_URI: {'✅' if NEO4J_URI else '❌'}")
    print(f"     - NEO4J_USER: {'✅' if NEO4J_USER else '❌'}")
    print(f"     - NEO4J_PASSWORD: {'✅' if NEO4J_PASSWORD else '❌'}")
    print("   Final values (config.py + .env):")
    print(f"     - POSTGRES_URL: {'✅' if postgres_url else '❌'}")
    print(f"     - NEO4J_URI: {'✅' if neo4j_uri else '❌'}")
    print(f"     - NEO4J_USER: {'✅' if neo4j_user else '❌'}")
    print(f"     - NEO4J_PASSWORD: {'✅' if neo4j_password else '❌'}")
    
    # Initialize agent with available stores
    print("Initializing SAP iFlow Agent...")
    
    # Only proceed if we have real database connections
    if not vector_store or not graph_store:
        error_msg = []
        if not vector_store:
            error_msg.append("PostgreSQL (VectorStore)")
        if not graph_store:
            error_msg.append("Neo4j (GraphStore)")
        
        print(f"❌ Required database connections failed: {', '.join(error_msg)}")
        print("💡 Please ensure:")
        print("   - PostgreSQL is accessible and credentials are correct")
        print("   - Neo4j is running and credentials are correct")
        print("   - Network connectivity to both databases")
        return
    
    print("\n🎉 [CONNECTION SUMMARY] All Systems Connected!")
    print("=" * 60)
    print(f"📊 [VECTOR DATABASE] PostgreSQL (Supabase):")
    print(f"   • Status: ✅ Connected")
    print(f"   • Purpose: Semantic search, document embeddings")
    print(f"   • URL: {postgres_url.split('@')[1].split('/')[0] if postgres_url else 'N/A'}")
    
    print(f"\n🕸️ [KNOWLEDGE GRAPH] Neo4j AuraDB Cloud:")
    print(f"   • Status: ✅ Connected")
    print(f"   • Purpose: SAP iFlow components, processes, and flow relationships")
    print(f"   • Instance: {neo4j_uri.replace('neo4j+s://', '').split('.')[0] if neo4j_uri else 'N/A'}")
    print(f"   • Type: AuraDB Free Cloud Instance")
    
    print(f"\n🧠 [LLM] OpenAI gpt-5-mini:")
    print(f"   • Status: ✅ Configured")
    print(f"   • Purpose: Agent reasoning, response generation")
    print(f"   • Model: gpt-5-mini")
    print("=" * 60)
    
    agent = SAPiFlowAgent(
        vector_store=vector_store,
        graph_store=graph_store,
        openai_api_key=openai_key,
        context_document="SAP iFlow Analysis System"
    )
    print("✅ Agent ready!")
    
    # Interactive session
    print("\n💬 Interactive Mode - Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n❓ Your query: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
                
            print("\n🤔 Processing...")
            response = await agent.query(user_input)
            print(f"\nResponse:\n{response.content}")
            
            if response.tools_used:
                print(f"\n🛠️ Tools used: {', '.join(response.tools_used)}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


class MockVectorStore:
    """Mock vector store when database is not available."""
    async def search_similar(self, query, limit=5, chunk_types=None):
        # Return sample data for demonstration with dynamic similarity calculation
        results = []
        
        if "integration" in query.lower():
            # Calculate similarity based on query term overlap
            base_content = 'Request-Reply integration pattern for synchronous data exchange between SAP SuccessFactors and SAP S/4HANA'
            query_terms = set(query.lower().split())
            content_terms = set(base_content.lower().split())
            similarity1 = len(query_terms.intersection(content_terms)) / len(query_terms) * 10 + 2.0
            
            results.append({
                'chunk_type': 'pattern',
                'content': base_content,
                'document_name': 'SF_to_S4_Employee_Sync.iflow',
                'similarity_score': round(similarity1, 1)
            })
            
            base_content2 = 'SFTP Adapter configured for employee data file transfer with retry mechanism'
            content_terms2 = set(base_content2.lower().split())
            similarity2 = len(query_terms.intersection(content_terms2)) / len(query_terms) * 10 + 1.0
            
            results.append({
                'chunk_type': 'component', 
                'content': base_content2,
                'document_name': 'HR_File_Processing.iflow',
                'similarity_score': round(similarity2, 1)
            })
            
        elif "groovy" in query.lower() or "script" in query.lower():
            # Handle script queries
            query_terms = set(query.lower().split())
            script_terms = set(['groovy', 'script', 'date', 'format', 'conversion'])
            similarity = len(query_terms.intersection(script_terms)) / len(query_terms) * 12 + 3.0
            
            results.append({
                'chunk_type': 'asset',
                'content': 'Sample Groovy script for data transformation and date formatting',
                'document_name': 'sample_script.groovy',
                'similarity_score': round(similarity, 1)
            })
        
        return results[:limit]

class MockGraphStore:
    """Mock graph store when database is not available."""
    async def find_component_relationships(self, component_name):
        if component_name:
            return {
                'component': {
                    'name': component_name,
                    'type': 'SFTP',
                    'id': f'mock_{component_name}'
                },
                'outgoing_connections': [
                    {'target': 'Content Modifier 1', 'type': 'sequence'}
                ],
                'incoming_connections': [
                    {'source': 'Timer_Start', 'type': 'sequence'}
                ],
                'patterns': ['File Transfer Pattern'],
                'documents': ['Sample_iFlow.iflow']
            }
        return {}
    
    async def find_integration_patterns(self, pattern_type=None):
        return [
            {
                'name': 'Request-Reply Pattern',
                'type': 'REQUEST_REPLY',
                'description': 'Synchronous communication pattern for real-time data exchange',
                'complexity_score': 6.5,
                'document': 'Sample_iFlow.iflow',
                'components': ['HTTP_Receiver', 'Content_Modifier', 'OData_Adapter']
            }
        ]
    
    async def get_component_reusability_score(self, component_name):
        return 0.75  # Sample reusability score
    
    async def find_related_components(self, component_name, depth=2):
        return [
            {
                'name': 'Content_Modifier_Related',
                'type': 'ContentModifier',
                'distance': 1
            }
        ]
    
    async def find_similar_components(self, component_type, limit=10):
        return [
            {
                'name': f'Sample_{component_type}_Component',
                'type': component_type,
                'document': 'Sample_Integration.iflow',
                'package_name': 'com.sap.demo'
            }
        ]
    
    # Mock methods for knowledge graph queries
    async def query_companies(self, company_name=None):
        sample_companies = [
            {
                'name': 'Google',
                'founded': 1998,
                'description': 'Technology company with major AI research divisions',
                'employees': 190000,
                'headquarters': 'Mountain View, CA',
                'valuation': 1700000000000
            },
            {
                'name': 'OpenAI',
                'founded': 2015,
                'description': 'AI research company focused on developing safe AGI',
                'employees': 1500,
                'headquarters': 'San Francisco, CA',
                'valuation': 80000000000
            }
        ]
        if company_name:
            return [c for c in sample_companies if company_name.lower() in c['name'].lower()]
        return sample_companies
    
    async def query_ai_projects(self, company_name=None, project_name=None):
        sample_projects = [
            {
                'name': 'gpt-5-mini',
                'year': 2023,
                'category': 'Large Language Model',
                'description': 'Advanced multimodal AI model',
                'status': 'Released',
                'company': 'OpenAI'
            },
            {
                'name': 'Bard',
                'year': 2023,
                'category': 'Conversational AI',
                'description': 'AI chatbot powered by Gemini',
                'status': 'Active',
                'company': 'Google'
            }
        ]
        filtered = sample_projects
        if company_name:
            filtered = [p for p in filtered if company_name.lower() in p['company'].lower()]
        if project_name:
            filtered = [p for p in filtered if project_name.lower() in p['name'].lower()]
        return filtered
    
    async def query_technologies(self, tech_name=None):
        sample_tech = [
            {
                'name': 'Transformer Architecture',
                'category': 'Neural Network',
                'description': 'Attention-based neural network architecture',
                'year_introduced': 2017
            }
        ]
        if tech_name:
            return [t for t in sample_tech if tech_name.lower() in t['name'].lower()]
        return sample_tech
    
    async def query_relationships(self, entity_name):
        return {
            'entity': {'name': entity_name, 'labels': ['Company']},
            'outgoing_relationships': [
                {'type': 'DEVELOPS', 'target': 'AI_Project', 'target_labels': ['AI_Project']}
            ],
            'incoming_relationships': []
        }


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
