import os

def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def build_requestreply_iflw() -> str:
    # Intentional EndpointRecevier spelling as per reference chunk
    # Process order: Start -> RequestReply -> End
    # Collaboration: IntegrationProcess participant + external receiver participant with HTTP messageFlow
    return (
        """<?xml version="1.0" encoding="UTF-8"?>"""
        + "<bpmn2:definitions xmlns:bpmn2=\"http://www.omg.org/spec/BPMN/20100524/MODEL\""
        + " xmlns:bpmndi=\"http://www.omg.org/spec/BPMN/20100524/DI\""
        + " xmlns:dc=\"http://www.omg.org/spec/DD/20100524/DC\""
        + " xmlns:di=\"http://www.omg.org/spec/DD/20100524/DI\""
        + " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""
        + " xmlns:ifl=\"http://com.sap.ifl.model/Ifl.xsd\" id=\"Definitions_ReqReply_1\">\n"
        + "    <bpmn2:collaboration id=\"Collaboration_ReqReply\" name=\"Default Collaboration\">\n"
        + "        <bpmn2:extensionElements>\n"
        + "            <ifl:property><key>cmdVariantUri</key><value>ctype::IFlowVariant/cname::IFlowConfiguration/version::1.2.4</value></ifl:property>\n"
        + "        </bpmn2:extensionElements>\n"
        + "        <bpmn2:participant id=\"Participant_Process_1\" ifl:type=\"IntegrationProcess\" name=\"Integration Process\" processRef=\"Process_ReqReply\">\n"
        + "            <bpmn2:extensionElements/>\n"
        + "        </bpmn2:participant>\n"
        + "        <bpmn2:participant id=\"Participant_Receiver_1\" ifl:type=\"EndpointRecevier\" name=\"Receiver1\">\n"
        + "            <bpmn2:extensionElements>\n"
        + "                <ifl:property><key>ifl:type</key><value>EndpointRecevier</value></ifl:property>\n"
        + "            </bpmn2:extensionElements>\n"
        + "        </bpmn2:participant>\n"
        + "        <bpmn2:messageFlow id=\"MessageFlow_HTTP_1\" name=\"HTTP\" sourceRef=\"ServiceTask_ReqReply\" targetRef=\"Participant_Receiver_1\">\n"
        + "            <bpmn2:extensionElements>\n"
        + "                <ifl:property><key>ComponentNS</key><value>sap</value></ifl:property>\n"
        + "                <ifl:property><key>httpMethod</key><value>POST</value></ifl:property>\n"
        + "                <ifl:property><key>Name</key><value>HTTP</value></ifl:property>\n"
        + "                <ifl:property><key>TransportProtocolVersion</key><value>1.17.0</value></ifl:property>\n"
        + "                <ifl:property><key>componentVersion</key><value>1.17</value></ifl:property>\n"
        + "                <ifl:property><key>TransportProtocol</key><value>HTTP</value></ifl:property>\n"
        + "                <ifl:property><key>cmdVariantUri</key><value>ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.17.0</value></ifl:property>\n"
        + "                <ifl:property><key>MessageProtocol</key><value>None</value></ifl:property>\n"
        + "                <ifl:property><key>MessageProtocolVersion</key><value>1.17.0</value></ifl:property>\n"
        + "            </bpmn2:extensionElements>\n"
        + "        </bpmn2:messageFlow>\n"
        + "    </bpmn2:collaboration>\n"
        + "    <bpmn2:process id=\"Process_ReqReply\" name=\"Integration Process\">\n"
        + "        <bpmn2:extensionElements>\n"
        + "            <ifl:property><key>transactionTimeout</key><value>30</value></ifl:property>\n"
        + "            <ifl:property><key>componentVersion</key><value>1.2</value></ifl:property>\n"
        + "            <ifl:property><key>cmdVariantUri</key><value>ctype::FlowElementVariant/cname::IntegrationProcess/version::1.2.1</value></ifl:property>\n"
        + "        </bpmn2:extensionElements>\n"
        + "        <bpmn2:startEvent id=\"StartEvent_1\" name=\"Start\">\n"
        + "            <bpmn2:extensionElements>\n"
        + "                <ifl:property><key>activityType</key><value>startEvent</value></ifl:property>\n"
        + "                <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageStartEvent</value></ifl:property>\n"
        + "                <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>\n"
        + "            </bpmn2:extensionElements>\n"
        + "            <bpmn2:messageEventDefinition/>\n"
        + "        </bpmn2:startEvent>\n"
        + "        <bpmn2:serviceTask id=\"ServiceTask_ReqReply\" name=\"Request Reply 1\">\n"
        + "            <bpmn2:extensionElements>\n"
        + "                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>\n"
        + "                <ifl:property><key>activityType</key><value>RequestReply</value></ifl:property>\n"
        + "                <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::RequestReply/version::1.0.0</value></ifl:property>\n"
        + "            </bpmn2:extensionElements>\n"
        + "        </bpmn2:serviceTask>\n"
        + "        <bpmn2:endEvent id=\"EndEvent_1\" name=\"End\">\n"
        + "            <bpmn2:extensionElements>\n"
        + "                <ifl:property><key>activityType</key><value>endEvent</value></ifl:property>\n"
        + "                <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value></ifl:property>\n"
        + "                <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>\n"
        + "            </bpmn2:extensionElements>\n"
        + "            <bpmn2:messageEventDefinition/>\n"
        + "        </bpmn2:endEvent>\n"
        + "        <bpmn2:sequenceFlow id=\"SequenceFlow_Start_to_ReqReply\" sourceRef=\"StartEvent_1\" targetRef=\"ServiceTask_ReqReply\"/>\n"
        + "        <bpmn2:sequenceFlow id=\"SequenceFlow_ReqReply_to_End\" sourceRef=\"ServiceTask_ReqReply\" targetRef=\"EndEvent_1\"/>\n"
        + "    </bpmn2:process>\n"
        + "    <bpmndi:BPMNDiagram id=\"BPMNDiagram_ReqReply\" name=\"Default Collaboration Diagram\">\n"
        + "        <bpmndi:BPMNPlane bpmnElement=\"Collaboration_ReqReply\" id=\"BPMNPlane_ReqReply\">\n"
        + "            <bpmndi:BPMNShape bpmnElement=\"ServiceTask_ReqReply\" id=\"BPMNShape_ServiceTask_ReqReply\">\n"
        + "                <dc:Bounds height=\"60.0\" width=\"100.0\" x=\"415.0\" y=\"200.0\"/>\n"
        + "            </bpmndi:BPMNShape>\n"
        + "            <bpmndi:BPMNShape bpmnElement=\"Participant_Process_1\" id=\"BPMNShape_Participant_Process_1\">\n"
        + "                <dc:Bounds height=\"225.0\" width=\"540.0\" x=\"250.0\" y=\"60.0\"/>\n"
        + "            </bpmndi:BPMNShape>\n"
        + "            <bpmndi:BPMNShape bpmnElement=\"Participant_Receiver_1\" id=\"BPMNShape_Participant_Receiver_1\">\n"
        + "                <dc:Bounds height=\"140.0\" width=\"100.0\" x=\"93.0\" y=\"297.0\"/>\n"
        + "            </bpmndi:BPMNShape>\n"
        + "            <bpmndi:BPMNShape bpmnElement=\"StartEvent_1\" id=\"BPMNShape_StartEvent_1\">\n"
        + "                <dc:Bounds height=\"32.0\" width=\"32.0\" x=\"299.0\" y=\"140.0\"/>\n"
        + "            </bpmndi:BPMNShape>\n"
        + "            <bpmndi:BPMNShape bpmnElement=\"EndEvent_1\" id=\"BPMNShape_EndEvent_1\">\n"
        + "                <dc:Bounds height=\"32.0\" width=\"32.0\" x=\"626.0\" y=\"140.0\"/>\n"
        + "            </bpmndi:BPMNShape>\n"
        + "            <bpmndi:BPMNEdge bpmnElement=\"SequenceFlow_Start_to_ReqReply\" id=\"BPMNEdge_SequenceFlow_Start_to_ReqReply\" sourceElement=\"BPMNShape_StartEvent_1\" targetElement=\"BPMNShape_ServiceTask_ReqReply\">\n"
        + "                <di:waypoint x=\"315.0\" xsi:type=\"dc:Point\" y=\"158.5\"/>\n"
        + "                <di:waypoint x=\"415.5\" xsi:type=\"dc:Point\" y=\"158.5\"/>\n"
        + "            </bpmndi:BPMNEdge>\n"
        + "            <bpmndi:BPMNEdge bpmnElement=\"SequenceFlow_ReqReply_to_End\" id=\"BPMNEdge_SequenceFlow_ReqReply_to_End\" sourceElement=\"BPMNShape_ServiceTask_ReqReply\" targetElement=\"BPMNShape_EndEvent_1\">\n"
        + "                <di:waypoint x=\"415.5\" xsi:type=\"dc:Point\" y=\"158.5\"/>\n"
        + "                <di:waypoint x=\"626.0\" xsi:type=\"dc:Point\" y=\"140.0\"/>\n"
        + "            </bpmndi:BPMNEdge>\n"
        + "            <bpmndi:BPMNEdge bpmnElement=\"MessageFlow_HTTP_1\" id=\"BPMNEdge_MessageFlow_HTTP_1\" sourceElement=\"BPMNShape_ServiceTask_ReqReply\" targetElement=\"BPMNShape_Participant_Receiver_1\">\n"
        + "                <di:waypoint x=\"465.0\" xsi:type=\"dc:Point\" y=\"230.0\"/>\n"
        + "                <di:waypoint x=\"143.0\" xsi:type=\"dc:Point\" y=\"367.0\"/>\n"
        + "            </bpmndi:BPMNEdge>\n"
        + "        </bpmndi:BPMNPlane>\n"
        + "    </bpmndi:BPMNDiagram>\n"
        + "</bpmn2:definitions>"
    )


def main() -> None:
    out_dir = os.path.join("generated_packages", "temp_requestreply")
    ensure_dir(out_dir)
    out_file = os.path.join(out_dir, "RequestReply_Test.iflw")
    xml = build_requestreply_iflw()
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Wrote: {out_file}")


if __name__ == "__main__":
    main()








