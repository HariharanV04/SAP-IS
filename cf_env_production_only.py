#!/usr/bin/env python3
"""
CF Environment Setup from .env.production files ONLY
Simple script that reads only .env.production files and sets them as CF environment variables
"""

import os
import subprocess
import sys
from pathlib import Path

def parse_env_file(file_path):
    """Parse .env file and return key-value pairs"""
    env_vars = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        env_vars[key] = value
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return env_vars

def find_env_production_files():
    """Find ALL .env.production files"""
    env_files = []
    
    # Check if we're in IMigrate directory or parent
    if Path('.').name == 'IMigrate':
        search_dir = Path('.')
    else:
        search_dir = Path('./IMigrate')
        if not search_dir.exists():
            search_dir = Path('.')
    
    print(f"🔍 Searching for .env.production files in: {search_dir.absolute()}")
    
    for path in search_dir.rglob('*.env.production'):
        if path.is_file():
            # Skip files in uploads, results, node_modules directories
            if not any(skip_dir in str(path) for skip_dir in ['uploads', 'results', 'node_modules', '__pycache__', 'extracted']):
                env_files.append(path)
    
    return env_files

def set_cf_env_var(app_name, key, value):
    """Set environment variable in CF"""
    try:
        cmd = ['cf', 'set-env', app_name, key, value]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"   ✅ {key}")
            return True
        else:
            print(f"   ❌ {key}: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ {key}: {str(e)}")
        return False

def main():
    print("🚀 Setting CF Environment Variables from .env.production files ONLY")
    print("=" * 70)
    
    # CF app names and their specific environment variables
    cf_apps = {
        'it-resonance-main-api': {
            'IFLOW_API_URL': 'https://mule-to-is-api.cfapps.eu10.hana.ondemand.com',
            'BOOMI_API_URL': 'https://boomi-to-is-api.cfapps.eu10.hana.ondemand.com'
        },
        'mule-to-is-api': {},
        'boomi-to-is-api': {}
    }
    
    # Find all .env.production files
    env_files = find_env_production_files()
    print(f"📁 Found {len(env_files)} .env.production files:")
    for file in env_files:
        print(f"   - {file}")
    
    if not env_files:
        print("❌ No .env.production files found!")
        return
    
    # Consolidate all environment variables from .env.production files
    print(f"\n📊 Reading .env.production files...")
    all_env_vars = {}
    
    for env_file in env_files:
        print(f"📖 Reading {env_file}...")
        env_vars = parse_env_file(env_file)
        
        if env_vars:
            print(f"   Found {len(env_vars)} variables:")
            for key in env_vars.keys():
                print(f"     - {key}")
            
            # Merge into consolidated dict (later files override earlier ones)
            all_env_vars.update(env_vars)
        else:
            print(f"   No variables found")
    
    if not all_env_vars:
        print("❌ No environment variables found in any .env.production files!")
        return
    
    print(f"\n🔗 Final consolidated variables ({len(all_env_vars)} total):")
    for key in sorted(all_env_vars.keys()):
        # Mask sensitive values for display
        value = all_env_vars[key]
        if any(keyword in key.lower() for keyword in ['key', 'secret', 'password', 'token']):
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"   {key} = {display_value}")
    
    # Set environment variables for each CF app
    for app_name, app_specific_vars in cf_apps.items():
        print(f"\n🔧 Setting ALL variables for {app_name}...")
        
        success_count = 0
        total_vars = len(all_env_vars) + len(app_specific_vars)
        
        # Set variables from .env.production files
        for key, value in all_env_vars.items():
            if set_cf_env_var(app_name, key, value):
                success_count += 1
        
        # Set app-specific variables
        for key, value in app_specific_vars.items():
            if set_cf_env_var(app_name, key, value):
                success_count += 1
        
        print(f"   📊 Set {success_count}/{total_vars} variables")
    
    print(f"\n✅ Environment setup complete!")
    print(f"\n🔄 Restart apps to apply changes:")
    for app in cf_apps.keys():
        print(f"   cf restart {app}")
    
    print(f"\n🔍 Verify with:")
    print(f"   cf env it-resonance-main-api")
    
    print(f"\n📡 App-specific variables set:")
    print(f"   Main API: IFLOW_API_URL, BOOMI_API_URL")

if __name__ == "__main__":
    main()
