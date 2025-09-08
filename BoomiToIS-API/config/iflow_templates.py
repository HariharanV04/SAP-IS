"""
SAP CPI iFlow Component Templates and Validation Rules
Based on comprehensive SAP CPI generation instructions
"""

# Component Templates with mandatory properties and mappings
COMPONENT_TEMPLATES = {
    "content_modifier": {
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "bodyType", "value": "constant"},
            {"key": "componentVersion", "value": "1.5"},
            {"key": "activityType", "value": "Enricher"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::Enricher/version::1.5.0"}
        ],
        "config_mapping": {
            "content": "bodyContent",
            "body_type": "bodyType"
        }
    },
    
    "groovy_script": {
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.1"},
            {"key": "activityType", "value": "Script"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2"},
            {"key": "subActivityType", "value": "GroovyScript"}
        ],
        "config_mapping": {
            "script": "script"
        }
    },
    
    "script": {  # Alias for groovy_script
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.1"},
            {"key": "activityType", "value": "Script"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::GroovyScript/version::1.1.2"},
            {"key": "subActivityType", "value": "GroovyScript"}
        ],
        "config_mapping": {
            "script": "script"
        }
    },
    
    "router": {
        "element_type": "exclusiveGateway",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.1"},
            {"key": "activityType", "value": "ExclusiveGateway"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.1.2"},
            {"key": "throwException", "value": "false"}
        ],
        "mandatory_attributes": ["default"],
        "requires_incoming_outgoing": True
    },
    
    "request_reply": {
        "element_type": "serviceTask",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.0"},
            {"key": "activityType", "value": "ExternalCall"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4"}
        ],
        "config_mapping": {
            "url": "address",
            "method": "httpMethod"
        }
    },
    
    "filter": {
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "activityType", "value": "MessageFilter"},
            {"key": "componentVersion", "value": "1.0"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::MessageFilter/version::1.0.1"},
            {"key": "xpathExpression", "value": ""}
        ],
        "config_mapping": {
            "expression": "filterExpression"
        }
    },
    

    
    "local_integration_process": {
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "activityType", "value": "ProcessCallElement"},
            {"key": "componentVersion", "value": "1.0"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::NonLoopingProcess/version::1.0.3"},
            {"key": "subActivityType", "value": "NonLoopingProcess"}
        ],
        "mandatory_attributes": ["calledElement"],
        "config_mapping": {
            "process_id": "processId"
        }
    },
    
    "exception_subprocess": {
        "element_type": "subProcess",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.1"},
            {"key": "activityType", "value": "ErrorEventSubProcessTemplate"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::ErrorEventSubProcessTemplate/version::1.1.0"}
        ],
        "special_handling": "exception_subprocess"
    },
    
    "enricher": {
        "element_type": "serviceTask",
        "mandatory_properties": [
            {"key": "enrichmentType", "value": "xmlLookupAggregation"},
            {"key": "componentVersion", "value": "1.2"},
            {"key": "activityType", "value": "contentEnricherWithLookup"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::contentEnricherWithLookup/version::1.2.0"}
        ],
        "config_mapping": {
            "resource_path": "resourceMessageNodePath",
            "original_path": "originalMessageNodePath",
            "key_element": "originalMessageKeyElement",
            "lookup_key": "resourceMessageKeyElement"
        }
    },
    
    "json_to_xml_converter": {
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.3"},
            {"key": "activityType", "value": "Converter"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::Converter/version::1.3.0"},
            {"key": "converterType", "value": "JSON to XML Converter"}
        ]
    },
    
    "xml_to_json_converter": {
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.3"},
            {"key": "activityType", "value": "Converter"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::Converter/version::1.3.0"},
            {"key": "converterType", "value": "XML to JSON Converter"}
        ]
    },
    
    "message_mapping": {
        "element_type": "callActivity",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.3"},
            {"key": "activityType", "value": "MessageMapping"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::MessageMapping/version::1.3.0"}
        ],
        "config_mapping": {
            "mapping_name": "mappingname",
            "mapping_uri": "mappinguri"
        }
    },
    
    "send": {
        "element_type": "serviceTask",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.0"},
            {"key": "activityType", "value": "Send"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::Send/version::1.0.4"}
        ]
    }
}

# Event Templates
EVENT_TEMPLATES = {
    "start_event": {
        "element_type": "startEvent",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.0"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::MessageStartEvent/version::1.0"}
        ],
        "requires_event_definition": "messageEventDefinition"
    },
    
    "end_event": {
        "element_type": "endEvent",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.1"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0"}
        ],
        "requires_event_definition": "messageEventDefinition"
    },
    
    "timer_start_event": {
        "element_type": "startEvent",
        "mandatory_properties": [
            {"key": "componentVersion", "value": "1.2"},
            {"key": "activityType", "value": "StartTimerEvent"},
            {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::intermediatetimer"}
        ],
        "requires_event_definition": "timerEventDefinition",
        "config_mapping": {
            "schedule": "scheduleKey"
        }
    }
}

# Adapter Templates for Message Flows
ADAPTER_TEMPLATES = {
    "https_sender": {
        "direction": "Sender",
        "component_type": "HTTPS",
        "mandatory_properties": [
            {"key": "ComponentType", "value": "HTTPS"},
            {"key": "maximumBodySize", "value": "40"},
            {"key": "ComponentNS", "value": "sap"},
            {"key": "componentVersion", "value": "1.4"},
            {"key": "TransportProtocolVersion", "value": "1.4.1"},
            {"key": "xsrfProtection", "value": "false"},
            {"key": "TransportProtocol", "value": "HTTPS"},
            {"key": "cmdVariantUri", "value": "ctype::AdapterVariant/cname::sap:HTTPS/tp::HTTPS/mp::None/direction::Sender/version::1.4.1"},
            {"key": "userRole", "value": "ESBMessaging.send"},
            {"key": "senderAuthType", "value": "RoleBased"},
            {"key": "MessageProtocol", "value": "None"},
            {"key": "direction", "value": "Sender"}
        ],
        "config_mapping": {
            "url_path": "urlPath",
            "auth_type": "senderAuthType",
            "user_role": "userRole"
        }
    },
    
    "http_receiver": {
        "direction": "Receiver",
        "component_type": "HTTP",
        "mandatory_properties": [
            {"key": "ComponentNS", "value": "sap"},
            {"key": "ComponentType", "value": "HTTP"},
            {"key": "TransportProtocolVersion", "value": "1.16.2"},
            {"key": "httpRequestTimeout", "value": "60000"},
            {"key": "MessageProtocol", "value": "None"},
            {"key": "direction", "value": "Receiver"},
            {"key": "throwExceptionOnFailure", "value": "true"},
            {"key": "componentVersion", "value": "1.16"},
            {"key": "TransportProtocol", "value": "HTTP"},
            {"key": "cmdVariantUri", "value": "ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.16.2"}
        ],
        "config_mapping": {
            "url": "httpAddressWithoutQuery",
            "method": "httpMethod",
            "timeout": "httpRequestTimeout"
        }
    },
    
    "odata_receiver": {
        "direction": "Receiver",
        "component_type": "HCIOData",
        "mandatory_properties": [
            {"key": "ComponentNS", "value": "sap"},
            {"key": "ComponentType", "value": "HCIOData"},
            {"key": "TransportProtocolVersion", "value": "1.25.0"},
            {"key": "MessageProtocol", "value": "OData V2"},
            {"key": "direction", "value": "Receiver"},
            {"key": "componentVersion", "value": "1.25"},
            {"key": "TransportProtocol", "value": "HTTP"},
            {"key": "cmdVariantUri", "value": "ctype::AdapterVariant/cname::sap:HCIOData/tp::HTTP/mp::OData V2/direction::Receiver/version::1.25.0"}
        ],
        "config_mapping": {
            "service_url": "address",
            "entity_set": "resourcePath",
            "operation": "operation",
            "query_options": "queryOptions"
        }
    },
    
    "soap_receiver": {
        "direction": "Receiver",
        "component_type": "SOAP",
        "mandatory_properties": [
            {"key": "ComponentNS", "value": "sap"},
            {"key": "ComponentType", "value": "SOAP"},
            {"key": "TransportProtocolVersion", "value": "1.9.0"},
            {"key": "MessageProtocol", "value": "Plain SOAP"},
            {"key": "direction", "value": "Receiver"},
            {"key": "componentVersion", "value": "1.7"},
            {"key": "TransportProtocol", "value": "HTTP"},
            {"key": "cmdVariantUri", "value": "ctype::AdapterVariant/cname::sap:SOAP/tp::HTTP/mp::Plain SOAP/direction::Receiver/version::1.7.0"}
        ],
        "config_mapping": {
            "address": "address",
            "timeout": "requestTimeout",
            "credential": "credentialName"
        }
    },
    
    "successfactors_receiver": {
        "direction": "Receiver",
        "component_type": "SuccessFactors",
        "mandatory_properties": [
            {"key": "ComponentNS", "value": "sap"},
            {"key": "ComponentType", "value": "SuccessFactors"},
            {"key": "TransportProtocolVersion", "value": "1.21.0"},
            {"key": "MessageProtocol", "value": "OData V2"},
            {"key": "direction", "value": "Receiver"},
            {"key": "componentVersion", "value": "1.21"},
            {"key": "TransportProtocol", "value": "HTTP"},
            {"key": "cmdVariantUri", "value": "ctype::AdapterVariant/cname::sap:SuccessFactors/tp::HTTP/mp::OData V2/direction::Receiver/version::1.21.0"}
        ],
        "config_mapping": {
            "url": "address",
            "entity_set": "resourcePath",
            "operation": "operation",
            "credential": "alias"
        }
    }
}

# Validation Rules based on SAP CPI Instructions
VALIDATION_RULES = {
    "forbidden_connections": [
        {
            "source_pattern": "SubProcess_*",
            "target": "EndEvent_2",
            "error": "Exception subprocess cannot connect to main EndEvent_2 - must be self-contained"
        },
        {
            "source_type": "multicast",
            "multiple_outgoing": True,
            "error": "Multicast cannot have multiple outgoing sequence flows - use parallel gateways instead"
        },
        {
            "source": "participant",
            "target": "participant",
            "error": "Participants cannot connect directly to other participants"
        }
    ],
    
    "mandatory_elements": [
        {
            "element": "process",
            "attribute": "isExecutable",
            "value": "true",
            "error": "Process must have isExecutable='true'"
        },
        {
            "element": "collaboration",
            "required_properties": [
                "httpSessionHandling",
                "returnExceptionToSender", 
                "corsEnabled",
                "ServerTrace",
                "cmdVariantUri"
            ],
            "error": "Collaboration missing mandatory properties"
        }
    ],
    
    "mandatory_attributes": [
        {
            "element": "sequenceFlow",
            "attributes": ["id", "sourceRef", "targetRef", "isImmediate"],
            "error": "SequenceFlow must have id, sourceRef, targetRef, and isImmediate attributes"
        },
        {
            "element": "exclusiveGateway",
            "attributes": ["default"],
            "error": "ExclusiveGateway must have default attribute pointing to default route"
        }
    ],
    
    "flow_continuity": [
        {
            "rule": "every_component_except_start_has_incoming",
            "error": "Every component except StartEvent must have incoming sequence flow"
        },
        {
            "rule": "every_component_except_end_has_outgoing", 
            "error": "Every component except EndEvent must have outgoing sequence flow"
        },
        {
            "rule": "all_branches_end_at_main_end",
            "error": "All routing branches must end at EndEvent_2"
        }
    ]
}

# Mandatory Collaboration Properties
COLLABORATION_PROPERTIES = [
    {"key": "namespaceMapping", "value": ""},
    {"key": "httpSessionHandling", "value": "None"},
    {"key": "returnExceptionToSender", "value": "false"},
    {"key": "log", "value": "All events"},
    {"key": "corsEnabled", "value": "false"},
    {"key": "componentVersion", "value": "1.2"},
    {"key": "ServerTrace", "value": "false"},
    {"key": "cmdVariantUri", "value": "ctype::IFlowVariant/cname::IFlowConfiguration/version::1.2.4"}
]

# Mandatory Process Properties
PROCESS_PROPERTIES = [
    {"key": "transactionTimeout", "value": "30"},
    {"key": "componentVersion", "value": "1.2"},
    {"key": "cmdVariantUri", "value": "ctype::FlowElementVariant/cname::IntegrationProcess/version::1.2.1"},
    {"key": "transactionalHandling", "value": "Not Required"}
]

# SAP-Specific Constants
SAP_CONSTANTS = {
    "ENDPOINT_RECEIVER_TYPO": "EndpointRecevier",  # SAP's intentional typo
    "ENDPOINT_SENDER": "EndpointSender",
    "INTEGRATION_PROCESS": "IntegrationProcess"
}

# Router Flow Properties
ROUTER_FLOW_PROPERTIES = {
    "conditional": [
        {"key": "expressionType", "value": "NonXML"},
        {"key": "componentVersion", "value": "1.0"},
        {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0"}
    ],
    "default": [
        {"key": "expressionType", "value": "XML"},
        {"key": "componentVersion", "value": "1.0"},
        {"key": "cmdVariantUri", "value": "ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0"}
    ]
}

# Standard Positioning for Diagram Elements
DIAGRAM_POSITIONS = {
    "sender_participant": {"x": 100, "y": 100, "width": 100, "height": 140},
    "integration_process": {"x": 220, "y": 150, "width": 957, "height": 294},
    "start_event": {"x": 263, "y": 126, "width": 32, "height": 32},
    "end_event": {"x": 950, "y": 112, "width": 32, "height": 32},
    "activity": {"width": 100, "height": 60, "spacing": 120},
    "gateway": {"width": 40, "height": 40},
    "exception_subprocess": {"x": 348, "y": 136, "width": 400, "height": 140},
    "receiver_participant": {"x": 850, "y": 150, "width": 100, "height": 140}
}
