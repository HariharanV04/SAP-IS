#!/usr/bin/env python3
"""
Script to verify that all Claude model references have been updated to claude-sonnet-4-20250514
"""

import os
import re
import glob

def search_files_for_patterns(directory, patterns, extensions):
    """Search for patterns in files with specific extensions"""
    results = []
    
    for ext in extensions:
        for file_path in glob.glob(f"{directory}/**/*{ext}", recursive=True):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = content.split('\n')[line_num - 1].strip()
                        results.append({
                            'file': file_path,
                            'line': line_num,
                            'pattern': pattern,
                            'match': match.group(),
                            'line_content': line_content
                        })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return results

def main():
    """Main verification function"""
    print("🔍 Verifying Claude model updates...")
    
    # Patterns to search for (old model references)
    old_patterns = [
        r'claude-3-sonnet-20240229',
        r'claude-3-opus-20240229',
        r'claude-3-haiku-20240307',
        r'gpt-4(?!o)',  # gpt-4 but not gpt-4o
        r'model="gpt-4"',
        r'model=.*gpt-4.*',
    ]
    
    # File extensions to search
    extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.md', '.json']
    
    # Directories to search
    directories = [
        'app',
        'MuleToIS-API',
        'BoomiToIS-API',
        'IFA-Project/frontend/src',
        '.'  # Root directory for config files
    ]
    
    all_results = []
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"📁 Searching in {directory}...")
            results = search_files_for_patterns(directory, old_patterns, extensions)
            all_results.extend(results)
    
    # Filter out acceptable patterns
    filtered_results = []
    acceptable_patterns = [
        'gpt-4o',  # This is the updated OpenAI model
        'claude-sonnet-4-20250514',  # This is our target model
        'model="claude-sonnet-4-20250514"',
        'args.model == \'gpt-4\'',  # Command line argument checks
        'default=\'gpt-4\'',  # Default values that get overridden
    ]
    
    for result in all_results:
        is_acceptable = False
        for acceptable in acceptable_patterns:
            if acceptable in result['line_content']:
                is_acceptable = True
                break
        
        if not is_acceptable:
            filtered_results.append(result)
    
    # Report results
    if filtered_results:
        print(f"\n❌ Found {len(filtered_results)} old model references that need updating:")
        print("=" * 80)
        
        for result in filtered_results:
            print(f"📄 File: {result['file']}")
            print(f"📍 Line {result['line']}: {result['line_content']}")
            print(f"🔍 Pattern: {result['pattern']}")
            print(f"🎯 Match: {result['match']}")
            print("-" * 40)
    else:
        print("\n✅ All model references have been successfully updated!")
        print("🎉 All files now use claude-sonnet-4-20250514 or gpt-4o")
    
    # Also check for the target model
    target_patterns = [r'claude-sonnet-4-20250514']
    target_results = []
    
    for directory in directories:
        if os.path.exists(directory):
            results = search_files_for_patterns(directory, target_patterns, extensions)
            target_results.extend(results)
    
    if target_results:
        print(f"\n✅ Found {len(target_results)} references to claude-sonnet-4-20250514:")
        for result in target_results:
            print(f"  📄 {result['file']}:{result['line']}")
    
    print(f"\n📊 Summary:")
    print(f"  • Old model references found: {len(filtered_results)}")
    print(f"  • New model references found: {len(target_results)}")
    print(f"  • Total files searched: {len(set(r['file'] for r in all_results))}")

if __name__ == "__main__":
    main()
