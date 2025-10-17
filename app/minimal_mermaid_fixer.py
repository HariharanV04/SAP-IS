#!/usr/bin/env python3
"""
Minimal Mermaid Syntax Fixer for Post-Document Generation

This script provides essential fixes for common Mermaid syntax errors that occur
during document generation. It's designed to be lightweight and reliable.
"""

import re
import os
import logging

logger = logging.getLogger(__name__)

def fix_mermaid_syntax_errors(html_file_path: str) -> bool:
    """
    Apply minimal essential fixes to Mermaid diagrams in HTML files
    
    Args:
        html_file_path: Path to the HTML file to fix
        
    Returns:
        bool: True if fixes were applied, False otherwise
    """
    if not os.path.exists(html_file_path):
        logger.error(f"File not found: {html_file_path}")
        return False
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = 0
        
        # Find all Mermaid diagrams
        mermaid_pattern = r'<pre class="mermaid">\s*(.*?)\s*</pre>'
        
        def fix_diagram(match):
            nonlocal fixes_applied
            diagram_content = match.group(1)
            
            # Apply essential fixes
            fixed_diagram = apply_essential_fixes(diagram_content)
            
            if fixed_diagram != diagram_content:
                fixes_applied += 1
                return f'<pre class="mermaid">\n{fixed_diagram}\n</pre>'
            
            return match.group(0)
        
        # Apply fixes to all diagrams
        content = re.sub(mermaid_pattern, fix_diagram, content, flags=re.DOTALL)
        
        # Write back if changes were made
        if content != original_content:
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Applied Mermaid fixes to {fixes_applied} diagrams in {html_file_path}")
            return True
        
        logger.info(f"No Mermaid fixes needed for {html_file_path}")
        return False
        
    except Exception as e:
        logger.error(f"Error fixing Mermaid syntax: {e}")
        return False

def apply_essential_fixes(diagram_content: str) -> str:
    """Apply essential fixes to a single Mermaid diagram"""
    
    lines = diagram_content.split('\n')
    fixed_lines = []
    
    # Track what we find
    has_flowchart = False
    node_definitions = set()
    referenced_nodes = set()
    connections = []
    
    # First pass: analyze the diagram
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('%%') or line.startswith('classDef'):
            fixed_lines.append(line)
            continue
        
        # Check for flowchart declaration
        if line.startswith('flowchart') or line.startswith('graph'):
            has_flowchart = True
            fixed_lines.append(line)
            continue
        
        # Find node definitions
        node_match = re.match(r'(\w+)(\[|\{|\()', line)
        if node_match:
            node_definitions.add(node_match.group(1))
            fixed_lines.append(line)
            continue
        
        # Find connections
        if '-->' in line:
            connections.append(line)
            
            # Extract referenced nodes
            parts = line.split('-->')
            if len(parts) >= 2:
                source = parts[0].strip().split()[0]
                target_part = parts[1].strip()
                target_part = re.sub(r'\|[^|]*\|', '', target_part)
                target = target_part.split()[0]
                
                referenced_nodes.add(source)
                referenced_nodes.add(target)
        
        fixed_lines.append(line)
    
    # Essential Fix 1: Add flowchart declaration if missing
    if not has_flowchart:
        fixed_lines.insert(0, 'flowchart TD')
    
    # Essential Fix 2: Add missing node definitions
    missing_nodes = referenced_nodes - node_definitions
    if missing_nodes:
        # Find where to insert definitions (after classDef, before connections)
        insert_index = 0
        for i, line in enumerate(fixed_lines):
            if line.startswith('classDef') or line.startswith('%%'):
                insert_index = i + 1
            elif '-->' in line:
                break
        
        # Add missing node definitions
        for node in sorted(missing_nodes):
            if node.lower() in ['start', 'begin']:
                definition = f"{node}((Start)):::event"
            elif node.lower() in ['end', 'endprocess', 'finish']:
                definition = f"{node}((End)):::event"
            elif '{' in node or 'check' in node.lower() or '?' in node:
                definition = f"{node}{{{node}}}:::router"
            else:
                definition = f"{node}[{node}]:::contentModifier"
            
            fixed_lines.insert(insert_index, definition)
            insert_index += 1
        
        # Add blank line after definitions
        if missing_nodes:
            fixed_lines.insert(insert_index, '')
    
    # Essential Fix 3: Remove problematic subgraph connections
    fixed_lines = [line for line in fixed_lines if not ('-.-> SubProcesses' in line)]
    
    # Essential Fix 4: Fix duplicate Start connections
    start_connections = [line for line in fixed_lines if line.strip().startswith('Start') and '-->' in line]
    if len(start_connections) > 1:
        # Keep only the first one
        kept_first = False
        new_fixed_lines = []
        for line in fixed_lines:
            if line.strip().startswith('Start') and '-->' in line:
                if not kept_first:
                    new_fixed_lines.append(line)
                    kept_first = True
                # Skip additional Start connections
            else:
                new_fixed_lines.append(line)
        fixed_lines = new_fixed_lines
    
    return '\n'.join(fixed_lines)

# Integration function for easy import
def post_process_mermaid_diagrams(html_file_path: str) -> None:
    """
    Convenience function for integration into documentation generators
    
    Args:
        html_file_path: Path to the HTML file to process
    """
    try:
        fix_mermaid_syntax_errors(html_file_path)
    except Exception as e:
        logger.warning(f"Mermaid post-processing failed: {e}")

if __name__ == "__main__":
    import sys
    import argparse
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = argparse.ArgumentParser(description='Minimal Mermaid syntax fixer')
    parser.add_argument('html_file', help='HTML file to fix')
    
    args = parser.parse_args()
    
    success = fix_mermaid_syntax_errors(args.html_file)
    
    if success:
        print("✅ Mermaid syntax fixes applied successfully!")
    else:
        print("✅ No Mermaid syntax fixes needed")
