"""
Runner for SAP iFlow RAG + Knowledge Graph Agent.
Updated to use Supabase vector database instead of PostgreSQL.
"""

import os
import asyncio
from pathlib import Path

from agent.agent import create_sap_iflow_agent
from knowledge_graph.graph_store import GraphStore
import config


async def main() -> None:
    # Load .env if present
    if Path(".env").exists():
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv()
            print("Loaded .env configuration")
        except Exception:
            print("⚠️  python-dotenv not installed; relying on environment variables only")

    # Use config.py credentials directly (no environment dependency)
    openai_api_key = config.OPENAI_API_KEY
    neo4j_uri = config.NEO4J_URI
    neo4j_user = config.NEO4J_USER
    neo4j_password = config.NEO4J_PASSWORD

    print("Using credentials from config.py")
    print(f"OpenAI API key length: {len(openai_api_key) if openai_api_key else 0}")
    print(f"Neo4j URI: {neo4j_uri}")
    print(f"Neo4j User: {neo4j_user}")
    print(f"Neo4j Password length: {len(neo4j_password) if neo4j_password else 0}")

    # Initialize graph store 
    print("Initializing GraphStore (Neo4j)...")
    try:
        graph_store = GraphStore(neo4j_uri, neo4j_user, neo4j_password)
        await graph_store.initialize()
        print("GraphStore ready")
    except Exception as e:
        print(f"Failed to initialize GraphStore: {e}")
        print("Please check your Neo4j credentials and connectivity")
        return

    # Initialize agent (includes Supabase vector store)
    print("Initializing SAP iFlow Agent with Supabase vector database...")
    try:
        agent = create_sap_iflow_agent(
            graph_store=graph_store,
            openai_api_key=openai_api_key,
            context_document="SAP iFlow RAG + Knowledge Graph System",
        )
        print("Agent initialized with Supabase vector store")
    except Exception as e:
        print(f"Failed to initialize Agent: {e}")
        print("Please check your Supabase configuration in config.py")
        return

    # Interactive query input
    print("\n" + "="*60)
    print("SAP iFlow Agent Ready!")
    print("="*60)
    print("Ask questions about your SAP iFlow integration patterns, components, or flows")
    print("\n" + "-"*60)
    
    while True:
        try:
            query = input("\nYour Query (or 'quit' to exit): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not query:
                print("Please enter a query or 'quit' to exit")
                continue
                
            print(f"\nProcessing: '{query}'")
            print("-" * 50)
            
            response = await agent.query(query)
            
            # Display the response properly
            print("\n" + "RESPONSE:")
            print("="*50)
            if hasattr(response, 'content'):
                print(response.content)
            else:
                print(str(response))
            print("="*50)
            
            # Show tools used if available
            if hasattr(response, 'tools_used') and response.tools_used:
                print(f"Tools used: {', '.join(response.tools_used)}")
            
            print("\nAsk another question or type 'quit' to exit.")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError processing query: {e}")
            print("Please try again with a different query")


if __name__ == "__main__":
    asyncio.run(main())



