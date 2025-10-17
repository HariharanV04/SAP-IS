#!/usr/bin/env python3
"""
Switch between local and cloud memory modes for ByteDover integration.
"""

import os
import sys
from pathlib import Path

def switch_to_cloud_mode(api_key: str = None):
    """Switch to cloud mode with ByteDover."""
    print("🌐 Switching to ByteDover Cloud Mode")
    print("=" * 40)
    
    if not api_key:
        api_key = input("Enter your ByteDover API key: ").strip()
        if not api_key:
            print("❌ No API key provided")
            return False
    
    # Update environment
    os.environ["BYTEDOVER_API_KEY"] = api_key
    os.environ["ENABLE_MEMORY"] = "true"
    
    # Update .env file
    env_content = f"""# ByteDover Cloud Configuration
BYTEDOVER_API_KEY={api_key}
BYTEDOVER_API_URL=https://api.byterover.dev
ENABLE_MEMORY=true
MEMORY_CONTEXT_LIMIT=3
"""
    
    with open(".env", 'w') as f:
        f.write(env_content)
    
    print("✅ Switched to cloud mode")
    print(f"🔑 API Key: {api_key[:20]}...")
    return True

def switch_to_local_mode():
    """Switch to local mode (offline)."""
    print("🏠 Switching to Local Mode")
    print("=" * 30)
    
    # Clear environment
    os.environ["BYTEDOVER_API_KEY"] = ""
    os.environ["ENABLE_MEMORY"] = "true"
    
    # Update .env file
    env_content = """# Local Memory Configuration
BYTEDOVER_API_KEY=
BYTEDOVER_API_URL=https://api.byterover.dev
ENABLE_MEMORY=true
MEMORY_CONTEXT_LIMIT=3
"""
    
    with open(".env", 'w') as f:
        f.write(env_content)
    
    print("✅ Switched to local mode")
    print("📁 Memory will be stored locally in memory/rag_memory.json")
    return True

def show_current_mode():
    """Show current memory mode."""
    api_key = os.getenv("BYTEDOVER_API_KEY")
    
    print("📊 Current Memory Mode:")
    print("=" * 25)
    
    if api_key and api_key.strip():
        print("🌐 Mode: Cloud (ByteDover)")
        print(f"🔑 API Key: {api_key[:20]}...")
    else:
        print("🏠 Mode: Local (Offline)")
        print("📁 Storage: memory/rag_memory.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python switch_memory_mode.py cloud [api_key]")
        print("  python switch_memory_mode.py local")
        print("  python switch_memory_mode.py status")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "cloud":
        api_key = sys.argv[2] if len(sys.argv) > 2 else None
        switch_to_cloud_mode(api_key)
    elif mode == "local":
        switch_to_local_mode()
    elif mode == "status":
        show_current_mode()
    else:
        print(f"❌ Unknown mode: {mode}")
        sys.exit(1)
