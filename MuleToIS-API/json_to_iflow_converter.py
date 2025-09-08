"""
JSON to iFlow XML Converter

This module converts a JSON intermediate representation into a complete and valid
SAP Integration Suite iFlow XML file following best practices.
"""

import json
import re
import uuid
import os
from typing import Dict, List, Any, Tuple, Optional

class JsonToIflowConverter:
    """
    Converts JSON intermediate representation to SAP Integration Suite iFlow XML.
    """

    def __init__(self):
        """Initialize the converter."""
        self.component_positions = {}
        self.next_x = 300
        self.next_y = 150
        self.x_spacing = 150
        self.y_spacing = 100

    def convert(self, json_data: Dict[str, Any], iflow_name: str) -> str:
        """
        Convert JSON data to iFlow XML.

        Args:
            json_data: The JSON data representing the iFlow
            iflow_name: The name of the iFlow

        Returns:
            str: The generated iFlow XML
        """
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string provided")

        # Extract basic metadata
        api_name = json_data.get("api_name", iflow_name)
        base_url = json_data.get("base_url", "/api/v1")
        description = json_data.get("description", f"Generated iFlow: {api_name}")

        # Initialize collections for different component types
        participants = []
        message_flows = []
        process_components = []
        sequence_flows = []
        shapes = []
        edges = []

        # Generate the core structure
        xml = self._generate_core_structure(api_name, description)

        # Process endpoints and components
        self._process_endpoints(
            json_data.get("endpoints", []),
            participants,
            message_flows,
            process_components,
            sequence_flows,
            shapes,
            edges
        )

        # Replace placeholders in the XML
        xml = self._replace_placeholders(
            xml,
            participants,
            message_flows,
            process_components,
            sequence_flows,
            shapes,
            edges
        )

        return xml

    def _generate_core_structure(self, api_name: str, description: str) -> str:
        """
        Generate the core XML structure.

        Args:
            api_name: The name of the API/iFlow
            description: The description of the iFlow

        Returns:
            str: The core XML structure with placeholders
        """
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:ifl="http:///com.sap.ifl.model/Ifl.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="Definitions_1">
  <bpmn2:collaboration id="Collaboration_1" name="Collaboration">
    <bpmn2:documentation id="Documentation_{self._generate_id()}" textFormat="text/plain">{description}</bpmn2:documentation>
    <bpmn2:extensionElements>
      <ifl:property>
        <key>namespaceMapping</key>
        <value></value>
      </ifl:property>
      <ifl:property>
        <key>allowedHeaderList</key>
        <value>*</value>
      </ifl:property>
      <ifl:property>
        <key>httpSessionHandling</key>
        <value>None</value>
      </ifl:property>
      <ifl:property>
        <key>ServerTrace</key>
        <value>false</value>
      </ifl:property>
      <ifl:property>
        <key>returnExceptionToSender</key>
        <value>false</value>
      </ifl:property>
      <ifl:property>
        <key>log</key>
        <value>All events</value>
      </ifl:property>
      <ifl:property>
        <key>componentVersion</key>
        <value>1.1</value>
      </ifl:property>
      <ifl:property>
        <key>cmdVariantUri</key>
        <value>ctype::IFlowVariant/cname::IFlowConfiguration/version::1.1.16</value>
      </ifl:property>
    </bpmn2:extensionElements>
    {{participants}}
    {{message_flows}}
  </bpmn2:collaboration>
  <bpmn2:process id="Process_1" name="Integration Process" isExecutable="true">
    {{process_components}}
    {{sequence_flows}}
  </bpmn2:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane bpmnElement="Collaboration_1" id="BPMNPlane_1">
      {{shapes}}
      {{edges}}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn2:definitions>'''

    def _process_endpoints(
        self,
        endpoints: List[Dict[str, Any]],
        participants: List[str],
        message_flows: List[str],
        process_components: List[str],
        sequence_flows: List[str],
        shapes: List[str],
        edges: List[str]
    ) -> None:
        """
        Process endpoints from the JSON data.

        Args:
            endpoints: List of endpoint definitions
            participants: List to append participant XML
            message_flows: List to append message flow XML
            process_components: List to append process component XML
            sequence_flows: List to append sequence flow XML
            shapes: List to append shape XML
            edges: List to append edge XML
        """
        # Add default HTTP sender participant
        sender_id = "Participant_1"
        sender = self._create_http_sender_participant(sender_id, "Sender")
        participants.append(sender["definition"])
        shapes.append(sender["shape"])

        # Add integration process participant
        process_id = "Participant_Process_1"
        process = self._create_integration_process_participant(process_id, "Integration Process", "Process_1")
        participants.append(process["definition"])
        shapes.append(process["shape"])

        # Add start event
        start_event_id = "StartEvent_2"
        start_event = self._create_start_event(start_event_id, "Start")
        process_components.append(start_event["definition"])
        shapes.append(start_event["shape"])

        # Add end event
        end_event_id = "EndEvent_2"
        end_event = self._create_end_event(end_event_id, "End")
        process_components.append(end_event["definition"])
        shapes.append(end_event["shape"])

        # Determine inbound path from first endpoint (default to /api)
        inbound_path = "/api"
        if endpoints and isinstance(endpoints, list):
            try:
                inbound_path = endpoints[0].get("path", "/api") or "/api"
            except Exception:
                inbound_path = "/api"

        # Add HTTP sender message flow using endpoint path
        http_flow_id = "MessageFlow_10"
        http_flow = self._create_http_sender_message_flow(http_flow_id, sender_id, start_event_id, inbound_path)
        message_flows.append(http_flow["definition"])
        edges.append(http_flow["edge"])

        # Process each endpoint
        component_ids = []
        for i, endpoint in enumerate(endpoints):
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")

            # Process components for this endpoint
            endpoint_components = self._process_endpoint_components(
                endpoint,
                i,
                process_components,
                sequence_flows,
                shapes,
                edges,
                participants,
                message_flows
            )

            component_ids.extend(endpoint_components)

        # If no components were added, create a direct flow from start to end
        if not component_ids:
            direct_flow_id = "SequenceFlow_Direct"
            direct_flow = self._create_sequence_flow(direct_flow_id, start_event_id, end_event_id)
            sequence_flows.append(direct_flow["definition"])
            edges.append(direct_flow["edge"])

    def _process_endpoint_components(
        self,
        endpoint: Dict[str, Any],
        endpoint_index: int,
        process_components: List[str],
        sequence_flows: List[str],
        shapes: List[str],
        edges: List[str],
        participants: List[str],
        message_flows: List[str]
    ) -> List[str]:
        """
        Process components for an endpoint.

        Args:
            endpoint: The endpoint definition
            endpoint_index: Index of the endpoint
            process_components: List to append process component XML
            sequence_flows: List to append sequence flow XML
            shapes: List to append shape XML
            edges: List to append edge XML
            participants: List to append participant XML
            message_flows: List to append message flow XML

        Returns:
            List[str]: List of component IDs created
        """
        component_ids = []

        # Get components for this endpoint
        components = endpoint.get("components", [])

        # Calculate positions
        x_pos = self.next_x
        y_pos = self.next_y + (endpoint_index * self.y_spacing)

        # Process each component
        for i, component in enumerate(components):
            component_type = component.get("type", "").lower()
            component_id = component.get("id", f"{component_type}_{len(component_ids)}")
            component_name = component.get("name", f"{component_type}_{i}")

            # Calculate position
            self.component_positions[component_id] = {"x": x_pos, "y": y_pos}
            x_pos += self.x_spacing

            # Create the component based on its type
            component_result = self._create_component(
                component_type,
                component_id,
                component_name,
                component.get("config", {}),
                process_components,
                shapes,
                participants,
                message_flows,
                edges
            )

            if component_result:
                component_ids.append(component_id)

            # Handle gateway branches with conditions
            if component_type in ["gateway", "router"]:
                config = component.get("config", {})
                branches = config.get("branches", []) if isinstance(config, dict) else []
                for bi, branch in enumerate(branches):
                    target_id = branch.get("to")
                    condition = branch.get("condition")
                    if target_id:
                        flow_id = f"SequenceFlow_Branch_{component_id}_{bi}_{endpoint_index}"
                        flow = self._create_sequence_flow(flow_id, component_id, target_id, condition)
                        sequence_flows.append(flow["definition"])
                        edges.append(flow["edge"])

        # Identify gateways that have explicit branches to skip linear flow after them
        skip_linear_after = set()
        for component in components:
            ctype = component.get("type", "").lower()
            if ctype in ["gateway", "router"]:
                cfg = component.get("config", {})
                branches = cfg.get("branches", []) if isinstance(cfg, dict) else []
                if branches:
                    cid = component.get("id")
                    if cid:
                        skip_linear_after.add(cid)

        # Create sequence flows to connect components
        if component_ids:
            # Connect start event to first component
            start_flow_id = f"SequenceFlow_Start_{endpoint_index}"
            start_flow = self._create_sequence_flow(start_flow_id, "StartEvent_2", component_ids[0])
            sequence_flows.append(start_flow["definition"])
            edges.append(start_flow["edge"])

            # Connect components in sequence (skip linear after gateways with branches)
            for i in range(len(component_ids) - 1):
                if component_ids[i] in skip_linear_after:
                    continue
                flow_id = f"SequenceFlow_{i}_{endpoint_index}"
                flow = self._create_sequence_flow(flow_id, component_ids[i], component_ids[i+1])
                sequence_flows.append(flow["definition"])
                edges.append(flow["edge"])

            # Connect last component to end event
            end_flow_id = f"SequenceFlow_End_{endpoint_index}"
            end_flow = self._create_sequence_flow(end_flow_id, component_ids[-1], "EndEvent_2")
            sequence_flows.append(end_flow["definition"])
            edges.append(end_flow["edge"])

        return component_ids

    def _create_component(
        self,
        component_type: str,
        component_id: str,
        component_name: str,
        config: Dict[str, Any],
        process_components: List[str],
        shapes: List[str],
        participants: List[str],
        message_flows: List[str],
        edges: List[str]
    ) -> bool:
        """
        Create a component based on its type.

        Args:
            component_type: The type of component
            component_id: The ID of the component
            component_name: The name of the component
            config: The component configuration
            process_components: List to append process component XML
            shapes: List to append shape XML
            participants: List to append participant XML
            message_flows: List to append message flow XML
            edges: List to append edge XML

        Returns:
            bool: True if component was created, False otherwise
        """
        position = self.component_positions.get(component_id, {"x": self.next_x, "y": self.next_y})

        if component_type in ["json_to_xml", "jsontoxml"]:
            # JSON to XML Converter
            component = self._create_json_to_xml_converter(component_id, component_name, position)
            process_components.append(component["definition"])
            shapes.append(component["shape"])
            return True

        elif component_type in ["content_enricher", "enricher"]:
            # Content Enricher
            component = self._create_content_enricher(component_id, component_name, config, position)
            process_components.append(component["definition"])
            shapes.append(component["shape"])
            return True

        elif component_type in ["content_modifier", "modifier"]:
            # Content Modifier
            component = self._create_content_modifier(component_id, component_name, config, position)
            process_components.append(component["definition"])
            shapes.append(component["shape"])
            return True

        elif component_type in ["odata_adapter", "odata_receiver", "odata"]:
            # OData Service Task
            service_task_id = f"ServiceTask_{component_id}"
            service_task = self._create_service_task(service_task_id, f"Call_{component_name}", position)
            process_components.append(service_task["definition"])
            shapes.append(service_task["shape"])

            # OData Receiver Participant
            participant_id = f"Participant_OData_{component_id}"
            participant_position = {"x": position["x"], "y": position["y"] + 200}
            odata_participant = self._create_odata_receiver_participant(participant_id, f"OData_{component_name}", participant_position)
            participants.append(odata_participant["definition"])
            shapes.append(odata_participant["shape"])

            # OData Message Flow
            message_flow_id = f"MessageFlow_OData_{component_id}"
            odata_message_flow = self._create_odata_message_flow(
                message_flow_id,
                service_task_id,
                participant_id,
                config.get("operation", "Query(GET)"),
                config.get("service_url", "https://example.com/odata/service"),
                config.get("entity_set", "Products")
            )
            message_flows.append(odata_message_flow["definition"])
            edges.append(odata_message_flow["edge"])

            return True

        elif component_type in ["request_reply", "http_adapter", "rest"]:
            # Request-Reply Service Task
            service_task = self._create_service_task(component_id, component_name, position)
            process_components.append(service_task["definition"])
            shapes.append(service_task["shape"])

            # HTTP Receiver Participant
            participant_id = f"Participant_HTTP_{component_id}"
            participant_position = {"x": position["x"], "y": position["y"] + 200}
            http_participant = self._create_http_receiver_participant(participant_id, f"HTTP_{component_name}", participant_position)
            participants.append(http_participant["definition"])
            shapes.append(http_participant["shape"])

            # HTTP Message Flow
            message_flow_id = f"MessageFlow_HTTP_{component_id}"
            http_message_flow = self._create_http_message_flow(
                message_flow_id,
                component_id,
                participant_id,
                config.get("method", "GET"),
                config.get("url", "https://example.com/api")
            )
            message_flows.append(http_message_flow["definition"])
            edges.append(http_message_flow["edge"])

            return True

        elif component_type in ["sftp", "sftp_receiver", "file_sftp"]:
            # SFTP Service Task + Participant + Message Flow
            service_task_id = f"ServiceTask_{component_id}"
            service_task = self._create_service_task(service_task_id, f"Call_{component_name}", position)
            process_components.append(service_task["definition"])
            shapes.append(service_task["shape"])

            participant_id = f"Participant_SFTP_{component_id}"
            participant_position = {"x": position["x"], "y": position["y"] + 200}
            sftp_participant = self._create_sftp_receiver_participant(participant_id, f"SFTP_{component_name}", participant_position)
            participants.append(sftp_participant["definition"])
            shapes.append(sftp_participant["shape"])

            message_flow_id = f"MessageFlow_SFTP_{component_id}"
            sftp_message_flow = self._create_sftp_message_flow(
                message_flow_id,
                service_task_id,
                participant_id,
                config.get("host", "sftp.example.com"),
                config.get("port", "22"),
                config.get("path", "/uploads"),
                config.get("username", "${sftp_username}"),
                config.get("auth_type", "Password"),
                config.get("operation", "PUT"),
            )
            message_flows.append(sftp_message_flow["definition"])
            edges.append(sftp_message_flow["edge"])

            return True

        elif component_type in ["successfactors", "sf", "success_factors", "sfsf"]:
            # SuccessFactors OData Service Task + Participant + Message Flow
            service_task_id = f"ServiceTask_{component_id}"
            service_task = self._create_service_task(service_task_id, f"Call_{component_name}", position)
            process_components.append(service_task["definition"])
            shapes.append(service_task["shape"])

            participant_id = f"Participant_SuccessFactors_{component_id}"
            participant_position = {"x": position["x"], "y": position["y"] + 200}
            sf_participant = self._create_successfactors_receiver_participant(participant_id, f"SuccessFactors_{component_name}", participant_position)
            participants.append(sf_participant["definition"])
            shapes.append(sf_participant["shape"])

            message_flow_id = f"MessageFlow_SuccessFactors_{component_id}"
            sf_message_flow = self._create_successfactors_message_flow(
                message_flow_id,
                service_task_id,
                participant_id,
                config.get("url", "https://api.successfactors.com/odata/v2/User"),
                config.get("operation", "Query(GET)"),
                config.get("auth_method", "OAuth"),
            )
            message_flows.append(sf_message_flow["definition"])
            edges.append(sf_message_flow["edge"])

            return True

        elif component_type in ["subprocess", "embedded_subprocess"]:
            # Embedded Subprocess container with nested components
            nested_components = component.get("config", {}).get("components", [])
            subprocess_component = self._create_subprocess_with_nested(component_id, component_name, nested_components, position)
            process_components.append(subprocess_component["definition"])
            shapes.append(subprocess_component["shape"])
            return True

        elif component_type in ["gateway", "router"]:
            # Gateway
            gateway = self._create_gateway(component_id, component_name, position)
            process_components.append(gateway["definition"])
            shapes.append(gateway["shape"])
            return True

        elif component_type in ["script", "groovy"]:
            # Script
            script = self._create_script(component_id, component_name, config, position)
            process_components.append(script["definition"])
            shapes.append(script["shape"])
            return True

        elif component_type in ["message_mapping", "mapping"]:
            # Message Mapping
            mapping = self._create_message_mapping(component_id, component_name, config, position)
            process_components.append(mapping["definition"])
            shapes.append(mapping["shape"])
            return True

        elif component_type in ["exception_subprocess"]:
            # Exception Subprocess container (triggeredByEvent) with nested components
            nested_components = component.get("config", {}).get("components", [])
            exception_component = self._create_exception_subprocess_with_nested(component_id, component_name, nested_components, position)
            process_components.append(exception_component["definition"])
            shapes.append(exception_component["shape"])
            return True

        # Default: Content Modifier
        component = self._create_content_modifier(component_id, component_name, config, position)
        process_components.append(component["definition"])
        shapes.append(component["shape"])
        return True

    def _create_http_sender_participant(self, id: str, name: str) -> Dict[str, str]:
        """Create an HTTP sender participant."""
        position = {"x": 66, "y": 92}

        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointSender" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>enableBasicAuthentication</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointSender</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_integration_process_participant(self, id: str, name: str, process_ref: str) -> Dict[str, str]:
        """Create an integration process participant."""
        position = {"x": 240, "y": 80}

        definition = f'''<bpmn2:participant id="{id}" ifl:type="IntegrationProcess" name="{name}" processRef="{process_ref}">
    <bpmn2:extensionElements/>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="220.0" width="1060.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_start_event(self, id: str, name: str) -> Dict[str, str]:
        """Create a start event."""
        position = {"x": 292, "y": 142}

        definition = f'''<bpmn2:startEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::MessageStartEvent/version::1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:startEvent>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="32.0" width="32.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_end_event(self, id: str, name: str) -> Dict[str, str]:
        """Create an end event."""
        position = {"x": 1158, "y": 142}

        definition = f'''<bpmn2:endEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="32.0" width="32.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_http_sender_message_flow(self, id: str, source_ref: str, target_ref: str, url_path: str) -> Dict[str, str]:
        """Create an HTTP sender message flow."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="HTTPS" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>HTTPS</value>
        </ifl:property>
        <ifl:property>
            <key>urlPath</key>
            <value>{url_path}</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.5</value>
        </ifl:property>
        <ifl:property>
            <key>senderAuthType</key>
            <value>RoleBased</value>
        </ifl:property>
        <ifl:property>
            <key>userRole</key>
            <value>ESBMessaging.send</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="116.0" xsi:type="dc:Point" y="160.0"/>
    <di:waypoint x="308.0" xsi:type="dc:Point" y="160.0"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    def _create_service_task(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create a service task."""
        definition = f'''<bpmn2:serviceTask id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>ExternalCall</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:serviceTask>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_odata_receiver_participant(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create an OData receiver participant."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointRecevier" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_http_receiver_participant(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create an HTTP receiver participant."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointRecevier" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_odata_message_flow(
        self,
        id: str,
        source_ref: str,
        target_ref: str,
        operation: str,
        service_url: str,
        entity_set: str
    ) -> Dict[str, str]:
        """Create an OData message flow."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="OData" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>Description</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>pagination</key>
            <value>0</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentType</key>
            <value>HCIOData</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocol</key>
            <value>OData V2</value>
        </ifl:property>
        <ifl:property>
            <key>operation</key>
            <value>{operation}</value>
        </ifl:property>
        <ifl:property>
            <key>address</key>
            <value>{service_url}</value>
        </ifl:property>
        <ifl:property>
            <key>resourcePath</key>
            <value>{entity_set}</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.25.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="{self.component_positions.get(source_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(source_ref, {'y': 150})['y'] + 30}"/>
    <di:waypoint x="{self.component_positions.get(target_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(target_ref, {'y': 300})['y']}"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    def _create_http_message_flow(
        self,
        id: str,
        source_ref: str,
        target_ref: str,
        method: str,
        url: str
    ) -> Dict[str, str]:
        """Create an HTTP message flow."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="HTTP" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>Description</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>ComponentType</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>httpMethod</key>
            <value>{method}</value>
        </ifl:property>
        <ifl:property>
            <key>address</key>
            <value>{url}</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.5</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="{self.component_positions.get(source_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(source_ref, {'y': 150})['y'] + 30}"/>
    <di:waypoint x="{self.component_positions.get(target_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(target_ref, {'y': 300})['y']}"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    def _create_sftp_receiver_participant(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create an SFTP receiver participant."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointRecevier" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_sftp_message_flow(
        self,
        id: str,
        source_ref: str,
        target_ref: str,
        host: str,
        port: str,
        path: str,
        username: str,
        auth_type: str,
        operation: str,
    ) -> Dict[str, str]:
        """Create an SFTP message flow."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="SFTP" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property><key>ComponentType</key><value>SFTP</value></ifl:property>
        <ifl:property><key>Description</key><value>SFTP Connection for file transfer</value></ifl:property>
        <ifl:property><key>ComponentNS</key><value>sap</value></ifl:property>
        <ifl:property><key>host</key><value>{host}</value></ifl:property>
        <ifl:property><key>port</key><value>{port}</value></ifl:property>
        <ifl:property><key>path</key><value>{path}</value></ifl:property>
        <ifl:property><key>authentication</key><value>{auth_type}</value></ifl:property>
        <ifl:property><key>username</key><value>{username}</value></ifl:property>
        <ifl:property><key>operation</key><value>{operation}</value></ifl:property>
        <ifl:property><key>TransportProtocolVersion</key><value>1.11.2</value></ifl:property>
        <ifl:property><key>MessageProtocol</key><value>File</value></ifl:property>
        <ifl:property><key>direction</key><value>Receiver</value></ifl:property>
        <ifl:property><key>TransportProtocol</key><value>SFTP</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="{self.component_positions.get(source_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(source_ref, {'y': 150})['y'] + 30}"/>
    <di:waypoint x="{self.component_positions.get(target_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(target_ref, {'y': 300})['y']}"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    def _create_successfactors_receiver_participant(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create a SuccessFactors receiver participant."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointRecevier" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_successfactors_message_flow(
        self,
        id: str,
        source_ref: str,
        target_ref: str,
        url: str,
        operation: str,
        auth_method: str,
    ) -> Dict[str, str]:
        """Create a SuccessFactors OData message flow."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="SuccessFactors" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property><key>ComponentType</key><value>SuccessFactors</value></ifl:property>
        <ifl:property><key>Description</key><value>SuccessFactors OData Connection</value></ifl:property>
        <ifl:property><key>ComponentNS</key><value>sap</value></ifl:property>
        <ifl:property><key>address</key><value>{url}</value></ifl:property>
        <ifl:property><key>operation</key><value>{operation}</value></ifl:property>
        <ifl:property><key>authenticationMethod</key><value>{auth_method}</value></ifl:property>
        <ifl:property><key>MessageProtocol</key><value>OData V2</value></ifl:property>
        <ifl:property><key>direction</key><value>Receiver</value></ifl:property>
        <ifl:property><key>TransportProtocol</key><value>HTTPS</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="{self.component_positions.get(source_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(source_ref, {'y': 150})['y'] + 30}"/>
    <di:waypoint x="{self.component_positions.get(target_ref, {'x': 500})['x'] + 50}" xsi:type="dc:Point" y="{self.component_positions.get(target_ref, {'y': 300})['y']}"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    def _create_subprocess(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create a generic embedded subprocess container."""
        definition = f'''<bpmn2:subProcess id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
        <ifl:property><key>activityType</key><value>EmbeddedSubprocess</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::Subprocess/version::1.0.0</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:subProcess>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="100.0" width="160.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_exception_subprocess(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create an exception subprocess container."""
        definition = f'''<bpmn2:subProcess id="{id}" name="{name}" triggeredByEvent="true">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
        <ifl:property><key>activityType</key><value>Exception Subprocess</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::ExceptionSubprocess/version::1.1.0</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:subProcess>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="120.0" width="200.0" x="{position['x']}" y="{position['y'] + 150}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_subprocess_with_nested(self, id: str, name: str, nested_components: List, position: Dict[str, int]) -> Dict[str, str]:
        """Create a subprocess with nested components."""
        # Process nested components to generate internal XML
        nested_xml = ""
        
        if nested_components:
            for i, nested_comp in enumerate(nested_components):
                nested_id = f"{id}_{nested_comp.get('id', f'nested_{i}')}"
                nested_name = nested_comp.get('name', f'Nested Component {i+1}')
                nested_type = nested_comp.get('type', 'content_modifier')
                
                # Generate nested component XML (simplified)
                if nested_type == "content_modifier":
                    nested_xml += f'''
        <bpmn2:serviceTask id="{nested_id}" name="{nested_name}">
            <bpmn2:extensionElements>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
                <ifl:property><key>activityType</key><value>Enricher</value></ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:serviceTask>'''
                elif nested_type == "script":
                    nested_xml += f'''
        <bpmn2:scriptTask id="{nested_id}" name="{nested_name}">
            <bpmn2:extensionElements>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
                <ifl:property><key>activityType</key><value>ScriptCollection</value></ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:scriptTask>'''
        
        definition = f'''<bpmn2:subProcess id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
        <ifl:property><key>activityType</key><value>EmbeddedSubprocess</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::Subprocess/version::1.0.0</value></ifl:property>
    </bpmn2:extensionElements>{nested_xml}
</bpmn2:subProcess>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="120.0" width="200.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_exception_subprocess_with_nested(self, id: str, name: str, nested_components: List, position: Dict[str, int]) -> Dict[str, str]:
        """Create an exception subprocess with nested components."""
        # Process nested components to generate internal XML  
        nested_xml = ""
        
        if nested_components:
            for i, nested_comp in enumerate(nested_components):
                nested_id = f"{id}_{nested_comp.get('id', f'nested_{i}')}"
                nested_name = nested_comp.get('name', f'Error Handler {i+1}')
                nested_type = nested_comp.get('type', 'content_modifier')
                
                # Generate nested component XML for error handling
                if nested_type == "content_modifier":
                    nested_xml += f'''
        <bpmn2:serviceTask id="{nested_id}" name="{nested_name}">
            <bpmn2:extensionElements>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
                <ifl:property><key>activityType</key><value>Enricher</value></ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:serviceTask>'''
        
        definition = f'''<bpmn2:subProcess id="{id}" name="{name}" triggeredByEvent="true">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
        <ifl:property><key>activityType</key><value>Exception Subprocess</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::ExceptionSubprocess/version::1.1.0</value></ifl:property>
    </bpmn2:extensionElements>{nested_xml}
</bpmn2:subProcess>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="100.0" width="180.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_message_mapping(self, id: str, name: str, config: Dict, position: Dict[str, int]) -> Dict[str, str]:
        """Create an enhanced message mapping component based on real SAP iFlow structure."""
        mapping_name = config.get("mapping_name", f"{name.replace(' ', '_')}_Mapping")
        source_schema = config.get("source_schema", "Source.xsd")
        target_schema = config.get("target_schema", "Target.xsd")
        source_format = config.get("source_format", "XML")
        target_format = config.get("target_format", "XML")
        
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.3</value></ifl:property>
        <ifl:property><key>activityType</key><value>Mapping</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageMapping/version::1.3.1</value></ifl:property>
        <ifl:property><key>mappinguri</key><value>dir://mapping/{mapping_name}.mmap</value></ifl:property>
        <ifl:property><key>mappingType</key><value>MessageMapping</value></ifl:property>
        <ifl:property><key>messageMappingBundleId</key><value>{mapping_name}</value></ifl:property>
        <ifl:property><key>sourceSchema</key><value>src/main/resources/xsd/{source_schema}</value></ifl:property>
        <ifl:property><key>targetSchema</key><value>src/main/resources/xsd/{target_schema}</value></ifl:property>
        <ifl:property><key>customFunctions</key><value>src/main/resources/script</value></ifl:property>
        <ifl:property><key>sourceFormat</key><value>{source_format}</value></ifl:property>
        <ifl:property><key>targetFormat</key><value>{target_format}</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="120.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_content_modifier(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int]) -> Dict[str, str]:
        """Create a content modifier."""
        body_type = config.get("body_type", "expression")
        content = config.get("content", "${body}")

        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>bodyType</key>
            <value>{body_type}</value>
        </ifl:property>
        <ifl:property>
            <key>bodyContent</key>
            <value><![CDATA[{content}]]></value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.5</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>ContentModifier</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ContentModifier/version::1.5.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_content_enricher(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int]) -> Dict[str, str]:
        """Create a content enricher."""
        body_type = config.get("body_type", "expression")
        body_content = config.get("body_content", "")
        header_table = config.get("header_table", "")

        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>bodyType</key>
            <value>{body_type}</value>
        </ifl:property>
        <ifl:property>
            <key>bodyContent</key>
            <value><![CDATA[{body_content}]]></value>
        </ifl:property>
        <ifl:property>
            <key>headerTable</key>
            <value>{header_table}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.6</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Enricher</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Enricher/version::1.6.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_json_to_xml_converter(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create a JSON to XML converter."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>additionalRootElementName</key>
            <value>root</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>JsonToXmlConverter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::JsonToXmlConverter/version::1.1.2</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_gateway(self, id: str, name: str, position: Dict[str, int]) -> Dict[str, str]:
        """Create an exclusive gateway."""
        definition = f'''<bpmn2:exclusiveGateway id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>ExclusiveGateway</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.1.2</value>
        </ifl:property>
        <ifl:property>
            <key>throwException</key>
            <value>false</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:exclusiveGateway>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="40.0" width="40.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_script(self, id: str, name: str, config: Dict[str, Any], position: Dict[str, int]) -> Dict[str, str]:
        """Create a script component."""
        script_type = config.get("script_type", "groovy")
        script_content = config.get("script", "// Default script content")

        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>scriptFunction</key>
            <value>script</value>
        </ifl:property>
        <ifl:property>
            <key>scriptBundleId</key>
            <value>com.sap.it.fn.script</value>
        </ifl:property>
        <ifl:property>
            <key>scriptCollection</key>
            <value>{script_type}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Script</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Script/version::1.1.1</value>
        </ifl:property>
        <ifl:property>
            <key>script</key>
            <value><![CDATA[{script_content}]]></value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="{position['x']}" y="{position['y']}"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def _create_sequence_flow(self, id: str, source_ref: str, target_ref: str, condition: str = None) -> Dict[str, str]:
        """Create a sequence flow."""
        if condition:
            definition = f'''<bpmn2:sequenceFlow id="{id}" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>expressionType</key>
            <value>NonXML</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:conditionExpression id="FormalExpression_{id}" xsi:type="bpmn2:tFormalExpression">{condition}</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>'''
        else:
            definition = f'''<bpmn2:sequenceFlow id="{id}" sourceRef="{source_ref}" targetRef="{target_ref}" isImmediate="true"/>'''

        # Calculate waypoints based on component positions
        source_pos = self.component_positions.get(source_ref, {"x": 300, "y": 150})
        target_pos = self.component_positions.get(target_ref, {"x": 450, "y": 150})

        # For start events (circles), connect from the right edge
        if "StartEvent" in source_ref:
            source_x = source_pos['x'] + 32  # Width of start event
            source_y = source_pos['y'] + 16  # Half height of start event
        else:
            # For activities (rectangles), connect from the right edge
            source_x = source_pos['x'] + 100  # Width of activity
            source_y = source_pos['y'] + 30  # Half height of activity

        # For end events (circles), connect to the left edge
        if "EndEvent" in target_ref:
            target_x = target_pos['x']
            target_y = target_pos['y'] + 16  # Half height of end event
        else:
            # For activities (rectangles), connect to the left edge
            target_x = target_pos['x']
            target_y = target_pos['y'] + 30  # Half height of activity

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="{source_x}" xsi:type="dc:Point" y="{source_y}"/>
    <di:waypoint x="{target_x}" xsi:type="dc:Point" y="{target_y}"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    def _replace_placeholders(
        self,
        xml: str,
        participants: List[str],
        message_flows: List[str],
        process_components: List[str],
        sequence_flows: List[str],
        shapes: List[str],
        edges: List[str]
    ) -> str:
        """
        Replace placeholders in the XML with actual content.

        Args:
            xml: The XML with placeholders
            participants: List of participant XML
            message_flows: List of message flow XML
            process_components: List of process component XML
            sequence_flows: List of sequence flow XML
            shapes: List of shape XML
            edges: List of edge XML

        Returns:
            str: The XML with placeholders replaced
        """
        xml = xml.replace("{{participants}}", "\n    ".join(participants))
        xml = xml.replace("{{message_flows}}", "\n    ".join(message_flows))
        xml = xml.replace("{{process_components}}", "\n    ".join(process_components))
        xml = xml.replace("{{sequence_flows}}", "\n    ".join(sequence_flows))
        xml = xml.replace("{{shapes}}", "\n      ".join(shapes))
        xml = xml.replace("{{edges}}", "\n      ".join(edges))
        return xml

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4()).replace("-", "")[:12]