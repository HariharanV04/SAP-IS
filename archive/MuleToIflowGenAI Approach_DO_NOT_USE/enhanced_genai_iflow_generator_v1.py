"""
Enhanced GenAI iFlow Generator V1

This module provides a self-contained implementation of the GenAI iFlow Generator
to ensure compatibility with SAP Integration Suite. It uses GenAI to generate iFlow XML
and adds all mandatory files required for SAP Integration Suite.

This version incorporates enhancements from json_to_iflow.py for better BPMN layout
and component handling.
"""

import os
import json
import re
import zipfile
import argparse
import datetime
from enhanced_iflow_templates import EnhancedIFlowTemplates

class EnhancedGenAIIFlowGenerator:
    """
    An enhanced version of the GenAI iFlow Generator that ensures compatibility with SAP Integration Suite
    """

    def __init__(self, api_key=None, model="gpt-4", provider="openai"):
        """
        Initialize the generator

        Args:
            api_key (str): API key for the LLM service (optional)
            model (str): Model to use for the LLM service
            provider (str): AI provider to use ('openai', 'claude', or 'local')
        """
        # Initialize the original generator
        self.templates = EnhancedIFlowTemplates()
        self.model = model
        self.provider = provider
        self.api_key = api_key

        # Track generation approach (GenAI or template-based)
        self.generation_approach = "unknown"
        self.generation_details = {}

        # Initialize OpenAI if needed
        if provider == "openai" and api_key:
            try:
                import openai
                openai.api_key = api_key
                self.openai = openai
            except ImportError:
                print("OpenAI package not found. Please install it with 'pip install openai'")
                self.provider = "local"

        # Initialize Anthropic if needed
        elif provider == "claude" and api_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("Anthropic package not found. Please install it with 'pip install anthropic'")
                self.provider = "local"

    def generate_iflow(self, markdown_content, output_path, iflow_name):
        """
        Generate an iFlow from markdown content

        Args:
            markdown_content (str): The markdown content to analyze
            output_path (str): Path to save the generated iFlow
            iflow_name (str): Name of the iFlow

        Returns:
            str: Path to the generated iFlow ZIP file
        """
        # Step 1: Use GenAI to analyze the markdown and determine components
        components = self._analyze_with_genai(markdown_content)

        # Step 2: Generate the iFlow files
        iflow_files = self._generate_iflow_files(components, iflow_name, markdown_content)

        # Step 3: Create the ZIP file
        zip_path = self._create_zip_file(iflow_files, output_path, iflow_name)

        return zip_path

    def _analyze_with_genai(self, markdown_content):
        """
        Use GenAI to analyze the markdown content and determine components

        Args:
            markdown_content (str): The markdown content to analyze

        Returns:
            dict: Structured representation of components needed for the iFlow
        """
        # Create a prompt for the LLM
        prompt = self._create_detailed_analysis_prompt(markdown_content)

        # Call the LLM API
        response = self._call_llm_api(prompt)

        # Save the raw response for debugging
        os.makedirs("genai_debug", exist_ok=True)
        with open("genai_debug/raw_analysis_response.txt", "w", encoding="utf-8") as f:
            f.write(response)
        print("Saved raw analysis response to genai_debug/raw_analysis_response.txt")

        # Parse the response to get the components
        components = self._parse_llm_response(response)

        # Save the parsed components for debugging
        with open("genai_debug/parsed_components.json", "w", encoding="utf-8") as f:
            json.dump(components, f, indent=2)
        print("Saved parsed components to genai_debug/parsed_components.json")

        # Generate Groovy scripts for complex transformations
        components = self._generate_transformation_scripts(components)

        # Apply intelligent connection logic to ensure proper component connections
        components = self._create_intelligent_connections(components)

        # Save the final components with scripts for debugging
        with open("genai_debug/final_components.json", "w", encoding="utf-8") as f:
            json.dump(components, f, indent=2)
        print("Saved final components to genai_debug/final_components.json")

        return components

    def _create_detailed_analysis_prompt(self, markdown_content):
        """
        Create a detailed prompt for analyzing the markdown content

        Args:
            markdown_content (str): The markdown content to analyze

        Returns:
            str: The prompt for analyzing the markdown content
        """
        # Use a regular string to avoid issues with raw strings and triple quotes
        template = """
        You are an expert in API design and SAP Integration Suite. Analyze the following markdown content
        and extract the components needed for an iFlow.

        IMPORTANT: You MUST return a valid JSON structure with the following format. Do NOT return XML directly.

        {
            "api_name": "Name of the API",
            "base_url": "Base URL of the API",
            "endpoints": [
                {
                    "method": "HTTP method (GET, POST, etc.)",
                    "path": "Path of the endpoint",
                    "purpose": "Purpose of the endpoint",
                    "components": [
                        {
                            "type": "Component type - MUST be one of: enricher, request_reply, json_to_xml_converter, groovy_script, odata, odata_receiver",
                            "name": "Component name - should be descriptive of its purpose",
                            "id": "Component ID - must be unique across all components",
                            "config": {
                                "endpoint_path": "For request_reply components, the path of the endpoint",
                                "content": "For content_modifier components, the content to set",
                                "script": "For groovy_script components, the name of the script file",
                                "address": "For odata components, the URL of the OData service",
                                "resource_path": "For odata components, the entity set or resource path to query",
                                "operation": "For odata components, the operation to perform (Query(GET), Create(POST), etc.)",
                                "query_options": "For odata components, query options like $select, $filter, etc."
                            }
                        }
                    ],
                    "sequence": [
                        "List of component IDs in the order they should be connected",
                        "For example: ['StartEvent_2', 'JSONtoXMLConverter_1', 'ContentModifier_1', 'RequestReply_1', 'EndEvent_2']"
                    ],
                    "transformations": [
                        {
                            "name": "Transformation name (e.g., 'TransformProductData.groovy')",
                            "type": "groovy",
                            "script": "Actual Groovy script content"
                        }
                    ]
                }
            ]
        }

        CRITICAL REQUIREMENTS:

        1. The JSON structure MUST be valid and complete
        2. Each component MUST have a unique ID
        3. Component types MUST be one of the allowed types listed above
        4. The "sequence" array MUST list ALL component IDs in the order they should be connected
        5. For OData operations, use the dedicated "odata" component type:
           ```json
           {
               "type": "odata",
               "name": "Get_Products",
               "id": "odata_1",
               "config": {
                   "address": "https://example.com/odata/service",
                   "resource_path": "Products",
                   "operation": "Query(GET)",
                   "query_options": "$select=Id,Name,Description"
               }
           }
           ```
        """

        # Add the markdown content using normal string formatting
        return template + f"""
        6. For each endpoint, include at minimum:
           - An enricher component to prepare the request (NOT content_modifier)
           - A request_reply component to handle the external call (which requires a receiver participant and message flow)
           - An enricher component to format the response (NOT content_modifier)

        Example of a valid component sequence for an OData endpoint:
        "sequence": ["StartEvent_2", "JSONtoXMLConverter_root", "ContentModifier_root_1", "odata_1", "ContentModifier_response", "EndEvent_2"]

        DO NOT include XML content in your response. Return ONLY the JSON structure as specified above.

        Markdown content:
        {markdown_content}"""

    def _parse_llm_response(self, response):
        """
        Parse the LLM response to get the components

        Args:
            response (str): The response from the LLM

        Returns:
            dict: Structured representation of components needed for the iFlow
        """
        # Try to extract JSON from the response
        try:
            # Find JSON content in the response (it might be wrapped in markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no code blocks, try to parse the entire response
                json_str = response

            # Parse the JSON
            components = json.loads(json_str)

            # Validate the structure
            if not isinstance(components, dict):
                raise ValueError("Response is not a valid JSON object")

            # Ensure required fields are present
            if "endpoints" not in components:
                components["endpoints"] = []

            # Add default endpoint if none are specified
            if not components["endpoints"]:
                components["endpoints"] = [{
                    "method": "GET",
                    "path": "/",
                    "purpose": "Default endpoint",
                    "components": [],
                    "connections": [],
                    "transformations": []
                }]

            return components

        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            # Return a default structure if parsing fails
            return {
                "api_name": "Default API",
                "base_url": "/api/v1",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/",
                        "purpose": "Default endpoint",
                        "components": [],
                        "connections": [],
                        "transformations": []
                    }
                ],
                "parameters": []
            }
