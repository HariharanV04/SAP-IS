#!/usr/bin/env python3
"""
ByteDover Memory Management Script for SAP iFlow RAG Agent.
Provides CLI interface for managing memory entries and statistics.
"""

import asyncio
import argparse
import json
from pathlib import Path
from typing import Optional

from memory.bytedover_memory import create_memory_manager


async def show_memory_stats(memory_manager):
    """Display memory statistics."""
    stats = memory_manager.get_memory_stats()
    
    print("🧠 ByteDover Memory Statistics")
    print("=" * 50)
    print(f"📊 Total Entries: {stats.get('total_entries', 0)}")
    print(f"📈 Average Confidence: {stats.get('average_confidence', 0):.2f}")
    print(f"📁 Memory File: {stats.get('memory_file_path', 'N/A')}")
    print(f"🕒 Last Updated: {stats.get('last_updated', 'Never')}")
    
    if stats.get('tool_usage'):
        print("\n🛠️ Tool Usage:")
        for tool, count in sorted(stats['tool_usage'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {tool}: {count} times")
    
    if stats.get('tag_usage'):
        print("\n🏷️ Tag Usage:")
        for tag, count in sorted(stats['tag_usage'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {tag}: {count} times")


async def search_memory(memory_manager, query: str, limit: int = 5):
    """Search memory for relevant entries."""
    print(f"🔍 Searching memory for: '{query}'")
    print("=" * 50)
    
    results = await memory_manager.search_memory(query, limit=limit)
    
    if not results:
        print("❌ No relevant memory entries found.")
        return
    
    for i, result in enumerate(results, 1):
        entry = result.entry
        print(f"\n📝 Result {i} (Similarity: {result.similarity_score:.2f})")
        print(f"🆔 ID: {entry.id}")
        print(f"🕒 Time: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"❓ Query: {entry.query[:100]}{'...' if len(entry.query) > 100 else ''}")
        print(f"🤖 Response: {entry.response[:150]}{'...' if len(entry.response) > 150 else ''}")
        print(f"🛠️ Tools: {', '.join(entry.tools_used)}")
        print(f"📊 Confidence: {entry.confidence_score:.2f}")
        print(f"🏷️ Tags: {', '.join(entry.tags)}")
        print(f"💡 Reason: {result.relevance_reason}")


async def clear_memory(memory_manager, confirm: bool = False):
    """Clear all memory entries."""
    if not confirm:
        print("⚠️  This will delete ALL memory entries. Use --confirm to proceed.")
        return
    
    # Clear memory by removing the file
    memory_file = Path(memory_manager.memory_file_path)
    if memory_file.exists():
        memory_file.unlink()
        print("✅ Memory cleared successfully.")
    else:
        print("ℹ️  No memory file found to clear.")


async def export_memory(memory_manager, output_file: str):
    """Export memory to JSON file."""
    stats = memory_manager.get_memory_stats()
    
    export_data = {
        "export_info": {
            "timestamp": memory_manager.memory_entries[0].timestamp.isoformat() if memory_manager.memory_entries else None,
            "total_entries": len(memory_manager.memory_entries),
            "exported_by": "ByteDover Memory Manager"
        },
        "entries": []
    }
    
    for entry in memory_manager.memory_entries:
        entry_data = {
            "id": entry.id,
            "timestamp": entry.timestamp.isoformat(),
            "query": entry.query,
            "response": entry.response,
            "context": entry.context,
            "tools_used": entry.tools_used,
            "confidence_score": entry.confidence_score,
            "user_feedback": entry.user_feedback,
            "tags": entry.tags
        }
        export_data["entries"].append(entry_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Memory exported to {output_file}")
    print(f"📊 Exported {len(memory_manager.memory_entries)} entries")


async def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="ByteDover Memory Management for SAP iFlow RAG Agent")
    parser.add_argument("command", choices=["stats", "search", "clear", "export"], 
                       help="Command to execute")
    parser.add_argument("--query", "-q", help="Search query (for search command)")
    parser.add_argument("--limit", "-l", type=int, default=5, 
                       help="Limit for search results (default: 5)")
    parser.add_argument("--confirm", action="store_true", 
                       help="Confirm destructive operations")
    parser.add_argument("--output", "-o", help="Output file for export")
    parser.add_argument("--api-key", help="ByteDover API key (optional)")
    
    args = parser.parse_args()
    
    # Initialize memory manager
    memory_manager = create_memory_manager(
        api_key=args.api_key,
        memory_file_path="memory/rag_memory.json"
    )
    
    try:
        if args.command == "stats":
            await show_memory_stats(memory_manager)
            
        elif args.command == "search":
            if not args.query:
                print("❌ Search query is required. Use --query or -q")
                return
            await search_memory(memory_manager, args.query, args.limit)
            
        elif args.command == "clear":
            await clear_memory(memory_manager, args.confirm)
            
        elif args.command == "export":
            output_file = args.output or f"memory_export_{memory_manager.memory_entries[0].timestamp.strftime('%Y%m%d_%H%M%S')}.json" if memory_manager.memory_entries else "memory_export.json"
            await export_memory(memory_manager, output_file)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
