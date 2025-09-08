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

    # 11. SFTP Receiver Components
    def sftp_receiver_participant_template(self, id="Participant_SFTP", name="SFTP_Server"):
        """Generate an SFTP receiver participant template."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointRecevier" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ifl:type</key>
                    <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="850" y="150"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def sftp_receiver_message_flow_template(self, id="MessageFlow_SFTP", source_ref="ServiceTask_1", target_ref="Participant_SFTP",
                                          host="sftp.example.com", port="22", path="/uploads", username="${sftp_username}",
                                          auth_type="Password", operation="PUT"):
        """Generate an SFTP receiver message flow template."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="SFTP" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>SFTP</value>
        </ifl:property>
        <ifl:property>
            <key>Description</key>
            <value>SFTP Connection for file upload</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>host</key>
            <value>{host}</value>
        </ifl:property>
        <ifl:property>
            <key>port</key>
            <value>{port}</value>
        </ifl:property>
        <ifl:property>
            <key>path</key>
            <value>{path}</value>
        </ifl:property>
        <ifl:property>
            <key>authentication</key>
            <value>{auth_type.lower()}</value>
        </ifl:property>
        <ifl:property>
            <key>username</key>
            <value>{username}</value>
        </ifl:property>
        <ifl:property>
            <key>operation</key>
            <value>{operation}</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocolVersion</key>
            <value>1.11.2</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocol</key>
            <value>File</value>
        </ifl:property>
        <ifl:property>
            <key>direction</key>
            <value>Receiver</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocol</key>
            <value>SFTP</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.11</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::AdapterVariant/cname::sap:SFTP/tp::SFTP/mp::File/direction::Receiver/version::1.11.2</value>
        </ifl:property>
        <ifl:property>
            <key>fileExist</key>
            <value>Override</value>
        </ifl:property>
        <ifl:property>
            <key>autoCreate</key>
            <value>1</value>
        </ifl:property>
        <ifl:property>
            <key>connectTimeout</key>
            <value>10000</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="757" xsi:type="dc:Point" y="140"/>
    <di:waypoint x="850" xsi:type="dc:Point" y="170"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    # 12. Request-Reply Service Task Components
    def request_reply_template(self, id, name, incoming_flow="{{incoming_flow}}", outgoing_flow="{{outgoing_flow}}"):
        """Generate a request-reply service task template."""
        definition = f'''<bpmn2:serviceTask id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>activityType</key>
            <value>ExternalCall</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.2</value>
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
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 13. SuccessFactors OData Receiver Components
    def successfactors_receiver_participant_template(self, id="Participant_SuccessFactors", name="SuccessFactors"):
        """Generate a SuccessFactors receiver participant template."""
        definition = f'''<bpmn2:participant id="{id}" ifl:type="EndpointRecevier" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ifl:type</key>
            <value>EndpointRecevier</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:participant>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="140.0" width="100.0" x="850" y="150"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def successfactors_receiver_message_flow_template(self, id="MessageFlow_SuccessFactors", source_ref="ServiceTask_1", target_ref="Participant_SuccessFactors",
                                                    url="https://api.successfactors.com/odata/v2/User", operation="Query(GET)", auth_method="OAuth"):
        """Generate a SuccessFactors receiver message flow template."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="SuccessFactors" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>SuccessFactors</value>
        </ifl:property>
        <ifl:property>
            <key>Description</key>
            <value>SuccessFactors OData Connection</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>address</key>
            <value>{url}</value>
        </ifl:property>
        <ifl:property>
            <key>operation</key>
            <value>{operation}</value>
        </ifl:property>
        <ifl:property>
            <key>authenticationMethod</key>
            <value>{auth_method}</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocolVersion</key>
            <value>1.25.0</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocol</key>
            <value>OData V2</value>
        </ifl:property>
        <ifl:property>
            <key>direction</key>
            <value>Receiver</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocol</key>
            <value>HTTPS</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.25</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::AdapterVariant/cname::sap:SuccessFactors/tp::HTTPS/mp::OData V2/direction::Receiver/version::1.25.0</value>
        </ifl:property>
        <ifl:property>
            <key>contentType</key>
            <value>application/json</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="757" xsi:type="dc:Point" y="140"/>
    <di:waypoint x="850" xsi:type="dc:Point" y="170"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    # 14. Mapping Components
    def operation_mapping_template(self, id, name, incoming_flow, outgoing_flow, mapping_uri="", mapping_name=""):
        """Generate an Operation Mapping template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>mappinguri</key>
            <value>{mapping_uri}</value>
        </ifl:property>
        <ifl:property>
            <key>mappingname</key>
            <value>{mapping_name}</value>
        </ifl:property>
        <ifl:property>
            <key>mappingType</key>
            <value>OperationMapping</value>
        </ifl:property>
        <ifl:property>
            <key>mappingpath</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Mapping</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::OperationMapping/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def xslt_mapping_template(self, id, name, incoming_flow, outgoing_flow, mapping_path="", output_format="Bytes"):
        """Generate an XSLT Mapping template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>mappingoutputformat</key>
            <value>{output_format}</value>
        </ifl:property>
        <ifl:property>
            <key>mappingHeaderNameKey</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>mappingpath</key>
            <value>{mapping_path}</value>
        </ifl:property>
        <ifl:property>
            <key>mappingSource</key>
            <value>mappingSrcIflow</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.2</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Mapping</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::XSLTMapping/version::1.2.0</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>XSLTMapping</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def message_mapping_template(self, id, name, incoming_flow, outgoing_flow, mapping_uri="", mapping_name=""):
        """Generate a Message Mapping template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>mappinguri</key>
            <value>{mapping_uri}</value>
        </ifl:property>
        <ifl:property>
            <key>mappingname</key>
            <value>{mapping_name}</value>
        </ifl:property>
        <ifl:property>
            <key>mappingSourceValue</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>mappingType</key>
            <value>MessageMapping</value>
        </ifl:property>
        <ifl:property>
            <key>mappingReference</key>
            <value>static</value>
        </ifl:property>
        <ifl:property>
            <key>mappingpath</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.3</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Mapping</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::MessageMapping/version::1.3.1</value>
        </ifl:property>
        <ifl:property>
            <key>messageMappingBundleId</key>
            <value/>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 15. Validation Components
    def xml_validator_template(self, id, name, incoming_flow, outgoing_flow, xsd_path="", prevent_exception="false"):
        """Generate an XML Validator template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>xmlSchemaSource</key>
            <value>iflowOption</value>
        </ifl:property>
        <ifl:property>
            <key>preventException</key>
            <value>{prevent_exception}</value>
        </ifl:property>
        <ifl:property>
            <key>xsd</key>
            <value>{xsd_path}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>2.2</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>XmlValidator</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::XmlValidator/version::2.2.3</value>
        </ifl:property>
        <ifl:property>
            <key>headerSource</key>
            <value/>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 16. Processing Components
    def filter_template(self, id, name, incoming_flow, outgoing_flow, xpath_type="Nodelist", wrap_content=""):
        """Generate a Filter template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>xpathType</key>
            <value>{xpath_type}</value>
        </ifl:property>
        <ifl:property>
            <key>wrapContent</key>
            <value>{wrap_content}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Filter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Filter/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def groovy_script_template(self, id, name, incoming_flow, outgoing_flow, script_function="", script_bundle_id="", script=""):
        """Generate a Groovy Script template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>scriptFunction</key>
            <value>{script_function}</value>
        </ifl:property>
        <ifl:property>
            <key>scriptBundleId</key>
            <value>{script_bundle_id}</value>
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
            <value>ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>GroovyScript</value>
        </ifl:property>
        <ifl:property>
            <key>script</key>
            <value>{script}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def xml_modifier_template(self, id, name, incoming_flow, outgoing_flow, remove_external_dtds="0", remove_xml_declaration="0", xml_character_handling="none"):
        """Generate an XML Modifier template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>removeExternalDTDs</key>
            <value>{remove_external_dtds}</value>
        </ifl:property>
        <ifl:property>
            <key>removeXmlDeclaration</key>
            <value>{remove_xml_declaration}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>XmlModifier</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::XmlModifier/version::1.1.0</value>
        </ifl:property>
        <ifl:property>
            <key>xmlCharacterHandling</key>
            <value>{xml_character_handling}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def write_variables_template(self, id, name, incoming_flow, outgoing_flow, visibility="local", encrypt="true", expire="90", variable=""):
        """Generate a Write Variables template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>visibility</key>
            <value>{visibility}</value>
        </ifl:property>
        <ifl:property>
            <key>encrypt</key>
            <value>{encrypt}</value>
        </ifl:property>
        <ifl:property>
            <key>expire</key>
            <value>{expire}</value>
        </ifl:property>
        <ifl:property>
            <key>variable</key>
            <value>{variable}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.2</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Variables</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Variables/version::1.2.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 17. Splitter Components
    def edi_splitter_template(self, id, name, incoming_flow, outgoing_flow, split_type="EDISplitter", parallel_processing="false", timeout=""):
        """Generate an EDI Splitter template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>edifactSourceEncoding</key>
            <value>UTF-8</value>
        </ifl:property>
        <ifl:property>
            <key>edifactValidateMessage</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>edifactTransactionMode</key>
            <value>interchange</value>
        </ifl:property>
        <ifl:property>
            <key>edifactUnaRequired</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>x12SourceEncoding</key>
            <value>UTF-8</value>
        </ifl:property>
        <ifl:property>
            <key>x12TransactionMode</key>
            <value>interchange</value>
        </ifl:property>
        <ifl:property>
            <key>parallelProcessing</key>
            <value>{parallel_processing}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>2.9</value>
        </ifl:property>
        <ifl:property>
            <key>splitType</key>
            <value>{split_type}</value>
        </ifl:property>
        <ifl:property>
            <key>timeOut</key>
            <value>{timeout}</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Splitter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::EDISplitter/version::2.9.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def idoc_splitter_template(self, id, name, incoming_flow, outgoing_flow, split_type="IDoc"):
        """Generate an IDoc Splitter template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Splitter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::IDoc/version::1.1.0</value>
        </ifl:property>
        <ifl:property>
            <key>splitType</key>
            <value>{split_type}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def general_splitter_template(self, id, name, incoming_flow, outgoing_flow, expr_type="XPath", streaming="true",
                                 stop_on_execution="true", splitter_threads="10", split_expr_value="",
                                 parallel_processing="false", grouping="", timeout="300"):
        """Generate a General Splitter template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>exprType</key>
            <value>{expr_type}</value>
        </ifl:property>
        <ifl:property>
            <key>Streaming</key>
            <value>{streaming}</value>
        </ifl:property>
        <ifl:property>
            <key>StopOnExecution</key>
            <value>{stop_on_execution}</value>
        </ifl:property>
        <ifl:property>
            <key>SplitterThreads</key>
            <value>{splitter_threads}</value>
        </ifl:property>
        <ifl:property>
            <key>splitExprValue</key>
            <value>{split_expr_value}</value>
        </ifl:property>
        <ifl:property>
            <key>ParallelProcessing</key>
            <value>{parallel_processing}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.6</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Splitter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::GeneralSplitter/version::1.6.0</value>
        </ifl:property>
        <ifl:property>
            <key>grouping</key>
            <value>{grouping}</value>
        </ifl:property>
        <ifl:property>
            <key>splitType</key>
            <value>GeneralSplitter</value>
        </ifl:property>
        <ifl:property>
            <key>timeOut</key>
            <value>{timeout}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 18. Gateway Components
    def sequential_multicast_template(self, id, name, incoming_flow, outgoing_flows, routing_sequence_table=""):
        """Generate a Sequential Multicast (Parallel Gateway) template."""
        outgoing_elements = "\n    ".join([f'<bpmn2:outgoing>{flow}</bpmn2:outgoing>' for flow in outgoing_flows])

        definition = f'''<bpmn2:parallelGateway id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>routingSequenceTable</key>
            <value>{routing_sequence_table}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>SequentialMulticast</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::SequentialMulticast/version::1.1.0</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>parallel</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    {outgoing_elements}
</bpmn2:parallelGateway>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="40.0" width="40.0" x="400.0" y="138.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def parallel_multicast_template(self, id, name, incoming_flow, outgoing_flows):
        """Generate a Parallel Multicast (Parallel Gateway) template."""
        outgoing_elements = "\n    ".join([f'<bpmn2:outgoing>{flow}</bpmn2:outgoing>' for flow in outgoing_flows])

        definition = f'''<bpmn2:parallelGateway id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Multicast</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Multicast/version::1.1.1</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>parallel</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    {outgoing_elements}
</bpmn2:parallelGateway>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="40.0" width="40.0" x="400.0" y="138.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def join_template(self, id, name, incoming_flows, outgoing_flow):
        """Generate a Join (Parallel Gateway) template."""
        incoming_elements = "\n    ".join([f'<bpmn2:incoming>{flow}</bpmn2:incoming>' for flow in incoming_flows])

        definition = f'''<bpmn2:parallelGateway id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Join</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Join/version::1.0.0</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>parallel</value>
        </ifl:property>
    </bpmn2:extensionElements>
    {incoming_elements}
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:parallelGateway>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="40.0" width="40.0" x="400.0" y="138.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def router_template(self, id, name, incoming_flow, outgoing_flows, default_flow=None, throw_exception="false"):
        """Generate a Router (Exclusive Gateway) template."""
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
            <value>{throw_exception}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    {outgoing_elements}
</bpmn2:exclusiveGateway>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="40.0" width="40.0" x="400.0" y="138.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 19. Storage Components
    def select_template(self, id, name, incoming_flow, outgoing_flow, visibility="local", max_results="1",
                       operation="select", delete="false", storage_name=""):
        """Generate a Select (DB Storage) template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>visibility</key>
            <value>{visibility}</value>
        </ifl:property>
        <ifl:property>
            <key>maxresults</key>
            <value>{max_results}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.7</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>DBstorage</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::select/version::1.7.1</value>
        </ifl:property>
        <ifl:property>
            <key>operation</key>
            <value>{operation}</value>
        </ifl:property>
        <ifl:property>
            <key>delete</key>
            <value>{delete}</value>
        </ifl:property>
        <ifl:property>
            <key>storageName</key>
            <value>{storage_name}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def write_template(self, id, name, incoming_flow, outgoing_flow, visibility="local", alert="2",
                      encrypt="true", expire="30", message_id="", override="false",
                      operation="put", storage_name="", include_message_headers="false"):
        """Generate a Write (DB Storage) template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>visibility</key>
            <value>{visibility}</value>
        </ifl:property>
        <ifl:property>
            <key>alert</key>
            <value>{alert}</value>
        </ifl:property>
        <ifl:property>
            <key>encrypt</key>
            <value>{encrypt}</value>
        </ifl:property>
        <ifl:property>
            <key>expire</key>
            <value>{expire}</value>
        </ifl:property>
        <ifl:property>
            <key>messageId</key>
            <value>{message_id}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.7</value>
        </ifl:property>
        <ifl:property>
            <key>override</key>
            <value>{override}</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>DBstorage</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::put/version::1.7.1</value>
        </ifl:property>
        <ifl:property>
            <key>operation</key>
            <value>{operation}</value>
        </ifl:property>
        <ifl:property>
            <key>storageName</key>
            <value>{storage_name}</value>
        </ifl:property>
        <ifl:property>
            <key>includeMessageHeaders</key>
            <value>{include_message_headers}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def get_template(self, id, name, incoming_flow, outgoing_flow, visibility="local", data_store_id="",
                    operation="get", delete="false", stop_on_missing_entry="true", storage_name=""):
        """Generate a Get (DB Storage) template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>visibility</key>
            <value>{visibility}</value>
        </ifl:property>
        <ifl:property>
            <key>dataStoreId</key>
            <value>{data_store_id}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.7</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>DBstorage</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::get/version::1.7.1</value>
        </ifl:property>
        <ifl:property>
            <key>operation</key>
            <value>{operation}</value>
        </ifl:property>
        <ifl:property>
            <key>delete</key>
            <value>{delete}</value>
        </ifl:property>
        <ifl:property>
            <key>stopOnMissingEntry</key>
            <value>{stop_on_missing_entry}</value>
        </ifl:property>
        <ifl:property>
            <key>storageName</key>
            <value>{storage_name}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def persist_template(self, id, name, incoming_flow, outgoing_flow, step_id="", enable_encrypt="true"):
        """Generate a Persist template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>stepid</key>
            <value>{step_id}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Persist</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Persist/version::1.0.2</value>
        </ifl:property>
        <ifl:property>
            <key>enableEncrypt</key>
            <value>{enable_encrypt}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def id_mapping_template(self, id, name, incoming_flow, outgoing_flow, visibility="local",
                           source_message_id="", expire="30", context="", target_header=""):
        """Generate an ID Mapping template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>visibility</key>
            <value>{visibility}</value>
        </ifl:property>
        <ifl:property>
            <key>sourceMessageID</key>
            <value>{source_message_id}</value>
        </ifl:property>
        <ifl:property>
            <key>expire</key>
            <value>{expire}</value>
        </ifl:property>
        <ifl:property>
            <key>context</key>
            <value>{context}</value>
        </ifl:property>
        <ifl:property>
            <key>targetHeader</key>
            <value>{target_header}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>IDMapper</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::IDMapper/version::1.0.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 20. Converter Components
    def xml_to_csv_template(self, id, name, incoming_flow, outgoing_flow, field_separator=",",
                           csv_header="none", xml_schema_file_path="", include_attribute="false",
                           include_master="false", master_xpath_field_location="", xpath_field_location=""):
        """Generate an XML to CSV Converter template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>Field_Separator_in_CSV</key>
            <value>{field_separator}</value>
        </ifl:property>
        <ifl:property>
            <key>CSV_Header</key>
            <value>{csv_header}</value>
        </ifl:property>
        <ifl:property>
            <key>XML_Schema_File_Path</key>
            <value>{xml_schema_file_path}</value>
        </ifl:property>
        <ifl:property>
            <key>Include_Attribute</key>
            <value>{include_attribute}</value>
        </ifl:property>
        <ifl:property>
            <key>Include_Master</key>
            <value>{include_master}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.2</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>XmlToCsvConverter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::XmlToCsvConverter/version::1.2.0</value>
        </ifl:property>
        <ifl:property>
            <key>Master_XPath_Field_Location</key>
            <value>{master_xpath_field_location}</value>
        </ifl:property>
        <ifl:property>
            <key>XPath_Field_Location</key>
            <value>{xpath_field_location}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def csv_to_xml_template(self, id, name, incoming_flow, outgoing_flow, field_separator=",",
                           ignore_first_line_as_header="false", xml_schema_file_path="",
                           header_mapping="mapHeadersToXSD", record_identifier_in_csv="", xpath_field_location=""):
        """Generate a CSV to XML Converter template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>Field_Separator_in_CSV</key>
            <value>{field_separator}</value>
        </ifl:property>
        <ifl:property>
            <key>ignoreFirstLineAsHeader</key>
            <value>{ignore_first_line_as_header}</value>
        </ifl:property>
        <ifl:property>
            <key>XML_Schema_File_Path</key>
            <value>{xml_schema_file_path}</value>
        </ifl:property>
        <ifl:property>
            <key>headerMapping</key>
            <value>{header_mapping}</value>
        </ifl:property>
        <ifl:property>
            <key>Record_Identifier_in_CSV</key>
            <value>{record_identifier_in_csv}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.4</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>CsvToXmlConverter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::CsvToXmlConverter/version::1.4.0</value>
        </ifl:property>
        <ifl:property>
            <key>XPath_Field_Location</key>
            <value>{xpath_field_location}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def xml_to_json_template(self, id, name, incoming_flow, outgoing_flow, use_streaming="false",
                            suppress_root_element="false", path_table="", json_output_encoding="",
                            json_namespace_mapping="", convert_all_elements="specific",
                            use_namespaces="true", json_namespace_separator=":"):
        """Generate an XML to JSON Converter template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>xmlJsonUseStreaming</key>
            <value>{use_streaming}</value>
        </ifl:property>
        <ifl:property>
            <key>xmlJsonSuppressRootElement</key>
            <value>{suppress_root_element}</value>
        </ifl:property>
        <ifl:property>
            <key>xmlJsonPathTable</key>
            <value>{path_table}</value>
        </ifl:property>
        <ifl:property>
            <key>jsonOutputEncoding</key>
            <value>{json_output_encoding}</value>
        </ifl:property>
        <ifl:property>
            <key>jsonNamespaceMapping</key>
            <value>{json_namespace_mapping}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>xmlJsonConvertAllElements</key>
            <value>{convert_all_elements}</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>XmlToJsonConverter</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::XmlToJsonConverter/version::1.0.8</value>
        </ifl:property>
        <ifl:property>
            <key>useNamespaces</key>
            <value>{use_namespaces}</value>
        </ifl:property>
        <ifl:property>
            <key>jsonNamespaceSeparator</key>
            <value>{json_namespace_separator}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def base64_encoder_template(self, id, name, incoming_flow, outgoing_flow, encoder_type="Base64 Encode"):
        """Generate a Base64 Encoder template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Encoder</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Base64 Encode/version::1.0.1</value>
        </ifl:property>
        <ifl:property>
            <key>encoderType</key>
            <value>{encoder_type}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def base64_decoder_template(self, id, name, incoming_flow, outgoing_flow, encoder_type="Base64 Decode"):
        """Generate a Base64 Decoder template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Decoder</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Base64 Decode/version::1.0.1</value>
        </ifl:property>
        <ifl:property>
            <key>encoderType</key>
            <value>{encoder_type}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 21. Event Components
    def timer_start_event_template(self, id, name, outgoing_flow, schedule_key=""):
        """Generate a Timer Start Event template."""
        definition = f'''<bpmn2:startEvent id="{id}" name="{name}">
    <bpmn2:timerEventDefinition id="TimerEventDefinition_{id}">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>scheduleKey</key>
                <value>{schedule_key}</value>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.4</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::FlowstepVariant/cname::intermediatetimer/version::1.4.0</value>
            </ifl:property>
            <ifl:property>
                <key>activityType</key>
                <value>StartTimerEvent</value>
            </ifl:property>
        </bpmn2:extensionElements>
    </bpmn2:timerEventDefinition>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:startEvent>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="32.0" width="32.0" x="292.0" y="142.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def error_end_event_template(self, id, name, incoming_flows=None):
        """Generate an Error End Event template."""
        if incoming_flows is None:
            incoming_flows = ["SequenceFlow_Error"]

        incoming_elements = "\n    ".join([f'<bpmn2:incoming>{flow}</bpmn2:incoming>' for flow in incoming_flows])

        definition = f'''<bpmn2:endEvent id="{id}" name="{name}">
    <bpmn2:errorEventDefinition>
        <bpmn2:extensionElements>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::FlowstepVariant/cname::ErrorEndEvent</value>
            </ifl:property>
            <ifl:property>
                <key>activityType</key>
                <value>EndErrorEvent</value>
            </ifl:property>
        </bpmn2:extensionElements>
    </bpmn2:errorEventDefinition>
    {incoming_elements}
</bpmn2:endEvent>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="32.0" width="32.0" x="1158.0" y="142.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def process_call_template(self, id, name, incoming_flow, outgoing_flow, process_id="", sub_activity_type="NonLoopingProcess"):
        """Generate a Process Call template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>processId</key>
            <value>{process_id}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>ProcessCallElement</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::NonLoopingProcess/version::1.0.3</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>{sub_activity_type}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    # 22. Processing Components (Aggregation and EDI)
    def aggregator_template(self, id, name, incoming_flow, outgoing_flow, aggregation_algorithm="Combine",
                           completion_timeout="60", completion_condition="", completion_condition_type="XPath",
                           correlation_expression="", correlation_expression_type="XPath",
                           data_store_name="", include_exception_in_response="false",
                           last_message_condition="", last_message_condition_type="XPath"):
        """Generate an Aggregator template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>aggregationAlgorithm</key>
            <value>{aggregation_algorithm}</value>
        </ifl:property>
        <ifl:property>
            <key>completionTimeout</key>
            <value>{completion_timeout}</value>
        </ifl:property>
        <ifl:property>
            <key>completionCondition</key>
            <value>{completion_condition}</value>
        </ifl:property>
        <ifl:property>
            <key>completionConditionType</key>
            <value>{completion_condition_type}</value>
        </ifl:property>
        <ifl:property>
            <key>correlationExpression</key>
            <value>{correlation_expression}</value>
        </ifl:property>
        <ifl:property>
            <key>correlationExpressionType</key>
            <value>{correlation_expression_type}</value>
        </ifl:property>
        <ifl:property>
            <key>dataStoreName</key>
            <value>{data_store_name}</value>
        </ifl:property>
        <ifl:property>
            <key>includeExceptionInResponse</key>
            <value>{include_exception_in_response}</value>
        </ifl:property>
        <ifl:property>
            <key>lastMessageCondition</key>
            <value>{last_message_condition}</value>
        </ifl:property>
        <ifl:property>
            <key>lastMessageConditionType</key>
            <value>{last_message_condition_type}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.4</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Aggregator</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Aggregator/version::1.4.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def gather_template(self, id, name, incoming_flow, outgoing_flow, correlation_expression="",
                       correlation_expression_type="XPath", completion_timeout="60",
                       completion_condition="", completion_condition_type="XPath"):
        """Generate a Gather template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>correlationExpression</key>
            <value>{correlation_expression}</value>
        </ifl:property>
        <ifl:property>
            <key>correlationExpressionType</key>
            <value>{correlation_expression_type}</value>
        </ifl:property>
        <ifl:property>
            <key>completionTimeout</key>
            <value>{completion_timeout}</value>
        </ifl:property>
        <ifl:property>
            <key>completionCondition</key>
            <value>{completion_condition}</value>
        </ifl:property>
        <ifl:property>
            <key>completionConditionType</key>
            <value>{completion_condition_type}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>Gather</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::Gather/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def edi_extractor_template(self, id, name, incoming_flow, outgoing_flow, extract_type="EDI",
                              edifact_source_encoding="UTF-8", x12_source_encoding="UTF-8"):
        """Generate an EDI Extractor template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>extractType</key>
            <value>{extract_type}</value>
        </ifl:property>
        <ifl:property>
            <key>edifactSourceEncoding</key>
            <value>{edifact_source_encoding}</value>
        </ifl:property>
        <ifl:property>
            <key>x12SourceEncoding</key>
            <value>{x12_source_encoding}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>EDIExtractor</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::EDIExtractor/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def edi_validator_template(self, id, name, incoming_flow, outgoing_flow, validate_type="EDI",
                              edifact_source_encoding="UTF-8", x12_source_encoding="UTF-8",
                              prevent_exception="false"):
        """Generate an EDI Validator template."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>validateType</key>
            <value>{validate_type}</value>
        </ifl:property>
        <ifl:property>
            <key>edifactSourceEncoding</key>
            <value>{edifact_source_encoding}</value>
        </ifl:property>
        <ifl:property>
            <key>x12SourceEncoding</key>
            <value>{x12_source_encoding}</value>
        </ifl:property>
        <ifl:property>
            <key>preventException</key>
            <value>{prevent_exception}</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>EDIValidator</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::EDIValidator/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        shape = f'''<bpmndi:BPMNShape bpmnElement="{id}" id="BPMNShape_{id}">
    <dc:Bounds height="60.0" width="100.0" x="400.0" y="128.0"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}


class ComponentPositionManager:
    """Manages component positioning with consistent spacing and alignment."""

    def __init__(self):
        # Layout configuration
        self.start_x = 300
        self.start_y = 140
        self.component_spacing_x = 150
        self.component_spacing_y = 100
        self.lane_height = 200
        self.participant_y_offset = 341

        # Component dimensions
        self.component_dimensions = {
            "start_event": {"width": 32, "height": 32},
            "end_event": {"width": 32, "height": 32},
            "timer_start_event": {"width": 32, "height": 32},
            "error_end_event": {"width": 32, "height": 32},
            "activity": {"width": 100, "height": 60},
            "gateway": {"width": 40, "height": 40},
            "participant": {"width": 100, "height": 140}
        }

        # Track positions
        self.component_positions = {}
        self.current_x = self.start_x
        self.current_y = self.start_y
        self.current_lane = 0

    def get_component_type_dimensions(self, component_type):
        """Get dimensions for a component type."""
        if "event" in component_type.lower():
            return self.component_dimensions["start_event"]
        elif "gateway" in component_type.lower():
            return self.component_dimensions["gateway"]
        else:
            return self.component_dimensions["activity"]

    def calculate_position(self, component_id, component_type="activity", lane=0):
        """Calculate position for a component with proper spacing."""
        dimensions = self.get_component_type_dimensions(component_type)

        # Calculate position based on lane
        y_position = self.start_y + (lane * self.lane_height)

        # Adjust Y position for events (center them vertically)
        if "event" in component_type.lower():
            y_position += (self.component_dimensions["activity"]["height"] - dimensions["height"]) // 2
        elif "gateway" in component_type.lower():
            y_position += (self.component_dimensions["activity"]["height"] - dimensions["height"]) // 2

        position = {
            "x": self.current_x,
            "y": y_position,
            "width": dimensions["width"],
            "height": dimensions["height"]
        }

        # Store position
        self.component_positions[component_id] = position

        # Advance X position for next component
        self.current_x += self.component_spacing_x

        return position

    def calculate_participant_position(self, participant_id, component_x):
        """Calculate position for a participant based on its associated component."""
        position = {
            "x": component_x,
            "y": self.participant_y_offset,
            "width": self.component_dimensions["participant"]["width"],
            "height": self.component_dimensions["participant"]["height"]
        }

        self.component_positions[participant_id] = position
        return position

    def reset_x_position(self):
        """Reset X position to start for new lane."""
        self.current_x = self.start_x

    def move_to_next_lane(self):
        """Move to next lane and reset X position."""
        self.current_lane += 1
        self.reset_x_position()

    def get_position(self, component_id):
        """Get stored position for a component."""
        return self.component_positions.get(component_id, {
            "x": self.start_x,
            "y": self.start_y,
            "width": 100,
            "height": 60
        })

    def calculate_sequence_flow_waypoints(self, source_id, target_id):
        """Calculate waypoints for sequence flows between components."""
        source_pos = self.get_position(source_id)
        target_pos = self.get_position(target_id)

        # Calculate connection points
        if "event" in source_id.lower() and "start" in source_id.lower():
            # Start events connect from right edge
            source_x = source_pos['x'] + source_pos['width']
            source_y = source_pos['y'] + source_pos['height'] // 2
        elif "gateway" in source_id.lower():
            # Gateways connect from right edge
            source_x = source_pos['x'] + source_pos['width']
            source_y = source_pos['y'] + source_pos['height'] // 2
        else:
            # Activities connect from right edge
            source_x = source_pos['x'] + source_pos['width']
            source_y = source_pos['y'] + source_pos['height'] // 2

        if "event" in target_id.lower() and "end" in target_id.lower():
            # End events connect to left edge
            target_x = target_pos['x']
            target_y = target_pos['y'] + target_pos['height'] // 2
        elif "gateway" in target_id.lower():
            # Gateways connect to left edge
            target_x = target_pos['x']
            target_y = target_pos['y'] + target_pos['height'] // 2
        else:
            # Activities connect to left edge
            target_x = target_pos['x']
            target_y = target_pos['y'] + target_pos['height'] // 2

        return {
            "source_x": source_x,
            "source_y": source_y,
            "target_x": target_x,
            "target_y": target_y
        }


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
        self.position_manager = ComponentPositionManager()

    def update_shape_position(self, shape_xml, component_id):
        """Update shape XML with position from position manager."""
        position = self.position_manager.get_position(component_id)

        # Replace the hardcoded coordinates in the shape XML
        import re

        # Pattern to match dc:Bounds attributes
        bounds_pattern = r'<dc:Bounds\s+height="([^"]+)"\s+width="([^"]+)"\s+x="([^"]+)"\s+y="([^"]+)"/>'

        def replace_bounds(match):
            height = match.group(1)
            width = match.group(2)
            return f'<dc:Bounds height="{height}" width="{width}" x="{position["x"]}" y="{position["y"]}"/>'

        updated_shape = re.sub(bounds_pattern, replace_bounds, shape_xml)
        return updated_shape

    def update_edge_waypoints(self, edge_xml, waypoints):
        """Update edge XML with calculated waypoints."""
        import re

        # Pattern to match waypoint elements
        waypoint_pattern = r'<di:waypoint x="[^"]*" xsi:type="dc:Point" y="[^"]*"/>'

        # Create new waypoint elements
        new_waypoints = f'''<di:waypoint x="{waypoints['source_x']}" xsi:type="dc:Point" y="{waypoints['source_y']}"/>
    <di:waypoint x="{waypoints['target_x']}" xsi:type="dc:Point" y="{waypoints['target_y']}"/>'''

        # Replace all existing waypoints with new ones
        updated_edge = re.sub(waypoint_pattern, '', edge_xml)
        updated_edge = updated_edge.replace('</bpmndi:BPMNEdge>', f'    {new_waypoints}\n</bpmndi:BPMNEdge>')

        return updated_edge

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

        # Add start event with proper positioning
        start_position = self.position_manager.calculate_position("StartEvent_2", "start_event")
        start_event = self.templates.start_event_template()
        process_components.append(start_event["definition"])
        shapes.append(self.update_shape_position(start_event["shape"], "StartEvent_2"))

        # Calculate end event position (will be updated later based on flow length)
        end_position = {"x": 950, "y": 142, "width": 32, "height": 32}
        self.position_manager.component_positions["EndEvent_2"] = end_position
        end_event = self.templates.end_event_template()
        process_components.append(end_event["definition"])
        shapes.append(self.update_shape_position(end_event["shape"], "EndEvent_2"))

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

        # Calculate positions for components using the new position manager
        self.position_manager.reset_x_position()

        # Second pass: create components and connections
        for i, endpoint in enumerate(components.get("endpoints", [])):
            for j, component in enumerate(endpoint.get("components", [])):
                component_type = component.get("type", "").lower()
                component_id = component.get("id", f"{component_type}_{j}")
                component_name = component.get("name", f"{component_type}_{j}")

                # Calculate position using the position manager
                position = self.position_manager.calculate_position(component_id, component_type)
                self.component_positions[component_id] = position

                # Determine incoming and outgoing flows
                incoming_flow = f"SequenceFlow_{len(sequence_flows)}"
                outgoing_flow = f"SequenceFlow_{len(sequence_flows) + 1}"

                # Create the component based on its type
                if component_type in ["json_to_xml", "jsontoxml", "json_to_xml_converter"]:
                    # JSON to XML Converter
                    json_to_xml = self.templates.json_to_xml_template(
                        id=component_id,
                        name=component_name,
                        incoming_flow=incoming_flow,
                        outgoing_flow=outgoing_flow
                    )
                    process_components.append(json_to_xml["definition"])
                    shapes.append(self.update_shape_position(json_to_xml["shape"], component_id))

                elif component_type == "content_enricher" or component_type == "enricher":
                    # Content Enricher
                    content_enricher = self.templates.content_enricher_template(
                        id=component_id,
                        name=component_name,
                        incoming_flow=incoming_flow,
                        outgoing_flow=outgoing_flow
                    )
                    process_components.append(content_enricher["definition"])
                    shapes.append(self.update_shape_position(content_enricher["shape"], component_id))

                elif component_type == "request_reply":
                    # Request-Reply Service Task
                    request_reply = self.templates.request_reply_template(
                        id=component_id,
                        name=component_name,
                        incoming_flow=incoming_flow,
                        outgoing_flow=outgoing_flow
                    )
                    process_components.append(request_reply["definition"])
                    shapes.append(self.update_shape_position(request_reply["shape"], component_id))

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
                    shapes.append(self.update_shape_position(service_task["shape"], component_id))

                    # OData Receiver Participant - position below the service task
                    participant_id = f"Participant_OData_{component_id}"
                    participant_position = self.position_manager.calculate_participant_position(
                        participant_id, position["x"]
                    )
                    odata_participant = self.templates.odata_receiver_template(
                        id=participant_id,
                        name=f"OData_{component_name}"
                    )
                    participants.append(odata_participant["definition"])
                    shapes.append(self.update_shape_position(odata_participant["shape"], participant_id))

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
                    shapes.append(self.update_shape_position(gateway["shape"], component_id))

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
                    # Update edge with proper waypoints
                    waypoints = self.position_manager.calculate_sequence_flow_waypoints("StartEvent_2", component_id)
                    updated_edge = self.update_edge_waypoints(start_flow["edge"], waypoints)
                    edges.append(updated_edge)

                if j == len(endpoint.get("components", [])) - 1 and i == len(components.get("endpoints", [])) - 1:
                    # Last component connects to end event
                    end_flow = self.templates.sequence_flow_template(
                        id=outgoing_flow,
                        source_ref=component_id,
                        target_ref="EndEvent_2"
                    )
                    sequence_flows.append(end_flow["definition"])
                    # Update edge with proper waypoints
                    waypoints = self.position_manager.calculate_sequence_flow_waypoints(component_id, "EndEvent_2")
                    updated_edge = self.update_edge_waypoints(end_flow["edge"], waypoints)
                    edges.append(updated_edge)
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
                    # Update edge with proper waypoints
                    waypoints = self.position_manager.calculate_sequence_flow_waypoints(component_id, next_id)
                    updated_edge = self.update_edge_waypoints(next_flow["edge"], waypoints)
                    edges.append(updated_edge)

        # Update end event position based on the final component positions
        if component_ids:
            # Position end event after the last component
            last_component_position = self.position_manager.get_position(component_ids[-1])
            end_x = last_component_position["x"] + self.position_manager.component_spacing_x
            self.position_manager.component_positions["EndEvent_2"]["x"] = end_x

        # If no components were added, create a direct flow from start to end
        if not component_ids:
            direct_flow = self.templates.sequence_flow_template(
                id="SequenceFlow_Direct",
                source_ref="StartEvent_2",
                target_ref="EndEvent_2"
            )
            sequence_flows.append(direct_flow["definition"])
            # Update edge with proper waypoints
            waypoints = self.position_manager.calculate_sequence_flow_waypoints("StartEvent_2", "EndEvent_2")
            updated_edge = self.update_edge_waypoints(direct_flow["edge"], waypoints)
            edges.append(updated_edge)

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