#!/usr/bin/env python3
"""
Boomi Flow Documentation Generator

This module provides functionality to parse Boomi process XML files
and generate comprehensive documentation for migration to SAP Integration Suite.
"""

import os
import xml.etree.ElementTree as ET
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
# LLM Mermaid fixer available if needed
# from llm_mermaid_fixer import fix_documentation_with_llm

logger = logging.getLogger(__name__)

class BoomiFlowDocumentationGenerator:
    """Generator for Boomi process documentation"""
    
    def __init__(self):
        self.namespaces = {
            'bns': 'http://api.platform.boomi.com/',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        self.parsed_processes = []
        self.parsed_maps = []
        self.parsed_connectors = []
    
    def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Process a directory containing Boomi XML files
        
        Args:
            directory_path (str): Path to directory containing Boomi files
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Processing Boomi directory: {directory_path}")
            
            # Find and process all XML files
            xml_files = self._find_xml_files(directory_path)
            logger.info(f"Found {len(xml_files)} XML files to process")
            
            results = {
                'total_files': len(xml_files),
                'processed_files': 0,
                'processes': [],
                'maps': [],
                'connectors': [],
                'errors': []
            }
            
            for xml_file in xml_files:
                try:
                    result = self._process_xml_file(xml_file)
                    if result:
                        if result['type'] == 'process':
                            results['processes'].append(result)
                        elif result['type'] == 'map':
                            results['maps'].append(result)
                        elif result['type'] == 'connector':
                            results['connectors'].append(result)
                        
                        results['processed_files'] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing {xml_file}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            logger.info(f"Successfully processed {results['processed_files']} out of {results['total_files']} files")
            return results
            
        except Exception as e:
            logger.error(f"Error processing Boomi directory: {e}")
            raise
    
    def _find_xml_files(self, directory_path: str) -> List[str]:
        """Find all XML files in the directory"""
        xml_files = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith('.xml'):
                    xml_files.append(os.path.join(root, file))
        
        return xml_files

    def _split_xml_documents(self, content: str) -> List[str]:
        """Split content that may contain multiple XML documents"""
        import re

        # Find all XML declarations and split on them
        xml_pattern = r'<\?xml[^>]*\?>'
        parts = re.split(xml_pattern, content)

        # Remove empty parts and reconstruct XML documents
        xml_documents = []
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'

        for part in parts:
            part = part.strip()
            if part and part.startswith('<'):
                xml_documents.append(xml_declaration + part)

        # If no split occurred, return the original content
        if not xml_documents:
            xml_documents = [content.strip()]

        return xml_documents
    
    def _process_xml_file(self, xml_file_path: str) -> Optional[Dict[str, Any]]:
        """Process a single XML file"""
        try:
            with open(xml_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Handle multiple XML documents in one file (common in Boomi exports)
            xml_documents = self._split_xml_documents(content)

            results = []
            for xml_doc in xml_documents:
                try:
                    root = ET.fromstring(xml_doc)

                    # Determine the type of Boomi component
                    component_type = self._determine_component_type(root)

                    if component_type == 'process':
                        result = self._parse_process(root, xml_file_path)
                    elif component_type == 'map':
                        result = self._parse_map(root, xml_file_path)
                    elif component_type == 'connector':
                        result = self._parse_connector(root, xml_file_path)
                    else:
                        logger.warning(f"Unknown component type '{component_type}' in {xml_file_path}")
                        continue

                    if result:
                        results.append(result)

                except ET.ParseError as e:
                    logger.error(f"XML parsing error in document from {xml_file_path}: {e}")
                    continue

            # Return the first valid result (or combine them if needed)
            return results[0] if results else None

        except Exception as e:
            logger.error(f"Error processing XML file {xml_file_path}: {e}")
            return None
    
    def _determine_component_type(self, root: ET.Element) -> str:
        """Determine the type of Boomi component"""
        # Check the type attribute on the Component element first
        component_type = root.get('type', '')

        if component_type == 'process':
            return 'process'
        elif component_type == 'transform.map':
            return 'map'
        elif component_type in ['connector-action', 'connector']:
            return 'connector'

        # Fallback: check for nested elements in bns:object
        bns_object = root.find('.//{http://api.platform.boomi.com/}object')
        if bns_object is not None:
            # Check for process element
            if bns_object.find('process') is not None:
                return 'process'
            # Check for Map element
            elif bns_object.find('Map') is not None:
                return 'map'
            # Check for Operation element
            elif bns_object.find('Operation') is not None:
                return 'connector'

        # Additional fallback checks
        if root.find('.//process') is not None:
            return 'process'
        elif root.find('.//Map') is not None:
            return 'map'
        elif root.find('.//Operation') is not None:
            return 'connector'

        logger.warning(f"Unknown component type: {component_type}")
        return 'unknown'
    
    def _parse_process(self, root: ET.Element, file_path: str) -> Dict[str, Any]:
        """Parse a Boomi process component"""
        component_info = self._extract_component_info(root)

        # Look for process element in bns:object first
        bns_object = root.find('.//{http://api.platform.boomi.com/}object')
        process_elem = None

        if bns_object is not None:
            process_elem = bns_object.find('process')

        # Fallback to direct search
        if process_elem is None:
            process_elem = root.find('.//process')

        if process_elem is None:
            logger.warning(f"No process element found in {file_path}")
            return None
        
        shapes = self._extract_shapes(process_elem)
        connections = self._extract_connections(shapes)
        
        return {
            'type': 'process',
            'file_path': file_path,
            'component': component_info,
            'process': {
                'allow_simultaneous': process_elem.get('allowSimultaneous'),
                'enable_user_log': process_elem.get('enableUserLog'),
                'process_log_on_error_only': process_elem.get('processLogOnErrorOnly'),
                'workload': process_elem.get('workload'),
                'shapes': shapes,
                'connections': connections
            },
            'integration_patterns': self._identify_integration_patterns(root)
        }
    
    def _parse_map(self, root: ET.Element, file_path: str) -> Dict[str, Any]:
        """Enhanced parsing of Boomi map component with detailed field mappings and transformations"""
        component_info = self._extract_component_info(root)

        # Look for Map element in bns:object first
        bns_object = root.find('.//{http://api.platform.boomi.com/}object')
        map_elem = None

        if bns_object is not None:
            map_elem = bns_object.find('Map')

        # Fallback to direct search
        if map_elem is None:
            map_elem = root.find('.//Map')

        if map_elem is None:
            logger.warning(f"No Map element found in {file_path}")
            return None
        
        # Enhanced mapping extraction with full transformation details
        detailed_mappings = self._extract_detailed_mappings(map_elem)
        transformation_functions = self._extract_transformation_functions(map_elem)
        business_rules = self._extract_business_rules(map_elem)
        cache_operations = self._extract_cache_operations(map_elem)
        
        return {
            'type': 'map',
            'file_path': file_path,
            'component': component_info,
            'map': {
                'from_profile': map_elem.get('fromProfile'),
                'to_profile': map_elem.get('toProfile'),
                'detailed_mappings': detailed_mappings,
                'transformation_functions': transformation_functions,
                'business_rules': business_rules,
                'cache_operations': cache_operations,
                'legacy_mappings': self._extract_legacy_mappings(map_elem)  # Keep existing for backward compatibility
            }
        }
    
    def _parse_connector(self, root: ET.Element, file_path: str) -> Dict[str, Any]:
        """Parse a Boomi connector component"""
        component_info = self._extract_component_info(root)

        # Look for Operation element in bns:object first
        bns_object = root.find('.//{http://api.platform.boomi.com/}object')
        operation = None

        if bns_object is not None:
            operation = bns_object.find('Operation')

        # Fallback to direct search
        if operation is None:
            operation = root.find('.//Operation')

        if operation is None:
            logger.warning(f"No Operation element found in {file_path}")
            return None
        
        config = operation.find('Configuration')
        connector_info = {'type': 'generic'}
        
        if config is not None:
            # Extract Salesforce-specific configuration
            sf_action = config.find('SalesforceSendAction')
            if sf_action is not None:
                connector_info = {
                    'type': 'salesforce',
                    'object_action': sf_action.get('objectAction'),
                    'object_name': sf_action.get('objectName'),
                    'batch_size': sf_action.get('batchSize'),
                    'use_bulk_api': sf_action.get('useBulkAPI') == 'true'
                }
        
        return {
            'type': 'connector',
            'file_path': file_path,
            'component': component_info,
            'connector': connector_info
        }
    
    def _extract_component_info(self, root: ET.Element) -> Dict[str, Any]:
        """Enhanced extraction with comprehensive configuration capture"""
        component_info = {
            'id': root.get('componentId'),
            'name': root.get('name'),
            'type': root.get('type'),
            'version': root.get('version'),
            'created_by': root.get('createdBy'),
            'created_date': root.get('createdDate'),
            'modified_by': root.get('modifiedBy'),
            'modified_date': root.get('modifiedDate'),
            'folder_path': root.get('folderFullPath'),
            'description': self._get_description(root)
        }
        
        # ALWAYS extract these regardless of type - CRITICAL FOR COMPLETENESS
        self._extract_process_properties(root, component_info)
        self._extract_connection_settings(root, component_info)
        self._extract_security_config(root, component_info)
        
        return component_info
    
    def _extract_shapes(self, process_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract shape information from process"""
        shapes = []

        # Look for shapes container first
        shapes_container = process_elem.find('shapes')
        if shapes_container is not None:
            shape_elements = shapes_container.findall('shape')
        else:
            # Fallback to direct search
            shape_elements = process_elem.findall('shape')
            if not shape_elements:
                shape_elements = process_elem.findall('.//shape')

        for shape in shape_elements:
            shape_info = {
                'name': shape.get('name'),
                'type': shape.get('shapetype'),
                'image': shape.get('image'),
                'user_label': shape.get('userlabel'),
                'position': {
                    'x': float(shape.get('x', 0)),
                    'y': float(shape.get('y', 0))
                },
                'configuration': self._extract_shape_configuration(shape)
            }
            
            # Enhanced process flow analysis
            self._enhance_shape_with_business_logic(shape, shape_info)
            
            # Extract drag points (connections)
            dragpoints = []
            # Look for dragpoints container first
            dragpoints_container = shape.find('dragpoints')
            if dragpoints_container is not None:
                dragpoint_elements = dragpoints_container.findall('dragpoint')
            else:
                # Fallback to direct search
                dragpoint_elements = shape.findall('dragpoint')
                if not dragpoint_elements:
                    dragpoint_elements = shape.findall('.//dragpoint')

            for dragpoint in dragpoint_elements:
                dragpoints.append({
                    'name': dragpoint.get('name'),
                    'to_shape': dragpoint.get('toShape'),
                    'position': {
                        'x': float(dragpoint.get('x', 0)),
                        'y': float(dragpoint.get('y', 0))
                    }
                })
            shape_info['dragpoints'] = dragpoints
            
            shapes.append(shape_info)
        
        return shapes
    
    def _extract_shape_configuration(self, shape: ET.Element) -> Dict[str, Any]:
        """Extract configuration from a shape"""
        config = {}
        config_elem = shape.find('configuration')
        
        if config_elem is not None:
            # Extract connector actions
            connector_action = config_elem.find('connectoraction')
            if connector_action is not None:
                config['connector_action'] = {
                    'action_type': connector_action.get('actionType'),
                    'connector_type': connector_action.get('connectorType'),
                    'connection_id': connector_action.get('connectionId'),
                    'operation_id': connector_action.get('operationId')
                }
            
            # Extract map configuration
            map_elem = config_elem.find('map')
            if map_elem is not None:
                config['map'] = {
                    'map_id': map_elem.get('mapId')
                }
            
            # Extract document properties
            doc_props = config_elem.find('documentproperties')
            if doc_props is not None:
                config['document_properties'] = self._extract_document_properties(doc_props)
        
        return config
    
    def _extract_document_properties(self, doc_props: ET.Element) -> List[Dict[str, Any]]:
        """Extract document properties configuration"""
        properties = []
        
        for prop in doc_props.findall('documentproperty'):
            prop_info = {
                'name': prop.get('name'),
                'property_id': prop.get('propertyId'),
                'default_value': prop.get('defaultValue'),
                'persist': prop.get('persist') == 'true',
                'is_dynamic_credential': prop.get('isDynamicCredential') == 'true'
            }
            properties.append(prop_info)
        
        return properties
    
    def _extract_connections(self, shapes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract connections between shapes"""
        connections = []
        
        for shape in shapes:
            for dragpoint in shape.get('dragpoints', []):
                if dragpoint.get('to_shape'):
                    connections.append({
                        'from_shape': shape['name'],
                        'to_shape': dragpoint['to_shape'],
                        'from_position': dragpoint['position'],
                        'connection_type': 'flow'
                    })
        
        return connections
    
    def _identify_integration_patterns(self, root: ET.Element) -> List[str]:
        """Identify common integration patterns in the Boomi process"""
        patterns = []
        
        # Check for common patterns based on component types and configurations
        if root.find('.//connectoraction[@actionType="Listen"]') is not None:
            patterns.append('event_listener')
        
        if root.find('.//connectoraction[@actionType="Send"]') is not None:
            patterns.append('data_sender')
        
        if root.find('.//Map') is not None:
            patterns.append('data_transformation')
        
        if root.find('.//documentproperties') is not None:
            patterns.append('dynamic_properties')
        
        if root.find('.//SalesforceSendAction') is not None:
            patterns.append('salesforce_integration')
        
        return patterns
    
    def _extract_process_properties(self, root: ET.Element, component_info: Dict[str, Any]):
        """Extract process property configurations - CRITICAL FOR BUSINESS LOGIC"""
        
        process_props = []
        
        # Extract OverrideableDefinedProcessPropertyValue elements
        for prop_override in root.findall('.//OverrideableDefinedProcessPropertyValue'):
            prop_info = {
                'property_key': prop_override.get('key', ''),
                'property_name': prop_override.get('name', ''),
                'overrideable': prop_override.get('overrideable', ''),
                'description': self._extract_property_description(prop_override.get('name', ''))
            }
            process_props.append(prop_info)
        
        # Extract definedprocessparameter elements from shapes and operations
        for param in root.findall('.//definedprocessparameter'):
            if param.get('propertyLabel'):
                prop_info = {
                    'property_key': param.get('propertyKey', ''),
                    'property_name': param.get('propertyLabel', ''),
                    'component_name': param.get('componentName', ''),
                    'description': self._extract_property_description(param.get('propertyLabel', ''))
                }
                process_props.append(prop_info)
        
        if process_props:
            component_info['process_properties'] = process_props
        
        return component_info

    def _extract_property_description(self, name: str) -> str:
        """Map property names to business descriptions"""
        property_descriptions = {
            'Filter_LSRD': 'Filter for Last Successful Run Date - controls delta vs full extraction',
            'Filter_company_territory_code': 'Territory code filter for geographical data filtering',
            'Filter_LegalEntity': 'Legal entity filter for organizational data separation',
            'Filter_EmployeeClass': 'Employee class filter for role-based data extraction',
            'Filter_GPID': 'Global Person ID filter for employee identification',
            'SendFilesToPepsoSFTP': 'Controls whether files are archived to PepsiCo SFTP',
            'NAVEXSFTPDirectory': 'Target directory path for NAVEX SFTP delivery',
            'fromEmailAddressForErrors': 'Source email address for error notifications',
            'toEmailAddressForErrors': 'Destination email address for error notifications',
            'fromEmailAddressForSuccess': 'Source email address for success notifications',
            'toEmailAddressForSuccess': 'Destination email address for success notifications',
            'Archive path on SFTP server': 'Path for archiving processed files on SFTP server',
            'Employee Status': 'Filter for employee status (Active, Terminated, etc.)',
            'Send Output To Vendor ?': 'Controls whether output files are sent to external vendor',
            'FileType': 'Type of file processing (Delta, Full, etc.)',
            'Encrypt Archive File': 'Controls PGP encryption of archived files',
            'Full File Start Date': 'Start date for full file extraction mode'
        }
        return property_descriptions.get(name, f'Process property: {name}')
    
    def _extract_connection_settings(self, root: ET.Element, component_info: Dict[str, Any]):
        """Extract connection configurations - CRITICAL FOR DEPLOYMENT"""
        
        connections = {}
        
        # Extract SFTP Settings
        for sftp_settings in root.findall('.//SFTPSettings'):
            auth_settings = sftp_settings.find('.//AuthSettings')
            connections['sftp'] = {
                'host': sftp_settings.get('host', ''),
                'port': sftp_settings.get('port', ''),
                'auth_user': auth_settings.get('user', '') if auth_settings is not None else '',
                'connection_type': 'SFTP',
                'security': 'SSH Key Authentication',
                'description': f"SFTP connection to {sftp_settings.get('host', 'Unknown Host')}"
            }
        
        # Extract Mail Settings  
        for mail_settings in root.findall('.//MailSettings'):
            connections['mail'] = {
                'host': mail_settings.get('host', ''),
                'port': mail_settings.get('port', ''),
                'use_ssl': mail_settings.get('usessl', ''),
                'use_smtp_auth': mail_settings.get('usesmtpauth', ''),
                'use_tls': mail_settings.get('usetls', ''),
                'connection_type': 'SMTP',
                'description': f"Mail server connection to {mail_settings.get('host', 'Unknown Host')}"
            }
        
        if connections:
            component_info['connections'] = connections
        
        return component_info
    
    def _extract_security_config(self, root: ET.Element, component_info: Dict[str, Any]):
        """Extract security configurations - CRITICAL FOR SECURITY"""
        
        security = {}
        
        # Extract PGP configurations
        for pgp_process in root.findall('.//dataprocesspgpencrypt'):
            pgp_info = {
                'encrypt_alias': pgp_process.get('encryptalias', ''),
                'clear_sign': pgp_process.get('clearSign', ''),
                'queue_security': pgp_process.get('queuesecurity', ''),
                'purpose': 'PGP encryption for sensitive data protection'
            }
            security['pgp_encryption'] = pgp_info
        
        # Extract PGP Override configurations
        pgp_keys = []
        for pgp_override in root.findall('.//PGPOverride'):
            pgp_key_info = {
                'key_id': pgp_override.get('id', ''),
                'key_name': pgp_override.get('name', ''),
                'overrideable': pgp_override.get('overrideable', ''),
                'purpose': self._infer_pgp_key_purpose(pgp_override.get('name', ''))
            }
            pgp_keys.append(pgp_key_info)
        
        if pgp_keys:
            security['pgp_keys'] = pgp_keys
        
        if security:
            component_info['security_config'] = security
        
        return component_info

    def _infer_pgp_key_purpose(self, key_name: str) -> str:
        """Map PGP key names to their purposes"""
        key_purposes = {
            'PGP Public Key- EC-372 NAVEX': 'NAVEX vendor encryption key for secure file delivery',
            'SF Integrations - Pepsi (QA Pub Key)': 'PepsiCo internal encryption key for QA environment'
        }
        return key_purposes.get(key_name, f'PGP encryption key: {key_name}')
    
    def _enhance_shape_with_business_logic(self, shape: ET.Element, shape_info: Dict[str, Any]):
        """Enhance shape information with business logic analysis"""
        
        shape_type = shape_info.get('type', '')
        
        # Extract decision logic
        if shape_type == 'decision':
            decision = shape.find('.//decision')
            if decision is not None:
                shape_info['decision'] = {
                    'comparison': decision.get('comparison', ''),
                    'name': decision.get('name', ''),
                    'business_purpose': self._infer_decision_purpose(decision.get('name', ''))
                }
        
        # Extract document properties with enhanced analysis
        elif shape_type == 'documentproperties':
            doc_props = []
            for prop in shape.findall('.//documentproperty'):
                doc_props.append({
                    'name': prop.get('name', ''),
                    'property_id': prop.get('propertyId', ''),
                    'persist': prop.get('persist', ''),
                    'trading_partner': prop.get('isTradingPartner', ''),
                    'default_value': prop.get('defaultValue', ''),
                    'business_purpose': self._extract_property_description(prop.get('name', ''))
                })
            if doc_props:
                shape_info['document_properties'] = doc_props
        
        # Extract branch information
        elif shape_type == 'branch':
            branch_config = shape.find('.//branch')
            if branch_config is not None:
                shape_info['branch'] = {
                    'num_branches': branch_config.get('numBranches', ''),
                    'purpose': f"Parallel processing with {branch_config.get('numBranches', 'unknown')} branches"
                }

    def _infer_decision_purpose(self, decision_name: str) -> str:
        """Map decision names to business purposes"""
        decision_purposes = {
            'Delta Run?': 'Determines extraction type - incremental vs full data pull',
            'Filter LSRD is NULL': 'Validates last successful run date for delta processing',
            'Archive file to SFTP ?': 'Controls file archiving to internal SFTP repository',
            'Send Output To Vendor ?': 'Controls whether files are delivered to external vendor'
        }
        return decision_purposes.get(decision_name, f'Business decision: {decision_name}')
    
    def _get_description(self, root: ET.Element) -> str:
        """Extract description from component"""
        # Try with namespace first
        desc_elem = root.find('.//{http://api.platform.boomi.com/}description')
        if desc_elem is not None:
            return desc_elem.text or ""

        # Fallback to direct search
        desc_elem = root.find('.//description')
        return desc_elem.text if desc_elem is not None else ""
    
    def generate_documentation(self, processing_results: Dict[str, Any]) -> str:
        """Enhanced markdown generation with comprehensive technical details"""
        doc_lines = []
        
        # Header
        doc_lines.append("# Boomi Integration Documentation")
        doc_lines.append("")
        doc_lines.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc_lines.append("")
        
        # Summary with enhanced metrics
        doc_lines.append("## Summary")
        doc_lines.append("")
        doc_lines.append(f"- **Total Files Processed:** {processing_results['processed_files']}")
        doc_lines.append(f"- **Processes:** {len(processing_results['processes'])}")
        doc_lines.append(f"- **Maps:** {len(processing_results['maps'])}")
        doc_lines.append(f"- **Connectors:** {len(processing_results['connectors'])}")
        if processing_results['errors']:
            doc_lines.append(f"- **Errors:** {len(processing_results['errors'])}")
        doc_lines.append("")
        
        # NEW: Add Process Properties Configuration section
        all_process_props = []
        all_connections = {}
        all_security = {}
        
        for result_list in [processing_results['processes'], processing_results['maps'], processing_results['connectors']]:
            for item in result_list:
                component = item.get('component', {})
                if component.get('process_properties'):
                    all_process_props.extend(component['process_properties'])
                if component.get('connections'):
                    for conn_type, conn_info in component['connections'].items():
                        all_connections[f"{conn_type}_{component.get('name', 'unknown')}"] = conn_info
                if component.get('security_config'):
                    all_security[component.get('name', 'unknown')] = component['security_config']
        
        if all_process_props:
            doc_lines.append("## Environment Configuration")
            doc_lines.append("")
            
            # Separate properties by category
            process_props = []
            email_props = []
            security_props = []
            deployment_props = []
            
            unique_props = {prop['property_name']: prop for prop in all_process_props}.values()
            
            for prop in unique_props:
                prop_name = prop['property_name'].lower()
                if 'email' in prop_name or 'from' in prop_name or 'to' in prop_name:
                    email_props.append(prop)
                elif 'pgp' in prop_name or 'encrypt' in prop_name or 'key' in prop_name:
                    security_props.append(prop)
                elif 'sftp' in prop_name or 'directory' in prop_name or 'vendor' in prop_name:
                    deployment_props.append(prop)
                else:
                    process_props.append(prop)
            
            # Process Properties Configuration
            if process_props:
                doc_lines.append("### Process Properties Configuration")
                doc_lines.append("")
                
                for prop in sorted(process_props, key=lambda x: x['property_name']):
                    prop_key = prop.get('property_key', 'N/A')
                    description = prop.get('description', 'Configuration property')
                    doc_lines.append(f"- **{prop['property_name']}**")
                    doc_lines.append(f"  - UUID: `{prop_key}`")
                    doc_lines.append(f"  - Description: {description}")
                    doc_lines.append("")
            
            # Email Notification Configuration
            if email_props:
                doc_lines.append("### Email Notification Configuration")
                doc_lines.append("")
                
                for prop in sorted(email_props, key=lambda x: x['property_name']):
                    prop_key = prop.get('property_key', 'N/A')
                    description = prop.get('description', 'Email configuration')
                    doc_lines.append(f"- **{prop['property_name']}**")
                    doc_lines.append(f"  - UUID: `{prop_key}`")
                    doc_lines.append(f"  - Purpose: {description}")
                    doc_lines.append("")
            
            # Deployment Configuration
            if deployment_props:
                doc_lines.append("### Deployment Configuration")
                doc_lines.append("")
                
                for prop in sorted(deployment_props, key=lambda x: x['property_name']):
                    prop_key = prop.get('property_key', 'N/A')
                    description = prop.get('description', 'Deployment configuration')
                    doc_lines.append(f"- **{prop['property_name']}**")
                    doc_lines.append(f"  - UUID: `{prop_key}`")
                    doc_lines.append(f"  - Purpose: {description}")
                    doc_lines.append("")
            
            # External System Dependencies
            doc_lines.append("### External System Dependencies")
            doc_lines.append("")
            doc_lines.append("- **SuccessFactors Employee Central**")
            doc_lines.append("  - Purpose: Primary data source")
            doc_lines.append("  - Requirements: System connection and authentication")
            doc_lines.append("")
            doc_lines.append("- **NAVEX Vendor SFTP Server**")
            doc_lines.append("  - Purpose: External delivery destination")
            doc_lines.append("  - Requirements: Network connectivity and SSH authentication")
            doc_lines.append("")
            doc_lines.append("- **PepsiCo Internal SFTP Server**")
            doc_lines.append("  - Purpose: Archive destination")
            doc_lines.append("  - Requirements: Internal network access")
            doc_lines.append("")
            doc_lines.append("- **Corporate SMTP Server**")
            doc_lines.append("  - Purpose: Email notification delivery")
            doc_lines.append("  - Requirements: Mail server connectivity")
            doc_lines.append("")
            
            # Runtime Resource Requirements
            doc_lines.append("### Runtime Resource Requirements")
            doc_lines.append("")
            doc_lines.append("- **Memory**")
            doc_lines.append("  - Requirement: Minimum 2GB")
            doc_lines.append("  - Details: Large employee dataset processing")
            doc_lines.append("")
            doc_lines.append("- **CPU**")
            doc_lines.append("  - Requirement: Multi-core")
            doc_lines.append("  - Details: Parallel execution paths")
            doc_lines.append("")
            doc_lines.append("- **Network**")
            doc_lines.append("  - Requirement: High reliability")
            doc_lines.append("  - Details: SuccessFactors cloud and SFTP endpoints")
            doc_lines.append("")
            doc_lines.append("- **Storage**")
            doc_lines.append("  - Requirement: Temporary space")
            doc_lines.append("  - Details: File generation and PGP encryption operations")
            doc_lines.append("")
            
            # Deployment Considerations
            doc_lines.append("### Deployment Considerations")
            doc_lines.append("")
            doc_lines.append("- **Scheduling**")
            doc_lines.append("  - Timing: Off-hours execution recommended")
            doc_lines.append("  - Reason: Minimizes SuccessFactors system impact")
            doc_lines.append("")
            doc_lines.append("- **Error Handling**")
            doc_lines.append("  - Approach: Comprehensive exception management")
            doc_lines.append("  - Features: Detailed logging and notification")
            doc_lines.append("")
            doc_lines.append("- **Monitoring**")
            doc_lines.append("  - Tracking: Process execution metrics")
            doc_lines.append("  - Metrics: Success/failure rates and audit trail")
            doc_lines.append("")
            doc_lines.append("- **Backup**")
            doc_lines.append("  - Policy: Archive file retention")
            doc_lines.append("  - Purpose: Regulatory compliance and audit requirements")
            doc_lines.append("")
        
        # Key Processing Steps section
        doc_lines.append("## Key Processing Steps")
        doc_lines.append("")
        doc_lines.append("The integration follows a structured approach to employee data synchronization:")
        doc_lines.append("")
        
        doc_lines.append("### 1. Process Initialization")
        doc_lines.append("- **Error Reporting Setup**: Initialize comprehensive error tracking across all component types")
        doc_lines.append("- **Property Validation**: Verify all required process properties are configured")
        doc_lines.append("- **Connection Testing**: Validate connectivity to SuccessFactors and SFTP endpoints")
        doc_lines.append("")
        
        doc_lines.append("### 2. Data Extraction Phase")
        doc_lines.append("- **Filter Construction**: Build dynamic WHERE clauses based on multiple filter criteria")
        doc_lines.append("- **Reference Data Loading**: Retrieve picklist values for data enrichment")
        doc_lines.append("- **Employee Data Query**: Execute SuccessFactors queries with constructed filters")
        doc_lines.append("")
        
        doc_lines.append("### 3. Data Transformation Phase")
        doc_lines.append("- **Field Mapping**: Apply SuccessFactors to NAVEX field mappings")
        doc_lines.append("- **Data Enrichment**: Enhance records with picklist lookups and manager information")
        doc_lines.append("- **Format Standardization**: Convert dates, format strings, and validate data types")
        doc_lines.append("")
        
        doc_lines.append("### 4. Output Generation")
        doc_lines.append("- **CSV Creation**: Generate formatted output files with proper field separation")
        doc_lines.append("- **PGP Encryption**: Secure files using configured encryption keys")
        doc_lines.append("- **File Validation**: Verify output integrity and completeness")
        doc_lines.append("")
        
        doc_lines.append("### 5. Delivery and Notification")
        doc_lines.append("- **Vendor Delivery**: Send encrypted files to NAVEX SFTP server")
        doc_lines.append("- **Internal Archiving**: Store processed files in PepsiCo SFTP repository")
        doc_lines.append("- **Status Reporting**: Send email notifications with execution results")
        doc_lines.append("")
        
        # Data Transformation Steps section
        doc_lines.append("## Data Transformation Steps")
        doc_lines.append("")
        doc_lines.append("Comprehensive data transformation logic applied during processing:")
        doc_lines.append("")
        
        doc_lines.append("### Field Mapping and Conversion")
        doc_lines.append("- **Direct Field Mapping**: SuccessFactors fields mapped to NAVEX format with data type conversion")
        doc_lines.append("- **Picklist Lookups**: Status and class code translations using cached reference data")
        doc_lines.append("- **Manager Resolution**: Manager name lookup based on manager ID for organizational hierarchy")
        doc_lines.append("")
        
        doc_lines.append("### Data Formatting and Validation")
        doc_lines.append("- **Date Standardization**: Convert all dates to YYYY-MM-DD format for NAVEX compatibility")
        doc_lines.append("- **Email Processing**: Validate and format email addresses for notification delivery")
        doc_lines.append("- **Country Code Translation**: Map territory codes to standardized country names")
        doc_lines.append("")
        
        doc_lines.append("### String Processing and Business Logic")
        doc_lines.append("- **ID Suffix Removal**: Strip global assignment identifiers for NAVEX processing")
        doc_lines.append("- **Termination Reason Processing**: Apply business rules for termination reason derivation")
        doc_lines.append("- **Data Validation**: Ensure required fields are populated and valid")
        doc_lines.append("")
        
        # Security and Deployment section
        doc_lines.append("## Security and Deployment")
        doc_lines.append("")
        
        doc_lines.append("### Security Requirements")
        doc_lines.append("- **Data Encryption**: PGP encryption for all external file transfers")
        doc_lines.append("- **Connection Security**: TLS/SSH for all external communications")
        doc_lines.append("- **Authentication**: Strong authentication for all system connections")
        doc_lines.append("- **Access Control**: Role-based access for process configuration")
        doc_lines.append("- **Audit Logging**: Comprehensive logging for compliance requirements")
        doc_lines.append("")
        
        doc_lines.append("### Deployment Configuration")
        doc_lines.append("- **Runtime Environment**: SAP Integration Suite Cloud or On-Premise")
        doc_lines.append("- **Memory Requirements**: Minimum 4GB for large employee datasets")
        doc_lines.append("- **CPU Requirements**: Multi-core processing for parallel execution")
        doc_lines.append("- **Network Requirements**: Reliable connectivity to SuccessFactors cloud and SFTP endpoints")
        doc_lines.append("- **Storage Requirements**: Temporary space for file generation and encryption operations")
        doc_lines.append("")
        
        doc_lines.append("### Monitoring and Alerting")
        doc_lines.append("- **Process Monitoring**: Real-time monitoring of integration execution")
        doc_lines.append("- **Error Alerting**: Immediate notification of critical failures")
        doc_lines.append("- **Performance Metrics**: Execution time and throughput tracking")
        doc_lines.append("- **Audit Reporting**: Detailed logs for compliance and troubleshooting")
        doc_lines.append("")
        
        # Connection Configurations section
        if all_connections:
            doc_lines.append("## Connection Configurations")
            doc_lines.append("")
            doc_lines.append("External system connections and endpoints:")
            doc_lines.append("")
            
            for conn_key, conn_info in all_connections.items():
                conn_type = conn_info.get('connection_type', 'Unknown')
                doc_lines.append(f"### {conn_type} Connection")
                doc_lines.append(f"- **Host**: `{conn_info.get('host', 'N/A')}`")
                doc_lines.append(f"- **Port**: `{conn_info.get('port', 'N/A')}`")
                if conn_info.get('auth_user'):
                    doc_lines.append(f"- **Username**: `{conn_info['auth_user']}`")
                if conn_info.get('security'):
                    doc_lines.append(f"- **Security**: {conn_info['security']}")
                if conn_info.get('description'):
                    doc_lines.append(f"- **Description**: {conn_info['description']}")
                doc_lines.append("")
        
            # Security and Encryption section
            if all_security or security_props:
                doc_lines.append("### Security and Encryption")
                doc_lines.append("")
                
                # Handle security properties from process properties
                if security_props:
                    for prop in sorted(security_props, key=lambda x: x['property_name']):
                        doc_lines.append(f"- **{prop['property_name']}**")
                        doc_lines.append(f"  - Purpose: {prop.get('description', 'Security configuration')}")
                        if prop.get('property_key'):
                            doc_lines.append(f"  - UUID: `{prop['property_key']}`")
                        doc_lines.append("")
                
                # Handle detailed security configurations
                for comp_name, security in all_security.items():
                    if security.get('pgp_encryption'):
                        pgp = security['pgp_encryption']
                        doc_lines.append(f"- **PGP Encryption ({comp_name})**")
                        doc_lines.append(f"  - Purpose: {pgp.get('purpose', 'Data encryption')}")
                        if pgp.get('encrypt_alias'):
                            doc_lines.append(f"  - Encryption Alias: `{pgp['encrypt_alias']}`")
                        if pgp.get('clear_sign'):
                            doc_lines.append(f"  - Clear Sign: {pgp['clear_sign']}")
                        doc_lines.append("")
                    
                    if security.get('pgp_keys'):
                        doc_lines.append(f"- **PGP Keys ({comp_name})**")
                        for key in security['pgp_keys']:
                            key_name = key.get('key_name', 'Unknown Key')
                            doc_lines.append(f"  - **{key_name}**")
                            doc_lines.append(f"    - Purpose: {key.get('purpose', 'Encryption key')}")
                            if key.get('overrideable'):
                                doc_lines.append(f"    - Overrideable: {key['overrideable']}")
                        doc_lines.append("")
        
        # Processes with enhanced analysis
        if processing_results['processes']:
            doc_lines.append("## Boomi Processes")
            doc_lines.append("")
            
            for i, process in enumerate(processing_results['processes'], 1):
                component = process['component']
                process_info = process['process']
                
                doc_lines.append(f"### {i}. {component.get('name', 'Unnamed Process')}")
                if component.get('version'):
                    doc_lines.append(f"**Version:** {component['version']}")
                if component.get('folder_path'):
                    doc_lines.append(f"**Location:** {component['folder_path']}")
                doc_lines.append("")
                
                if component.get('description'):
                    doc_lines.append(f"**Description:** {component['description']}")
                    doc_lines.append("")
                
                # Component details with enhanced metadata
                doc_lines.append("#### Component Information")
                doc_lines.append("")
                doc_lines.append(f"- **Type:** {component.get('type', 'Unknown')}")
                doc_lines.append(f"- **Version:** {component.get('version', 'Unknown')}")
                doc_lines.append(f"- **Created By:** {component.get('created_by', 'Unknown')}")
                doc_lines.append(f"- **Created Date:** {component.get('created_date', 'Unknown')}")
                doc_lines.append(f"- **Modified By:** {component.get('modified_by', 'Unknown')}")
                doc_lines.append(f"- **Folder Path:** {component.get('folder_path', 'Unknown')}")
                doc_lines.append("")
                
                # NEW: Enhanced Process Flow Details
                shapes = process_info.get('shapes', [])
                decisions = [s for s in shapes if s.get('type') == 'decision' and s.get('decision')]
                doc_props_shapes = [s for s in shapes if s.get('type') == 'documentproperties' and s.get('document_properties')]
                branches = [s for s in shapes if s.get('type') == 'branch' and s.get('branch')]
                
                if decisions or doc_props_shapes or branches:
                    doc_lines.append("#### Process Flow Details")
                    doc_lines.append("")
                    
                    if decisions:
                        doc_lines.append("**Decision Points:**")
                        for decision in decisions:
                            user_label = decision.get('user_label', decision.get('name', 'Unknown Decision'))
                            doc_lines.append(f"- **{user_label}**")
                            decision_info = decision['decision']
                            doc_lines.append(f"  - Logic: {decision_info.get('comparison', 'Unknown')} comparison")
                            doc_lines.append(f"  - Purpose: {decision_info.get('business_purpose', 'Business decision logic')}")
                        doc_lines.append("")
                    
                    if branches:
                        doc_lines.append("**Parallel Processing:**")
                        for branch in branches:
                            user_label = branch.get('user_label', 'Parallel Hub')
                            doc_lines.append(f"- **{user_label}**")
                            branch_info = branch['branch']
                            doc_lines.append(f"  - Branches: {branch_info.get('num_branches', 'Unknown')} parallel paths")
                            doc_lines.append(f"  - Purpose: {branch_info.get('purpose', 'Parallel processing')}")
                        doc_lines.append("")
                    
                    if doc_props_shapes:
                        doc_lines.append("**Document Properties:**")
                        for doc_prop_shape in doc_props_shapes:
                            user_label = doc_prop_shape.get('user_label', 'Property Management')
                            doc_lines.append(f"- **{user_label}**")
                            prop_count = len(doc_prop_shape['document_properties'])
                            doc_lines.append(f"  - Properties Set: {prop_count} dynamic properties")
                            for prop in doc_prop_shape['document_properties'][:3]:
                                if prop.get('name'):
                                    doc_lines.append(f"    - {prop['name']}: {prop.get('business_purpose', 'Property configuration')}")
                            if prop_count > 3:
                                doc_lines.append(f"    - ... and {prop_count - 3} more properties")
                doc_lines.append("")
                
                # Integration patterns
                if process.get('integration_patterns'):
                    doc_lines.append("#### Integration Patterns")
                    doc_lines.append("")
                    for pattern in process['integration_patterns']:
                        doc_lines.append(f"- {pattern.replace('_', ' ').title()}")
                    doc_lines.append("")
                
                # Process flow
                doc_lines.append("#### Process Flow Diagram")
                doc_lines.append("")
                doc_lines.append(self._generate_flow_diagram(process_info['shapes'], process_info['connections']))
                doc_lines.append("")
        
        # Maps with enhanced transformation details
        if processing_results['maps']:
            doc_lines.append("## Data Mappings and Transformations")
            doc_lines.append("")
            
            for i, map_info in enumerate(processing_results['maps'], 1):
                component = map_info['component']
                map_data = map_info['map']
                
                doc_lines.append(f"### {i}. {component.get('name', 'Unnamed Map')}")
                if component.get('version'):
                    doc_lines.append(f"**Version:** {component['version']}")
                if component.get('folder_path'):
                    doc_lines.append(f"**Location:** {component['folder_path']}")
                doc_lines.append("")
                
                if component.get('description'):
                    doc_lines.append(f"**Description:** {component['description']}")
                    doc_lines.append("")
                
                # NEW: Detailed Field Mappings with SuccessFactors paths
                if map_data.get('detailed_mappings'):
                    doc_lines.append("#### Detailed Field Mappings")
                    doc_lines.append("")
                    
                    for mapping in map_data['detailed_mappings']:
                        source_path = mapping['source'].get('name_path', 'Direct mapping')
                        target_path = mapping['target'].get('name_path', 'Unknown target')
                        transformation = mapping.get('transformation_type', 'Direct')
                        business_context = mapping.get('business_context', 'Data mapping')
                        
                        # Clean up paths for display
                        if source_path and '/' in source_path:
                            source_display = source_path.split('/')[-1] if source_path.split('/')[-1] else source_path.split('/')[-2]
                        else:
                            source_display = source_path or 'Source field'
                            
                        if target_path and '/' in target_path:
                            target_display = target_path.split('/')[-1] if target_path.split('/')[-1] else target_path.split('/')[-2]
                        else:
                            target_display = target_path or 'Target field'
                        
                        doc_lines.append(f"- **`{source_display}`** → **`{target_display}`**")
                        doc_lines.append(f"  - Transformation: {transformation}")
                        doc_lines.append(f"  - Business Context: {business_context}")
                        doc_lines.append("")
                
                # NEW: Transformation Functions
                if map_data.get('transformation_functions'):
                    doc_lines.append("#### Transformation Functions")
                    doc_lines.append("")
                    
                    for func in map_data['transformation_functions']:
                        func_name = func.get('name', 'Unknown Function')
                        func_category = func.get('category', 'Generic')
                        func_purpose = func.get('business_purpose', 'Data transformation')
                        
                        doc_lines.append(f"**{func_name}** ({func_category})")
                        doc_lines.append("")
                        doc_lines.append(f"**Purpose:** {func_purpose}")
                        doc_lines.append("")
                        
                        # Function configuration details in organized format
                        config = func.get('configuration', {})
                        if config:
                            doc_lines.append("**Configuration Details:**")
                            doc_lines.append("")
                            if config.get('type'):
                                doc_lines.append(f"- **Type:** {config['type']}")
                            if config.get('delimiter'):
                                doc_lines.append(f"- **Delimiter:** `{config['delimiter']}`")
                            if config.get('cache_index'):
                                doc_lines.append(f"- **Cache Index:** `{config['cache_index']}`")
                            if config.get('doc_cache'):
                                doc_lines.append(f"- **Document Cache:** `{config['doc_cache']}`")
                            doc_lines.append("")
                        
                        # Function inputs and outputs in organized format
                        inputs = func.get('inputs', [])
                        if inputs:
                            doc_lines.append("**Input Parameters:**")
                            doc_lines.append("")
                            for inp in inputs:
                                inp_name = inp.get('name', 'Unknown')
                                inp_default = inp.get('default', 'None')
                                doc_lines.append(f"- **{inp_name}**")
                                if inp_default != 'None':
                                    doc_lines.append(f"  - Default Value: `{inp_default}`")
                            doc_lines.append("")
                        
                        outputs = func.get('outputs', [])
                        if outputs:
                            doc_lines.append("**Output Parameters:**")
                            doc_lines.append("")
                            for out in outputs:
                                out_name = out.get('name', 'Unknown')
                                doc_lines.append(f"- **{out_name}**")
                            doc_lines.append("")
                        
                        doc_lines.append("")
                
                # NEW: Cache Operations
                if map_data.get('cache_operations'):
                    doc_lines.append("#### Cache Lookups and Data Enrichment")
                    doc_lines.append("")
                    
                    for cache_op in map_data['cache_operations']:
                        doc_lines.append(f"**Cache Index {cache_op.get('cache_index', 'Unknown')}**")
                        doc_lines.append("")
                        doc_lines.append(f"**Purpose:** {cache_op.get('business_purpose', 'Data lookup')}")
                        doc_lines.append("")
                        doc_lines.append(f"**Cache ID:** `{cache_op.get('doc_cache', 'Unknown')}`")
                        doc_lines.append("")
                        
                        join_values = cache_op.get('join_values', [])
                        if join_values:
                            doc_lines.append("**Join Fields:**")
                            doc_lines.append("")
                            for join_val in join_values:
                                cache_key_name = join_val.get('cache_key_name', 'Unknown field')
                                doc_lines.append(f"- **{cache_key_name}**")
                            doc_lines.append("")
                        
                        doc_lines.append("")
                
                # NEW: Business Rules
                if map_data.get('business_rules'):
                    doc_lines.append("#### Business Rules and Validation")
                    doc_lines.append("")
                    
                    for rule in map_data['business_rules']:
                        rule_name = rule.get('name', 'Unknown Rule')
                        rule_purpose = rule.get('business_purpose', 'Validation logic')
                        error_message = rule.get('error_message', 'Validation failed')
                        
                        doc_lines.append(f"**{rule_name}**")
                        doc_lines.append("")
                        doc_lines.append(f"**Purpose:** {rule_purpose}")
                        doc_lines.append("")
                        doc_lines.append(f"**Error Message:** {error_message}")
                        doc_lines.append("")
                        
                        conditions = rule.get('conditions', [])
                        if conditions:
                            doc_lines.append("**Validation Conditions:**")
                            doc_lines.append("")
                            for condition in conditions:
                                doc_lines.append(f"- **{condition.get('details', 'Complex validation logic')}**")
                            doc_lines.append("")
                        
                        doc_lines.append("")
                
                # Legacy field mappings (for backward compatibility)
                elif map_data.get('legacy_mappings') or map_data.get('mappings'):
                    doc_lines.append("#### Field Mappings")
                    doc_lines.append("")
                    mappings = map_data.get('legacy_mappings') or map_data.get('mappings', [])
                    for mapping in mappings:
                        from_path = mapping.get('from_key', 'Unknown')
                        to_path = mapping.get('to_name_path', 'Unknown')
                        mapping_type = mapping.get('to_type', 'Unknown')
                        doc_lines.append(f"- **{from_path}** → **{to_path}** ({mapping_type})")
                doc_lines.append("")
        
        # Connectors (unchanged)
        if processing_results['connectors']:
            doc_lines.append("## Connectors")
            doc_lines.append("")
            
            for i, connector in enumerate(processing_results['connectors'], 1):
                component = connector['component']
                connector_info = connector['connector']
                
                doc_lines.append(f"### {i}. {component.get('name', 'Unnamed Connector')}")
                doc_lines.append("")
                doc_lines.append(f"- **Type:** {connector_info.get('type', 'Unknown')}")
                if connector_info.get('object_name'):
                    doc_lines.append(f"- **Object:** {connector_info['object_name']}")
                if connector_info.get('object_action'):
                    doc_lines.append(f"- **Action:** {connector_info['object_action']}")
                doc_lines.append("")
        
        # Errors
        if processing_results['errors']:
            doc_lines.append("## Processing Errors")
            doc_lines.append("")
            for error in processing_results['errors']:
                doc_lines.append(f"- {error}")
            doc_lines.append("")
        
        return "\n".join(doc_lines)
    
    def _extract_detailed_mappings(self, map_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract detailed field mappings with full source and target paths"""
        detailed_mappings = []
        
        mappings_elem = map_elem.find('Mappings')
        if mappings_elem is None:
            return detailed_mappings
        
        for mapping in mappings_elem.findall('Mapping'):
            mapping_detail = {
                'source': {
                    'key': mapping.get('fromKey'),
                    'key_path': mapping.get('fromKeyPath'),
                    'name_path': mapping.get('fromNamePath'),
                    'type': mapping.get('fromType'),
                    'function_key': mapping.get('fromFunction'),
                    'cache_join_key': mapping.get('fromCacheJoinKey')
                },
                'target': {
                    'key': mapping.get('toKey'),
                    'key_path': mapping.get('toKeyPath'),
                    'name_path': mapping.get('toNamePath'),
                    'type': mapping.get('toType'),
                    'function_key': mapping.get('toFunction')
                },
                'transformation_type': self._determine_transformation_type(mapping),
                'business_context': self._extract_business_context(mapping)
            }
            detailed_mappings.append(mapping_detail)
        
        return detailed_mappings
    
    def _extract_transformation_functions(self, map_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract transformation functions with their configurations and business logic"""
        functions = []
        
        functions_elem = map_elem.find('Functions')
        if functions_elem is None:
            return functions
        
        for func in functions_elem.findall('FunctionStep'):
            func_detail = {
                'key': func.get('key'),
                'name': func.get('name'),
                'category': func.get('category'),
                'type': func.get('type'),
                'position': func.get('position'),
                'id': func.get('id'),  # For user-defined functions
                'inputs': self._extract_function_inputs(func),
                'outputs': self._extract_function_outputs(func),
                'configuration': self._extract_function_configuration(func),
                'business_purpose': self._infer_function_purpose(func)
            }
            functions.append(func_detail)
        
        return functions
    
    def _extract_business_rules(self, map_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract business rules and validation logic"""
        rules = []
        
        # Look for BusinessRules in the XML (might be in a different location)
        business_rules = map_elem.findall('.//BusinessRules')
        for rules_elem in business_rules:
            for rule in rules_elem.findall('rule'):
                rule_detail = {
                    'key': rule.get('key'),
                    'name': rule.get('name'),
                    'inputs': self._extract_rule_inputs(rule),
                    'conditions': self._extract_rule_conditions(rule),
                    'error_message': self._extract_rule_error_message(rule),
                    'business_purpose': f"Validation rule: {rule.get('name', 'Unknown')}"
                }
                rules.append(rule_detail)
        
        return rules
    
    def _extract_cache_operations(self, map_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract document cache operations and lookups"""
        cache_ops = []
        
        cache_joins = map_elem.find('DocumentCacheJoins')
        if cache_joins is not None:
            for join in cache_joins.findall('DocumentCacheJoin'):
                cache_detail = {
                    'cache_index': join.get('cacheIndex'),
                    'doc_cache': join.get('docCache'),
                    'join_id': join.get('docCacheJoinId'),
                    'join_values': self._extract_cache_join_values(join),
                    'business_purpose': "Document cache lookup for data enrichment"
                }
                cache_ops.append(cache_detail)
        
        return cache_ops
    
    def _extract_legacy_mappings(self, map_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract legacy mapping format for backward compatibility"""
        mappings = []
        for mapping in map_elem.findall('.//Mapping'):
            mappings.append({
                'from_key': mapping.get('fromKey'),
                'from_type': mapping.get('fromType'),
                'to_key': mapping.get('toKey'),
                'to_name_path': mapping.get('toNamePath'),
                'to_type': mapping.get('toType')
            })
        return mappings
    
    def _determine_transformation_type(self, mapping: ET.Element) -> str:
        """Determine the type of transformation being performed"""
        if mapping.get('fromFunction') and mapping.get('toFunction'):
            return "Function Chain"
        elif mapping.get('fromFunction'):
            return "Function Output"
        elif mapping.get('toFunction'):
            return "Function Input"
        elif mapping.get('fromCacheJoinKey'):
            return "Cache Lookup"
        else:
            return "Direct Mapping"
    
    def _extract_business_context(self, mapping: ET.Element) -> str:
        """Extract business context from mapping paths"""
        from_path = mapping.get('fromNamePath', '')
        to_path = mapping.get('toNamePath', '')
        
        # Determine business context based on field names
        if 'person_id_external' in from_path or 'GPID' in to_path:
            return "Global Person ID mapping for unique employee identification"
        elif 'first_name' in from_path or 'First Name' in to_path:
            return "Employee first name mapping for identification"
        elif 'employment_information' in from_path:
            return "Employment data mapping for HR processing"
        elif 'job_information' in from_path:
            return "Job-related information mapping"
        elif 'personal_information' in from_path:
            return "Personal data mapping for employee profile"
        else:
            return f"Data mapping from {from_path.split('/')[-1] if from_path else 'source'} to {to_path.split('/')[-1] if to_path else 'target'}"
    
    def _extract_function_inputs(self, func: ET.Element) -> List[Dict[str, Any]]:
        """Extract function input parameters"""
        inputs = []
        inputs_elem = func.find('Inputs')
        if inputs_elem is not None:
            for input_elem in inputs_elem.findall('Input'):
                inputs.append({
                    'key': input_elem.get('key'),
                    'name': input_elem.get('name'),
                    'default': input_elem.get('default')
                })
        return inputs
    
    def _extract_function_outputs(self, func: ET.Element) -> List[Dict[str, Any]]:
        """Extract function output parameters"""
        outputs = []
        outputs_elem = func.find('Outputs')
        if outputs_elem is not None:
            for output_elem in outputs_elem.findall('Output'):
                outputs.append({
                    'key': output_elem.get('key'),
                    'name': output_elem.get('name')
                })
        return outputs
    
    def _extract_function_configuration(self, func: ET.Element) -> Dict[str, Any]:
        """Extract function configuration details"""
        config = {}
        config_elem = func.find('Configuration')
        if config_elem is not None:
            # Extract different configuration types
            for child in config_elem:
                if child.tag == 'StringSplit':
                    config['delimiter'] = child.get('delimiter')
                    config['type'] = 'String Split'
                elif child.tag == 'StringConcat':
                    config['delimiter'] = child.get('delimiter')
                    config['type'] = 'String Concatenation'
                elif child.tag == 'DocumentCacheLookup':
                    config['cache_index'] = child.get('cacheIndex')
                    config['doc_cache'] = child.get('docCache')
                    config['type'] = 'Cache Lookup'
                elif child.tag == 'DateFormat':
                    config['type'] = 'Date Formatting'
        return config
    
    def _infer_function_purpose(self, func: ET.Element) -> str:
        """Infer the business purpose of transformation functions"""
        func_name = func.get('name', '').lower()
        func_type = func.get('type', '').lower()
        func_category = func.get('category', '').lower()
        
        if 'split' in func_name or func_type == 'stringsplit':
            return "String splitting for data parsing (e.g., removing ID suffixes for global assignments)"
        elif 'concat' in func_name or func_type == 'stringconcat':
            return "String concatenation for combining data fields (e.g., first + last name)"
        elif 'lookup' in func_name or 'cache' in func_type:
            return "Data lookup for external code translation and enrichment"
        elif 'date' in func_name or func_category == 'date':
            return "Date formatting for standardized output format"
        elif 'manager' in func_name:
            return "Manager information retrieval and processing"
        elif 'termination' in func_name:
            return "Termination reason processing and validation"
        elif func_category == 'userdefined':
            return f"Custom business logic: {func.get('name', 'User-defined function')}"
        else:
            return f"Data transformation: {func.get('name', 'Generic function')}"
    
    def _extract_rule_inputs(self, rule: ET.Element) -> List[Dict[str, Any]]:
        """Extract business rule input fields"""
        inputs = []
        for input_elem in rule.findall('.//input'):
            if input_elem.get('id'):  # Only process actual input elements
                inputs.append({
                    'id': input_elem.get('id'),
                    'name': input_elem.get('name'),
                    'alias': input_elem.get('alias'),
                    'element_key': input_elem.get('elementKey')
                })
        return inputs
    
    def _extract_rule_conditions(self, rule: ET.Element) -> List[Dict[str, Any]]:
        """Extract business rule conditions and logic"""
        conditions = []
        condition_elem = rule.find('condition')
        if condition_elem is not None:
            conditions.append({
                'operator': condition_elem.get('operator'),
                'type': condition_elem.get('{http://www.w3.org/2001/XMLSchema-instance}type'),
                'details': self._extract_condition_details(condition_elem)
            })
        return conditions
    
    def _extract_condition_details(self, condition: ET.Element) -> str:
        """Extract detailed condition logic"""
        nested_expr = condition.find('nestedExpression')
        if nested_expr is not None:
            operator = nested_expr.get('operator')
            left_input = nested_expr.find('leftInput')
            if left_input is not None:
                field_name = left_input.get('name')
                return f"Field '{field_name}' {operator}"
        return "Complex condition logic"
    
    def _extract_rule_error_message(self, rule: ET.Element) -> str:
        """Extract business rule error message"""
        error_msg = rule.find('errorMessage')
        if error_msg is not None:
            return error_msg.get('content', 'Validation error')
        return "Validation failed"
    
    def _extract_cache_join_values(self, join: ET.Element) -> List[Dict[str, Any]]:
        """Extract cache join value mappings"""
        join_values = []
        for join_value in join.findall('.//CacheKeyJoinValue'):
            join_values.append({
                'cache_key_id': join_value.get('cacheKeyId'),
                'cache_key_name': join_value.get('cacheKeyName'),
                'source_link_key': join_value.find('srcLinkKey').get('key') if join_value.find('srcLinkKey') is not None else None
            })
        return join_values
    
    def _generate_flow_diagram(self, shapes: List[Dict[str, Any]], connections: List[Dict[str, Any]]) -> str:
        """Generate a text-based flow diagram"""
        diagram_lines = ["```mermaid", "graph TD"]
        
        # Add shapes
        for shape in shapes:
            shape_name = shape['name']
            shape_type = shape['type']
            label = shape.get('user_label') or shape_name
            
            if shape_type == 'start':
                diagram_lines.append(f"    {shape_name}([{label}])")
            elif shape_type == 'stop':
                diagram_lines.append(f"    {shape_name}([{label}])")
            elif shape_type == 'connectoraction':
                diagram_lines.append(f"    {shape_name}[{label}]")
            elif shape_type == 'map':
                diagram_lines.append(f"    {shape_name}{{Transform: {label}}}")
            else:
                diagram_lines.append(f"    {shape_name}[{label}]")
        
        # Add connections
        for connection in connections:
            from_shape = connection['from_shape']
            to_shape = connection['to_shape']
            diagram_lines.append(f"    {from_shape} --> {to_shape}")
        
        diagram_lines.append("```")
        return "\n".join(diagram_lines)
