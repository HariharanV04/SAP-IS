"""
LLM-powered Mermaid diagram fixer
Uses AI to intelligently fix Mermaid syntax errors in documentation
"""

import os
import re
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the app directory
app_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(app_dir, '.env')
load_dotenv(env_path)

# Try to import Anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic package not installed. LLM Mermaid fixing will not be available.")

class LLMMermaidFixer:
    """Uses LLM to fix Mermaid diagram syntax errors and enhance HTML styling"""

    def __init__(self):
        self.anthropic_client = None
        self.api_key = os.getenv('ANTHROPIC_API_KEY')

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("LLM Mermaid fixer initialized with Anthropic")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
        else:
            logger.warning("LLM Mermaid fixer not available - missing Anthropic API key or package")
    
    def fix_mermaid_documentation(self, documentation_content: str) -> Tuple[str, bool]:
        """
        Fix Mermaid diagrams in documentation using LLM
        
        Args:
            documentation_content: Full documentation content with Mermaid diagrams
            
        Returns:
            tuple: (fixed_content, success_flag)
        """
        if not self.anthropic_client:
            logger.warning("LLM Mermaid fixer not available")
            return documentation_content, False
        
        try:
            # Extract Mermaid blocks
            mermaid_blocks = self._extract_mermaid_blocks(documentation_content)
            
            if not mermaid_blocks:
                logger.info("No Mermaid blocks found in documentation")
                return documentation_content, True
            
            logger.info(f"Found {len(mermaid_blocks)} Mermaid blocks to fix")
            
            fixed_content = documentation_content
            all_fixes_successful = True
            
            # Fix each Mermaid block
            for i, (original_block, mermaid_content, block_format) in enumerate(mermaid_blocks):
                logger.info(f"Fixing Mermaid block {i+1}/{len(mermaid_blocks)} (format: {block_format})")

                fixed_mermaid, success = self._fix_single_mermaid_block(mermaid_content)

                if success:
                    # Replace the original block with the fixed one in the appropriate format
                    if block_format == 'markdown':
                        fixed_block = f"```mermaid\n{fixed_mermaid}\n```"
                    else:  # HTML format
                        fixed_block = f'<pre class="mermaid">\n{fixed_mermaid}\n</pre>'

                    fixed_content = fixed_content.replace(original_block, fixed_block)
                    logger.info(f"Successfully fixed Mermaid block {i+1}")
                else:
                    logger.warning(f"Failed to fix Mermaid block {i+1}")
                    all_fixes_successful = False
            
            # Enhance HTML styling for professional appearance
            if fixed_content.strip().startswith('<!DOCTYPE html') or fixed_content.strip().startswith('<html'):
                logger.info("Enhancing HTML styling for professional appearance")
                fixed_content = self._enhance_html_styling(fixed_content)

            return fixed_content, all_fixes_successful

        except Exception as e:
            logger.error(f"Error during LLM Mermaid fixing: {e}")
            return documentation_content, False
    
    def _extract_mermaid_blocks(self, content: str) -> list:
        """Extract all Mermaid code blocks from content (both markdown and HTML format)"""
        blocks = []

        # Pattern for markdown format: ```mermaid ... ```
        markdown_pattern = r'```mermaid\n(.*?)\n```'
        for match in re.finditer(markdown_pattern, content, re.DOTALL):
            full_block = match.group(0)
            mermaid_content = match.group(1)
            blocks.append((full_block, mermaid_content, 'markdown'))

        # Pattern for HTML format: <pre class="mermaid"> ... </pre>
        html_pattern = r'<pre class="mermaid">\s*(.*?)\s*</pre>'
        for match in re.finditer(html_pattern, content, re.DOTALL):
            full_block = match.group(0)
            mermaid_content = match.group(1)
            blocks.append((full_block, mermaid_content, 'html'))

        return blocks
    
    def _fix_single_mermaid_block(self, mermaid_content: str) -> Tuple[str, bool]:
        """Fix a single Mermaid diagram using LLM"""
        try:
            prompt = f"""You are a Mermaid diagram syntax expert. Fix the following Mermaid diagram to ensure it renders correctly in browsers.

Common issues to fix:
1. Node IDs with hyphens should use underscores instead
2. Labels with special characters (/, $, {{, }}, :, *, ?) should be quoted
3. Ensure proper flowchart syntax
4. Fix any malformed node definitions
5. Ensure all connections reference valid node IDs

Original Mermaid diagram:
```mermaid
{mermaid_content}
```

Please provide ONLY the corrected Mermaid diagram content (without the ```mermaid wrapper). Maintain the same structure and styling, just fix syntax errors.

Fixed Mermaid diagram:"""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            fixed_content = response.content[0].text.strip()
            
            # Remove any markdown wrapper if present
            if fixed_content.startswith('```mermaid'):
                fixed_content = fixed_content.replace('```mermaid\n', '').replace('\n```', '')
            elif fixed_content.startswith('```'):
                fixed_content = fixed_content.replace('```\n', '').replace('\n```', '')
            
            # Basic validation
            if self._validate_mermaid_syntax(fixed_content):
                return fixed_content, True
            else:
                logger.warning("LLM-fixed Mermaid still has syntax issues")
                return mermaid_content, False
                
        except Exception as e:
            logger.error(f"Error fixing Mermaid with LLM: {e}")
            return mermaid_content, False
    
    def _validate_mermaid_syntax(self, mermaid_content: str) -> bool:
        """Basic validation of Mermaid syntax"""
        try:
            # Check for basic structure
            if not mermaid_content.strip():
                return False
            
            # Check for diagram type declaration
            first_line = mermaid_content.strip().split('\n')[0]
            valid_types = ['flowchart', 'graph', 'sequenceDiagram', 'classDiagram', 'stateDiagram']
            
            if not any(diagram_type in first_line for diagram_type in valid_types):
                logger.warning("No valid diagram type found")
                return False
            
            # Check for balanced brackets
            open_brackets = mermaid_content.count('[')
            close_brackets = mermaid_content.count(']')
            
            if open_brackets != close_brackets:
                logger.warning(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating Mermaid syntax: {e}")
            return False

    def _enhance_html_styling(self, html_content: str) -> str:
        """Enhance HTML styling to look like a professional technical design document"""
        try:
            # Professional CSS styles for technical documentation
            professional_styles = """
    <style>
        /* Professional Technical Document Styling */
        body {
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fafafa;
            color: #333;
        }

        /* Header and Title Styling */
        h1 {
            color: #1e3a8a;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 10px;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 600;
        }

        h2 {
            color: #1e40af;
            border-left: 4px solid #3b82f6;
            padding-left: 15px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 500;
        }

        h3 {
            color: #1e40af;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
            font-weight: 500;
        }

        h4 {
            color: #374151;
            margin-top: 25px;
            margin-bottom: 12px;
            font-size: 1.2em;
            font-weight: 500;
        }

        /* Content Container */
        .document-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }

        /* Table of Contents */
        .toc {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            margin: 20px 0;
        }

        .toc h2 {
            margin-top: 0;
            color: #1e40af;
            border: none;
            padding: 0;
        }

        .toc ol {
            margin: 0;
            padding-left: 20px;
        }

        .toc li {
            margin: 8px 0;
        }

        .toc a {
            color: #3b82f6;
            text-decoration: none;
            font-weight: 500;
        }

        .toc a:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }

        /* Code and Technical Elements */
        code {
            background: #f1f5f9;
            color: #e11d48;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }

        pre {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }

        /* Mermaid Diagrams */
        pre.mermaid {
            text-align: center;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        /* Tables */
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        th {
            background: #3b82f6;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }

        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e2e8f0;
        }

        tr:nth-child(even) {
            background: #f8fafc;
        }

        tr:hover {
            background: #f1f5f9;
        }

        /* Lists */
        ul, ol {
            margin: 15px 0;
            padding-left: 25px;
        }

        li {
            margin: 8px 0;
            line-height: 1.5;
        }

        /* Strong and Emphasis */
        strong {
            color: #1e40af;
            font-weight: 600;
        }

        em {
            color: #6b7280;
            font-style: italic;
        }

        /* Paragraphs */
        p {
            margin: 15px 0;
            text-align: justify;
            line-height: 1.7;
        }

        /* Links */
        a {
            color: #3b82f6;
            text-decoration: none;
        }

        a:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }

        /* Blockquotes */
        blockquote {
            border-left: 4px solid #3b82f6;
            margin: 20px 0;
            padding: 15px 20px;
            background: #f8fafc;
            border-radius: 0 6px 6px 0;
            font-style: italic;
        }

        /* Document Header */
        .document-header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .document-header h1 {
            color: white;
            border: none;
            margin: 0;
            font-size: 2.8em;
        }

        .document-subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }

        /* Company Logo */
        .company-logo {
            position: absolute;
            top: 20px;
            left: 30px;
            height: 60px;
            width: auto;
            opacity: 0.9;
        }

        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }

        .logo-container svg {
            height: 80px;
            width: auto;
            margin-right: 20px;
        }

        /* Footer */
        .document-footer {
            margin-top: 50px;
            padding: 20px;
            text-align: center;
            color: #6b7280;
            border-top: 1px solid #e2e8f0;
            font-size: 0.9em;
        }

        /* Print Styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }

            .document-container {
                box-shadow: none;
                padding: 20px;
            }

            .document-header {
                background: #3b82f6 !important;
                -webkit-print-color-adjust: exact;
            }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            body {
                padding: 20px 10px;
            }

            .document-container {
                padding: 20px;
            }

            h1 {
                font-size: 2em;
            }

            h2 {
                font-size: 1.5em;
            }
        }
    </style>"""

            # Find the existing <style> tag and replace it
            style_pattern = r'<style>.*?</style>'
            if re.search(style_pattern, html_content, re.DOTALL):
                # Replace existing styles
                enhanced_content = re.sub(style_pattern, professional_styles, html_content, flags=re.DOTALL)
            else:
                # Insert styles after <head>
                head_pattern = r'(<head[^>]*>)'
                enhanced_content = re.sub(head_pattern, r'\1' + professional_styles, html_content)

            # Wrap content in professional container if not already wrapped
            if '<div class="document-container">' not in enhanced_content:
                # Find the body content and wrap it
                body_pattern = r'(<body[^>]*>)(.*?)(</body>)'

                def wrap_body_content(match):
                    body_tag = match.group(1)
                    content = match.group(2)
                    closing_tag = match.group(3)

                    # Add document header with logo if title exists
                    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)

                    # Company logo SVG (embedded)
                    logo_svg = '''<svg width="507" height="206" viewBox="0 0 507 206" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M70.2578 134.616C71.3379 112.751 80.8662 95.298 100.193 83.445C108.911 78.1131 118.478 74.7759 128.469 72.7812C133.754 71.7455 139.154 71.1318 144.516 70.4029C146.599 70.1344 148.683 70.0194 150.766 69.9043C151.036 69.9043 151.46 70.2879 151.614 70.5947C153.543 74.5457 155.086 78.6501 156.282 82.8696C157.555 87.4344 158.519 92.0758 158.751 96.8323C158.944 100.63 159.137 104.427 158.867 108.225C157.786 123.453 152.579 137.148 143.089 149.192C132.404 162.733 118.593 171.594 101.851 175.89C96.9909 177.118 92.0532 177.77 87.0383 178C86.7297 178 86.3054 177.731 86.1125 177.463C81.9849 172.208 78.5516 166.531 75.8899 160.432C73.4211 154.793 71.6851 148.885 70.875 142.786C70.5279 140.255 70.4893 137.685 70.2578 134.616Z" fill="#F36F21"/>
<path d="M9 91.999C12.6261 63.8435 35.6173 34.729 71.3386 29.0135C109.76 22.876 139.464 45.6613 150.766 69.0987C150.303 69.0987 149.956 69.0987 149.57 69.0987C125.383 69.0987 101.158 69.0987 76.9706 69.022C73.8074 69.022 70.6056 68.8302 67.4424 68.9069C48.1931 69.2905 30.6796 74.9676 15.2493 86.5521C13.2819 88.0481 11.5074 89.7742 9.61721 91.4237C9.42433 91.5771 9.23146 91.7689 9 91.999Z" fill="#F36F21"/>
<path d="M61.3469 174.855C58.8781 173.934 56.7179 173.128 54.519 172.323C54.3647 172.284 54.2104 172.208 54.0561 172.131C51.0986 170.878 48.9255 168.794 47.5368 165.878C44.2578 159.089 42.0976 151.993 41.0946 144.512C40.516 140.331 40.2074 136.15 40.6317 131.969C41.2489 125.947 42.7148 120.078 44.9522 114.439C50.1985 101.205 59.4181 91.5005 71.6853 84.4041C80.6349 79.2256 90.3174 75.8883 100.308 73.4716C101.196 73.2415 102.083 73.0498 103.24 72.7812C100.347 73.8937 97.724 74.8143 95.178 75.8884C83.8753 80.6832 73.5755 87.0125 65.1274 96.0269C57.8366 103.775 52.8603 112.751 50.7772 123.185C50.1985 126.062 49.7742 129.015 49.6971 131.969C49.3113 147.044 53.0917 161.084 60.9226 174.011C61.0383 174.164 61.1155 174.356 61.3469 174.778V174.855Z" fill="#F36F21"/>
<path d="M90.1253 71.5151C75.0421 73.5098 60.6533 77.5375 47.6533 85.6696C37.6236 91.9221 29.7155 100.169 24.6235 110.91C22.0775 116.319 20.303 121.996 19.6087 127.941C19.0686 132.353 18.8757 136.802 18.5285 141.099C18.5285 141.099 18.3357 140.83 18.1814 140.6C15.9054 136.649 14.0152 132.506 12.4336 128.248C12.0864 127.328 12.125 126.484 12.3178 125.601C14.2852 116.012 17.9885 107.189 24.0449 99.3638C29.7155 92.0372 36.7749 86.3984 44.9916 82.1405C53.2854 77.806 62.1192 75.1592 71.3003 73.5098C77.5496 72.3974 83.8374 71.7452 90.1639 71.5535L90.1253 71.5151Z" fill="#F36F21"/>
<path d="M189.28 104V57.14H196.672V104H189.28ZM250.888 63.674H235.312V104H227.854V63.674H212.212V57.14H250.888V63.674ZM266.412 104V57.14H286.806C288.918 57.14 290.854 57.58 292.614 58.46C294.374 59.34 295.892 60.506 297.168 61.958C298.488 63.41 299.5 65.038 300.204 66.842C300.952 68.646 301.326 70.494 301.326 72.386C301.326 74.454 300.952 76.434 300.204 78.326C299.456 80.218 298.378 81.846 296.97 83.21C295.606 84.574 294 85.564 292.152 86.18L303.174 104H294.858L284.694 87.698H273.804V104H266.412ZM273.804 81.164H286.74C288.104 81.164 289.314 80.768 290.37 79.976C291.426 79.184 292.262 78.128 292.878 76.808C293.494 75.444 293.802 73.97 293.802 72.386C293.802 70.758 293.45 69.306 292.746 68.03C292.042 66.71 291.118 65.654 289.974 64.862C288.874 64.07 287.664 63.674 286.344 63.674H273.804V81.164ZM347.271 65.918C346.611 65.17 345.841 64.51 344.961 63.938C344.081 63.322 343.091 62.794 341.991 62.354C340.891 61.914 339.703 61.562 338.427 61.298C337.195 61.034 335.875 60.902 334.467 60.902C330.375 60.902 327.361 61.694 325.425 63.278C323.533 64.818 322.587 66.93 322.587 69.614C322.587 71.462 323.027 72.914 323.907 73.97C324.831 75.026 326.261 75.884 328.197 76.544C330.133 77.204 332.597 77.886 335.589 78.59C338.933 79.294 341.815 80.13 344.235 81.098C346.655 82.066 348.525 83.386 349.845 85.058C351.165 86.686 351.825 88.908 351.825 91.724C351.825 93.88 351.407 95.75 350.571 97.334C349.735 98.918 348.569 100.238 347.073 101.294C345.577 102.35 343.795 103.142 341.727 103.67C339.659 104.154 337.393 104.396 334.929 104.396C332.509 104.396 330.177 104.154 327.933 103.67C325.733 103.142 323.643 102.394 321.663 101.426C319.683 100.414 317.835 99.138 316.119 97.598L318.429 93.836C319.265 94.716 320.255 95.552 321.399 96.344C322.587 97.092 323.885 97.774 325.293 98.39C326.745 99.006 328.285 99.49 329.913 99.842C331.585 100.15 333.301 100.304 335.061 100.304C338.801 100.304 341.705 99.622 343.773 98.258C345.885 96.894 346.941 94.87 346.941 92.186C346.941 90.25 346.413 88.71 345.357 87.566C344.301 86.378 342.717 85.41 340.605 84.662C338.493 83.914 335.897 83.188 332.817 82.484C329.561 81.736 326.811 80.9 324.567 79.976C322.323 79.052 320.629 77.842 319.485 76.346C318.385 74.806 317.835 72.782 317.835 70.274C317.835 67.37 318.539 64.928 319.947 62.948C321.399 60.924 323.379 59.406 325.887 58.394C328.395 57.338 331.277 56.81 334.533 56.81C336.601 56.81 338.515 57.03 340.275 57.47C342.079 57.866 343.729 58.46 345.225 59.252C346.765 60.044 348.195 61.034 349.515 62.222L347.271 65.918ZM397.195 104H392.707V84.794C392.707 80.922 392.025 78.018 390.661 76.082C389.297 74.102 387.339 73.112 384.787 73.112C383.115 73.112 381.443 73.552 379.771 74.432C378.143 75.268 376.691 76.434 375.415 77.93C374.183 79.382 373.303 81.054 372.775 82.946V104H368.287V55.82H372.775V77.402C374.139 74.85 376.031 72.826 378.451 71.33C380.915 69.79 383.533 69.02 386.305 69.02C388.285 69.02 389.957 69.372 391.321 70.076C392.729 70.78 393.851 71.814 394.687 73.178C395.567 74.498 396.205 76.06 396.601 77.864C396.997 79.624 397.195 81.626 397.195 83.87V104ZM416.005 104V69.614H420.493V104H416.005ZM416.005 62.42V55.82H420.493V62.42H416.005ZM441.269 104V73.178H436.517V69.614H441.269V68.69C441.269 65.874 441.665 63.454 442.457 61.43C443.293 59.406 444.459 57.866 445.955 56.81C447.495 55.71 449.299 55.16 451.367 55.16C452.731 55.16 454.051 55.358 455.327 55.754C456.603 56.15 457.703 56.678 458.627 57.338L457.241 60.572C456.669 60.088 455.921 59.714 454.997 59.45C454.073 59.186 453.149 59.054 452.225 59.054C450.157 59.054 448.551 59.868 447.407 61.496C446.307 63.124 445.757 65.478 445.757 68.558V69.614H455.261V73.178H445.757V104H441.269ZM487.144 102.35C486.792 102.482 486.242 102.724 485.494 103.076C484.746 103.428 483.844 103.736 482.788 104C481.732 104.264 480.588 104.396 479.356 104.396C478.08 104.396 476.87 104.154 475.726 103.67C474.626 103.186 473.746 102.46 473.086 101.492C472.426 100.48 472.096 99.248 472.096 97.796V73.178H467.344V69.614H472.096V57.998H476.584V69.614H484.504V73.178H476.584V96.542C476.672 97.774 477.112 98.698 477.904 99.314C478.74 99.93 479.686 100.238 480.742 100.238C481.974 100.238 483.096 100.04 484.108 99.644C485.12 99.204 485.736 98.896 485.956 98.72L487.144 102.35Z" fill="black"/>
<path d="M186.96 155V126.6H206.04V131.44H192.48V138.76H203.76V143.24H192.48V155H186.96ZM219.929 155V126.6H225.449V150.16H239.929V155H219.929ZM264.783 155.2C262.703 155.2 260.81 154.8 259.103 154C257.423 153.2 255.97 152.12 254.743 150.76C253.543 149.373 252.61 147.827 251.943 146.12C251.276 144.387 250.943 142.613 250.943 140.8C250.943 138.907 251.29 137.107 251.983 135.4C252.703 133.667 253.676 132.133 254.903 130.8C256.156 129.44 257.623 128.373 259.303 127.6C261.01 126.8 262.876 126.4 264.903 126.4C266.956 126.4 268.823 126.813 270.503 127.64C272.21 128.467 273.663 129.573 274.863 130.96C276.063 132.347 276.996 133.893 277.663 135.6C278.33 137.307 278.663 139.067 278.663 140.88C278.663 142.747 278.316 144.547 277.623 146.28C276.93 147.987 275.956 149.52 274.703 150.88C273.476 152.213 272.01 153.267 270.303 154.04C268.623 154.813 266.783 155.2 264.783 155.2ZM256.543 140.8C256.543 142.027 256.73 143.213 257.103 144.36C257.476 145.507 258.01 146.533 258.703 147.44C259.423 148.32 260.29 149.027 261.303 149.56C262.343 150.067 263.516 150.32 264.823 150.32C266.156 150.32 267.343 150.053 268.383 149.52C269.423 148.96 270.29 148.227 270.983 147.32C271.676 146.387 272.196 145.36 272.543 144.24C272.916 143.093 273.103 141.947 273.103 140.8C273.103 139.573 272.903 138.4 272.503 137.28C272.13 136.133 271.583 135.12 270.863 134.24C270.17 133.333 269.303 132.627 268.263 132.12C267.25 131.587 266.103 131.32 264.823 131.32C263.463 131.32 262.263 131.6 261.223 132.16C260.21 132.693 259.356 133.413 258.663 134.32C257.97 135.227 257.436 136.24 257.063 137.36C256.716 138.48 256.543 139.627 256.543 140.8ZM301.485 126.68H306.605L309.845 136.08L313.125 126.68H318.205L313.325 139.6L316.925 148.64L324.965 126.6H330.965L319.605 155H314.845L309.845 143.08L304.885 155H300.125L288.805 126.6H294.725L302.805 148.64L306.325 139.6L301.485 126.68Z" fill="#F36F21"/>
</svg>'''

                    if title_match:
                        title = title_match.group(1)
                        header = f'''
    <div class="document-header">
        <div class="logo-container">
            {logo_svg}
            <div>
                <h1>{title}</h1>
                <div class="document-subtitle">Technical Design Document</div>
            </div>
        </div>
    </div>'''
                        content = content.replace(title_match.group(0), '')
                    else:
                        header = f'''
    <div class="document-header">
        <div class="logo-container">
            {logo_svg}
            <div>
                <h1>Technical Design Document</h1>
                <div class="document-subtitle">System Integration Documentation</div>
            </div>
        </div>
    </div>'''

                    # Wrap in container
                    wrapped_content = f'''
    <div class="document-container">
{header}
{content}
        <div class="document-footer">
            Generated on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Technical Design Document
        </div>
    </div>'''

                    return body_tag + wrapped_content + closing_tag

                enhanced_content = re.sub(body_pattern, wrap_body_content, enhanced_content, flags=re.DOTALL)

            logger.info("Successfully enhanced HTML styling for professional appearance")
            return enhanced_content

        except Exception as e:
            logger.error(f"Error enhancing HTML styling: {e}")
            return html_content

def fix_documentation_with_llm(documentation_content: str) -> str:
    """
    Convenience function to fix Mermaid diagrams in documentation using LLM
    
    Args:
        documentation_content: Full documentation content
        
    Returns:
        Fixed documentation content
    """
    fixer = LLMMermaidFixer()
    fixed_content, success = fixer.fix_mermaid_documentation(documentation_content)
    
    if success:
        logger.info("Successfully fixed Mermaid diagrams with LLM")
    else:
        logger.warning("LLM Mermaid fixing had some issues")
    
    return fixed_content

# CLI interface for testing
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Fix Mermaid diagrams and enhance HTML styling')
    parser.add_argument('file_path', help='Path to the HTML file to fix')
    parser.add_argument('--professional', '-p', action='store_true',
                       help='Apply professional styling (default: enabled for HTML files)')
    parser.add_argument('--mermaid-only', '-m', action='store_true',
                       help='Only fix Mermaid diagrams, skip styling enhancement')

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"File not found: {args.file_path}")
        sys.exit(1)

    print("🔧 Starting LLM-powered documentation enhancement...")

    # Read the file
    with open(args.file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"📄 Processing file: {args.file_path} ({len(content)} characters)")

    # Fix Mermaid diagrams and enhance styling
    fixer = LLMMermaidFixer()

    if args.mermaid_only:
        print("🎯 Mermaid-only mode: Fixing diagrams without styling enhancement")
        # Temporarily disable styling enhancement
        original_method = fixer._enhance_html_styling
        fixer._enhance_html_styling = lambda x: x
        fixed_content, success = fixer.fix_mermaid_documentation(content)
        fixer._enhance_html_styling = original_method
    else:
        print("✨ Full enhancement mode: Fixing Mermaid diagrams and applying professional styling")
        fixed_content, success = fixer.fix_mermaid_documentation(content)

    if success:
        # Save the fixed file
        if args.mermaid_only:
            output_path = args.file_path.replace('.html', '_mermaid_fixed.html')
        else:
            output_path = args.file_path.replace('.html', '_professional.html')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"✅ Enhanced documentation saved to: {output_path}")
        print(f"🌐 Open {output_path} in your browser to see the results")

        # Show what was enhanced
        if not args.mermaid_only:
            print("\n📊 Enhancements applied:")
            print("  • Professional typography and spacing")
            print("  • Enhanced color scheme and layout")
            print("  • Improved table and code styling")
            print("  • Better Mermaid diagram presentation")
            print("  • Responsive design for mobile devices")
            print("  • Print-friendly styling")
    else:
        print("❌ Failed to enhance documentation")
        print("💡 Check the logs for more details")
