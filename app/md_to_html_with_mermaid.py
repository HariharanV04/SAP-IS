#!/usr/bin/env python
"""
Convert a Markdown file to HTML with Mermaid diagram support.
"""
import os
import sys
import argparse
import re
import markdown
from pathlib import Path

# Import Mermaid validator
try:
    from mermaid_validator import MermaidValidator
except ImportError:
    MermaidValidator = None

def convert_markdown_to_html(markdown_file, output_file=None):
    """
    Convert Markdown file to HTML with Mermaid support.
    
    Args:
        markdown_file: Path to the markdown file
        output_file: Optional path for the output file. If not provided, 
                    will use the same filename with .html extension.
    
    Returns:
        Path to the generated HTML file
    """
    # Default output file
    if output_file is None:
        output_file = os.path.splitext(markdown_file)[0] + '_with_mermaid.html'
    
    # Read the markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Find Mermaid code blocks and save them before markdown conversion
    mermaid_blocks = []
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    # Function to replace code blocks with placeholders
    def replace_mermaid(match):
        mermaid_content = match.group(1)

        # Validate and fix Mermaid syntax if validator is available
        if MermaidValidator:
            try:
                validator = MermaidValidator()
                fixed_content, issues = validator.validate_and_fix(mermaid_content)
                if issues:
                    print(f"Fixed Mermaid syntax issues: {issues}")
                mermaid_content = fixed_content
            except Exception as e:
                print(f"Mermaid validation failed: {e}")

        mermaid_blocks.append(mermaid_content)
        return f'MERMAID_PLACEHOLDER_{len(mermaid_blocks) - 1}'
    
    # Replace Mermaid blocks with placeholders
    processed_markdown = re.sub(mermaid_pattern, replace_mermaid, markdown_content, flags=re.DOTALL)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        processed_markdown,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc'
        ]
    )
    
    # Replace placeholders with Mermaid pre tags
    for i, block in enumerate(mermaid_blocks):
        placeholder = f'<p>MERMAID_PLACEHOLDER_{i}</p>'
        mermaid_html = f'<pre class="mermaid">\n{block}\n</pre>'
        html_content = html_content.replace(placeholder, mermaid_html)
    
    # Create the HTML document with Mermaid support
    final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation with Mermaid</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #1565c0;
        }}
        pre {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            background: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        pre.mermaid {{
            text-align: center;
            background: white;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .note {{
            background: #e3f2fd;
            padding: 10px;
            border-left: 4px solid #1565c0;
            margin: 10px 0;
        }}
        .insights {{
            background: #f3e5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .best-practices {{
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .security {{
            background: #ffebee;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    {html_content}
    
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</body>
</html>"""
    
    # Write the HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)

    # Apply enhanced LLM Mermaid fixes to ensure diagrams render correctly
    try:
        from llm_mermaid_fixer import fix_documentation_with_llm

        # Read the generated HTML file
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Apply LLM-powered fixes and professional styling
        fixed_content = fix_documentation_with_llm(html_content)

        # Write back the enhanced content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"Applied enhanced LLM Mermaid fixes and professional styling to {output_file}")

    except ImportError as ie:
        print(f"Enhanced LLM Mermaid fixer not available ({ie}), trying minimal fixer...")
        try:
            from minimal_mermaid_fixer import fix_mermaid_syntax_in_html
            fix_mermaid_syntax_in_html(output_file)
            print(f"Applied minimal Mermaid syntax fixes to {output_file}")
        except ImportError:
            print("Mermaid fixer not available, skipping syntax fixes")
        except Exception as e:
            print(f"Warning: Could not apply minimal Mermaid fixes: {e}")
    except Exception as e:
        print(f"Warning: Could not apply enhanced Mermaid fixes: {e}")
        # Fallback to minimal fixer
        try:
            from minimal_mermaid_fixer import fix_mermaid_syntax_in_html
            fix_mermaid_syntax_in_html(output_file)
            print(f"Applied fallback minimal Mermaid syntax fixes to {output_file}")
        except Exception as fallback_e:
            print(f"Warning: Fallback Mermaid fixes also failed: {fallback_e}")

    print(f"HTML file generated successfully: {output_file}")
    return output_file

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert Markdown to HTML with Mermaid support')
    parser.add_argument('--input', '-i', required=True, help='Input markdown file path')
    parser.add_argument('--output', '-o', help='Output HTML file path')
    args = parser.parse_args()
    
    # Validate that input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Convert markdown to HTML
    html_file = convert_markdown_to_html(args.input, args.output)
    print(f"You can open {html_file} in your browser to view the documentation with rendered Mermaid diagrams")

if __name__ == "__main__":
    main() 