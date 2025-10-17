"""
Enhanced Prompt Generator

This script enhances the prompt to better guide the AI in generating iFlows with specific components.
"""

import os
import json
import re
import zipfile
import datetime
import argparse
import dotenv
from run_final_generator import FinalIFlowGenerator
from project_template import generate_project_file

class EnhancedPromptGenerator(FinalIFlowGenerator):
    """
    A class that extends FinalIFlowGenerator with an enhanced prompt and improved component handling
    """

    def __init__(self, api_key=None, model="claude-sonnet-4-20250514", provider="claude"):
        """
        Initialize the generator

        Args:
            api_key (str): API key for the LLM service (optional)
            model (str): Model to use for the LLM service
            provider (str): AI provider to use ('openai', 'claude', or 'local')
        """
        # Call the parent's __init__ method to initialize self.templates
        super().__init__(api_key=api_key, model=model, provider=provider)

        # Import the enhanced templates
        from enhanced_iflow_templates import EnhancedIFlowTemplates
        self.templates = EnhancedIFlowTemplates()

    def get_completion(self, prompt):
        """
        Get a completion from the AI model

        Args:
            prompt (str): The prompt to send to the AI model

        Returns:
            str: The AI model's response
        """
        # Check which provider to use
        if self.provider == 'claude':
            return self._get_claude_completion(prompt)
        elif self.provider == 'openai':
            return self._get_openai_completion(prompt)
        else:
            # Local mode - return a simple response
            return self._get_local_completion(prompt)

    def _get_claude_completion(self, prompt):
        """
        Get a completion from Claude

        Args:
            prompt (str): The prompt to send to Claude

        Returns:
            str: Claude's response
        """
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.2,
                system="You are an expert in SAP Integration Suite and API design.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text
        except Exception as e:
            print(f"Error getting Claude completion: {str(e)}")
            return self._get_local_completion(prompt)

    def _get_openai_completion(self, prompt):
        """
        Get a completion from OpenAI

        Args:
            prompt (str): The prompt to send to OpenAI

        Returns:
            str: OpenAI's response
        """
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": "You are an expert in SAP Integration Suite and API design."},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting OpenAI completion: {str(e)}")
            return self._get_local_completion(prompt)

    def _get_local_completion(self, prompt):
        """
        Get a local completion (fallback when AI services are not available)

        Args:
            prompt (str): The prompt

        Returns:
            str: A simple response
        """
        print("Using local completion mode (no AI service)")

        # Return a simple JSON structure for the Product API with request_reply_pattern components
        return '''
        {
            "api_name": "Product API",
            "base_url": "/api/products",
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/products",
                    "purpose": "Get all products",
                    "components": [
                        {
                            "type": "request_reply_pattern",
                            "name": "GET_products_Flow",
                            "id": "request_reply_products",
                            "config": {
                                "endpoint_path": "/products",
                                "log_level": "Information"
                            }
                        }
                    ]
                },
                {
                    "method": "GET",
                    "path": "/products/{product_id}",
                    "purpose": "Get product by ID",
                    "components": [
                        {
                            "type": "request_reply_pattern",
                            "name": "GET_product_by_id_Flow",
                            "id": "request_reply_product_id",
                            "config": {
                                "endpoint_path": "/products/{product_id}",
                                "log_level": "Information"
                            }
                        }
                    ]
                },
                {
                    "method": "GET",
                    "path": "/products/odata",
                    "purpose": "OData endpoint for products",
                    "components": [
                        {
                            "type": "request_reply_pattern",
                            "name": "GET_products_odata_Flow",
                            "id": "request_reply_odata",
                            "config": {
                                "endpoint_path": "/products/odata",
                                "log_level": "Information"
                            }
                        },
                        {
                            "type": "odata_receiver",
                            "name": "OData_Products_Service",
                            "id": "odata_receiver_products",
                            "config": {
                                "service_url": "https://example.com/odata/service",
                                "entity_set": "Products"
                            }
                        }
                    ]
                }
            ]
        }
        '''

    def _get_ai_response(self, prompt):
        """
        Get a response from the AI model

        Args:
            prompt (str): The prompt to send to the AI model

        Returns:
            str: The AI model's response
        """
        return self.get_completion(prompt)

    def _parse_api_analysis(self, api_analysis):
        """
        Parse the API analysis from the AI model with improved error handling

        Args:
            api_analysis (str): The API analysis from the AI model

        Returns:
            dict: Parsed API data
        """
        try:
            # Find JSON content in the response and strip whitespace
            json_start = api_analysis.find('{')
            json_end = api_analysis.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_content = api_analysis[json_start:json_end].strip()

                # Try to fix common JSON issues
                # Replace unescaped quotes in strings
                json_content = re.sub(r'(?<!\\)\"([^\"]*?)(?<!\\)\":\s*\"(.*?)(?<!\\)\"', r'"\1": "\2"', json_content)

                # Fix trailing commas in objects and arrays
                json_content = re.sub(r',\s*}', '}', json_content)
                json_content = re.sub(r',\s*]', ']', json_content)

                # Save the fixed JSON for debugging
                debug_dir = os.path.join("output_folder", "debug")
                os.makedirs(debug_dir, exist_ok=True)
                with open(os.path.join(debug_dir, "fixed_api_analysis.json"), "w") as f:
                    f.write(json_content)
                print(f"Saved fixed API analysis to {os.path.join(debug_dir, 'fixed_api_analysis.json')}")

                try:
                    return json.loads(json_content)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}")
                    print("Attempting to fix JSON...")

                    # More aggressive fixing - remove problematic sections and repair incomplete JSON
                    lines = json_content.split('\n')
                    fixed_lines = []

                    for line in lines:
                        # Skip lines that might cause issues
                        if '"type":' in line and ('etc.' in line or '...' in line):
                            continue
                        fixed_lines.append(line)

                    fixed_json = '\n'.join(fixed_lines)

                    # Check if JSON is incomplete and try to repair it
                    open_braces = fixed_json.count('{')
                    close_braces = fixed_json.count('}')
                    open_brackets = fixed_json.count('[')
                    close_brackets = fixed_json.count(']')

                    # Add missing closing braces and brackets
                    if open_braces > close_braces:
                        fixed_json += '}' * (open_braces - close_braces)
                    if open_brackets > close_brackets:
                        fixed_json += ']' * (open_brackets - close_brackets)

                    # Try to repair common JSON syntax errors
                    # Replace trailing commas before closing brackets/braces
                    fixed_json = re.sub(r',\s*}', '}', fixed_json)
                    fixed_json = re.sub(r',\s*]', ']', fixed_json)

                    # Fix missing commas between objects
                    fixed_json = re.sub(r'}\s*{', '},{', fixed_json)

                    # Fix missing commas between array items
                    fixed_json = re.sub(r']\s*\[', '],[', fixed_json)

                    # Save the aggressively fixed JSON for debugging
                    with open(os.path.join(debug_dir, "aggressively_fixed_api_analysis.json"), "w") as f:
                        f.write(fixed_json)
                    print(f"Saved aggressively fixed API analysis to {os.path.join(debug_dir, 'aggressively_fixed_api_analysis.json')}")

                    try:
                        return json.loads(fixed_json)
                    except Exception as json_error:
                        print(f"Could not fix JSON: {str(json_error)}")

                        # Try one more approach - use a partial JSON parser
                        try:
                            # Extract what we can from the partial JSON
                            import json5
                            partial_data = json5.loads(fixed_json)
                            print("Successfully parsed partial JSON with json5")
                            return partial_data
                        except:
                            print("Could not parse with json5, using fallback structure")

            # Fallback to a simple API structure with request-reply pattern
            return {
                "api_name": "Product API",
                "base_url": "/api/products",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/products",
                        "purpose": "Get all products",
                        "components": [
                            {
                                "type": "request_reply_pattern",
                                "name": "GET_products_Flow",
                                "config": {
                                    "endpoint_path": "/products",
                                    "log_level": "Information"
                                }
                            }
                        ]
                    },
                    {
                        "method": "GET",
                        "path": "/products/{id}",
                        "purpose": "Get product by ID",
                        "components": [
                            {
                                "type": "request_reply_pattern",
                                "name": "GET_product_by_id_Flow",
                                "config": {
                                    "endpoint_path": "/products/{id}",
                                    "log_level": "Information"
                                }
                            }
                        ]
                    }
                ]
            }
        except Exception as e:
            print(f"Error parsing API analysis: {str(e)}")
            # Return a simple fallback structure with request-reply pattern
            return {
                "api_name": "Product API",
                "base_url": "/api/products",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/products",
                        "purpose": "Get all products",
                        "components": [
                            {
                                "type": "request_reply_pattern",
                                "name": "GET_products_Flow",
                                "config": {
                                    "endpoint_path": "/products",
                                    "log_level": "Information"
                                }
                            }
                        ]
                    }
                ]
            }

# In the EnhancedPromptGenerator class
    def _generate_iflw_content(self, api_data, iflow_name):
        """
        Generate the iFlow content based on the API data

        Args:
            api_data (dict): The API data
            iflow_name (str): The name of the iFlow

        Returns:
            str: The iFlow content
        """
        # Initialize the templates
        templates = self.templates

        # Create the basic iFlow configuration
        iflow_config = templates.iflow_configuration_template(
            namespace_mapping="",
            log_level="All events",
            csrf_protection="false"
        )

        # Create participants and message flows
        participants = []
        message_flows = []
        process_components = []
        sequence_flows = []
        used_ids = set()  # Track used IDs to prevent duplicates

        # Add default sender participant
        sender_participant = templates.participant_template(
            id="Participant_1",
            name="Sender",
            type="EndpointSender",
            enable_basic_auth="false"
        )
        participants.append(sender_participant)

        # Add integration process participant
        process_participant = templates.integration_process_participant_template(
            id="Participant_Process_1",
            name="Integration Process",
            process_ref="Process_1"
        )
        participants.append(process_participant)

        # Add default HTTPS message flow
        https_flow = templates.https_sender_template(
            id="MessageFlow_10",
            name="HTTPS",
            url_path="/",  # Ensure URL path is not empty
            sender_auth="RoleBased",
            user_role="ESBMessaging.send"
        ).replace("{{source_ref}}", "Participant_1").replace("{{target_ref}}", "StartEvent_2")
        message_flows.append(https_flow)

        # Add start event
        start_event = templates.message_start_event_template(
            id="StartEvent_2",
            name="Start"
        ).replace("{{outgoing_flow}}", "SequenceFlow_Start")
        process_components.append(start_event)
        used_ids.add("StartEvent_2")

        # Process each endpoint
        for i, endpoint in enumerate(api_data.get("endpoints", [])):
            # Create components for the endpoint
            endpoint_components = self._create_endpoint_components(endpoint, templates)

            # Add participants and message flows
            participants.extend(endpoint_components.get("participants", []))
            message_flows.extend(endpoint_components.get("message_flows", []))

            # Add process components - check for ID duplicates
            for component in endpoint_components.get("process_components", []):
                id_match = re.search(r'id="([^"]+)"', component)
                if id_match:
                    component_id = id_match.group(1)
                    if component_id in used_ids:
                        # Generate a new unique ID for this component
                        new_id = templates.generate_unique_id(component_id.split('_')[0] if '_' in component_id else component_id)
                        component = component.replace(f'id="{component_id}"', f'id="{new_id}"')
                        print(f"Fixed duplicate ID: {component_id} -> {new_id}")
                        component_id = new_id
                    
                    used_ids.add(component_id)
                    process_components.append(component)

            # Add sequence flows
            sequence_flows.extend(endpoint_components.get("sequence_flows", []))

        # Add end event
        end_event = templates.message_end_event_template(
            id="EndEvent_2",
            name="End"
        ).replace("{{incoming_flow}}", "SequenceFlow_End")
        process_components.append(end_event)
        used_ids.add("EndEvent_2")

        # Ensure we have a sequence flow from last component to end event
        if process_components and len(process_components) > 2:  # Start event + at least one component + end event
            # Find the last component ID before the end event
            last_component_id = None
            for component in reversed(process_components[:-1]):  # Skip the end event
                id_match = re.search(r'id="([^"]+)"', component)
                if id_match and id_match.group(1) != "StartEvent_2":
                    last_component_id = id_match.group(1)
                    break
            
            if last_component_id:
                end_flow = templates.sequence_flow_template(
                    id="SequenceFlow_End",
                    source_ref=last_component_id,
                    target_ref="EndEvent_2"
                )
                sequence_flows.append(end_flow)

        # Add sequence flow from start event to first component (if any)
        if len(process_components) > 2:  # Start event + at least one component + end event
            first_component_id = None
            for component in process_components[1:-1]:  # Skip start and end events
                id_match = re.search(r'id="([^"]+)"', component)
                if id_match:
                    first_component_id = id_match.group(1)
                    break
            
            if first_component_id:
                start_flow = templates.sequence_flow_template(
                    id="SequenceFlow_Start",
                    source_ref="StartEvent_2",
                    target_ref=first_component_id
                )
                sequence_flows.append(start_flow)
        else:
            # If there are no intermediate components, connect start directly to end
            direct_flow = templates.sequence_flow_template(
                id="SequenceFlow_Direct",
                source_ref="StartEvent_2",
                target_ref="EndEvent_2"
            )
            sequence_flows.append(direct_flow)

        # If no endpoint components were created, add a simple content modifier
        if len(process_components) <= 2:  # Only start and end events
            dummy_component_id = templates.generate_unique_id("Component")
            dummy_component = templates.content_modifier_template(
                id=dummy_component_id,
                name="Default_Response",
                body_type="constant",
                content="{\"status\": \"success\", \"message\": \"API is working\"}"
            )
            process_components.insert(1, dummy_component)  # Insert before end event
            
            # Connect start event to dummy component
            start_to_dummy = templates.sequence_flow_template(
                id="SequenceFlow_Start",
                source_ref="StartEvent_2",
                target_ref=dummy_component_id
            )
            # Connect dummy component to end event
            dummy_to_end = templates.sequence_flow_template(
                id="SequenceFlow_End", 
                source_ref=dummy_component_id,
                target_ref="EndEvent_2"
            )
            sequence_flows = [start_to_dummy, dummy_to_end]

        # Create the collaboration content
        collaboration_content = iflow_config
        collaboration_content += "\n" + "\n".join(participants)
        collaboration_content += "\n" + "\n".join(message_flows)

        # Create the process content with proper indentation
        process_content_formatted = "\n            " + "\n            ".join(process_components)
        process_content_formatted += "\n            " + "\n            ".join(sequence_flows)
        
        # Generate the complete iFlow XML
        process_template = templates.process_template(
            id="Process_1",
            name="Integration Process"
        )
        
        # Replace the process content placeholder - important to use the same format as in the template
        process_content_with_components = process_template.replace("{{process_content}}", process_content_formatted)
        
        # Generate the full XML by combining collaboration and process content
        template_xml = templates.generate_iflow_xml(collaboration_content, process_content_with_components)
        
        # Add proper BPMN diagram layout
        final_iflow_xml = self._add_bpmn_diagram_layout(template_xml, participants, message_flows, process_components)

        return final_iflow_xml

    def _add_bpmn_diagram_layout(self, iflow_xml, participants, message_flows, process_components):
        """
        Add proper BPMN diagram layout to the iFlow XML

        Args:
            iflow_xml (str): The iFlow XML content
            participants (list): List of participant XML strings
            message_flows (list): List of message flow XML strings
            process_components (list): List of process component XML strings

        Returns:
            str: The iFlow XML with proper BPMN diagram layout
        """
        # Extract component IDs
        component_shapes = []
        component_edges = []
        
        # Add shape for each participant
        x_pos = 100
        for participant in participants:
            id_match = re.search(r'id="([^"]+)"', participant)
            if id_match:
                participant_id = id_match.group(1)
                shape = f'''
                    <bpmndi:BPMNShape bpmnElement="{participant_id}" id="BPMNShape_{participant_id}">
                        <dc:Bounds height="140.0" width="100.0" x="{x_pos}" y="100.0"/>
                    </bpmndi:BPMNShape>'''
                component_shapes.append(shape)
                x_pos += 150
        
        # Extract all component IDs from process_components
        component_ids = []
        for component in process_components:
            id_match = re.search(r'id="([^"]+)"', component)
            if id_match:
                component_ids.append(id_match.group(1))
        
        # Add shapes for ALL process components
        x_pos = 250
        y_pos = 142
        for component_id in component_ids:
            if "StartEvent" in component_id or "EndEvent" in component_id:
                # Events are circles
                shape = f'''
                    <bpmndi:BPMNShape bpmnElement="{component_id}" id="BPMNShape_{component_id}">
                        <dc:Bounds height="32.0" width="32.0" x="{x_pos}" y="{y_pos}"/>
                    </bpmndi:BPMNShape>'''
            else:
                # Activities are rectangles
                shape = f'''
                    <bpmndi:BPMNShape bpmnElement="{component_id}" id="BPMNShape_{component_id}">
                        <dc:Bounds height="60.0" width="100.0" x="{x_pos}" y="{y_pos - 14}"/>
                    </bpmndi:BPMNShape>'''
            component_shapes.append(shape)
            x_pos += 120
        
        # Extract sequence flow IDs and source/target refs using regex
        sequence_flows = []
        pattern = r'<bpmn2:sequenceFlow id="([^"]+)" sourceRef="([^"]+)" targetRef="([^"]+)"'
        for match in re.finditer(pattern, iflow_xml):
            sequence_flows.append({
                'id': match.group(1),
                'sourceRef': match.group(2),
                'targetRef': match.group(3)
            })
        
        # Add edges for sequence flows
        for flow in sequence_flows:
            flow_id = flow['id']
            source_id = flow['sourceRef']
            target_id = flow['targetRef']
            
            # Skip invalid flows that reference non-existent components
            if source_id not in component_ids or target_id not in component_ids:
                continue
                
            # Find positions for source and target
            source_index = component_ids.index(source_id)
            target_index = component_ids.index(target_id)
            source_x = 250 + (source_index * 120) + (32 if "Event" in source_id else 50)
            target_x = 250 + (target_index * 120)
            
            edge = f'''
                    <bpmndi:BPMNEdge bpmnElement="{flow_id}" id="BPMNEdge_{flow_id}">
                        <di:waypoint x="{source_x}" y="{y_pos}"/>
                        <di:waypoint x="{target_x}" y="{y_pos}"/>
                    </bpmndi:BPMNEdge>'''
            component_edges.append(edge)
        
        # Add edges for message flows
        for message_flow in message_flows:
            id_match = re.search(r'id="([^"]+)"', message_flow)
            source_match = re.search(r'sourceRef="([^"]+)"', message_flow)
            target_match = re.search(r'targetRef="([^"]+)"', message_flow)
            
            if id_match and source_match and target_match:
                flow_id = id_match.group(1)
                source_id = source_match.group(1)
                target_id = target_match.group(1)
                
                edge = f'''
                    <bpmndi:BPMNEdge bpmnElement="{flow_id}" id="BPMNEdge_{flow_id}">
                        <di:waypoint x="140.0" y="170.0"/>
                        <di:waypoint x="250.0" y="170.0"/>
                    </bpmndi:BPMNEdge>'''
                component_edges.append(edge)
        
        # Build the final diagram layout
        diagram_layout = f'''
                <bpmndi:BPMNPlane bpmnElement="Collaboration_1" id="BPMNPlane_1">{"".join(component_shapes)}{"".join(component_edges)}
                </bpmndi:BPMNPlane>
            '''
        
        # Replace the placeholder diagram layout
        return re.sub(
            r'<bpmndi:BPMNPlane bpmnElement="Collaboration_1" id="BPMNPlane_1">.*?</bpmndi:BPMNPlane>',
            diagram_layout,
            iflow_xml,
            flags=re.DOTALL
        )

    def _create_zip_file(self, source_dir, zip_path):
        """
        Create a ZIP file from a directory

        Args:
            source_dir (str): The source directory
            zip_path (str): The path to save the ZIP file

        Returns:
            None
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

    def _create_fallback_iflow(self, output_path, iflow_name):
        """
        Create a fallback iFlow when the AI analysis fails

        Args:
            output_path (str): The output path
            iflow_name (str): The name of the iFlow

        Returns:
            str: The path to the generated iFlow ZIP file
        """
        # Create a simple API structure
        api_data = {
            "api_name": "Product API",
            "base_url": "/api/products",
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/products",
                    "purpose": "Get all products"
                }
            ]
        }

        # Generate the iFlow
        return self.generate_iflow(api_data, output_path, iflow_name)

    def _create_endpoint_components(self, endpoint, templates):
        """
        Create components for an endpoint with enhanced support for various component types

        Args:
            endpoint (dict): Endpoint information
            templates (EnhancedIFlowTemplates): Templates library

        Returns:
            dict: Components for the endpoint
        """
        endpoint_components = {
            "participants": [],
            "message_flows": [],
            "process_components": [],
            "sequence_flows": [],
            "edmx_files": {}
        }

        # Create components based on the endpoint configuration
        components = endpoint.get("components", [])

        # Add default components if none are specified
        if not components:
            # ALWAYS use a comprehensive request-reply pattern for all endpoints
            components = [
                {
                    "type": "request_reply_pattern",
                    "name": f"{endpoint.get('method', 'GET')}_{endpoint.get('path', '/').replace('/', '_')}_Flow",
                    "config": {
                        "endpoint_path": endpoint.get("path", "/"),
                        "log_level": "Information"
                    }
                }
            ]

            # Add OData components if OData is mentioned in the endpoint
            if "odata" in endpoint.get("purpose", "").lower() or any("odata" in str(t).lower() for t in endpoint.get("transformations", [])):
                components.extend([
                    {
                        "type": "odata_receiver",
                        "name": "OData_Service_Call",
                        "config": {
                            "service_url": "https://example.com/odata/service",
                            "entity_set": "Products"
                        }
                    },
                    {
                        "type": "content_modifier",
                        "name": "Transform_OData_Response",
                        "config": {
                            "target": "body",
                            "content": "${body}"
                        }
                    }
                ])

                # Add EDMX file for OData
                entity_properties = [
                    {"name": "ID", "type": "Edm.String", "nullable": "false"},
                    {"name": "Name", "type": "Edm.String", "nullable": "false"},
                    {"name": "Description", "type": "Edm.String", "nullable": "true"},
                    {"name": "Price", "type": "Edm.Decimal", "nullable": "false", "precision": "10", "scale": "2"}
                ]

                edmx_content = templates.edmx_template(
                    namespace="com.example.odata",
                    entity_type_name="Product",
                    properties=entity_properties
                )

                endpoint_components["edmx_files"]["Products"] = edmx_content

        # Track used IDs to prevent duplicates
        used_ids = set()

        # Process each component
        prev_component_id = None
        for i, component in enumerate(components):
            component_type = component.get("type")
            component_name = component.get("name", f"Component_{i}")
            component_config = component.get("config", {})

            # Generate a unique ID for the component if not already present or duplicate
            if "id" not in component:
                component["id"] = templates.generate_unique_id(component_type)
            elif component["id"] in used_ids:
                # Generate a new ID if this one is already used
                old_id = component["id"]
                component["id"] = templates.generate_unique_id(component_type)
                print(f"Replaced duplicate ID {old_id} with {component['id']}")
            
            used_ids.add(component["id"])
            current_component_id = component["id"]

            # Create the component based on its type
            if component_type == "https_sender":
                # Add a participant for the sender
                sender_participant_id = templates.generate_unique_id("Participant")
                endpoint_components["participants"].append(templates.participant_template(
                    id=sender_participant_id,
                    name=f"Sender_{component_name}",
                    type="EndpointSender"
                ))

                # Add the HTTPS sender
                endpoint_components["message_flows"].append(templates.https_sender_template(
                    id=component["id"],
                    name=component_name,
                    url_path=component_config.get("url_path", "/"),  # Default path to "/"
                    sender_auth=component_config.get("sender_auth", "None"),
                    user_role=component_config.get("user_role", "ESBMessaging.send")
                ).replace("{{source_ref}}", sender_participant_id).replace("{{target_ref}}", "Participant_Process_1"))

            elif component_type == "http_receiver" or component_type == "https_receiver":
                # Add a participant for the receiver
                receiver_participant_id = templates.generate_unique_id("Participant")
                endpoint_components["participants"].append(templates.participant_template(
                    id=receiver_participant_id,
                    name=f"Receiver_{component_name}",
                    type="EndpointReceiver"
                ))

                # Add the HTTP receiver
                endpoint_components["message_flows"].append(templates.http_receiver_template(
                    id=component["id"],
                    name=component_name,
                    address=component_config.get("address", "https://example.com"),  # Default address
                    auth_method=component_config.get("auth_method", "None"),
                    credential_name=component_config.get("credential_name", "")
                ).replace("{{source_ref}}", "Participant_Process_1").replace("{{target_ref}}", receiver_participant_id))

            elif component_type == "content_modifier":
                # Add a content modifier to the process
                endpoint_components["process_components"].append(templates.content_modifier_template(
                    id=component["id"],
                    name=component_name,
                    property_table=component_config.get("property_table", ""),
                    header_table=component_config.get("header_table", ""),
                    body_type=component_config.get("body_type", "expression"),
                    wrap_content=component_config.get("wrap_content", ""),
                    content=component_config.get("content", "")
                ))

            elif component_type == "enricher":
                # Add an enricher to the process
                endpoint_components["process_components"].append(templates.enricher_template(
                    id=component["id"],
                    name=component_name,
                    body_type=component_config.get("body_type", "constant"),
                    wrap_content=component_config.get("wrap_content", "")
                ))

            elif component_type == "odata_adapter" or component_type == "odata_receiver":
                # Add a participant for the OData receiver
                odata_participant_id = templates.generate_unique_id("Participant")
                endpoint_components["participants"].append(templates.participant_template(
                    id=odata_participant_id,
                    name=f"OData_{component_name}",
                    type="EndpointReceiver"
                ))

                # Add the OData receiver
                endpoint_components["message_flows"].append(templates.odata_receiver_template(
                    id=component["id"],
                    name=component_name,
                    service_url=component_config.get("service_url", "https://example.com/odata/service"),
                    entity_set=component_config.get("entity_set", ""),
                    auth_method=component_config.get("auth_method", "None"),
                    credential_name=component_config.get("credential_name", "")
                ).replace("{{source_ref}}", "Participant_Process_1").replace("{{target_ref}}", odata_participant_id))

                # Add EDMX file for OData if not already added
                if not endpoint_components["edmx_files"] and component_config.get("entity_set"):
                    entity_set = component_config.get("entity_set")
                    entity_properties = [
                        {"name": "ID", "type": "Edm.String", "nullable": "false"},
                        {"name": "Name", "type": "Edm.String", "nullable": "false"},
                        {"name": "Description", "type": "Edm.String", "nullable": "true"},
                        {"name": "Price", "type": "Edm.Decimal", "nullable": "false", "precision": "10", "scale": "2"}
                    ]

                    edmx_content = templates.edmx_template(
                        namespace="com.example.odata",
                        entity_type_name=entity_set.rstrip("s"),  # Remove trailing 's' for singular entity type name
                        properties=entity_properties
                    )

                    endpoint_components["edmx_files"][entity_set] = edmx_content

            elif component_type == "router" or component_type == "exclusive_gateway":
                # Add a router to the process - make sure it's an exclusiveGateway, not a callActivity
                endpoint_components["process_components"].append(templates.router_template(
                    id=component["id"],
                    name=component_name,
                    # Make sure there are no default routes with broken IDs
                    conditions=component_config.get("conditions", [])
                ))

            elif component_type == "exception_subprocess":
                # Add an exception subprocess to the process
                endpoint_components["process_components"].append(templates.exception_subprocess_template(
                    id=component["id"],
                    name=component_name,
                    error_type=component_config.get("error_type", "All")
                ))

            elif component_type == "write_to_log":
                # Add a write to log component to the process
                endpoint_components["process_components"].append(templates.write_to_log_template(
                    id=component["id"],
                    name=component_name,
                    log_level=component_config.get("log_level", "Info"),
                    message=component_config.get("message", "Log message")
                ))

            elif component_type == "message_mapping":
                # Add a message mapping component to the process
                endpoint_components["process_components"].append(templates.message_mapping_template(
                    id=component["id"],
                    name=component_name,
                    source_type=component_config.get("source_type", "XML"),
                    target_type=component_config.get("target_type", "XML")
                ))

            elif component_type == "call_activity":
                # Add a call activity to the process
                endpoint_components["process_components"].append(templates.call_activity_template(
                    id=component["id"],
                    name=component_name,
                    activity_type=component_config.get("activity_type", "Process")
                ))

            elif component_type == "request_reply_pattern":
                # Add a comprehensive request-reply pattern
                request_reply_components = templates.comprehensive_request_reply_template(
                    id=component["id"],
                    name=component_name,
                    endpoint_path=component_config.get("endpoint_path", "/"),
                    log_level=component_config.get("log_level", "Information")
                )

                # Add all components from the request-reply pattern
                endpoint_components["process_components"].extend(request_reply_components["components"])
                endpoint_components["sequence_flows"].extend(request_reply_components["sequence_flows"])

                # Set the current component ID to the end component of the request-reply pattern
                current_component_id = request_reply_components["end_component_id"]

                # If this is the first component, set the previous component ID to the start component
                if prev_component_id is None:
                    prev_component_id = request_reply_components["start_component_id"]

            # Add sequence flow if this is not the first component and we're not using a request_reply_pattern
            # (request_reply_pattern adds its own sequence flows)
            if prev_component_id and component_type != "request_reply_pattern":
                sequence_flow_id = templates.generate_unique_id("SequenceFlow")
                endpoint_components["sequence_flows"].append(
                    templates.sequence_flow_template(
                        id=sequence_flow_id,
                        source_ref=prev_component_id,
                        target_ref=current_component_id,
                        is_immediate="true"
                    )
                )

            prev_component_id = current_component_id

        # Make sure all process components have unique IDs
        unique_process_components = []
        used_process_ids = set()
        
        for component in endpoint_components["process_components"]:
            id_match = re.search(r'id="([^"]+)"', component)
            if id_match:
                component_id = id_match.group(1)
                if component_id in used_process_ids:
                    # Generate a new ID and replace in the component XML
                    new_id = templates.generate_unique_id(component_id.split('_')[0] if '_' in component_id else "Component")
                    component = component.replace(f'id="{component_id}"', f'id="{new_id}"')
                    
                    # Also update any sequence flows that reference this component
                    for i, flow in enumerate(endpoint_components["sequence_flows"]):
                        flow = flow.replace(f'sourceRef="{component_id}"', f'sourceRef="{new_id}"')
                        flow = flow.replace(f'targetRef="{component_id}"', f'targetRef="{new_id}"')
                        endpoint_components["sequence_flows"][i] = flow
                    
                    component_id = new_id
                    print(f"Fixed duplicate process component ID by creating new ID: {new_id}")
                
                used_process_ids.add(component_id)
                unique_process_components.append(component)
        
        # Replace the process components with the de-duplicated list
        endpoint_components["process_components"] = unique_process_components

        return endpoint_components

    def _generate_simplified_project_content(self, iflow_name):
        """
        Generate simplified content for the .project file with the correct <name> tag

        Args:
            iflow_name (str): Name of the iFlow

        Returns:
            str: Simplified content for the .project file
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
\t<name>{iflow_name}</name>
\t<comment></comment>
\t<projects>
\t</projects>
\t<buildSpec>
\t</buildSpec>
\t<natures>
\t</natures>
</projectDescription>
"""


    def generate_iflow(self, markdown_content, output_path, iflow_name):
        """
        Generate an iFlow from markdown content with enhanced components

        Args:
            markdown_content (str): Markdown content describing the API
            output_path (str): Path to save the generated iFlow
            iflow_name (str): Name of the iFlow

        Returns:
            str: Path to the generated iFlow ZIP file
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Create the iFlow directory structure
        iflow_dir = os.path.join(output_path, iflow_name)
        os.makedirs(iflow_dir, exist_ok=True)

        # Create the META-INF directory
        meta_inf_dir = os.path.join(iflow_dir, "META-INF")
        os.makedirs(meta_inf_dir, exist_ok=True)

        # Create the src/main/resources directory
        resources_dir = os.path.join(iflow_dir, "src", "main", "resources")
        os.makedirs(resources_dir, exist_ok=True)

        # Create the scenarioflows/integrationflow directory
        iflow_dir_path = os.path.join(resources_dir, "scenarioflows", "integrationflow")
        os.makedirs(iflow_dir_path, exist_ok=True)

        # Create the edmx directory for OData metadata
        edmx_dir = os.path.join(resources_dir, "edmx")
        os.makedirs(edmx_dir, exist_ok=True)

        # Generate the .project file with the correct <name> tag
        project_content = generate_project_file(iflow_name)
        with open(os.path.join(iflow_dir, ".project"), "w") as f:
            f.write(project_content)

        # Generate the metainfo.prop file
        metainfo_content = f"#Store metainfo properties\n#Tue May 06 17:43:30  2025\ndescription={iflow_name}\n"
        with open(os.path.join(iflow_dir, "metainfo.prop"), "w") as f:
            f.write(metainfo_content)

        # Generate the MANIFEST.MF file
        manifest_content = f"""Manifest-Version: 1.0
Bundle-ManifestVersion: 2
Bundle-Name: {iflow_name}
Bundle-SymbolicName: {iflow_name}; singleton:=true
Bundle-Version: 1.0.0
SAP-BundleType: IntegrationFlow
SAP-NodeType: IFLMAP
SAP-RuntimeProfile: iflmap
Import-Package: com.sap.esb.application.services.cxf.interceptor,com.sap
 .esb.security,com.sap.it.op.agent.api,com.sap.it.op.agent.collector.cam
 el,com.sap.it.op.agent.collector.cxf,com.sap.it.op.agent.mpl,javax.jms,
 javax.jws,javax.wsdl,javax.xml.bind.annotation,javax.xml.namespace,java
 x.xml.ws,org.apache.camel;version="2.8",org.apache.camel.builder;versio
 n="2.8",org.apache.camel.builder.xml;version="2.8",org.apache.camel.com
 ponent.cxf,org.apache.camel.model;version="2.8",org.apache.camel.proces
 sor;version="2.8",org.apache.camel.processor.aggregate;version="2.8",or
 g.apache.camel.spring.spi;version="2.8",org.apache.commons.logging,org.
 apache.cxf.binding,org.apache.cxf.binding.soap,org.apache.cxf.binding.s
 oap.spring,org.apache.cxf.bus,org.apache.cxf.bus.resource,org.apache.cx
 f.bus,org.apache.cxf.bus.spring,org.apache.cxf.buslifecycle,org.apache.cxf.catalog,org.apa
 che.cxf.configuration.jsse;version="2.5",org.apache.cxf.configuration.s
 pring,org.apache.cxf.endpoint,org.apache.cxf.headers,org.apache.cxf.int
 erceptor,org.apache.cxf.management.counters;version="2.5",org.apache.cx
 f.message,org.apache.cxf.phase,org.apache.cxf.resource,org.apache.cxf.s
 ervice.factory,org.apache.cxf.service.model,org.apache.cxf.transport,or
 g.apache.cxf.transport.common.gzip,org.apache.cxf.transport.http,org.ap
 ache.cxf.transport.http.policy,org.apache.cxf.workqueue,org.apache.cxf.
 ws.rm.persistence,org.apache.cxf.wsdl11,org.osgi.framework;version="1.6
 .0",org.slf4j;version="1.6",org.springframework.beans.factory.config;ve
 rsion="3.0",com.sap.esb.camel.security.cms,org.apache.camel.spi,com.sap
 .esb.webservice.audit.log,com.sap.esb.camel.endpoint.configurator.api,c
 om.sap.esb.camel.jdbc.idempotency.reorg,javax.sql,org.apache.camel.proc
 essor.idempotent.jdbc,org.osgi.service.blueprint;version="[1.0.0,2.0.0)
 "
Origin-Bundle-Name: {iflow_name}
Origin-Bundle-SymbolicName: {iflow_name}
"""
        with open(os.path.join(meta_inf_dir, "MANIFEST.MF"), "w") as f:
            f.write(manifest_content)

        # Generate the parameters.prop file
        parameters_prop_content = "#Store parameters\n#Tue May 06 17:43:30  2025\n"
        with open(os.path.join(resources_dir, "parameters.prop"), "w") as f:
            f.write(parameters_prop_content)

        # Generate the parameters.propdef file
        parameters_propdef_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?><parameters><param_references/></parameters>'
        with open(os.path.join(resources_dir, "parameters.propdef"), "w") as f:
            f.write(parameters_propdef_content)

        # Generate the iFlow content using the AI model
        prompt = self._create_detailed_analysis_prompt(markdown_content)
        api_analysis = self._get_ai_response(prompt)

        # Save the API analysis to a file for debugging
        debug_dir = os.path.join(output_path, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        with open(os.path.join(debug_dir, "api_analysis.json"), "w") as f:
            f.write(api_analysis)
        print(f"Saved API analysis to {os.path.join(debug_dir, 'api_analysis.json')}")

        # Parse the API analysis
        try:
            api_data = self._parse_api_analysis(api_analysis)

            # Create the iFlow file
            iflow_content = self._generate_iflw_content(api_data, iflow_name)

            # Write the iFlow file
            iflow_file_path = os.path.join(iflow_dir_path, f"{iflow_name}.iflw")
            with open(iflow_file_path, "w") as f:
                f.write(iflow_content)

            # Generate EDMX files for OData services
            for endpoint in api_data.get("endpoints", []):
                components = self._create_endpoint_components(endpoint, self.templates)

                # Write EDMX files
                for entity_set, edmx_content in components.get("edmx_files", {}).items():
                    edmx_file_path = os.path.join(edmx_dir, f"{entity_set.lower()}.edmx")
                    with open(edmx_file_path, "w") as f:
                        f.write(edmx_content)

            # Create a ZIP file of the iFlow
            zip_path = os.path.join(output_path, f"{iflow_name}.zip")
            self._create_zip_file(iflow_dir, zip_path)

            return zip_path

        except Exception as e:
            print(f"Error generating iFlow: {str(e)}")
            # Create a simple iFlow as fallback
            return self._create_fallback_iflow(output_path, iflow_name)

    def _create_detailed_analysis_prompt(self, markdown_content):
        """
        Create an enhanced prompt for the LLM to analyze the markdown content

        Args:
            markdown_content (str): The markdown content to analyze

        Returns:
            str: The enhanced prompt for the LLM
        """
        return f"""
        You are an expert in SAP Integration Suite and API design. Your task is to analyze the following markdown content
        that describes an API and determine the appropriate SAP Integration Suite components needed to implement
        an equivalent iFlow.

        # CONTEXT
        The markdown describes an API with various endpoints, request/response structures, and data transformations.
        Your job is to convert this into an SAP Integration Suite iFlow design with specific components.

        # TASK
        For each endpoint in the API, identify:
        1. The HTTP method and path
        2. Required components (HTTP adapters, content modifiers, OData adapters, mappings, etc.)
        3. Configuration details for each component
        4. Flow connections between components
        5. Data transformations needed

        # REQUIRED COMPONENTS
        You MUST include the following SAP Integration Suite components in your design:
        - HTTP/HTTPS Sender Adapter: For receiving API requests
        - HTTP/HTTPS Receiver Adapter: For sending responses or making external calls
        - Content Modifier: For modifying message body, headers, or properties
        - OData Adapter: For OData service calls mentioned in the API
        - Message Mapping: For complex data transformations
        - Router: For conditional processing
        - Exception Subprocess: For error handling
        - Write to Log: For logging operations
        - Request-Reply Pattern: For endpoints that receive a request and send back a response

        # SPECIFIC MAPPING INSTRUCTIONS
        - For each API endpoint, create an HTTP Sender Adapter
        - For each backend call, create an appropriate Receiver Adapter (HTTP, OData, etc.)
        - For each data transformation, create a Content Modifier or Message Mapping
        - For each validation step, create a Router with appropriate conditions
        - For each error handling scenario, create an Exception Subprocess
        - For each logging requirement, create a Write to Log component
        - For endpoints that follow a request-reply pattern (receive request, process, return response), use a "request_reply_pattern" component type

        # RESPONSE FORMAT
        Return your analysis as a JSON object with the following structure:
        {{
            "api_name": "Name of the API",
            "base_url": "Base URL of the API",
            "endpoints": [
                {{
                    "method": "HTTP method",
                    "path": "Endpoint path",
                    "purpose": "Purpose of the endpoint",
                    "components": [
                        {{
                            "type": "Component type (https_sender, content_modifier, odata_adapter, message_mapping, router, exception_subprocess, write_to_log, request_reply_pattern, etc.)",
                            "name": "Component name",
                            "id": "Unique ID for the component",
                            "config": {{}}
                        }}
                    ],
                    "connections": [
                        {{
                            "source": "Source component name",
                            "target": "Target component name"
                        }}
                    ],
                    "transformations": [
                        {{
                            "name": "Transformation name",
                            "input_structure": "Description of input structure",
                            "output_structure": "Description of output structure",
                            "logic": "Description of transformation logic"
                        }}
                    ]
                }}
            ],
            "parameters": [
                {{
                    "name": "Parameter name",
                    "type": "Parameter type (string, boolean, etc.)",
                    "default_value": "Default value",
                    "description": "Parameter description"
                }}
            ]
        }}

        # IMPORTANT NOTES
        - You MUST include at least one Content Modifier in each endpoint flow
        - If OData services are mentioned, you MUST include OData adapters
        - You MUST create proper connections between all components
        - You MUST include error handling for each endpoint
        - You MUST include logging for each endpoint
        - For any endpoint that receives a request and sends a response, use the "request_reply_pattern" component type
        - IMPORTANT: For GET /products and GET /products/{id} endpoints, use the "request_reply_pattern" component type
        - Your response MUST be valid JSON. Do not include any comments in the JSON.
        - Make sure all JSON objects have proper closing braces and commas.
        - Double-check your JSON syntax before submitting.

        # MARKDOWN CONTENT
        {markdown_content}
        """

def main():
    """
    Main function to run the enhanced prompt generator
    """
    # Load environment variables from .env file
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description='Generate an iFlow from markdown content using Enhanced Prompt Generator')
    parser.add_argument('--markdown', required=True, help='Path to the markdown file')
    parser.add_argument('--output', required=True, help='Path to save the generated iFlow')
    parser.add_argument('--name', required=True, help='Name of the iFlow')
    parser.add_argument('--api-key', help='API key for the LLM service (overrides .env file)')
    parser.add_argument('--model', default='claude-sonnet-4-20250514', help='Model to use for the LLM service')
    parser.add_argument('--provider', default='claude', choices=['openai', 'claude', 'local'],
                        help='AI provider to use (openai, claude, or local)')

    args = parser.parse_args()

    # Set default models based on provider
    if args.provider == 'claude' and args.model == 'claude-sonnet-4-20250514':
        # Use the correct Claude model name
        args.model = 'claude-sonnet-4-20250514'

    # Get API key from .env file if not provided in command line
    api_key = args.api_key
    if not api_key:
        if args.provider == 'claude':
            api_key = os.getenv('CLAUDE_API_KEY')
            if not api_key:
                print("Warning: No Claude API key found in .env file. Using local mode.")
                args.provider = 'local'
        elif args.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: No OpenAI API key found in .env file. Using local mode.")
                args.provider = 'local'

    # Read the markdown content
    with open(args.markdown, 'r') as f:
        markdown_content = f.read()

    # Create the enhanced prompt generator
    generator = EnhancedPromptGenerator(api_key=api_key, model=args.model, provider=args.provider)

    # Generate the iFlow
    zip_path = generator.generate_iflow(markdown_content, args.output, args.name)

    print(f"Generated iFlow: {zip_path}")
    print("This enhanced version includes specific components like Content Modifiers and OData adapters.")
    print("The generated iFlow should better reflect the API requirements in the markdown file.")

if __name__ == "__main__":
    main()
