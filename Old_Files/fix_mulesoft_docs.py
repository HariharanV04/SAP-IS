#!/usr/bin/env python3
"""
Script to fix the MuleSoft documentation Mermaid diagrams using LLM
"""

import os
import sys

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from llm_mermaid_fixer import LLMMermaidFixer

def main():
    """Fix the MuleSoft documentation"""
    
    # Path to the problematic documentation
    doc_path = "MuleToIS-API/mulesoft_documentation.html"
    
    if not os.path.exists(doc_path):
        print(f"Documentation file not found: {doc_path}")
        return
    
    print("🔧 Starting LLM-powered Mermaid diagram fixing...")
    
    # Read the documentation
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Read documentation file: {len(content)} characters")
    
    # Initialize the LLM fixer
    fixer = LLMMermaidFixer()
    
    if not fixer.anthropic_client:
        print("❌ LLM fixer not available - check Anthropic API key")
        return
    
    print("🤖 Using Anthropic Claude to fix Mermaid diagrams...")
    
    # Fix the documentation
    fixed_content, success = fixer.fix_mermaid_documentation(content)
    
    if success:
        # Save the fixed documentation
        output_path = doc_path.replace('.html', '_fixed.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Successfully fixed Mermaid diagrams!")
        print(f"📁 Fixed documentation saved to: {output_path}")
        print(f"🌐 Open {output_path} in your browser to test the fixed diagrams")
        
        # Also replace the original if user wants
        replace_original = input("\n🔄 Replace the original file with the fixed version? (y/N): ")
        if replace_original.lower() in ['y', 'yes']:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Original file updated: {doc_path}")
        
    else:
        print("❌ Failed to fix Mermaid diagrams")
        print("💡 Check the logs for more details")

if __name__ == "__main__":
    main()
