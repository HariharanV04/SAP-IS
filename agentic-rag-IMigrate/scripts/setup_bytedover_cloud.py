#!/usr/bin/env python3
"""
Setup script to connect to ByteDover Cloud instead of local memory.
This script helps configure the system for cloud-based memory management.
"""

import os
import sys
from pathlib import Path

def setup_bytedover_cloud():
    """Setup ByteDover cloud connection."""
    
    print("🌐 ByteDover Cloud Setup")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv("BYTEDOVER_API_KEY")
    if current_key and current_key != "None":
        print(f"✅ ByteDover API key already configured: {current_key[:20]}...")
        use_existing = input("Use existing key? (y/n): ").lower().strip()
        if use_existing == 'y':
            return True
    
    print("\n📋 To connect to ByteDover Cloud, you need:")
    print("1. A ByteDover account (sign up at https://byterover.dev)")
    print("2. Your API key from the ByteDover dashboard")
    print("3. Internet connection for cloud sync")
    
    print("\n🔑 Enter your ByteDover API key:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting setup.")
        return False
    
    # Validate API key format (basic check)
    if not api_key.startswith(('sk-', 'bt-', 'bytedover-')):
        print("⚠️  Warning: API key doesn't match expected format")
        proceed = input("Continue anyway? (y/n): ").lower().strip()
        if proceed != 'y':
            return False
    
    # Set environment variable for current session
    os.environ["BYTEDOVER_API_KEY"] = api_key
    
    # Update config.py
    config_path = Path("config.py")
    if config_path.exists():
        print("\n🔧 Updating config.py...")
        
        # Read current config
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the API key line
        old_line = 'BYTEDOVER_API_KEY = os.getenv("BYTEDOVER_API_KEY", None)'
        new_line = f'BYTEDOVER_API_KEY = os.getenv("BYTEDOVER_API_KEY", "{api_key}")'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print("✅ Config.py updated with your API key")
        else:
            print("⚠️  Could not find BYTEDOVER_API_KEY line in config.py")
    
    # Create .env file for persistent storage
    env_path = Path(".env")
    env_content = f"""# ByteDover Cloud Configuration
BYTEDOVER_API_KEY={api_key}
BYTEDOVER_API_URL=https://api.byterover.dev
ENABLE_MEMORY=true
MEMORY_CONTEXT_LIMIT=3
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file for persistent configuration")
    
    # Test connection
    print("\n🧪 Testing ByteDover connection...")
    try:
        from memory.bytedover_memory import create_memory_manager
        import asyncio
        
        async def test_connection():
            memory_manager = create_memory_manager(api_key=api_key)
            async with memory_manager:
                # Try to make a test API call
                stats = memory_manager.get_memory_stats()
                print(f"✅ Connection successful! Found {stats.get('total_entries', 0)} existing entries")
                return True
        
        result = asyncio.run(test_connection())
        if result:
            print("\n🎉 ByteDover Cloud setup complete!")
            print("\n📝 Next steps:")
            print("1. Run: python run_agent.py")
            print("2. Your interactions will now sync to ByteDover cloud")
            print("3. Check your ByteDover dashboard to see stored memories")
            return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check your internet connection")
        print("3. Ensure ByteDover service is available")
        return False

def show_current_status():
    """Show current ByteDover configuration status."""
    print("\n📊 Current ByteDover Configuration:")
    print("=" * 40)
    
    api_key = os.getenv("BYTEDOVER_API_KEY")
    api_url = os.getenv("BYTEDOVER_API_URL", "https://api.byterover.dev")
    enable_memory = os.getenv("ENABLE_MEMORY", "true")
    
    print(f"API URL: {api_url}")
    print(f"API Key: {'✅ Set' if api_key and api_key != 'None' else '❌ Not set'}")
    print(f"Memory Enabled: {enable_memory}")
    
    if api_key and api_key != "None":
        print(f"Key Preview: {api_key[:20]}...")
        print("🌐 Mode: Cloud (ByteDover)")
    else:
        print("🏠 Mode: Local (Offline)")
    
    # Check for .env file
    if Path(".env").exists():
        print("📁 .env file: ✅ Found")
    else:
        print("📁 .env file: ❌ Not found")

if __name__ == "__main__":
    print("ByteDover Cloud Setup Tool")
    print("=" * 30)
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_current_status()
    else:
        setup_bytedover_cloud()
