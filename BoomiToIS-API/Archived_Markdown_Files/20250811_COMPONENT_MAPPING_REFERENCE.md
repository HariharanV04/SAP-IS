# Boomi to SAP Integration Suite Component Mapping Reference

This document provides a comprehensive mapping between Dell Boomi components and their SAP Integration Suite equivalents, including all the newly added components in the bpmn_templates.py file.

## Core Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| Start Shape | Start Event (Message) | `start_event_template()` | Entry point for integration flow |
| Stop Shape | End Event (Message) | `end_event_template()` | Exit point for integration flow |
| HTTP Listener | HTTPS Adapter (Receiver) | `http_sender_participant_template()` | Receives HTTP requests |
| HTTP Request | Service Task + Adapter | `service_task_template()` | Makes HTTP requests |

## Mapping Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| Data Mapping | Message Mapping | `message_mapping_template()` | Field-to-field data transformation |
| XSLT Transform | XSLT Mapping | `xslt_mapping_template()` | XML transformation using XSLT |
| Operation Mapping | Operation Mapping | `operation_mapping_template()` | Complex mapping operations |

## Processing Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| Set Properties | Content Enricher | `content_enricher_template()` | Sets headers and properties |
| Content Enricher | Content Enricher (with lookup) | `content_enricher_template()` | Enriches message content |
| Filter | Filter | `filter_template()` | Filters message content using XPath |
| Groovy Script | Groovy Script | `groovy_script_template()` | Custom scripting logic |
| XML Modifier | XML Modifier | `xml_modifier_template()` | Modifies XML structure |
| Write Variables | Write Variables | `write_variables_template()` | Stores variables for later use |

## Gateway Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| Decision | Router (Exclusive Gateway) | `exclusive_gateway_template()` | Conditional routing |
| Parallel Processing | Sequential Multicast | `sequential_multicast_template()` | Sequential parallel processing |
| Parallel Processing | Parallel Multicast | `parallel_multicast_template()` | True parallel processing |
| Join | Join (Parallel Gateway) | `join_template()` | Joins parallel branches |
| Router | Router (Exclusive Gateway) | `router_template()` | Enhanced routing with conditions |

## Splitter Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| EDI Splitter | EDI Splitter | `edi_splitter_template()` | Splits EDI documents |
| IDoc Splitter | IDoc Splitter | `idoc_splitter_template()` | Splits SAP IDoc documents |
| General Splitter | General Splitter | `general_splitter_template()` | General purpose message splitting |

## Storage Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| Database Select | Select (DB Storage) | `select_template()` | Retrieves data from storage |
| Database Write | Write (DB Storage) | `write_template()` | Writes data to storage |
| Database Get | Get (DB Storage) | `get_template()` | Gets specific data by key |
| Persist | Persist | `persist_template()` | Persists message for later processing |
| ID Mapping | ID Mapping | `id_mapping_template()` | Maps IDs between systems |

## Converter Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| JSON to XML | JSON to XML Converter | `json_to_xml_template()` | Converts JSON to XML |
| XML to CSV | XML to CSV Converter | `xml_to_csv_template()` | Converts XML to CSV format |
| CSV to XML | CSV to XML Converter | `csv_to_xml_template()` | Converts CSV to XML format |
| XML to JSON | XML to JSON Converter | `xml_to_json_template()` | Converts XML to JSON |
| Base64 Encode | Base64 Encoder | `base64_encoder_template()` | Encodes content to Base64 |
| Base64 Decode | Base64 Decoder | `base64_decoder_template()` | Decodes Base64 content |

## Event Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| Timer/Scheduler | Timer Start Event | `timer_start_event_template()` | Scheduled process execution |
| Error End | Error End Event | `error_end_event_template()` | Error termination |
| Process Call | Process Call | `process_call_template()` | Calls another process |

## Processing Components (Advanced)

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| Aggregator | Aggregator | `aggregator_template()` | Aggregates multiple messages |
| Gather | Gather | `gather_template()` | Gathers related messages |
| EDI Extractor | EDI Extractor | `edi_extractor_template()` | Extracts data from EDI |
| EDI Validator | EDI Validator | `edi_validator_template()` | Validates EDI documents |

## Adapter Components

| Boomi Component | SAP Integration Suite Equivalent | Template Method | Notes |
|-----------------|----------------------------------|-----------------|-------|
| OData Connector | OData Adapter | `odata_receiver_template()` | Connects to OData services |
| SFTP Connector | SFTP Adapter | `sftp_receiver_participant_template()` | File transfer via SFTP |
| SuccessFactors Connector | SuccessFactors Adapter | `successfactors_receiver_template()` | Connects to SuccessFactors |
| Salesforce Connector | Salesforce Adapter | Custom implementation | Connects to Salesforce |

## Positioning and Layout

The new positioning system uses the `ComponentPositionManager` class to ensure proper alignment:

- **Start X Position**: 300
- **Start Y Position**: 140  
- **Component Spacing X**: 150
- **Component Spacing Y**: 100
- **Lane Height**: 200

### Component Dimensions

- **Events**: 32x32 pixels
- **Activities**: 100x60 pixels
- **Gateways**: 40x40 pixels
- **Participants**: 100x140 pixels

## Usage Guidelines

1. **Template Selection**: Choose the appropriate template method based on the Boomi component type
2. **Configuration**: Provide component-specific configuration parameters
3. **Positioning**: Use the `ComponentPositionManager` for consistent layout
4. **Connections**: Use `calculate_sequence_flow_waypoints()` for proper flow connections
5. **Validation**: Test generated iFlows in SAP Integration Suite

## Migration Best Practices

1. **Analyze Dependencies**: Map all component dependencies before migration
2. **Configuration Review**: Review all component configurations for SAP compatibility
3. **Testing Strategy**: Test each component type individually before full integration
4. **Error Handling**: Implement proper error handling using Exception Subprocess
5. **Performance**: Consider performance implications of component choices

## Notes

- All templates support dynamic positioning through the `ComponentPositionManager`
- Edge waypoints are automatically calculated for proper flow visualization
- Component shapes are updated dynamically based on calculated positions
- The system maintains backward compatibility with existing implementations
