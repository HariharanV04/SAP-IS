"""
RAG API Service - Flask API wrapper for RAG agent
This service exposes RAG system's iFlow generation capabilities via REST API

Port: 5010
Purpose: Bridge between IMigrate and RAG system for intelligent iFlow generation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import os
import logging
import json
from datetime import datetime
from pathlib import Path

from agent.agent import create_sap_iflow_agent
from knowledge_graph.graph_store import GraphStore
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for agent
graph_store = None
rag_agent = None

# Paths configuration - ABSOLUTE PATHS to avoid confusion
BASE_DIR = Path(__file__).parent
METADATA_OUTPUT_DIR = BASE_DIR / "component_metadata"
PACKAGES_OUTPUT_DIR = BASE_DIR / "generated_packages"
QUERY_LOG_DIR = BASE_DIR / "query_logs"
STRATEGIC_PLANS_DIR = BASE_DIR / "strategic_plans"

# Ensure directories exist
METADATA_OUTPUT_DIR.mkdir(exist_ok=True)
PACKAGES_OUTPUT_DIR.mkdir(exist_ok=True)
QUERY_LOG_DIR.mkdir(exist_ok=True)
STRATEGIC_PLANS_DIR.mkdir(exist_ok=True)

logger.info(f"Query logs will be saved to: {QUERY_LOG_DIR}")
logger.info(f"Strategic plans will be saved to: {STRATEGIC_PLANS_DIR}")
logger.info(f"Metadata will be saved to: {METADATA_OUTPUT_DIR}")
logger.info(f"Packages will be saved to: {PACKAGES_OUTPUT_DIR}")


def initialize_agent():
    """
    Initialize RAG agent on startup.

    Gracefully handles Neo4j connection failures by allowing the agent
    to work with just the vector store (Supabase).

    Returns:
        bool: True if fully initialized, False if partial initialization
    """
    global graph_store, rag_agent

    try:
        logger.info("="*80)
        logger.info("INITIALIZING RAG API SERVICE")
        logger.info("="*80)

        # Try to initialize Neo4j (optional - will continue without it)
        graph_store_available = False
        try:
            logger.info(f"📊 Connecting to Neo4j at: {config.NEO4J_URI}")
            graph_store = GraphStore(
                config.NEO4J_URI,
                config.NEO4J_USER,
                config.NEO4J_PASSWORD
            )
            asyncio.run(graph_store.initialize())
            graph_store_available = True
            logger.info("✅ Neo4j Knowledge Graph connected")
        except Exception as neo4j_error:
            logger.warning(f"⚠️ Neo4j connection failed: {str(neo4j_error)}")
            logger.warning("⚠️ Continuing with vector store only (degraded mode)")
            logger.warning("⚠️ Knowledge Graph features will be unavailable")
            graph_store = None

        # Initialize RAG Agent (works with or without graph store)
        logger.info("🤖 Creating RAG Agent...")
        try:
            rag_agent = create_sap_iflow_agent(
                graph_store=graph_store,  # Can be None
                openai_api_key=config.OPENAI_API_KEY,
                context_document="SAP iFlow RAG + Knowledge Graph System"
            )
            logger.info("✅ RAG Agent initialized successfully")
        except Exception as agent_error:
            logger.error(f"❌ Failed to create RAG Agent: {str(agent_error)}")
            logger.error("❌ Service will not be available")
            raise

        logger.info("="*80)
        if graph_store_available:
            logger.info("✅ RAG API SERVICE READY (Full mode - Vector DB + Knowledge Graph)")
        else:
            logger.info("⚠️ RAG API SERVICE READY (Degraded mode - Vector DB only)")
        logger.info("="*80)

        return graph_store_available

    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG Agent: {str(e)}")
        logger.error("❌ RAG API Service cannot start")
        raise


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns service status including:
    - Agent initialization status
    - Graph store connection status (Neo4j)
    - Operating mode (full/degraded)
    - File system paths
    """
    agent_ok = rag_agent is not None
    graph_ok = graph_store is not None

    # Determine operating mode
    if agent_ok and graph_ok:
        mode = "full"
        status_msg = "Fully operational with Vector DB + Knowledge Graph"
    elif agent_ok and not graph_ok:
        mode = "degraded"
        status_msg = "Degraded mode - Vector DB only (Knowledge Graph unavailable)"
    else:
        mode = "error"
        status_msg = "Service unavailable - Agent not initialized"

    return jsonify({
        'status': 'ok' if agent_ok else 'error',
        'mode': mode,
        'message': status_msg,
        'service': 'RAG API Service',
        'agent_initialized': agent_ok,
        'graph_store_connected': graph_ok,
        'vector_store_available': True,  # Supabase - always available if agent is initialized
        'query_logs_dir': str(QUERY_LOG_DIR),
        'strategic_plans_dir': str(STRATEGIC_PLANS_DIR),
        'metadata_dir': str(METADATA_OUTPUT_DIR),
        'packages_dir': str(PACKAGES_OUTPUT_DIR),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/generate-iflow-from-markdown', methods=['POST'])
def generate_iflow_from_markdown():
    """
    Generate iFlow from markdown documentation using RAG system
    
    Expected JSON body:
    {
        "markdown_content": "...",
        "iflow_name": "MyFlow",
        "job_id": "uuid",
        "output_dir": "/path/to/output" (optional - will use generated_packages if not provided)
    }
    
    Returns:
    {
        "status": "success",
        "message": "...",
        "files": {
            "zip": "/path/to/package.zip"
        },
        "iflow_name": "MyFlow",
        "metadata_path": "/path/to/metadata.json"
    }
    """
    try:
        logger.info("\n" + "="*80)
        logger.info("🚀 RAG API: Received iFlow generation request")
        logger.info("="*80)
        
        data = request.json
        markdown_content = data.get('markdown_content')
        iflow_name = data.get('iflow_name', 'GeneratedIFlow')
        job_id = data.get('job_id')
        output_dir = data.get('output_dir')
        
        logger.info(f"📝 iFlow Name: {iflow_name}")
        logger.info(f"🔑 Job ID: {job_id}")
        logger.info(f"📄 Markdown length: {len(markdown_content) if markdown_content else 0} characters")
        
        if not markdown_content:
            logger.error("❌ Missing markdown_content in request")
            return jsonify({
                'status': 'error',
                'message': 'Missing markdown_content'
            }), 400
        
        # Use absolute paths for output
        if not output_dir:
            output_dir = str(PACKAGES_OUTPUT_DIR)
            logger.info(f"📁 Using default output directory: {output_dir}")
        else:
            logger.info(f"📁 Using provided output directory: {output_dir}")
        
        # Convert markdown to query for RAG agent
        # The markdown contains the documentation, we extract key information
        logger.info("🔍 Analyzing markdown documentation...")
        
        # Extract key components from markdown
        query = f"""Create a complete SAP iFlow integration package named '{iflow_name}' with the following requirements from the documentation:

{markdown_content[:2000]}

Generate a production-ready iFlow with proper:
1. Start and End events
2. Required adapters and connectors
3. Content modifiers and processing steps
4. Proper sequence flows
5. Error handling
6. SAP Integration Suite compliance
"""
        
        logger.info("🤖 Calling RAG Agent to generate iFlow...")
        logger.info(f"📋 Query length: {len(query)} characters")
        
        # Save query and markdown for debugging/tracing
        query_log_dir = BASE_DIR / "query_logs"
        query_log_dir.mkdir(exist_ok=True)
        
        query_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        query_log_file = query_log_dir / f"query_{query_timestamp}.json"
        
        query_log_data = {
            "timestamp": query_timestamp,
            "job_id": job_id,
            "iflow_name": iflow_name,
            "original_markdown": markdown_content,
            "markdown_length": len(markdown_content),
            "constructed_query": query,
            "query_length": len(query),
            "markdown_truncated_at": 2000,  # First 2000 chars used in query
            "api_endpoint": "/api/generate-iflow-from-markdown",
            "request_time": datetime.now().isoformat()
        }
        
        with open(query_log_file, 'w', encoding='utf-8') as f:
            json.dump(query_log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📝 Query log saved to: {query_log_file}")
        
        # Call RAG agent to generate iFlow package
        result = asyncio.run(
            rag_agent.create_complete_iflow_package(query)
        )
        
        # Extract package info from result (agent returns nested structure)
        package_info = result.get('package_info', {})
        package_path = package_info.get('package_path', result.get('package_path', ''))
        components = package_info.get('components', result.get('components', []))
        generation_successful = bool(package_path) or len(components) > 0
        
        logger.info(f"✅ RAG Agent completed")
        logger.info(f"   Package Path: {package_path}")
        logger.info(f"   Components: {len(components)}")
        logger.info(f"   Success: {generation_successful}")
        
        # Save metadata to component_metadata directory
        metadata_filename = f"iflow_components_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        metadata_path = METADATA_OUTPUT_DIR / metadata_filename
        
        metadata = {
            'iflow_name': iflow_name,
            'job_id': job_id,
            'generated_at': datetime.now().isoformat(),
            'components': components,
            'metadata': package_info,  # Include full package_info
            'package_path': package_path,
            'generation_method': 'RAG Agent (Dynamic)',
            'status': 'success' if generation_successful else 'failed',
            'final_response': result.get('final_response', '')
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Metadata saved to: {metadata_path}")
        
        # Format response to match IMigrate's expected format
        if generation_successful:
            package_path = result.get('package_path', '')
            
            logger.info("="*80)
            logger.info("✅ iFlow Generation SUCCESSFUL")
            logger.info(f"📦 Package: {package_path}")
            logger.info(f"📊 Metadata: {metadata_path}")
            logger.info(f"🔧 Components: {len(result.get('components', []))}")
            logger.info("="*80)
            
            return jsonify({
                'status': 'success',
                'message': f'Generated iFlow: {package_path}',
                'files': {
                    'zip': package_path,
                    'debug': {}
                },
                'iflow_name': iflow_name,
                'components': result.get('components', []),
                'metadata': result.get('metadata', {}),
                'metadata_path': str(metadata_path),
                'generation_method': 'RAG Agent (Dynamic)',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            error_msg = result.get('message', 'Failed to generate iFlow')
            logger.error(f"❌ iFlow Generation FAILED: {error_msg}")
            
            return jsonify({
                'status': 'error',
                'message': error_msg,
                'metadata_path': str(metadata_path)
            }), 500
            
    except Exception as e:
        logger.error(f"❌ ERROR in iFlow generation: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/test', methods=['POST'])
def test_generation():
    """
    Test endpoint for quick RAG agent testing
    """
    try:
        data = request.json
        query = data.get('query', 'Create an HTTP sender with content modifier')
        
        logger.info(f"🧪 Test query: {query}")
        
        result = asyncio.run(
            rag_agent.create_complete_iflow_package(query)
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Initialize agent before starting server
    try:
        graph_available = initialize_agent()

        # Start Flask server
        port = int(os.getenv('RAG_API_PORT', 5010))
        logger.info(f"\n🚀 Starting RAG API Service on port {port}")
        logger.info(f"📍 http://localhost:{port}")
        logger.info(f"📊 Health check: http://localhost:{port}/api/health")

        if not graph_available:
            logger.warning("\n⚠️ WARNING: Neo4j Knowledge Graph unavailable")
            logger.warning("⚠️ Service running in DEGRADED MODE (Vector DB only)")
            logger.warning("⚠️ To fix: Check Neo4j AuraDB instance status")
            logger.warning("⚠️ To fix: Verify network connectivity to Neo4j")
            logger.warning("⚠️ To fix: Verify credentials in config.py\n")

        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

    except Exception as init_error:
        logger.error(f"\n❌ FATAL: Cannot start RAG API Service")
        logger.error(f"❌ Error: {str(init_error)}")
        logger.error(f"❌ Please check configuration and try again\n")
        import sys
        sys.exit(1)

