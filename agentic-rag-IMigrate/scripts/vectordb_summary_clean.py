#!/usr/bin/env python3
"""
Supabase Vector Database Summary Tool - Enhanced Version

Shows comprehensive details of your SAP iFlow vector database with full snapshots:
- Table structure and row counts
- Sample data from each table
- Embedding column information
- Vector search testing
- Detailed analysis saved to JSON snapshot

This tool helps you monitor and verify your vector database schema.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    from rag.supabase_vector_store import create_supabase_vector_store
    SUPABASE_AVAILABLE = True
except ImportError:
    print("❌ Supabase vector store not available")
    SUPABASE_AVAILABLE = False
    exit(1)

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📊 {title}")
    print("-" * 50)

async def analyze_vectordb():
    """Comprehensive analysis of the Supabase vector database"""
    
    print_header("SUPABASE VECTOR DATABASE SUMMARY")
    
    try:
        # Create vector store
        print("🔗 Connecting to Supabase vector database...")
        vector_store = create_supabase_vector_store(use_codebert=False)  # Skip CodeBERT for faster loading
        print("✅ Connected successfully!")
        print(f"   Database URL: {vector_store.supabase_url}")
        
        # Initialize enhanced snapshot data structure
        snapshot_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database_url": vector_store.supabase_url,
            "total_documents": 0,
            "tables": {},
            "health_status": "unknown",
            "detailed_analysis": {},
            "vector_search_tests": [],
            "summary_statistics": {}
        }
        
        # Get database statistics
        print_section("DATABASE OVERVIEW")
        stats = await vector_store.get_stats()
        
        total_docs = stats['total_documents']
        print(f"📈 Total Documents: {total_docs:,}")
        print(f"📋 Total Tables: {len(stats['tables'])}")
        
        # Update snapshot with basic info
        snapshot_data["total_documents"] = total_docs
        snapshot_data["tables"] = stats['tables']
        snapshot_data["health_status"] = "healthy" if total_docs > 0 else "empty"
        
        if total_docs == 0:
            print("⚠️  Database appears empty - check your Supabase connection")
            # Still save snapshot even if empty
            snapshot_file = f"vectordb_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2, default=str)
            print(f"\n💾 Basic snapshot saved: {snapshot_file}")
            return
        
        # Analyze each table in detail
        print_section("TABLE DETAILS")
        
        for table_key, table_info in stats['tables'].items():
            table_name = table_info['name']
            row_count = table_info.get('count', 0)
            
            print(f"\n📄 TABLE: {table_name}")
            print("-" * 30)
            print(f"   📊 Rows: {row_count:,}")
            
            if 'error' in table_info:
                print(f"   ❌ Error: {table_info['error']}")
                snapshot_data["detailed_analysis"][table_name] = {
                    "row_count": row_count,
                    "status": "error",
                    "error": table_info['error']
                }
                continue
                
            if row_count == 0:
                print("   (Empty table)")
                snapshot_data["detailed_analysis"][table_name] = {
                    "row_count": row_count,
                    "status": "empty"
                }
                continue
            
            # Detailed analysis for tables with data
            try:
                # Get sample data to analyze structure
                sample_result = vector_store.supabase.table(table_name).select("*").limit(3).execute()
                
                detailed_table_info = {
                    "row_count": row_count,
                    "columns": [],
                    "column_analysis": {
                        "vector_columns": [],
                        "text_columns": [],
                        "json_columns": [],
                        "total_columns": 0
                    },
                    "sample_data": [],
                    "data_quality": {
                        "has_embeddings": False,
                        "has_content": False,
                        "content_preview_length": 0
                    }
                }
                
                if sample_result.data:
                    first_row = sample_result.data[0]
                    columns = list(first_row.keys())
                    
                    print(f"   📋 Columns ({len(columns)}): {', '.join(columns[:5])}")
                    if len(columns) > 5:
                        print(f"       ... and {len(columns) - 5} more columns")
                    
                    detailed_table_info["columns"] = columns
                    detailed_table_info["column_analysis"]["total_columns"] = len(columns)
                    
                    # Identify special column types
                    vector_columns = []
                    text_columns = []
                    json_columns = []
                    
                    for col, value in first_row.items():
                        if 'embedding' in col.lower():
                            detailed_table_info["data_quality"]["has_embeddings"] = True
                            if isinstance(value, str) and value.startswith('['):
                                # Parse embedding to get dimension
                                try:
                                    parsed = json.loads(value) if isinstance(value, str) else value
                                    if isinstance(parsed, list):
                                        vector_columns.append({"name": col, "dimension": len(parsed)})
                                    else:
                                        vector_columns.append({"name": col, "dimension": "unknown"})
                                except:
                                    vector_columns.append({"name": col, "dimension": "parse_error"})
                            else:
                                vector_columns.append({"name": col, "dimension": "unknown"})
                        elif isinstance(value, str) and len(value) > 100:
                            detailed_table_info["data_quality"]["has_content"] = True
                            text_columns.append({
                                "name": col, 
                                "sample_length": len(value),
                                "preview": value[:100] + "..." if len(value) > 100 else value
                            })
                            if col in ['content', 'description', 'code']:
                                detailed_table_info["data_quality"]["content_preview_length"] = len(value)
                        elif isinstance(value, dict) or (isinstance(value, str) and value.startswith('{')):
                            json_columns.append({"name": col, "type": "json_object"})
                    
                    detailed_table_info["column_analysis"]["vector_columns"] = vector_columns
                    detailed_table_info["column_analysis"]["text_columns"] = text_columns
                    detailed_table_info["column_analysis"]["json_columns"] = json_columns
                    
                    if vector_columns:
                        vector_display = []
                        for vc in vector_columns:
                            if isinstance(vc, dict):
                                dim_info = f" (dim: {vc['dimension']})" if vc['dimension'] not in ['unknown', 'parse_error'] else ""
                                vector_display.append(f"{vc['name']}{dim_info}")
                            else:
                                vector_display.append(str(vc))
                        print(f"   🧮 Vector Columns: {', '.join(vector_display)}")
                    
                    if text_columns:
                        text_names = [tc['name'] if isinstance(tc, dict) else tc for tc in text_columns]
                        print(f"   📝 Text Columns: {', '.join(text_names)}")
                    
                    if json_columns:
                        json_names = [jc['name'] if isinstance(jc, dict) else jc for jc in json_columns]
                        print(f"   📋 JSON Columns: {', '.join(json_names)}")
                    
                    # Show sample data
                    print(f"   📄 Sample Data (first 2 rows):")
                    for i, row in enumerate(sample_result.data[:2], 1):
                        print(f"      Row {i}:")
                        for key, value in list(row.items())[:4]:  # Show first 4 columns
                            if isinstance(value, str):
                                if len(value) > 60:
                                    display_value = value[:60] + "..."
                                elif 'embedding' in key.lower() and value.startswith('['):
                                    try:
                                        parsed = json.loads(value)
                                        display_value = f"[{len(parsed)} values]"
                                    except:
                                        display_value = value[:30] + "..."
                                else:
                                    display_value = value
                            elif isinstance(value, dict):
                                display_value = f"{{...{len(value)} keys...}}"
                            elif isinstance(value, list):
                                display_value = f"[{len(value)} items]"
                            else:
                                display_value = value
                            
                            print(f"         {key}: {display_value}")
                        
                        if len(row) > 4:
                            print(f"         ... and {len(row) - 4} more columns")
                        
                        if i < len(sample_result.data):
                            print()
                    
                    # Add sample data to snapshot (limited for size)
                    for i, row in enumerate(sample_result.data[:2]):
                        sample_row = {}
                        for key, value in list(row.items())[:6]:  # First 6 columns
                            if isinstance(value, str) and len(value) > 100:
                                sample_row[key] = value[:100] + f"... ({len(value)} chars)"
                            elif isinstance(value, dict):
                                sample_row[key] = f"{{JSON object with {len(value)} keys}}"
                            elif isinstance(value, list):
                                sample_row[key] = f"[Array with {len(value)} items]"
                            else:
                                sample_row[key] = value
                        
                        detailed_table_info["sample_data"].append({
                            "row_number": i + 1,
                            "data": sample_row,
                            "total_columns_in_row": len(row)
                        })
                
                snapshot_data["detailed_analysis"][table_name] = detailed_table_info
                
            except Exception as e:
                print(f"   ❌ Error getting sample data: {e}")
                snapshot_data["detailed_analysis"][table_name] = {
                    "error": f"Failed to analyze: {str(e)}",
                    "row_count": row_count
                }
        
        # Vector search test
        print_section("VECTOR SEARCH TEST")
        
        test_queries = [
            "groovy script",
            "date conversion", 
            "BPMN component",
            "integration flow"
        ]
        
        print("Testing semantic search capabilities...")
        
        search_test_results = []
        for query in test_queries:
            try:
                results = await vector_store.search_similar(query, limit=2)
                print(f"   🔍 '{query}': {len(results)} results")
                
                query_result = {
                    "query": query,
                    "results_count": len(results),
                    "results": [],
                    "status": "success"
                }
                
                if results:
                    for result in results[:1]:  # Show top result
                        doc_name = result.get('document_name', 'Unknown')[:40]
                        score = result.get('similarity_score', 0.0)
                        table = result.get('source_table', 'unknown')
                        doc_type = result.get('document_type', 'unknown')
                        
                        print(f"      • {doc_name}... (score: {score:.2f}, table: {table})")
                        
                        query_result["results"].append({
                            "document_name": result.get('document_name', 'Unknown'),
                            "similarity_score": score,
                            "source_table": table,
                            "document_type": doc_type,
                            "content_preview": str(result.get('content', ''))[:150] + "..." if len(str(result.get('content', ''))) > 150 else str(result.get('content', ''))
                        })
                
                search_test_results.append(query_result)
                
            except Exception as e:
                error_msg = str(e)[:50]
                print(f"   ❌ Search failed for '{query}': {error_msg}...")
                search_test_results.append({
                    "query": query,
                    "results_count": 0,
                    "error": error_msg,
                    "status": "failed"
                })
                break
        
        snapshot_data["vector_search_tests"] = search_test_results
        
        # Summary and recommendations
        print_section("SUMMARY & RECOMMENDATIONS")
        
        database_status = 'Healthy' if total_docs > 0 else 'Needs Attention'
        print(f"✅ Database Status: {database_status}")
        print(f"📊 Total Content: {total_docs:,} documents across {len(stats['tables'])} tables")
        
        # Count embedding columns
        embedding_count = 0
        total_tables_with_data = 0
        tables_with_embeddings = []
        
        for table_key, table_info in stats['tables'].items():
            if table_info.get('count', 0) > 0:
                total_tables_with_data += 1
                try:
                    sample = vector_store.supabase.table(table_info['name']).select("*").limit(1).execute()
                    if sample.data:
                        embedding_cols = [k for k in sample.data[0].keys() if 'embedding' in k.lower()]
                        if embedding_cols:
                            tables_with_embeddings.append({
                                "table": table_info['name'],
                                "embedding_columns": embedding_cols,
                                "count": len(embedding_cols)
                            })
                        embedding_count += len(embedding_cols)
                except:
                    pass
        
        print(f"🧮 Vector Capabilities: {embedding_count} embedding columns detected")
        
        # Enhanced summary statistics
        summary_stats = {
            "database_status": database_status,
            "total_documents": total_docs,
            "total_tables": len(stats['tables']),
            "tables_with_data": total_tables_with_data,
            "total_embedding_columns": embedding_count,
            "tables_with_embeddings": tables_with_embeddings,
            "search_ready": total_docs > 0 and embedding_count > 0,
            "recommendations": []
        }
        
        if total_docs > 0:
            print(f"✅ Vector database is ready for semantic search")
            print(f"💡 Use the main agent (run_agent.py) to query this data")
            summary_stats["recommendations"].extend([
                "Vector database is ready for semantic search",
                "Use the main agent (run_agent.py) to query this data"
            ])
        else:
            print(f"⚠️  Vector database appears empty")
            print(f"💡 Check your Supabase configuration and data import")
            summary_stats["recommendations"].extend([
                "Vector database appears empty",
                "Check your Supabase configuration and data import"
            ])
        
        # Additional recommendations based on data analysis
        if embedding_count == 0:
            recommendation = "No embedding columns found - vector search may not work properly"
            print(f"⚠️  {recommendation}")
            summary_stats["recommendations"].append(recommendation)
        
        if total_tables_with_data < len(stats['tables']):
            empty_tables = len(stats['tables']) - total_tables_with_data
            recommendation = f"{empty_tables} tables are empty - consider populating them"
            print(f"💡 {recommendation}")
            summary_stats["recommendations"].append(recommendation)
        
        snapshot_data["summary_statistics"] = summary_stats
        
        # Save comprehensive snapshot
        snapshot_file = f"vectordb_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot_data, f, indent=2, default=str)
        
        print(f"\n💾 Comprehensive snapshot saved: {snapshot_file}")
        print(f"   📋 Includes: detailed analysis, search tests, recommendations")
        print(f"✅ Vector database analysis complete!")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        print(f"💡 Check your Supabase configuration in config.py")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_vectordb())

