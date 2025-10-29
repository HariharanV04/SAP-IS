"""
BPMN Templates for SAP Integration Suite iFlow generation.
These templates are based on the Simple_Hello_iFlow.iflw file.
"""

class BpmnTemplates:
    """
    Class containing BPMN templates for SAP Integration Suite iFlow generation.
    """

    def __init__(self):
        """Initialize the templates."""
        pass

    # 1. Start Event Components
    def start_event_template(self, id="StartEvent_2", name="Start"):
        """Generate a start event template."""
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
    <bpmn2:outgoing>SequenceFlow_Start</bpmn2:outgoing>
    <bpmn2:messageEventDefinition/>
</bpmn2:startEvent>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="32.0" width="32.0" x="292.0" y="142.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 2. End Event Components
    def end_event_template(self, id="EndEvent_2", name="End", incoming_flows=None):
        """Generate an end event template."""
        if incoming_flows is None:
            incoming_flows = ["SequenceFlow_End"]

        incoming_elements = "\n    ".join([f'<bpmn2:incoming>{flow}</bpmn2:incoming>' for flow in incoming_flows])

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
    {incoming_elements}
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="32.0" width="32.0" x="1158.0" y="142.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 3. Service Task Components (OData)
    def service_task_template(self, id, name, incoming_flow, outgoing_flow):
        """Generate a service task template for OData calls."""
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
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:serviceTask>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="821.0" y="132.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 4. OData Receiver Participant Components
    def odata_receiver_template(self, id, name):
        """Generate an OData receiver participant template."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointRecevier" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="821.0" y="315.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 5. OData Message Flow Components
    def odata_message_flow_template(self, id, source_ref, target_ref, operation="Query(GET)"):
        """Generate an OData message flow template."""
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
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="871.0" xsi:type="dc:Point" y="162.0"/>
    <di:waypoint x="871.0" xsi:type="dc:Point" y="385.0"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    # 6. JSON to XML Converter Components
    def json_to_xml_template(self, id, name, incoming_flow, outgoing_flow):
        """Generate a JSON to XML converter template."""
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
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="394.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 7. Content Enricher Components
    def content_enricher_template(self, id, name, incoming_flow, outgoing_flow, header_table=""):
        """Generate a content enricher template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>bodyType</key>
            <value>constant</value>
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
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="543.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 8. Gateway Components
    def exclusive_gateway_template(self, id, name, incoming_flow, outgoing_flows, default_flow=None):
        """Generate an exclusive gateway template."""
        default_attr = f' default="{default_flow}"' if default_flow else ""
        outgoing_elements = "\n    ".join([f'<bpmn2:outgoing>{flow}</bpmn2:outgoing>' for flow in outgoing_flows])

        definition = f'''<bpmn2:exclusiveGateway{default_attr} id="{id}" name="{name}">
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
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    {outgoing_elements}
</bpmn2:exclusiveGateway>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="40.0" width="40.0" x="675.0" y="142.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 9. Sequence Flow Components
    def sequence_flow_template(self, id, source_ref, target_ref, condition=None, name=None):
        """Generate a sequence flow template."""
        name_attr = f' name="{name}"' if name else ""

        if condition:
            definition = f'''<bpmn2:sequenceFlow id="{id}"{name_attr} sourceRef="{source_ref}" targetRef="{target_ref}">
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
            definition = f'''<bpmn2:sequenceFlow id="{id}"{name_attr} sourceRef="{source_ref}" targetRef="{target_ref}"/>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="308.0" xsi:type="dc:Point" y="158.0"/>
    <di:waypoint x="444.0" xsi:type="dc:Point" y="158.0"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    # 10. HTTP Sender Components
    def http_sender_participant_template(self, id="Participant_1", name="Sender"):
        """Generate an HTTP sender participant template."""
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
    <dc:Bounds height="140.0" width="100.0" x="66.0" y="92.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def http_sender_message_flow_template(self, id="MessageFlow_10", source_ref="Participant_1", target_ref="StartEvent_2", url_path="/"):
        """Generate an HTTP sender message flow template."""
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

    # Integration Process Participant
    def integration_process_participant_template(self, id="Participant_Process", name="Integration Process", process_ref="Process_1"):
        """Generate an integration process participant template."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="IntegrationProcess" name="{name}" processRef="{process_ref}">
    <bpmn2:extensionElements/>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="220.0" width="1060.0" x="240.0" y="80.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # Process Template
    def process_template(self, id="Process_1", name="Integration Process"):
        """Generate a process template."""
        return f'''<bpmn2:process id="{id}" name="{name}" isExecutable="true">
    {{process_content}}
</bpmn2:process>'''

    # Full iFlow XML Template
    def iflow_xml_template(self):
        """Generate the full iFlow XML template."""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:ifl="http:///com.sap.ifl.model/Ifl.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="Definitions_1">
  <bpmn2:collaboration id="Collaboration_1" name="Collaboration">
    <bpmn2:documentation id="Documentation_1671742909132" textFormat="text/plain">{{description}}</bpmn2:documentation>
    <bpmn2:extensionElements>
      <ifl:property>
        <key>namespaceMapping</key>
        <value>{{namespace_mapping}}</value>
      </ifl:property>
      <ifl:property>
        <key>allowedHeaderList</key>
        <value>{{allowed_headers}}</value>
      </ifl:property>
      <ifl:property>
        <key>httpSessionHandling</key>
        <value>{{http_session_handling}}</value>
      </ifl:property>
      <ifl:property>
        <key>ServerTrace</key>
        <value>{{server_trace}}</value>
      </ifl:property>
      <ifl:property>
        <key>returnExceptionToSender</key>
        <value>{{return_exception}}</value>
      </ifl:property>
      <ifl:property>
        <key>log</key>
        <value>{{log_level}}</value>
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
  {{process}}
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane bpmnElement="Collaboration_1" id="BPMNPlane_1">
      {{shapes}}
      {{edges}}
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn2:definitions>'''


class TemplateBpmnGenerator:
    """
    Class for generating BPMN files using templates from Simple_Hello_iFlow.iflw.
    """

    def __init__(self):
        """Initialize the generator."""
        self.templates = BpmnTemplates()
        self.component_positions = {}
        self.next_x = 300
        self.next_y = 140

    def generate_iflow_xml(self, components, iflow_name):
        """
        Generate the iFlow XML using templates.

        Args:
            components (dict): The components to include in the iFlow
            iflow_name (str): The name of the iFlow

        Returns:
            str: The generated iFlow XML
        """
        # Initialize collections for different component types
        participants = []
        message_flows = []
        process_components = []
        sequence_flows = []
        shapes = []
        edges = []

        # Add HTTP sender participant
        http_sender = self.templates.http_sender_participant_template()
        participants.append(http_sender["definition"])
        shapes.append(http_sender["shape"])

        # Add integration process participant
        process_participant = self.templates.integration_process_participant_template()
        participants.append(process_participant["definition"])
        shapes.append(process_participant["shape"])

        # Add HTTP sender message flow
        http_flow = self.templates.http_sender_message_flow_template(url_path=f"/{iflow_name}")
        message_flows.append(http_flow["definition"])
        edges.append(http_flow["edge"])

        # Add start event
        start_event = self.templates.start_event_template()
        process_components.append(start_event["definition"])
        shapes.append(start_event["shape"])

        # Add end event
        end_event = self.templates.end_event_template()
        process_components.append(end_event["definition"])
        shapes.append(end_event["shape"])

        # Process the components from the input
        component_ids = []
        component_sequence = []

        # First pass: collect all component IDs and create a sequence
        for endpoint in components.get("endpoints", []):
            for component in endpoint.get("components", []):
                component_type = component.get("type", "").lower()
                component_id = component.get("id", f"{component_type}_{len(component_ids)}")
                component_ids.append(component_id)
                component_sequence.append(component_id)

        # Calculate positions for components
        x_spacing = 150
        x_pos = 350  # Start after the start event

        # Second pass: create components and connections
        for i, endpoint in enumerate(components.get("endpoints", [])):
            for j, component in enumerate(endpoint.get("components", [])):
                component_type = component.get("type", "").lower()
                component_id = component.get("id", f"{component_type}_{j}")
                component_name = component.get("name", f"{component_type}_{j}")

                # Calculate position
                self.component_positions[component_id] = {"x": x_pos, "y": self.next_y}
                x_pos += x_spacing

                # Determine incoming and outgoing flows
                incoming_flow = f"SequenceFlow_{len(sequence_flows)}"
                outgoing_flow = f"SequenceFlow_{len(sequence_flows) + 1}"

                # Create the component based on its type
                if component_type == "json_to_xml" or component_type == "jsontoxml":
                    # JSON to XML Converter
                    json_to_xml = self.templates.json_to_xml_template(
                        id=component_id,
                        name=component_name,
                        incoming_flow=incoming_flow,
                        outgoing_flow=outgoing_flow
                    )
                    process_components.append(json_to_xml["definition"])
                    shapes.append(json_to_xml["shape"])

                elif component_type == "content_enricher" or component_type == "enricher":
                    # Content Enricher
                    content_enricher = self.templates.content_enricher_template(
                        id=component_id,
                        name=component_name,
                        incoming_flow=incoming_flow,
                        outgoing_flow=outgoing_flow
                    )
                    process_components.append(content_enricher["definition"])
                    shapes.append(content_enricher["shape"])

                elif component_type == "odata_adapter" or component_type == "odata_receiver":
                    # OData Service Task
                    service_task_id = f"ServiceTask_{component_id}"
                    service_task = self.templates.service_task_template(
                        id=service_task_id,
                        name=f"Call_{component_name}",
                        incoming_flow=incoming_flow,
                        outgoing_flow=outgoing_flow
                    )
                    process_components.append(service_task["definition"])
                    shapes.append(service_task["shape"])

                    # OData Receiver Participant
                    participant_id = f"Participant_OData_{component_id}"
                    odata_participant = self.templates.odata_receiver_template(
                        id=participant_id,
                        name=f"OData_{component_name}"
                    )
                    participants.append(odata_participant["definition"])
                    shapes.append(odata_participant["shape"])

                    # OData Message Flow
                    message_flow_id = f"MessageFlow_OData_{component_id}"
                    odata_message_flow = self.templates.odata_message_flow_template(
                        id=message_flow_id,
                        source_ref=service_task_id,
                        target_ref=participant_id,
                        operation=component.get("config", {}).get("operation", "Query(GET)")
                    )
                    message_flows.append(odata_message_flow["definition"])
                    edges.append(odata_message_flow["edge"])

                elif component_type == "gateway" or component_type == "router":
                    # Gateway with conditions
                    conditions = component.get("config", {}).get("conditions", [])
                    outgoing_flows = [f"SequenceFlow_{len(sequence_flows) + 1 + k}" for k in range(len(conditions) + 1)]

                    gateway = self.templates.exclusive_gateway_template(
                        id=component_id,
                        name=component_name,
                        incoming_flow=incoming_flow,
                        outgoing_flows=outgoing_flows,
                        default_flow=outgoing_flows[-1]
                    )
                    process_components.append(gateway["definition"])
                    shapes.append(gateway["shape"])

                    # Add conditional sequence flows
                    for k, condition in enumerate(conditions):
                        condition_flow = self.templates.sequence_flow_template(
                            id=outgoing_flows[k],
                            source_ref=component_id,
                            target_ref="EndEvent_2",  # Default target, will be updated later
                            condition=condition.get("expression", ""),
                            name=condition.get("name", f"Route_{k+1}")
                        )
                        sequence_flows.append(condition_flow["definition"])
                        edges.append(condition_flow["edge"])

                    # Add default sequence flow
                    default_flow = self.templates.sequence_flow_template(
                        id=outgoing_flows[-1],
                        source_ref=component_id,
                        target_ref="EndEvent_2",  # Default target, will be updated later
                        name="Default"
                    )
                    sequence_flows.append(default_flow["definition"])
                    edges.append(default_flow["edge"])

                    # Skip adding regular sequence flows since we've added conditional ones
                    continue

                # Add sequence flows (except for gateways which have special handling)
                if j == 0 and i == 0:
                    # First component connects from start event
                    start_flow = self.templates.sequence_flow_template(
                        id=incoming_flow,
                        source_ref="StartEvent_2",
                        target_ref=component_id
                    )
                    sequence_flows.append(start_flow["definition"])
                    edges.append(start_flow["edge"])

                if j == len(endpoint.get("components", [])) - 1 and i == len(components.get("endpoints", [])) - 1:
                    # Last component connects to end event
                    end_flow = self.templates.sequence_flow_template(
                        id=outgoing_flow,
                        source_ref=component_id,
                        target_ref="EndEvent_2"
                    )
                    sequence_flows.append(end_flow["definition"])
                    edges.append(end_flow["edge"])
                elif j < len(endpoint.get("components", [])) - 1:
                    # Connect to the next component in this endpoint
                    next_component = endpoint["components"][j + 1]
                    next_id = next_component.get("id", f"{next_component.get('type', 'component')}_{j+1}")

                    next_flow = self.templates.sequence_flow_template(
                        id=outgoing_flow,
                        source_ref=component_id,
                        target_ref=next_id
                    )
                    sequence_flows.append(next_flow["definition"])
                    edges.append(next_flow["edge"])

        # If no components were added, create a direct flow from start to end
        if not component_ids:
            direct_flow = self.templates.sequence_flow_template(
                id="SequenceFlow_Direct",
                source_ref="StartEvent_2",
                target_ref="EndEvent_2"
            )
            sequence_flows.append(direct_flow["definition"])
            edges.append(direct_flow["edge"])

        # Create the process content
        process_content = "\n".join(process_components + sequence_flows)

        # Create the process
        process = self.templates.process_template().replace("{process_content}", process_content)

        # Create the full XML
        xml_template = self.templates.iflow_xml_template()
        xml = xml_template.replace("{{participants}}", "\n".join(participants))
        xml = xml.replace("{{message_flows}}", "\n".join(message_flows))
        xml = xml.replace("{{process}}", process)
        xml = xml.replace("{{shapes}}", "\n".join(shapes))
        xml = xml.replace("{{edges}}", "\n".join(edges))
        xml = xml.replace("{{description}}", f"Generated iFlow: {iflow_name}")
        xml = xml.replace("{{namespace_mapping}}", "")
        xml = xml.replace("{{allowed_headers}}", "*")
        xml = xml.replace("{{http_session_handling}}", "None")
        xml = xml.replace("{{server_trace}}", "false")
        xml = xml.replace("{{return_exception}}", "false")
        xml = xml.replace("{{log_level}}", "All events")

        return xml