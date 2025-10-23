"""
LangGraph Documentation Refinement Agent for IMigrate
Uses Supabase feedback to continuously improve Boomi/MuleSoft/Sterling → SAP iFlow conversions
"""

import os
import json
from typing import TypedDict, Annotated, List, Dict
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import operator
from supabase import create_client, Client

# Supabase Configuration (from config.py)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Agent State
class DocumentationAgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    source_platform: str  # boomi, mulesoft, sterling
    source_file_content: str
    source_description: str
    integration_pattern: str  # e.g., "sftp_polling", "odata_integration"
    initial_documentation: str
    learned_patterns: List[Dict]
    high_quality_examples: List[Dict]
    missing_components_warnings: List[str]
    refined_documentation: str
    metadata: Dict
    quality_score: int
    iteration_count: int
    job_id: str


# ============================================================================
# SUPABASE TOOLS - Mapped to Your Existing Tables
# ============================================================================

@tool
def detect_integration_pattern(source_content: str, platform: str) -> str:
    """
    Detect integration pattern from source content
    Uses component_pattern_library to match patterns
    
    Your table: component_pattern_library
    Columns: trigger_phrase, component_type, pattern_category
    """
    try:
        # Fetch all patterns from your component_pattern_library
        response = supabase.table('component_pattern_library')\
            .select('pattern_category, trigger_phrase, component_type, confidence_score')\
            .gte('confidence_score', 0.70)\
            .order('confidence_score', desc=True)\
            .execute()
        
        patterns = response.data
        content_lower = source_content.lower()
        
        # Score each pattern
        pattern_scores = {}
        for pattern in patterns:
            trigger = pattern['trigger_phrase'].lower()
            category = pattern['pattern_category']
            confidence = pattern['confidence_score']
            
            if trigger in content_lower:
                pattern_scores[category] = pattern_scores.get(category, 0) + confidence
        
        # Return highest scoring pattern
        if pattern_scores:
            best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
            return best_pattern[0]
        
        return 'general_integration'
    
    except Exception as e:
        print(f"Error detecting pattern: {e}")
        return 'general_integration'


@tool
def fetch_learned_patterns(integration_pattern: str, platform: str, limit: int = 10) -> List[Dict]:
    """
    Fetch learned patterns from your component_pattern_library
    
    Your table: component_pattern_library
    Columns: trigger_phrase, component_type, confidence_score, typical_requirements
    """
    try:
        response = supabase.table('component_pattern_library')\
            .select('*')\
            .eq('pattern_category', integration_pattern)\
            .gte('confidence_score', 0.80)\
            .order('confidence_score', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data
    
    except Exception as e:
        print(f"Error fetching learned patterns: {e}")
        return []


@tool
def fetch_high_quality_feedback(platform: str, pattern: str, limit: int = 5) -> List[Dict]:
    """
    Fetch high-quality migration feedback (5-star conversions)
    
    Your table: migration_feedback
    Columns: job_id, source_platform, overall_rating, what_worked_well, 
             deployment_successful, component_mapping_accuracy
    """
    try:
        response = supabase.table('migration_feedback')\
            .select('job_id, source_file_name, overall_rating, documentation_quality_rating, '
                   'what_worked_well, component_mapping_accuracy, business_logic_preserved')\
            .eq('source_platform', platform)\
            .gte('overall_rating', 4)\
            .gte('documentation_quality_rating', 4)\
            .eq('deployment_successful', True)\
            .order('overall_rating', desc=True)\
            .order('documentation_quality_rating', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data
    
    except Exception as e:
        print(f"Error fetching high-quality feedback: {e}")
        return []


@tool
def fetch_common_missing_components(platform: str, pattern: str = None) -> Dict:
    """
    Get most commonly missed components from feedback
    
    Your table: migration_feedback
    Uses: missing_components, what_needs_improvement
    """
    try:
        query = supabase.table('migration_feedback')\
            .select('missing_components, what_needs_improvement')\
            .eq('source_platform', platform)\
            .lte('overall_rating', 3)
        
        response = query.execute()
        
        # Aggregate missing components
        missing_freq = {}
        improvement_freq = {}
        
        for record in response.data:
            # Count missing components
            for comp in record.get('missing_components', []):
                missing_freq[comp] = missing_freq.get(comp, 0) + 1
            
            # Count improvement areas
            for issue in record.get('what_needs_improvement', []):
                improvement_freq[issue] = improvement_freq.get(issue, 0) + 1
        
        # Sort by frequency
        top_missing = sorted(missing_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        top_issues = sorted(improvement_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'missing_components': [{'component': comp, 'frequency': freq} for comp, freq in top_missing],
            'common_issues': [{'issue': issue, 'frequency': freq} for issue, freq in top_issues],
            'total_low_ratings': len(response.data)
        }
    
    except Exception as e:
        print(f"Error fetching common issues: {e}")
        return {'missing_components': [], 'common_issues': [], 'total_low_ratings': 0}


@tool
def fetch_component_co_occurrences(component_type: str) -> List[Dict]:
    """
    Fetch components that typically appear together
    
    Your table: component_co_occurrence
    Columns: component_a, component_b, co_occurrence_count, confidence_score
    """
    try:
        response = supabase.table('component_co_occurrence')\
            .select('*')\
            .or_(f'component_a.eq.{component_type},component_b.eq.{component_type}')\
            .gte('confidence_score', 0.70)\
            .order('co_occurrence_count', desc=True)\
            .limit(10)\
            .execute()
        
        return response.data
    
    except Exception as e:
        print(f"Error fetching co-occurrences: {e}")
        return []


@tool
def fetch_documentation_feedback(platform: str, limit: int = 5) -> List[Dict]:
    """
    Fetch documentation-specific feedback
    
    Your table: documentation_feedback
    Columns: documentation_completeness_score, metadata_accuracy_score, 
             documentation_issues, suggested_improvements
    """
    try:
        response = supabase.table('documentation_feedback')\
            .select('*')\
            .eq('source_platform', platform)\
            .gte('documentation_completeness_score', 7)\
            .gte('metadata_accuracy_score', 7)\
            .order('documentation_completeness_score', desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data
    
    except Exception as e:
        print(f"Error fetching documentation feedback: {e}")
        return []


@tool
def save_refined_documentation_feedback(
    job_id: str,
    platform: str,
    pattern: str,
    original_doc: str,
    refined_doc: str,
    quality_score: int,
    improvements_made: List[str]
) -> Dict:
    """
    Save refined documentation back to Supabase for future learning
    
    Your table: learned_migration_patterns
    """
    try:
        data = {
            'job_id': job_id,
            'source_platform': platform,
            'integration_pattern': pattern,
            'original_documentation': original_doc[:5000],  # Truncate if needed
            'refined_documentation': refined_doc[:5000],
            'quality_score': quality_score,
            'improvements_made': improvements_made,
            'success_count': 1 if quality_score >= 8 else 0,
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('learned_migration_patterns').insert(data).execute()
        return {'success': True, 'data': response.data}
    
    except Exception as e:
        print(f"Error saving learned pattern: {e}")
        return {'success': False, 'error': str(e)}


@tool
def get_feedback_analytics(platform: str = None) -> Dict:
    """
    Get aggregate analytics from feedback_analytics view
    
    Your view: feedback_analytics
    """
    try:
        query = supabase.table('feedback_analytics').select('*')
        
        if platform:
            query = query.eq('source_platform', platform)
        
        response = query.execute()
        
        if response.data:
            return {
                'total_migrations': sum(r.get('total_migrations', 0) for r in response.data),
                'avg_overall_rating': sum(r.get('avg_overall_rating', 0) for r in response.data) / len(response.data),
                'successful_deployments': sum(r.get('successful_deployments', 0) for r in response.data),
                'platforms': [r.get('source_platform') for r in response.data]
            }
        
        return {'total_migrations': 0, 'avg_overall_rating': 0, 'successful_deployments': 0}
    
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return {}


# ============================================================================
# LANGGRAPH NODES
# ============================================================================

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def detect_pattern_node(state: DocumentationAgentState) -> DocumentationAgentState:
    """Detect integration pattern from source content"""
    pattern = detect_integration_pattern.invoke({
        "source_content": state["source_file_content"],
        "platform": state["source_platform"]
    })
    
    state["integration_pattern"] = pattern
    state["messages"].append(f"🔍 Detected integration pattern: {pattern}")
    return state


def fetch_learning_data_node(state: DocumentationAgentState) -> DocumentationAgentState:
    """Fetch all learning data from Supabase"""
    
    # 1. Fetch learned patterns
    patterns = fetch_learned_patterns.invoke({
        "integration_pattern": state["integration_pattern"],
        "platform": state["source_platform"],
        "limit": 10
    })
    state["learned_patterns"] = patterns
    state["messages"].append(f"📚 Retrieved {len(patterns)} learned patterns from pattern library")
    
    # 2. Fetch high-quality examples
    examples = fetch_high_quality_feedback.invoke({
        "platform": state["source_platform"],
        "pattern": state["integration_pattern"],
        "limit": 5
    })
    state["high_quality_examples"] = examples
    state["messages"].append(f"⭐ Retrieved {len(examples)} high-quality 5-star examples")
    
    # 3. Fetch common mistakes
    common_issues = fetch_common_missing_components.invoke({
        "platform": state["source_platform"],
        "pattern": state["integration_pattern"]
    })
    
    warnings = []
    for item in common_issues.get('missing_components', []):
        warnings.append(f"⚠️ {item['component']} (missed in {item['frequency']} conversions)")
    
    state["missing_components_warnings"] = warnings
    state["messages"].append(f"⚠️ Identified {len(warnings)} common missing components")
    
    return state


def generate_documentation_node(state: DocumentationAgentState) -> DocumentationAgentState:
    """Generate initial documentation using learned patterns"""
    
    # Build context from learned patterns
    patterns_context = "\n".join([
        f"- {p['trigger_phrase']} → {p['component_type']} (confidence: {p['confidence_score']:.2f})"
        for p in state["learned_patterns"][:5]
    ])
    
    # Build context from high-quality examples
    examples_context = "\n".join([
        f"- {ex['source_file_name']} (rated {ex['overall_rating']}/5): {', '.join(ex.get('what_worked_well', []))}"
        for ex in state["high_quality_examples"][:3]
    ])
    
    # Build warnings
    warnings_text = "\n".join(state["missing_components_warnings"])
    
    prompt = f"""
You are an expert at analyzing {state['source_platform']} integration files and creating comprehensive documentation for SAP Integration Suite migration.

INTEGRATION PATTERN: {state['integration_pattern']}

📚 LEARNED PATTERNS (from {len(state['learned_patterns'])} successful conversions):
{patterns_context}

⭐ HIGH-QUALITY EXAMPLES (5-star rated):
{examples_context}

⚠️ COMMON MISTAKES TO AVOID:
{warnings_text}

SOURCE FILE CONTENT:
{state['source_file_content'][:8000]}

Generate comprehensive documentation in markdown format that:
1. Explicitly identifies ALL components (especially commonly missed ones)
2. Describes the integration pattern clearly
3. Details the data flow step-by-step
4. Captures business logic and transformations
5. Includes configuration details (endpoints, auth, polling intervals)
6. Documents error handling if present

Follow the patterns and quality standards from the successful examples above.
"""
    
    response = llm.invoke(prompt)
    state["initial_documentation"] = response.content
    state["messages"].append(f"📝 Generated initial documentation ({len(response.content)} chars)")
    
    return state


def extract_metadata_node(state: DocumentationAgentState) -> DocumentationAgentState:
    """Extract structured metadata from documentation"""
    
    # Get component co-occurrences for validation
    components_mentioned = []
    for pattern in state["learned_patterns"]:
        components_mentioned.append(pattern['component_type'])
    
    prompt = f"""
Extract structured metadata from this documentation for SAP iFlow generation.

DOCUMENTATION:
{state['initial_documentation']}

EXPECTED COMPONENTS (based on learned patterns):
{', '.join(set(components_mentioned))}

Extract and return JSON with this structure:
{{
    "components": [
        {{
            "type": "component_type",
            "name": "component_name",
            "description": "what it does",
            "configuration": {{}},
            "confidence": 0.0-1.0
        }}
    ],
    "integration_pattern": "{state['integration_pattern']}",
    "data_flow": ["step1", "step2", ...],
    "business_logic": "key business rules",
    "endpoints": {{}},
    "authentication": {{}},
    "error_handling": "description",
    "quality_score": 0.0-10.0
}}

Ensure ALL expected components are present. If a component is missing, include it with low confidence.
"""
    
    response = llm.invoke([
        {"role": "system", "content": "You are an expert at extracting structured metadata from integration documentation. Always return valid JSON."},
        {"role": "user", "content": prompt}
    ])
    
    try:
        metadata = json.loads(response.content)
        state["metadata"] = metadata
        state["messages"].append(f"🔍 Extracted metadata with {len(metadata.get('components', []))} components")
    except json.JSONDecodeError:
        state["metadata"] = {"components": [], "quality_score": 5.0}
        state["messages"].append(f"⚠️ Failed to parse metadata JSON")
    
    return state


def validate_and_refine_node(state: DocumentationAgentState) -> DocumentationAgentState:
    """Validate against learned patterns and refine if needed"""
    
    # Check if all expected components are present
    expected_components = set(p['component_type'] for p in state["learned_patterns"])
    documented_components = set(c['type'] for c in state["metadata"].get('components', []))
    
    missing = expected_components - documented_components
    
    if missing:
        state["messages"].append(f"⚠️ Missing components detected: {', '.join(missing)}")
        
        # Refine to add missing components
        refinement_prompt = f"""
The documentation is missing these components that are typically required for this pattern:
{', '.join(missing)}

ORIGINAL DOCUMENTATION:
{state['initial_documentation']}

LEARNED PATTERNS showing these are needed:
{json.dumps([p for p in state['learned_patterns'] if p['component_type'] in missing], indent=2)}

Please refine the documentation to explicitly include these missing components with proper descriptions.
"""
        
        refined = llm.invoke(refinement_prompt)
        state["refined_documentation"] = refined.content
        state["messages"].append(f"✨ Documentation refined to include missing components")
    else:
        state["refined_documentation"] = state["initial_documentation"]
        state["messages"].append(f"✅ All expected components documented")
    
    return state


def evaluate_quality_node(state: DocumentationAgentState) -> DocumentationAgentState:
    """Evaluate documentation quality"""
    
    evaluation_prompt = f"""
Evaluate this SAP iFlow migration documentation on a scale of 1-10:

CRITERIA:
1. All components explicitly identified (especially {', '.join(state['missing_components_warnings'][:3])})
2. Clear integration pattern description
3. Step-by-step data flow
4. Business logic captured
5. Configuration details included
6. Error handling documented
7. Follows best practices from high-quality examples

DOCUMENTATION:
{state['refined_documentation']}

METADATA:
{json.dumps(state['metadata'], indent=2)}

Respond with ONLY a number from 1-10.
"""
    
    result = llm.invoke(evaluation_prompt)
    
    try:
        score = int(result.content.strip())
    except:
        score = 7  # Default
    
    state["quality_score"] = score
    state["messages"].append(f"⭐ Quality score: {score}/10")
    
    return state


def save_learning_node(state: DocumentationAgentState) -> DocumentationAgentState:
    """Save refined documentation to Supabase if quality is good"""
    
    if state["quality_score"] >= 7:
        improvements = []
        if state["refined_documentation"] != state["initial_documentation"]:
            improvements.append("Added missing components based on learned patterns")
        
        result = save_refined_documentation_feedback.invoke({
            "job_id": state.get("job_id", f"langgraph_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "platform": state["source_platform"],
            "pattern": state["integration_pattern"],
            "original_doc": state["initial_documentation"],
            "refined_doc": state["refined_documentation"],
            "quality_score": state["quality_score"],
            "improvements_made": improvements
        })
        
        if result['success']:
            state["messages"].append(f"💾 Saved refined documentation to Supabase for future learning")
        else:
            state["messages"].append(f"⚠️ Failed to save: {result.get('error', 'Unknown error')}")
    else:
        state["messages"].append(f"⏭️ Quality score too low, skipping save")
    
    return state


# ============================================================================
# CONDITIONAL ROUTING
# ============================================================================

def should_refine_again(state: DocumentationAgentState) -> str:
    """Decide if another refinement iteration is needed"""
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    
    # Refine again if quality is low and haven't exceeded max iterations
    if state.get("quality_score", 0) < 7 and state["iteration_count"] < 2:
        return "refine_again"
    else:
        return "save_and_end"


# ============================================================================
# BUILD LANGGRAPH WORKFLOW
# ============================================================================

workflow = StateGraph(DocumentationAgentState)

# Add nodes
workflow.add_node("detect_pattern", detect_pattern_node)
workflow.add_node("fetch_learning", fetch_learning_data_node)
workflow.add_node("generate_docs", generate_documentation_node)
workflow.add_node("extract_metadata", extract_metadata_node)
workflow.add_node("validate_refine", validate_and_refine_node)
workflow.add_node("evaluate", evaluate_quality_node)
workflow.add_node("save_learning", save_learning_node)

# Define flow
workflow.set_entry_point("detect_pattern")
workflow.add_edge("detect_pattern", "fetch_learning")
workflow.add_edge("fetch_learning", "generate_docs")
workflow.add_edge("generate_docs", "extract_metadata")
workflow.add_edge("extract_metadata", "validate_refine")
workflow.add_edge("validate_refine", "evaluate")

# Conditional edge after evaluation
workflow.add_conditional_edges(
    "evaluate",
    should_refine_again,
    {
        "refine_again": "fetch_learning",  # Re-fetch and try again
        "save_and_end": "save_learning"
    }
)

workflow.add_edge("save_learning", END)

# Compile the graph
app = workflow.compile()


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def run_documentation_refinement_agent(
    source_platform: str,
    source_file_content: str,
    source_description: str = "",
    job_id: str = None
) -> Dict:
    """
    Run the Supabase-backed documentation refinement agent
    
    Args:
        source_platform: 'boomi', 'mulesoft', or 'sterling'
        source_file_content: Raw source file content
        source_description: Optional brief description
        job_id: Optional job ID for tracking
    
    Returns:
        Dict with refined documentation and metadata
    """
    
    initial_state = {
        "messages": [],
        "source_platform": source_platform,
        "source_file_content": source_file_content,
        "source_description": source_description,
        "integration_pattern": "",
        "initial_documentation": "",
        "learned_patterns": [],
        "high_quality_examples": [],
        "missing_components_warnings": [],
        "refined_documentation": "",
        "metadata": {},
        "quality_score": 0,
        "iteration_count": 0,
        "job_id": job_id or f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    result = app.invoke(initial_state)
    
    print("\n" + "="*80)
    print("🤖 LANGGRAPH DOCUMENTATION AGENT - EXECUTION TRACE")
    print("="*80)
    for msg in result["messages"]:
        print(f"  {msg}")
    
    print("\n" + "="*80)
    print("✅ FINAL REFINED DOCUMENTATION")
    print("="*80)
    print(result["refined_documentation"][:1000] + "..." if len(result["refined_documentation"]) > 1000 else result["refined_documentation"])
    print(f"\n⭐ Quality Score: {result['quality_score']}/10")
    print(f"🔧 Components: {len(result['metadata'].get('components', []))}")
    print("="*80 + "\n")
    
    return {
        'documentation': result["refined_documentation"],
        'metadata': result["metadata"],
        'quality_score': result['quality_score'],
        'integration_pattern': result['integration_pattern'],
        'learned_from': len(result['learned_patterns']),
        'messages': result['messages']
    }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "🚀 LangGraph Documentation Refinement Agent for IMigrate")
    print("="*80)
    
    # Example Boomi process
    example_boomi = """
    <process>
        <component type="SFTP">
            <name>PollEmployeeFiles</name>
            <operation>GET</operation>
            <schedule>Every 5 minutes</schedule>
            <directory>/inbound/employees/</directory>
        </component>
        <component type="DataTransform">
            <script>transformEmployeeData.groovy</script>
        </component>
        <component type="HTTPAdapter">
            <operation>POST</operation>
            <endpoint>/sap/odata/EmployeeService</endpoint>
            <authentication>OAuth2</authentication>
        </component>
    </process>
    """
    
    # Run the agent
    result = run_documentation_refinement_agent(
        source_platform='boomi',
        source_file_content=example_boomi,
        source_description="Poll SFTP for employee files every 5 minutes, transform, and post to SAP OData",
        job_id="test_001"
    )
    
    print("\n📊 RESULT SUMMARY:")
    print(f"  Quality Score: {result['quality_score']}/10")
    print(f"  Integration Pattern: {result['integration_pattern']}")
    print(f"  Learned from {result['learned_from']} patterns")
    print(f"  Components: {len(result['metadata'].get('components', []))}")

