"""
Script to generate an iFlow using GenAI (Claude) or template-based approach

This script can use either:
1. The enhanced GenAI iFlow generator to create an iFlow based on a markdown file
2. A template-based approach using components from Simple_Hello_iFlow.iflw

It reads the Claude API key from the .env file.
"""

import os
import sys
import argparse
import dotenv
from enhanced_genai_iflow_generator import EnhancedGenAIIFlowGenerator
from bpmn_templates import TemplateBpmnGenerator
from json_to_iflow_converter import JsonToIflowConverter

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate an iFlow using GenAI or template-based approach with GenAI enhancement")

    # Add mutually exclusive group for approach selection
    approach_group = parser.add_mutually_exclusive_group()
    approach_group.add_argument("--use-templates", action="store_true",
                      help="Use template-based approach with GenAI enhancement (uses templates from Simple_Hello_iFlow.iflw)")
    approach_group.add_argument("--use-json-converter", action="store_true",
                      help="Use JSON to iFlow converter with GenAI enhancement (converts JSON to iFlow XML)")

    parser.add_argument("--markdown-file", default="simple_api_test.md",
                      help="Path to the markdown file")
    parser.add_argument("--output-dir", default="genai_output",
                      help="Output directory for the generated iFlow")
    parser.add_argument("--iflow-name", default="SimpleProductAPI",
                      help="Name of the generated iFlow")
    return parser.parse_args()

def read_markdown_file(file_path):
    """Read markdown content from a file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
        print(f"Successfully read markdown content from {file_path}")
        return content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        print("Using default markdown content instead...")
        # Fallback to default markdown content if file can't be read
        return """
# Simple Product API

## Overview
This API provides access to product information.

## Base URL
`https://example.com/api`

## Endpoints

### Get Products
Retrieves a list of all products.

**Method**: GET
**Path**: `/products`
**Response**: JSON array of product objects

**Process Flow**:
1. Prepare request headers
2. Log the request
3. Call OData Products service
4. Set response headers
5. Transform response to required format

### Get Product Details
Retrieves details for a specific product.

**Method**: GET
**Path**: `/products/{id}`
**Parameters**:
- `id` (path parameter): The product ID

**Response**: JSON object with product details

**Process Flow**:
1. Extract product ID from request
2. Log the request with product ID
3. Call OData Product Detail service
4. Set response headers
5. Transform product detail to required format
"""

def generate_with_genai(markdown_content, output_dir, iflow_name):
    """Generate an iFlow using the GenAI approach."""
    # Load environment variables from .env file
    dotenv.load_dotenv()

    # Get the Claude API key from the .env file
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("Error: No Claude API key found in .env file.")
        print("Please add your Claude API key to the .env file as CLAUDE_API_KEY=your_api_key")
        return None

    # Create the generator with Claude API
    print("Initializing GenAI iFlow generator with Claude API...")
    generator = EnhancedGenAIIFlowGenerator(
        api_key=api_key,
        provider="claude",
        model="claude-3-7-sonnet-20250219"
    )

    # Generate the iFlow
    print(f"Generating iFlow '{iflow_name}' using Claude API...")
    return generator.generate_iflow(markdown_content, output_dir, iflow_name)

def generate_with_templates(markdown_content, output_dir, iflow_name):
    """Generate an iFlow using the template-based approach with GenAI enhancement."""
    print("Initializing template-based iFlow generator...")
    generator = TemplateBpmnGenerator()

    # First, use the GenAI approach to analyze the markdown and get the components
    print("Analyzing markdown with GenAI to extract components...")
    dotenv.load_dotenv()
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("Error: No Claude API key found in .env file.")
        print("Please add your Claude API key to the .env file as CLAUDE_API_KEY=your_api_key")
        return None

    genai_generator = EnhancedGenAIIFlowGenerator(
        api_key=api_key,
        provider="claude",
        model="claude-3-7-sonnet-20250219"
    )

    # Analyze the markdown to get components
    components = genai_generator._analyze_with_genai(markdown_content)

    # Save the components for debugging
    os.makedirs("genai_debug", exist_ok=True)
    import json
    with open(f"genai_debug/components_{iflow_name}.json", "w") as f:
        json.dump(components, f, indent=2)
    print(f"Saved components to genai_debug/components_{iflow_name}.json")

    # Generate the iFlow XML using templates
    print(f"Generating iFlow '{iflow_name}' using template-based approach...")
    iflow_xml = generator.generate_iflow_xml(components, iflow_name)

    # Save the initial template-based iFlow XML for comparison
    os.makedirs(output_dir, exist_ok=True)
    initial_iflow_path = os.path.join(output_dir, f"{iflow_name}_template_initial.iflw")
    with open(initial_iflow_path, "w") as f:
        f.write(iflow_xml)
    print(f"Saved initial template-based iFlow XML to {initial_iflow_path}")

    # Enhance the iFlow XML using GenAI
    print("Enhancing the iFlow XML with GenAI...")
    enhancement_prompt = f"""
You are an expert in SAP Integration Suite iFlow development. I have generated an iFlow XML file using templates from Simple_Hello_iFlow.iflw.
Please review and enhance this iFlow XML to ensure it follows best practices and will work correctly in SAP Integration Suite.

The iFlow is based on this markdown description:
{markdown_content}

The current iFlow XML is:
{iflow_xml}

Please provide an enhanced version of this iFlow XML that:
1. Ensures all component connections are correct
2. Adds any missing properties or attributes needed for SAP Integration Suite
3. Improves the layout and positioning of components
4. Ensures OData components are properly configured
5. Adds any missing components that would be needed based on the markdown description

Return ONLY the enhanced XML without any explanations or markdown formatting.
"""

    # Call Claude API to enhance the iFlow XML
    enhanced_iflow_xml = genai_generator._call_llm_api(enhancement_prompt)

    # Clean up the response to extract just the XML
    if "```xml" in enhanced_iflow_xml:
        enhanced_iflow_xml = enhanced_iflow_xml.split("```xml")[1].split("```")[0].strip()
    elif "```" in enhanced_iflow_xml:
        enhanced_iflow_xml = enhanced_iflow_xml.split("```")[1].split("```")[0].strip()

    # Save the enhanced iFlow XML
    enhanced_iflow_path = os.path.join(output_dir, f"{iflow_name}.iflw")
    with open(enhanced_iflow_path, "w") as f:
        f.write(enhanced_iflow_xml)
    print(f"Saved GenAI-enhanced iFlow XML to {enhanced_iflow_path}")

    # Save the enhancement prompt and response for debugging
    with open(f"genai_debug/enhancement_prompt_{iflow_name}.txt", "w") as f:
        f.write(enhancement_prompt)
    with open(f"genai_debug/enhancement_response_{iflow_name}.txt", "w") as f:
        f.write(enhanced_iflow_xml)
    print(f"Saved enhancement details to genai_debug/")

    # Create a ZIP file with the enhanced iFlow
    import zipfile
    zip_path = os.path.join(output_dir, f"{iflow_name}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(enhanced_iflow_path, arcname=f"src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw")
    print(f"Created ZIP file at {zip_path}")

    return zip_path

def generate_with_json_converter(markdown_content, output_dir, iflow_name):
    """Generate an iFlow using the JSON to iFlow converter with GenAI enhancement."""
    print("Initializing JSON to iFlow converter...")
    converter = JsonToIflowConverter()

    # First, use the GenAI approach to analyze the markdown and get the components
    print("Analyzing markdown with GenAI to extract components...")
    dotenv.load_dotenv()
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("Error: No Claude API key found in .env file.")
        print("Please add your Claude API key to the .env file as CLAUDE_API_KEY=your_api_key")
        return None

    genai_generator = EnhancedGenAIIFlowGenerator(
        api_key=api_key,
        provider="claude",
        model="claude-3-7-sonnet-20250219"
    )

    # Analyze the markdown to get components
    components = genai_generator._analyze_with_genai(markdown_content)

    # Save the components for debugging
    os.makedirs("genai_debug", exist_ok=True)
    import json
    with open(f"genai_debug/components_{iflow_name}.json", "w") as f:
        json.dump(components, f, indent=2)
    print(f"Saved components to genai_debug/components_{iflow_name}.json")

    # Generate the iFlow XML using the JSON to iFlow converter
    print(f"Generating iFlow '{iflow_name}' using JSON to iFlow converter...")
    iflow_xml = converter.convert(components, iflow_name)

    # Save the initial converter-based iFlow XML for comparison
    os.makedirs(output_dir, exist_ok=True)
    initial_iflow_path = os.path.join(output_dir, f"{iflow_name}_converter_initial.iflw")
    with open(initial_iflow_path, "w") as f:
        f.write(iflow_xml)
    print(f"Saved initial converter-based iFlow XML to {initial_iflow_path}")

    # Enhance the iFlow XML using GenAI
    print("Enhancing the iFlow XML with GenAI...")
    enhancement_prompt = f"""
You are an expert in SAP Integration Suite iFlow development. I have generated an iFlow XML file using a JSON to iFlow converter.
Please review and enhance this iFlow XML to ensure it follows best practices and will work correctly in SAP Integration Suite.

The iFlow is based on this markdown description:
{markdown_content}

The current iFlow XML is:
{iflow_xml}

Please provide an enhanced version of this iFlow XML that:
1. Ensures all component connections are correct
2. Adds any missing properties or attributes needed for SAP Integration Suite
3. Improves the layout and positioning of components
4. Ensures OData components are properly configured
5. Adds any missing components that would be needed based on the markdown description

Return ONLY the enhanced XML without any explanations or markdown formatting.
"""

    # Call Claude API to enhance the iFlow XML
    enhanced_iflow_xml = genai_generator._call_llm_api(enhancement_prompt)

    # Clean up the response to extract just the XML
    if "```xml" in enhanced_iflow_xml:
        enhanced_iflow_xml = enhanced_iflow_xml.split("```xml")[1].split("```")[0].strip()
    elif "```" in enhanced_iflow_xml:
        enhanced_iflow_xml = enhanced_iflow_xml.split("```")[1].split("```")[0].strip()

    # Save the enhanced iFlow XML
    enhanced_iflow_path = os.path.join(output_dir, f"{iflow_name}.iflw")
    with open(enhanced_iflow_path, "w") as f:
        f.write(enhanced_iflow_xml)
    print(f"Saved GenAI-enhanced iFlow XML to {enhanced_iflow_path}")

    # Save the enhancement prompt and response for debugging
    with open(f"genai_debug/enhancement_prompt_{iflow_name}.txt", "w") as f:
        f.write(enhancement_prompt)
    with open(f"genai_debug/enhancement_response_{iflow_name}.txt", "w") as f:
        f.write(enhanced_iflow_xml)
    print(f"Saved enhancement details to genai_debug/")

    # Create a ZIP file with the enhanced iFlow
    import zipfile
    zip_path = os.path.join(output_dir, f"{iflow_name}.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(enhanced_iflow_path, arcname=f"src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw")
    print(f"Created ZIP file at {zip_path}")

    return zip_path

def main():
    """
    Main function to generate an iFlow using GenAI, template-based approach, or JSON converter
    """
    # Parse command-line arguments
    args = parse_args()

    # Read the markdown content
    markdown_content = read_markdown_file(args.markdown_file)

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate the iFlow using the selected approach
    if args.use_templates:
        print("Using template-based approach with GenAI enhancement...")
        zip_path = generate_with_templates(markdown_content, args.output_dir, args.iflow_name)
    elif args.use_json_converter:
        print("Using JSON to iFlow converter with GenAI enhancement...")
        zip_path = generate_with_json_converter(markdown_content, args.output_dir, args.iflow_name)
    else:
        print("Using GenAI approach...")
        zip_path = generate_with_genai(markdown_content, args.output_dir, args.iflow_name)

    if zip_path:
        print(f"\nGenerated iFlow: {zip_path}")
        print("You can now import this ZIP file into SAP Integration Suite.")
    else:
        print("\nFailed to generate iFlow.")
        sys.exit(1)

if __name__ == "__main__":
    main()
