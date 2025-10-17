"""
Mermaid Diagram Syntax Validator and Fixer
Prevents syntax errors in generated Mermaid diagrams
"""

import re
import logging

logger = logging.getLogger(__name__)

class MermaidValidator:
    """Validates and fixes Mermaid diagram syntax"""
    
    def __init__(self):
        self.common_fixes = [
            # Fix special characters in labels
            (r'\|"([^"]*\{[^}]*\}[^"]*)"\|', r'|"\1"|'),  # Escape curly braces in labels
            (r'\|"([^"]*\$[^"]*)"\|', r'|"\1"|'),         # Escape dollar signs in labels

            # Fix node ID naming issues - replace hyphens with underscores
            (r'([A-Za-z0-9_]+)-([A-Za-z0-9_-]+)', r'\1_\2'),  # Replace hyphens in node IDs

            # Fix node labels with special characters
            (r'([A-Za-z0-9_]+)\[([^\]]*\{[^}]*\}[^\]]*)\]', r'\1["\2"]'),  # Quote labels with curly braces
            (r'([A-Za-z0-9_]+)\[([^\]]*\$[^\]]*)\]', r'\1["\2"]'),         # Quote labels with dollar signs
            (r'([A-Za-z0-9_]+)\[([^\]]*\/[^\]]*)\]', r'\1["\2"]'),         # Quote labels with slashes

            # Fix arrow syntax
            (r'-->\s*\|\s*([^|]*)\s*\|\s*', r'-->|"\1"| '),  # Ensure labels are quoted

            # Fix class definitions
            (r'classDef\s+([^\s]+)\s+([^;]*);?', r'classDef \1 \2'),  # Normalize classDef syntax

            # Fix comment syntax
            (r'%%\s*([^\n]*)', r'%% \1'),  # Normalize comments
        ]
        
        self.reserved_words = [
            'graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram',
            'journey', 'gantt', 'pie', 'gitgraph', 'mindmap', 'timeline'
        ]
        
        self.invalid_chars = ['<', '>', '&', '"', "'"]
    
    def validate_and_fix(self, mermaid_content: str) -> tuple[str, list[str]]:
        """
        Validates and fixes Mermaid diagram syntax
        
        Args:
            mermaid_content: Raw Mermaid diagram content
            
        Returns:
            tuple: (fixed_content, list_of_issues_found)
        """
        issues = []
        fixed_content = mermaid_content
        
        try:
            # Apply common fixes
            for pattern, replacement in self.common_fixes:
                old_content = fixed_content
                fixed_content = re.sub(pattern, replacement, fixed_content)
                if old_content != fixed_content:
                    issues.append(f"Applied fix: {pattern} -> {replacement}")
            
            # Validate diagram type
            if not self._has_valid_diagram_type(fixed_content):
                issues.append("Missing or invalid diagram type declaration")
                fixed_content = "flowchart TD\n" + fixed_content
            
            # Fix node labels with special characters
            fixed_content, label_issues = self._fix_node_labels(fixed_content)
            issues.extend(label_issues)
            
            # Fix arrow labels
            fixed_content, arrow_issues = self._fix_arrow_labels(fixed_content)
            issues.extend(arrow_issues)
            
            # Validate class definitions
            class_issues = self._validate_class_definitions(fixed_content)
            issues.extend(class_issues)
            
            # Remove invalid characters
            fixed_content, char_issues = self._remove_invalid_characters(fixed_content)
            issues.extend(char_issues)
            
            logger.info(f"Mermaid validation completed. Found {len(issues)} issues.")
            
        except Exception as e:
            logger.error(f"Error during Mermaid validation: {str(e)}")
            issues.append(f"Validation error: {str(e)}")
        
        return fixed_content, issues
    
    def _has_valid_diagram_type(self, content: str) -> bool:
        """Check if content starts with a valid diagram type"""
        first_line = content.strip().split('\n')[0].strip()
        return any(word in first_line for word in self.reserved_words)
    
    def _fix_node_labels(self, content: str) -> tuple[str, list[str]]:
        """Fix node labels that contain special characters"""
        issues = []
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            original_line = line

            # Fix node IDs with hyphens (replace with underscores)
            line = re.sub(r'([A-Za-z0-9_]+)-([A-Za-z0-9_-]+)', r'\1_\2', line)

            # Fix labels with special characters
            if '[' in line and ']' in line:
                # Extract node definitions - handle both quoted and unquoted labels
                node_pattern = r'([A-Za-z0-9_]+)\[([^\]]*)\]'
                matches = re.findall(node_pattern, line)

                for node_id, label in matches:
                    # Skip if already quoted
                    if label.startswith('"') and label.endswith('"'):
                        continue

                    # Check for special characters that need quoting
                    special_chars = ['{', '}', '$', '/', '#', ':', '*', '?', '<', '>', '|']
                    if any(char in label for char in special_chars):
                        # Quote the label if it contains special characters
                        quoted_label = f'"{label}"'
                        line = line.replace(f'{node_id}[{label}]', f'{node_id}[{quoted_label}]')
                        issues.append(f"Quoted label with special characters: {label}")

            if line != original_line:
                issues.append(f"Fixed node definition: {original_line.strip()} -> {line.strip()}")

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), issues
    
    def _fix_arrow_labels(self, content: str) -> tuple[str, list[str]]:
        """Fix arrow labels that might cause syntax errors"""
        issues = []
        
        # Fix arrow labels with special characters
        arrow_pattern = r'-->\s*\|\s*([^|]*)\s*\|'
        
        def fix_arrow_label(match):
            label = match.group(1)
            if any(char in label for char in ['{', '}', '$', '/', '#']):
                issues.append(f"Fixed arrow label with special characters: {label}")
                return f'-->|"{label}"|'
            return match.group(0)
        
        fixed_content = re.sub(arrow_pattern, fix_arrow_label, content)
        
        return fixed_content, issues
    
    def _validate_class_definitions(self, content: str) -> list[str]:
        """Validate class definitions"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('classDef'):
                # Check for proper classDef syntax
                if not re.match(r'classDef\s+\w+\s+[^;]*', line.strip()):
                    issues.append(f"Line {line_num}: Invalid classDef syntax: {line.strip()}")
        
        return issues
    
    def _remove_invalid_characters(self, content: str) -> tuple[str, list[str]]:
        """Remove or escape invalid characters"""
        issues = []
        fixed_content = content
        
        # Replace problematic characters in labels
        replacements = {
            '&': 'and',
            '<': 'lt',
            '>': 'gt',
        }
        
        for char, replacement in replacements.items():
            if char in fixed_content:
                fixed_content = fixed_content.replace(char, replacement)
                issues.append(f"Replaced invalid character '{char}' with '{replacement}'")
        
        return fixed_content, issues

def validate_mermaid_in_documentation(documentation_content: str) -> str:
    """
    Validates and fixes Mermaid diagrams in documentation content
    
    Args:
        documentation_content: Full documentation content with Mermaid diagrams
        
    Returns:
        Fixed documentation content
    """
    validator = MermaidValidator()
    
    # Find Mermaid code blocks
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    def fix_mermaid_block(match):
        mermaid_content = match.group(1)
        fixed_content, issues = validator.validate_and_fix(mermaid_content)
        
        if issues:
            logger.info(f"Fixed Mermaid diagram issues: {issues}")
        
        return f"```mermaid\n{fixed_content}\n```"
    
    # Apply fixes to all Mermaid blocks
    fixed_documentation = re.sub(mermaid_pattern, fix_mermaid_block, documentation_content, flags=re.DOTALL)
    
    return fixed_documentation
