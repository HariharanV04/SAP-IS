"""
Enhanced iFlow Component Templates Library

This module provides comprehensive templates for SAP Integration Suite components
based on analysis of real-world iFlow files. It includes detailed configuration
options and supports a wide range of component types.

Each template is parameterized with placeholders that can be replaced
with actual values when generating the iFlow.
"""

import uuid
import xml.dom.minidom
import re
from typing import Dict, List, Optional, Union, Any

class EnhancedIFlowTemplates:
    """
    A comprehensive collection of templates for SAP Integration Suite components.
    """

    def __init__(self):
        """Initialize the templates library"""
        pass
    


    # ===== iFlow Configuration =====

    def iflow_configuration_template(self, namespace_mapping="", log_level="All events", csrf_protection="false"):
        """
        Template for iFlow configuration

        Args:
            namespace_mapping (str): XML namespace mappings
            log_level (str): Logging level (e.g., "All events", "Errors only")
            csrf_protection (str): CSRF protection enabled ("true"/"false")

        Returns:
            str: XML template for iFlow configuration
        """
        return f'''<bpmn2:extensionElements>
            <ifl:property>
                <key>namespaceMapping</key>
                <value>{namespace_mapping}</value>
            </ifl:property>
            <ifl:property>
                <key>httpSessionHandling</key>
                <value>None</value>
            </ifl:property>
            <ifl:property>
                <key>returnExceptionToSender</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>log</key>
                <value>{log_level}</value>
            </ifl:property>
            <ifl:property>
                <key>corsEnabled</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.2</value>
            </ifl:property>
            <ifl:property>
                <key>ServerTrace</key>
                <value>false</value>
            </ifl:property>
            <ifl:property>
                <key>xsrfProtection</key>
                <value>{csrf_protection}</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::IFlowVariant/cname::IFlowConfiguration/version::1.2.4</value>
            </ifl:property>
        </bpmn2:extensionElements>'''

    # ===== Participant Templates =====

    def participant_template(self, id, name, type="EndpointRecevier", enable_basic_auth="false"):
        """
        Template for Participant

        Args:
            id (str): Participant ID
            name (str): Participant name
            type (str): Participant type (EndpointSender, EndpointRecevier, IntegrationProcess)
            enable_basic_auth (str): Enable basic authentication ("true"/"false")

        Returns:
            str: XML template for Participant
        """
        auth_element = ""
        if type == "EndpointSender":
            auth_element = f'''
                <ifl:property>
                    <key>enableBasicAuthentication</key>
                    <value>{enable_basic_auth}</value>
                </ifl:property>'''

        return f'''<bpmn2:participant id="{id}" ifl:type="{type}" name="{name}">
            <bpmn2:extensionElements>{auth_element}
                <ifl:property>
                    <key>ifl:type</key>
                    <value>{type}</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:participant>'''

    def integration_process_participant_template(self, id, name, process_ref):
        """
        Template for Integration Process Participant

        Args:
            id (str): Participant ID
            name (str): Participant name
            process_ref (str): Process reference ID

        Returns:
            str: XML template for Integration Process Participant
        """
        return f'''<bpmn2:participant id="{id}" ifl:type="IntegrationProcess" name="{name}" processRef="{process_ref}">
            <bpmn2:extensionElements/>
        </bpmn2:participant>'''

    # ===== Adapter Templates =====

    def odata_receiver_template(self, id, name, service_url, entity_set="", auth_method="None", credential_name="", timeout="60000", system="", operation="Query(GET)", resource_path=""):
        """
        Template for OData Receiver Adapter with enhanced SAP Integration Suite compatibility

        Args:
            id (str): Component ID
            name (str): Component name
            service_url (str): OData service URL
            entity_set (str): Entity set name
            auth_method (str): Authentication method
            credential_name (str): Credential name
            timeout (str): Request timeout
            system (str): System name
            operation (str): OData operation (Query(GET), Create(POST), etc.)
            resource_path (str): Resource path for the OData call
        """
        # Ensure serviceUrl has a default value
        if not service_url:
            service_url = "https://example.com/odata/service"

        # Use entity_set as resource_path if resource_path is not provided
        if not resource_path and entity_set:
            resource_path = entity_set

        return f'''<bpmn2:messageFlow id="{id}" name="{name}" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>HCIOData</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value>OData connection to {entity_set}</value>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>OData</value>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{service_url}</value>
                </ifl:property>
                <ifl:property>
                    <key>resourcePath</key>
                    <value>{resource_path}</value>
                </ifl:property>
                <ifl:property>
                    <key>operation</key>
                    <value>{operation}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.25</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.25.0</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.25.0</value>
                </ifl:property>
                <ifl:property>
                    <key>authenticationMethod</key>
                    <value>{auth_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>credentialName</key>
                    <value>{credential_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>httpRequestTimeout</key>
                    <value>{timeout}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
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
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVId</key>
                    <value>1.25.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::sap:HCIOData/tp::HTTP/mp::OData V2/direction::Receiver/version::1.25.0</value>
                </ifl:property>
                <ifl:property>
                    <key>isCSRFEnabled</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>enableMPLAttachments</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>contentType</key>
                    <value>application/atom+xml</value>
                </ifl:property>
                <ifl:property>
                    <key>proxyType</key>
                    <value>default</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''

    def edmx_template(self, namespace, entity_type_name, properties):
        """
        Template for EDMX file (OData metadata)

        Args:
            namespace (str): Namespace for the OData service
            entity_type_name (str): Name of the entity type
            properties (list): List of property dictionaries with name, type, and nullable

        Returns:
            str: XML template for EDMX file
        """
        # Generate property elements
        property_elements = ""
        key_property = properties[0]["name"] if properties else "Id"

        for prop in properties:
            nullable = prop.get("nullable", "false")
            max_length = f' MaxLength="{prop.get("max_length")}"' if "max_length" in prop else ""
            precision = f' Precision="{prop.get("precision")}"' if "precision" in prop else ""
            scale = f' Scale="{prop.get("scale")}"' if "scale" in prop else ""

            property_elements += f'''
        <Property Name="{prop["name"]}" Type="{prop["type"]}" Nullable="{nullable}"{max_length}{precision}{scale} />'''

        return f'''<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="1.0" xmlns:edmx="http://schemas.microsoft.com/ado/2007/06/edmx" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:sap="http://www.sap.com/Protocols/SAPData">
  <edmx:DataServices m:DataServiceVersion="2.0">
    <Schema Namespace="{namespace}" xmlns="http://schemas.microsoft.com/ado/2008/09/edm">
      <EntityType Name="{entity_type_name}">
        <Key>
          <PropertyRef Name="{key_property}" />
        </Key>{property_elements}
      </EntityType>
      <EntityContainer Name="{namespace}" m:IsDefaultEntityContainer="true">
        <EntitySet Name="{entity_type_name}s" EntityType="{namespace}.{entity_type_name}" />
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>'''

    def http_receiver_template(self, id, name, address, auth_method="None", credential_name="",
                              timeout="60000", throw_exception="true", system="", http_method="POST"):
        """
        Template for HTTP Receiver Adapter

        Args:
            id (str): Component ID
            name (str): Component name
            address (str): HTTP endpoint address
            auth_method (str): Authentication method
            credential_name (str): Credential name
            timeout (str): Request timeout in milliseconds
            throw_exception (str): Throw exception on failure ("true"/"false")
            system (str): System name
            http_method (str): HTTP method (GET, POST, PUT, DELETE)

        Returns:
            str: XML template for HTTP Receiver Adapter
        """
        return f'''<bpmn2:messageFlow id="{id}" name="{name}" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>httpMethod</key>
                    <value>{http_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>httpRequestTimeout</key>
                    <value>{timeout}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>authenticationMethod</key>
                    <value>{auth_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>credentialName</key>
                    <value>{credential_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>None</value>
                </ifl:property>
                <ifl:property>
                    <key>httpAddressWithoutQuery</key>
                    <value>{address}</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
                <ifl:property>
                    <key>throwExceptionOnFailure</key>
                    <value>{throw_exception}</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.15</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.15.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''

    def https_sender_template(self, id, name, url_path, sender_auth="None", user_role="ESBMessaging.send", csrf_protection="false", client_certificates=""):
        """
        Template for HTTPS Sender Adapter with default values for empty properties
        """
        # Ensure url_path has a default value
        if not url_path:
            url_path = "/"

        return f'''<bpmn2:messageFlow id="{id}" name="HTTPS" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>maximumBodySize</key>
                    <value>40</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.4</value>
                </ifl:property>
                <ifl:property>
                    <key>urlPath</key>
                    <value>{url_path}</value>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.4.1</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>ESBMessaging</value>
                </ifl:property>
                <ifl:property>
                    <key>xsrfProtection</key>
                    <value>{csrf_protection}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTPS</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::sap:HTTPS/tp::HTTPS/mp::None/direction::Sender/version::1.4.1</value>
                </ifl:property>
                <ifl:property>
                    <key>userRole</key>
                    <value>{user_role}</value>
                </ifl:property>
                <ifl:property>
                    <key>senderAuthType</key>
                    <value>{sender_auth}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>None</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.4.1</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVId</key>
                    <value>1.4.1</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Sender</value>
                </ifl:property>
                <ifl:property>
                    <key>clientCertificates</key>
                    <value>{client_certificates}</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''


    def soap_receiver_template(self, id, name, address, auth_method="None", credential_name="",
                              timeout="60000", system="", compress_message="false", location_id=""):
        """
        Template for SOAP Receiver Adapter

        Args:
            id (str): Component ID
            name (str): Component name
            address (str): SOAP endpoint address
            auth_method (str): Authentication method
            credential_name (str): Credential name
            timeout (str): Request timeout in milliseconds
            system (str): System name
            compress_message (str): Compress message ("true"/"false")
            location_id (str): Location ID

        Returns:
            str: XML template for SOAP Receiver Adapter
        """
        return f'''<bpmn2:messageFlow id="{id}" name="{name}" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>cleanupHeaders</key>
                    <value>1</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>location_id</key>
                    <value>{location_id}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.10.0</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>CompressMessage</key>
                    <value>{compress_message}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>Plain SOAP</value>
                </ifl:property>
                <ifl:property>
                    <key>requestTimeout</key>
                    <value>{timeout}</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
                <ifl:property>
                    <key>authentication</key>
                    <value>{auth_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>SOAP</value>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{address}</value>
                </ifl:property>
                <ifl:property>
                    <key>allowChunking</key>
                    <value>1</value>
                </ifl:property>
                <ifl:property>
                    <key>SapRmMessageIdDetermination</key>
                    <value>Reuse</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.9</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::sap:SOAP/tp::HTTP/mp::Plain SOAP/direction::Receiver/version::1.9.0</value>
                </ifl:property>
                <ifl:property>
                    <key>credentialName</key>
                    <value>{credential_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.10.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''

    def process_direct_template(self, id, name, address, system=""):
        """
        Template for ProcessDirect Adapter

        Args:
            id (str): Component ID
            name (str): Component name
            address (str): ProcessDirect endpoint address
            system (str): System name

        Returns:
            str: XML template for ProcessDirect Adapter
        """
        return f'''<bpmn2:messageFlow id="{id}" name="ProcessDirect" sourceRef="{{{{source_ref}}}}" targetRef="{{{{target_ref}}}}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>ProcessDirect</value>
                </ifl:property>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{address}</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>Vendor</key>
                    <value>SAP</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>{system}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>Not Applicable</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::ProcessDirect/vendor::SAP/tp::Not Applicable/mp::Not Applicable/direction::Receiver/version::1.1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>Not Applicable</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''

    # ===== Process Component Templates =====

    def enricher_template(self, id, name, body_type="constant", wrap_content=""):
        """
        Template for Enricher component (used in request-reply patterns)

        Args:
            id (str): Component ID
            name (str): Component name
            body_type (str): Body type (constant, expression)
            wrap_content (str): Wrap content value

        Returns:
            str: XML template for Enricher
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>bodyType</key>
                    <value>{body_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>propertyTable</key>
                    <value>[]</value>
                </ifl:property>
                <ifl:property>
                    <key>headerTable</key>
                    <value>[]</value>
                </ifl:property>
                <ifl:property>
                    <key>wrapContent</key>
                    <value>{wrap_content}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.5</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Enricher</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::Enricher/version::1.5.1</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def content_modifier_template(self, id, name, property_table="", header_table="", body_type="expression", wrap_content="", content=""):
        """
        Template for Content Modifier

        Args:
            id (str): Component ID
            name (str): Component name
            property_table (str): XML representation of property table
            header_table (str): XML representation of header table
            body_type (str): Body type (expression/constant)
            wrap_content (str): Wrap content configuration
            content (str): Content to set

        Returns:
            str: XML template for Content Modifier
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>bodyType</key>
                    <value>{body_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>propertyTable</key>
                    <value>{property_table}</value>
                </ifl:property>
                <ifl:property>
                    <key>headerTable</key>
                    <value>{header_table}</value>
                </ifl:property>
                <ifl:property>
                    <key>wrapContent</key>
                    <value>{wrap_content}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.5</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Enricher</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::Enricher/version::1.5.0</value>
                </ifl:property>
                <ifl:property>
                    <key>bodyContent</key>
                    <value>{content}</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def content_enricher_template(self, id, name, property_table="", header_table="", body_type="expression", body_content="", wrap_content=""):
        """
        Template for Content Enricher (SAP Integration Suite uses Enricher for content modifiers)

        Args:
            id (str): Component ID
            name (str): Component name
            property_table (str): XML representation of property table
            header_table (str): XML representation of header table
            body_type (str): Body type (expression/constant)
            body_content (str): Content to set
            wrap_content (str): Wrap content configuration

        Returns:
            str: XML template for Content Enricher
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>bodyType</key>
                    <value>{body_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>propertyTable</key>
                    <value>{property_table}</value>
                </ifl:property>
                <ifl:property>
                    <key>headerTable</key>
                    <value>{header_table}</value>
                </ifl:property>
                <ifl:property>
                    <key>wrapContent</key>
                    <value>{wrap_content}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.4</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Enricher</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::Enricher/version::1.4.2</value>
                </ifl:property>
                <ifl:property>
                    <key>bodyContent</key>
                    <value>{body_content}</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def router_template(self, id, name, conditions=[]):
        """
        Template for Router (Exclusive Gateway)

        Args:
            id (str): Component ID
            name (str): Component name
            conditions (list): List of routing conditions

        Returns:
            str: XML template for Router
        """
        return f'''<bpmn2:exclusiveGateway id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.3</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>ExclusiveGateway</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.3.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:exclusiveGateway>'''

    def call_activity_template(self, id, name, activity_type):
        """
        Template for Call Activity (used for various component types)

        Args:
            id (str): Component ID
            name (str): Component name
            activity_type (str): Type of activity (e.g., "OData", "Router")

        Returns:
            str: XML template for Call Activity
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentType</key>
                    <value>{activity_type}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def local_integration_process_template(self, id, name):
        """
        Template for Local Integration Process (represented as a callActivity).

        Args:
            id (str): Component ID
            name (str): Component name

        Returns:
            str: XML template for a Local Integration Process call
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>activityType</key>
                    <value>ProcessCallElement</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::NonLoopingProcess/version::1.0.3</value>
                </ifl:property>
                <ifl:property>
                    <key>subActivityType</key>
                    <value>NonLoopingProcess</value>
                </ifl:property>
                <ifl:property>
                    <key>processId</key>
                    <value></value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def exception_subprocess_template(self, id, name, error_type="All"):
        """
        Template for Exception Subprocess

        Args:
            id (str): Component ID
            name (str): Component name
            error_type (str): Type of error to handle

        Returns:
            str: XML template for Exception Subprocess
        """
        start_id = f"StartEvent_{id}"
        end_id = f"EndEvent_{id}"
        flow_id = f"SequenceFlow_{id}"
        return f'''<bpmn2:subProcess id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>ErrorEventSubProcessTemplate</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::ErrorEventSubProcessTemplate/version::1.1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:endEvent id="{end_id}" name="End 1">
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
                <bpmn2:incoming>{flow_id}</bpmn2:incoming>
                <bpmn2:messageEventDefinition/>
            </bpmn2:endEvent>
            <bpmn2:startEvent id="{start_id}" name="Error Start 1">
                <bpmn2:outgoing>{flow_id}</bpmn2:outgoing>
                <bpmn2:errorEventDefinition>
                    <bpmn2:extensionElements>
                        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::ErrorStartEvent</value></ifl:property>
                        <ifl:property><key>activityType</key><value>StartErrorEvent</value></ifl:property>
                    </bpmn2:extensionElements>
                </bpmn2:errorEventDefinition>
            </bpmn2:startEvent>
            <bpmn2:sequenceFlow id="{flow_id}" sourceRef="{start_id}" targetRef="{end_id}"/>
        </bpmn2:subProcess>'''

    # ===== Additional Activity Templates from reference iFlow =====
    def filter_template(self, id, name, expression=""):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>Filter</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
                <ifl:property><key>filterExpression</key><value>{expression}</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def multicast_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>Multicast</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def sequential_multicast_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>SequentialMulticast</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def process_call_element_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>ProcessCallElement</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def send_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>Send</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def xml_to_csv_converter_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>XmlToCsvConverter</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def xml_to_json_converter_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>XmlToJsonConverter</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def json_to_xml_converter_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property><key>activityType</key><value>JsonToXmlConverter</value></ifl:property>
                <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def parallel_gateway_template(self, id, name, gateway_type="parallel"):
        """
        Template for Parallel Gateway

        Args:
            id (str): Component ID
            name (str): Component name
            gateway_type (str): Gateway type (parallel, exclusive)

        Returns:
            str: XML template for Parallel Gateway
        """
        return f'''<bpmn2:parallelGateway id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>activityType</key>
                    <value>ParallelGateway</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::ParallelGateway/version::1.0.0</value>
                </ifl:property>
                <ifl:property>
                    <key>gatewayType</key>
                    <value>{gateway_type}</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:parallelGateway>'''

    def join_gateway_template(self, id, name, join_type="parallel"):
        """
        Template for Join Gateway (Parallel Gateway)

        Args:
            id (str): Component ID
            name (str): Component name
            join_type (str): Join type (parallel, exclusive)

        Returns:
            str: XML template for Join Gateway
        """
        return f'''<bpmn2:parallelGateway id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>activityType</key>
                    <value>ParallelGateway</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::ParallelGateway/version::1.0.0</value>
                </ifl:property>
                <ifl:property>
                    <key>joinType</key>
                    <value>{join_type}</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:parallelGateway>'''

    def write_to_log_template(self, id, name, log_level="Info", message="Log message"):
        """
        Template for Write to Log

        Args:
            id (str): Component ID
            name (str): Component name
            log_level (str): Log level (Info, Warning, Error)
            message (str): Log message

        Returns:
            str: XML template for Write to Log
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>logLevel</key>
                    <value>{log_level}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Logger</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::WriteToLog/version::1.0.0</value>
                </ifl:property>
                <ifl:property>
                    <key>logMessage</key>
                    <value>{message}</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:callActivity>'''

    def message_mapping_template(self, id, name, source_type="XML", target_type="XML"):
        """
        Template for Message Mapping

        Args:
            id (str): Component ID
            name (str): Component name
            source_type (str): Source message type
            target_type (str): Target message type

        Returns:
            str: XML template for Message Mapping
        """
        return f'''<bpmn2:task id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>mappinguri</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>mappingname</key>
                    <value>{name}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Message Mapping</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::MessageMapping/version::1.1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:task>'''

    def enhanced_message_mapping_template(self, id, name, mapping_name="DataMapping", source_schema="Source.xsd", target_schema="Target.xsd"):
        """
        Enhanced Message Mapping template based on real SAP iFlow structure
        
        Args:
            id (str): Component ID
            name (str): Component name
            mapping_name (str): Name of the mapping bundle
            source_schema (str): Source XSD file name
            target_schema (str): Target XSD file name
            
        Returns:
            str: XML template for enhanced Message Mapping
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
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
                    <key>mappinguri</key>
                    <value>dir://mapping/{mapping_name}.mmap</value>
                </ifl:property>
                <ifl:property>
                    <key>mappingType</key>
                    <value>MessageMapping</value>
                </ifl:property>
                <ifl:property>
                    <key>messageMappingBundleId</key>
                    <value>{mapping_name}</value>
                </ifl:property>
                <ifl:property>
                    <key>sourceSchema</key>
                    <value>src/main/resources/xsd/{source_schema}</value>
                </ifl:property>
                <ifl:property>
                    <key>targetSchema</key>
                    <value>src/main/resources/xsd/{target_schema}</value>
                </ifl:property>
                <ifl:property>
                    <key>customFunctions</key>
                    <value>src/main/resources/script</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    # ===== Event Templates =====

    def message_start_event_template(self, id, name):
        """
        Template for Message Start Event with proper messageEventDefinition
        """
        return f'''<bpmn2:startEvent id="{id}" name="{name}">
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
                <bpmn2:outgoing>{{{{outgoing_flow}}}}</bpmn2:outgoing>
                <bpmn2:messageEventDefinition id="MessageEventDefinition_{id}"/>
            </bpmn2:startEvent>'''

    def message_end_event_template(self, id, name):
        """
        Template for Message End Event with proper messageEventDefinition
        """
        return f'''<bpmn2:endEvent id="{id}" name="{name}">
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
                <bpmn2:incoming>{{{{incoming_flow}}}}</bpmn2:incoming>
                <bpmn2:messageEventDefinition id="MessageEventDefinition_{id}"/>
            </bpmn2:endEvent>'''

    def timer_start_event_template(self, id, name, schedule_key):
        """
        Template for Timer Start Event

        Args:
            id (str): Component ID
            name (str): Component name
            schedule_key (str): Timer schedule expression (e.g., "0 0 * * * ?")

        Returns:
            str: XML template for Timer Start Event
        """
        return f'''<bpmn2:startEvent id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>scheduleKey</key>
                    <value>{schedule_key}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::intermediatetimer/version::1.2.0</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>StartTimerEvent</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:outgoing>{{{{outgoing_flow}}}}</bpmn2:outgoing>
            <bpmn2:timerEventDefinition id="TimerEventDefinition_{id}"/>
        </bpmn2:startEvent>'''

    # ===== Processing Components =====



    def create_property_table(self, properties):
        """
        Create XML representation of property table

        Args:
            properties (list): List of property entries in format [{"action": "Create/Delete", "type": "constant/expression", "name": "propName", "value": "propValue"}]

        Returns:
            str: XML representation of property table
        """
        property_table = ""
        if properties:
            for prop in properties:
                property_table += f'<row><cell id="Action">{prop.get("action", "Create")}</cell><cell id="Type">{prop.get("type", "constant")}</cell><cell id="Value">{prop.get("value", "")}</cell><cell id="Default"></cell><cell id="Name">{prop.get("name", "")}</cell><cell id="Datatype"></cell></row>'
        return property_table

    def create_header_table(self, headers):
        """
        Create XML representation of header table

        Args:
            headers (list): List of header entries in format [{"action": "Create/Delete", "type": "constant/expression", "name": "headerName", "value": "headerValue"}]

        Returns:
            str: XML representation of header table
        """
        header_table = ""
        if headers:
            for header in headers:
                header_table += f'<row><cell id="Action">{header.get("action", "Create")}</cell><cell id="Type">{header.get("type", "constant")}</cell><cell id="Value">{header.get("value", "")}</cell><cell id="Default"></cell><cell id="Name">{header.get("name", "")}</cell><cell id="Datatype"></cell></row>'
        return header_table

    def request_reply_template(self, id, name):
        """
        Template for Request-Reply component (External Call)

        Args:
            id (str): Component ID
            name (str): Component name

        Returns:
            str: XML template for Request-Reply
        """
        return f'''<bpmn2:serviceTask id="{id}" name="{name}">
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
            <bpmn2:incoming>{{{{incoming_flow}}}}</bpmn2:incoming>
            <bpmn2:outgoing>{{{{outgoing_flow}}}}</bpmn2:outgoing>
        </bpmn2:serviceTask>'''

    # ===== Generic Embedded Subprocess (Safe Addition) =====

    def subprocess_template(self, id, name):
        """Create a generic embedded subprocess container (non-breaking)."""
        return f'''<bpmn2:subProcess id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
        <ifl:property><key>activityType</key><value>EmbeddedSubprocess</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::Subprocess/version::1.0.0</value></ifl:property>
    </bpmn2:extensionElements>
    <!-- Add internal flow elements here (start, tasks, end) as needed by generator -->
</bpmn2:subProcess>'''

    def odata_request_reply_pattern(self, service_task_id, participant_id, message_flow_id, name, service_url="https://example.com/odata/service", operation="Query(GET)", resource_path=""):
        """
        Template for a complete OData request-reply pattern with all required components

        Args:
            service_task_id (str): ID for the service task
            participant_id (str): ID for the participant
            message_flow_id (str): ID for the message flow
            name (str): Name for the components
            service_url (str): URL for the OData service

        Returns:
            dict: Dictionary containing all components for the OData pattern
        """
        # 1. Create the service task (ExternalCall) with proper sequence flow placeholders
        service_task = f'''<bpmn2:serviceTask id="{service_task_id}" name="Call_{name}">
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
            <bpmn2:incoming>{{{{incoming_flow}}}}</bpmn2:incoming>
            <bpmn2:outgoing>{{{{outgoing_flow}}}}</bpmn2:outgoing>
        </bpmn2:serviceTask>'''

        # 2. Create the participant (Use typo from working iFlow: EndpointRecevier)
        participant = f'''<bpmn2:participant id="{participant_id}" ifl:type="EndpointRecevier" name="OData_{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ifl:type</key>
                    <value>EndpointRecevier</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:participant>'''

        # 3. Create the message flow with detailed OData properties
        message_flow = f'''<bpmn2:messageFlow id="{message_flow_id}" name="OData" sourceRef="{service_task_id}" targetRef="{participant_id}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>pagination</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>odataCertAuthPrivateKeyAlias</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>apiArtifactType</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>providerAuth</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>ComponentNS</key>
                    <value>sap</value>
                </ifl:property>
                <ifl:property>
                    <key>resourcePath</key>
                    <value>{resource_path}</value>
                </ifl:property>
                <ifl:property>
                    <key>customQueryOptions</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>metadataAllowedURIParams</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>OData</value>
                </ifl:property>
                <ifl:property>
                    <key>internetProxyType</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.25.1</value>
                </ifl:property>
                <ifl:property>
                    <key>proxyPort</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>enableMPLAttachments</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>receiveTimeOut</key>
                    <value>1</value>
                </ifl:property>
                <ifl:property>
                    <key>alias</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>contentType</key>
                    <value>application/atom+xml</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVId</key>
                    <value>1.25.1</value>
                </ifl:property>
                <ifl:property>
                    <key>providerName</key>
                    <value/>
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
                    <key>scc_location_id</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>metadataAllowedHeaders</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>HCIOData</value>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{service_url}</value>
                </ifl:property>
                <ifl:property>
                    <key>queryOptions</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>proxyType</key>
                    <value>default</value>
                </ifl:property>
                <ifl:property>
                    <key>isCSRFEnabled</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.25</value>
                </ifl:property>
                <ifl:property>
                    <key>proxyHost</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>edmxFilePath</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>providerUrl</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>enableTLSSessionReuse</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>odatapagesize</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>system</key>
                    <value>Receiver3</value>
                </ifl:property>
                <ifl:property>
                    <key>authenticationMethod</key>
                    <value>None</value>
                </ifl:property>
                <ifl:property>
                    <key>whitelistResponseHeaders</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>enableBatchProcessing</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>characterEncoding</key>
                    <value>none</value>
                </ifl:property>
                <ifl:property>
                    <key>fields</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::sap:HCIOData/tp::HTTP/mp::OData V2/direction::Receiver/version::1.25.1</value>
                </ifl:property>
                <ifl:property>
                    <key>whitelistRequestHeaders</key>
                    <value/>
                </ifl:property>

                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.25.1</value>
                </ifl:property>
                <ifl:property>
                    <key>providerRelativeUrl</key>
                    <value/>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''

        return {
            "service_task": service_task,
            "participant": participant,
            "message_flow": message_flow,
            "service_task_id": service_task_id,
            "participant_id": participant_id,
            "message_flow_id": message_flow_id
        }

    def http_request_reply_pattern(self, service_task_id, participant_id, message_flow_id, name, service_url, http_method="POST"):
        """Template for a complete HTTP request-reply pattern matching corrected .iflw structure"""

        # Service Task
        service_task = f'''<bpmn2:serviceTask id="{service_task_id}" name="{name}">
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
            <bpmn2:incoming>{{{{incoming_flow}}}}</bpmn2:incoming>
            <bpmn2:outgoing>{{{{outgoing_flow}}}}</bpmn2:outgoing>
        </bpmn2:serviceTask>'''

        # Participant (Use typo from working iFlow: EndpointRecevier not EndpointReceiver)
        participant = f'''<bpmn2:participant id="{participant_id}" ifl:type="EndpointRecevier" name="{name}_Receiver">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>ifl:type</key>
                    <value>EndpointRecevier</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:participant>'''

        # HTTP Message Flow (matching corrected .iflw structure)
        message_flow = f'''<bpmn2:messageFlow id="{message_flow_id}" name="HTTP" sourceRef="{service_task_id}" targetRef="{participant_id}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>Description</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>methodSourceExpression</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>allowedRequestHeaders</key>
                    <value>*</value>
                </ifl:property>
                <ifl:property>
                    <key>httpMethod</key>
                    <value>{http_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>allowedResponseHeaders</key>
                    <value>*</value>
                </ifl:property>
                <ifl:property>
                    <key>Name</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>internetProxyType</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocolVersion</key>
                    <value>1.16.2</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVName</key>
                    <value>external</value>
                </ifl:property>
                <ifl:property>
                    <key>enableMPLAttachments</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>httpAddressQuery</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>httpRequestTimeout</key>
                    <value>60000</value>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocol</key>
                    <value>None</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentSWCVId</key>
                    <value>1.16.2</value>
                </ifl:property>
                <ifl:property>
                    <key>direction</key>
                    <value>Receiver</value>
                </ifl:property>
                <ifl:property>
                    <key>ComponentType</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>httpShouldSendBody</key>
                    <value>false</value>
                </ifl:property>
                <ifl:property>
                    <key>throwExceptionOnFailure</key>
                    <value>true</value>
                </ifl:property>
                <ifl:property>
                    <key>proxyType</key>
                    <value>default</value>
                </ifl:property>
                <ifl:property>
                    <key>address</key>
                    <value>{service_url}</value>
                </ifl:property>
                <ifl:property>
                    <key>TransportProtocol</key>
                    <value>HTTP</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.16.2</value>
                </ifl:property>
                <ifl:property>
                    <key>credentialName</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>httpErrorResponseCodes</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>MessageProtocolVersion</key>
                    <value>1.16.2</value>
                </ifl:property>
                <ifl:property>
                    <key>httpAddressWithoutQuery</key>
                    <value/>
                </ifl:property>
                <ifl:property>
                    <key>providerRelativeUrl</key>
                    <value/>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:messageFlow>'''

        return {
            "service_task": service_task,
            "participant": participant,
            "message_flow": message_flow,
            "service_task_id": service_task_id,
            "participant_id": participant_id,
            "message_flow_id": message_flow_id
        }

    def comprehensive_request_reply_template(self, id, name, endpoint_path="", log_level="Information"):
        """
        Template for a comprehensive Request-Reply pattern with logging and error handling

        This template creates a complete request-reply flow with:
        1. API Endpoint (Enricher)
        2. Request Logger
        3. Request Validation
        4. Parameter Extraction
        5. Parameter Logger
        6. External Service Call
        7. Response Logger
        8. Error Logger
        9. Error Response Handler

        Args:
            id (str): Base Component ID (will be used as prefix)
            name (str): Base Component name
            endpoint_path (str): API endpoint path
            log_level (str): Logging level

        Returns:
            dict: Dictionary containing all components for the request-reply pattern
        """
        # Generate unique IDs for all components
        api_endpoint_id = f"{id}_Endpoint"
        request_logger_id = f"{id}_ReqLogger"
        request_validator_id = f"{id}_Validator"
        param_extractor_id = f"{id}_ParamExtractor"
        param_logger_id = f"{id}_ParamLogger"
        service_call_id = f"{id}_ServiceCall"
        response_logger_id = f"{id}_RespLogger"
        error_logger_id = f"{id}_ErrorLogger"
        error_response_id = f"{id}_ErrorResponse"
        end_event_id = f"{id}_End"

        # Generate sequence flow IDs
        seq_flow_1_id = f"SequenceFlow_{id}_1"
        seq_flow_2_id = f"SequenceFlow_{id}_2"
        seq_flow_3_id = f"SequenceFlow_{id}_3"
        seq_flow_4_id = f"SequenceFlow_{id}_4"
        seq_flow_5_id = f"SequenceFlow_{id}_5"
        seq_flow_6_id = f"SequenceFlow_{id}_6"
        seq_flow_7_id = f"SequenceFlow_{id}_7"
        seq_flow_8_id = f"SequenceFlow_{id}_8"
        seq_flow_last_id = f"SequenceFlow_{id}_Last"

        # Create components
        api_endpoint = f'''<bpmn2:callActivity id="{api_endpoint_id}" name="{name} API Endpoint">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>bodyType</key>
                    <value>constant</value>
                </ifl:property>
                <ifl:property>
                    <key>propertyTable</key>
                    <value>[]</value>
                </ifl:property>
                <ifl:property>
                    <key>headerTable</key>
                    <value>[]</value>
                </ifl:property>
                <ifl:property>
                    <key>wrapContent</key>
                    <value></value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.5</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Enricher</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::Enricher/version::1.5.1</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_Start</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_1_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        request_logger = f'''<bpmn2:callActivity id="{request_logger_id}" name="Logger - Request Received">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>logLevel</key>
                    <value>{log_level}</value>
                </ifl:property>
                <ifl:property>
                    <key>logText</key>
                    <value>Request Received for {name}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>WriteLog</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::WriteLog/version::1.2.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_1_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_2_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        request_validator = f'''<bpmn2:callActivity id="{request_validator_id}" name="Validate Request">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentType</key>
                    <value>content_modifier</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_2_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_3_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        param_extractor = f'''<bpmn2:callActivity id="{param_extractor_id}" name="Extract Parameters">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentType</key>
                    <value>content_modifier_header</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_3_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_4_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        param_logger = f'''<bpmn2:callActivity id="{param_logger_id}" name="Log Parameters">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>logLevel</key>
                    <value>{log_level}</value>
                </ifl:property>
                <ifl:property>
                    <key>logText</key>
                    <value>Parameters for {name}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>WriteLog</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::WriteLog/version::1.2.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_4_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_5_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        service_call = f'''<bpmn2:callActivity id="{service_call_id}" name="Call External Service">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentType</key>
                    <value>router</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_5_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_6_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        response_logger = f'''<bpmn2:callActivity id="{response_logger_id}" name="Response Logger">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>logLevel</key>
                    <value>{log_level}</value>
                </ifl:property>
                <ifl:property>
                    <key>logText</key>
                    <value>Response from External Service</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>WriteLog</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::WriteLog/version::1.2.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_6_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_7_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        error_logger = f'''<bpmn2:callActivity id="{error_logger_id}" name="Error Logger">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>logLevel</key>
                    <value>{log_level}</value>
                </ifl:property>
                <ifl:property>
                    <key>logText</key>
                    <value>Error Logger</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.2</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>WriteLog</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::WriteLog/version::1.2.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_7_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_8_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        error_response = f'''<bpmn2:callActivity id="{error_response_id}" name="Error Response">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>bodyType</key>
                    <value>constant</value>
                </ifl:property>
                <ifl:property>
                    <key>propertyTable</key>
                    <value>[]</value>
                </ifl:property>
                <ifl:property>
                    <key>headerTable</key>
                    <value>[]</value>
                </ifl:property>
                <ifl:property>
                    <key>wrapContent</key>
                    <value></value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.5</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>Enricher</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::Enricher/version::1.5.1</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{seq_flow_8_id}</bpmn2:incoming>
            <bpmn2:outgoing>{seq_flow_last_id}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

        end_event = f'''<bpmn2:endEvent id="{end_event_id}" name="End">
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
            <bpmn2:incoming>{seq_flow_last_id}</bpmn2:incoming>
            <bpmn2:messageEventDefinition/>
        </bpmn2:endEvent>'''

        # Create sequence flows
        seq_flow_1 = f'''<bpmn2:sequenceFlow id="{seq_flow_1_id}" sourceRef="{api_endpoint_id}" targetRef="{request_logger_id}" isImmediate="true"/>'''
        seq_flow_2 = f'''<bpmn2:sequenceFlow id="{seq_flow_2_id}" sourceRef="{request_logger_id}" targetRef="{request_validator_id}" isImmediate="true"/>'''
        seq_flow_3 = f'''<bpmn2:sequenceFlow id="{seq_flow_3_id}" sourceRef="{request_validator_id}" targetRef="{param_extractor_id}" isImmediate="true"/>'''
        seq_flow_4 = f'''<bpmn2:sequenceFlow id="{seq_flow_4_id}" sourceRef="{param_extractor_id}" targetRef="{param_logger_id}" isImmediate="true"/>'''
        seq_flow_5 = f'''<bpmn2:sequenceFlow id="{seq_flow_5_id}" sourceRef="{param_logger_id}" targetRef="{service_call_id}" isImmediate="true"/>'''
        seq_flow_6 = f'''<bpmn2:sequenceFlow id="{seq_flow_6_id}" sourceRef="{service_call_id}" targetRef="{response_logger_id}" isImmediate="true"/>'''
        seq_flow_7 = f'''<bpmn2:sequenceFlow id="{seq_flow_7_id}" sourceRef="{response_logger_id}" targetRef="{error_logger_id}" isImmediate="true"/>'''
        seq_flow_8 = f'''<bpmn2:sequenceFlow id="{seq_flow_8_id}" sourceRef="{error_logger_id}" targetRef="{error_response_id}" isImmediate="true"/>'''
        seq_flow_last = f'''<bpmn2:sequenceFlow id="{seq_flow_last_id}" sourceRef="{error_response_id}" targetRef="{end_event_id}" isImmediate="true"/>'''

        # Return all components and flows
        return {
            "components": [
                api_endpoint,
                request_logger,
                request_validator,
                param_extractor,
                param_logger,
                service_call,
                response_logger,
                error_logger,
                error_response,
                end_event
            ],
            "sequence_flows": [
                seq_flow_1,
                seq_flow_2,
                seq_flow_3,
                seq_flow_4,
                seq_flow_5,
                seq_flow_6,
                seq_flow_7,
                seq_flow_8,
                seq_flow_last
            ],
            "start_component_id": api_endpoint_id,
            "end_component_id": end_event_id
        }

    def groovy_script_template(self, id, name, script_name="", script_function="", script_content=""):
        """
        Template for Groovy Script (SAP Integration Suite compatible)

        Args:
            id (str): Component ID
            name (str): Component name
            script_name (str): Name of the Groovy script file (e.g., "validation.groovy")
            script_function (str): Name of the function to call in the script
            script_content (str): Inline script content (fallback if no file reference)

        Returns:
            str: XML template for Groovy Script
        """
        # Always use script file name if provided, otherwise use inline content
        script_value = script_name if script_name and script_name != "GroovyScript.groovy" else script_content
        
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>scriptFunction</key>
                    <value>{script_function}</value>
                </ifl:property>
                <ifl:property>
                    <key>scriptBundleId</key>
                    <value/>
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
                    <value>{script_value}</value>
                </ifl:property>

            </bpmn2:extensionElements>
        </bpmn2:callActivity>'''

    def mapping_template(self, id, name, mapping_name, mapping_path):
        """
        Template for Message Mapping

        Args:
            id (str): Component ID
            name (str): Component name
            mapping_name (str): Name of the mapping
            mapping_path (str): Path to the mapping file

        Returns:
            str: XML template for Message Mapping
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>mappinguri</key>
                    <value>dir://{mapping_path}.mmap</value>
                </ifl:property>
                <ifl:property>
                    <key>mappingname</key>
                    <value>{mapping_name}</value>
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
                    <value>{mapping_path}</value>
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
            <bpmn2:incoming>SequenceFlow_In</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_Out</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def router_template(self, id, name, conditions=[]):
        """
        Template for Router (Exclusive Gateway) with fixed ID
        """
        # Make sure this is an exclusive gateway, not a callActivity
        return f'''<bpmn2:exclusiveGateway id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.3</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>ExclusiveGateway</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.3.0</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>SequenceFlow_1</bpmn2:incoming>
            <bpmn2:outgoing>SequenceFlow_2</bpmn2:outgoing>
        </bpmn2:exclusiveGateway>'''

    def router_condition_template(self, id, name, source_ref, target_ref, expression="", expression_type="NonXML"):
        """
        Template for Router Condition (Gateway Route)

        Args:
            id (str): Sequence flow ID
            name (str): Route name
            source_ref (str): Source component ID (router ID)
            target_ref (str): Target component ID
            expression (str): Condition expression
            expression_type (str): Expression type (NonXML/XML)

        Returns:
            str: XML template for Router Condition
        """
        condition_element = ""
        if expression:
            condition_element = f'<bpmn2:conditionExpression id="FormalExpression_{id}" xsi:type="bpmn2:tFormalExpression">{expression}</bpmn2:conditionExpression>'

        return f'''<bpmn2:sequenceFlow id="{id}" name="{name}" sourceRef="{source_ref}" targetRef="{target_ref}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>expressionType</key>
                    <value>{expression_type}</value>
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
            {condition_element}
        </bpmn2:sequenceFlow>'''

    # ===== Flow Control =====

    def sequence_flow_template(self, id, source_ref, target_ref, is_immediate="true"):
        """
        Template for Sequence Flow with proper immediate attribute

        Args:
            id (str): ID of the sequence flow
            source_ref (str): ID of the source component
            target_ref (str): ID of the target component
            is_immediate (str): Whether the flow is immediate ("true"/"false")

        Returns:
            str: XML template for Sequence Flow
        """
        return f'''<bpmn2:sequenceFlow id="{id}" sourceRef="{source_ref}" targetRef="{target_ref}" isImmediate="{is_immediate}"/>'''

    def process_template(self, id, name, transaction_timeout="30", transactional_handling="Not Required"):
        """
        Template for Integration Process with correct placeholder

        Args:
            id (str): Process ID
            name (str): Process name
            transaction_timeout (str): Transaction timeout in seconds
            transactional_handling (str): Transactional handling mode

        Returns:
            str: XML template for Integration Process
        """
        return f'''<bpmn2:process id="{id}" name="{name}" isExecutable="true">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>transactionTimeout</key>
                <value>{transaction_timeout}</value>
            </ifl:property>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.2</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::FlowElementVariant/cname::IntegrationProcess/version::1.2.1</value>
            </ifl:property>
            <ifl:property>
                <key>transactionalHandling</key>
                <value>{transactional_handling}</value>
            </ifl:property>
        </bpmn2:extensionElements>
        {{process_content}}
    </bpmn2:process>'''
    # ===== Helper Methods =====

    def generate_unique_id(self, prefix=""):
        """
        Generate a unique ID for a component with better collision avoidance
        """
        import time
        import uuid

        unique_id = str(uuid.uuid4()).replace('-', '')[:8]
        timestamp = str(int(time.time() * 1000))[-4:]  # Last 4 digits of current timestamp in milliseconds

        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}"
        return f"ID_{timestamp}_{unique_id}"

    def generate_iflow_xml(self, collaboration_content, process_content, additional_processes=None):
        """
        Generate complete iFlow XML

        Args:
            collaboration_content (str): XML content for collaboration section
            process_content (str): XML content for process section
            additional_processes (list, optional): List of additional process definitions

        Returns:
            str: Complete iFlow XML
        """
        # Make sure process_content doesn't contain any unresolved placeholders
        if "{{process_content}}" in process_content:
            print("Warning: process_content still contains unresolved placeholder!")

        # Prepare additional processes content
        additional_processes_content = ""
        if additional_processes:
            additional_processes_content = "\n    " + "\n    ".join(additional_processes)

        # Use string concatenation instead of f-string to avoid issues with curly braces
        xml_template = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
            '<bpmn2:definitions xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL"\n' + \
            '                   xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"\n' + \
            '                   xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"\n' + \
            '                   xmlns:di="http://www.omg.org/spec/DD/20100524/DI"\n' + \
            '                   xmlns:ifl="http:///com.sap.ifl.model/Ifl.xsd"\n' + \
            '                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="Definitions_1">\n' + \
            '    <bpmn2:collaboration id="Collaboration_1" name="Default Collaboration">\n' + \
            '        {}\n' + \
            '    </bpmn2:collaboration>\n' + \
            '    {}\n' + \
            '    {}\n' + \
            '    <bpmndi:BPMNDiagram id="BPMNDiagram_1" name="Default Collaboration Diagram">\n' + \
            '        <bpmndi:BPMNPlane bpmnElement="Collaboration_1" id="BPMNPlane_1">\n' + \
            '            <!-- Diagram layout information would go here -->\n' + \
            '        </bpmndi:BPMNPlane>\n' + \
            '    </bpmndi:BPMNDiagram>\n' + \
            '</bpmn2:definitions>'

        # Format the XML template with the provided content
        return xml_template.format(collaboration_content, process_content, additional_processes_content)

    # ===== SFTP Receiver Components =====

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

    def sftp_component_template(self, id, name, host="sftp.example.com", port="22", path="/uploads", username="${sftp_username}",
                               auth_type="Password", operation="PUT"):
        """Generate a main SFTP component template for file operations."""
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
    <dc:Bounds height="80.0" width="100.0" x="400" y="140"/>
</bpmndi:BPMNShape>'''

        return {"definition": definition, "shape": shape}

    def sftp_receiver_message_flow_template(self, id="MessageFlow_SFTP", name="SFTP", source_ref="ServiceTask_1", target_ref="Participant_SFTP",
                                          host="sftp.example.com", port="22", path="/uploads", username="${sftp_username}",
                                          auth_type="Password", operation="PUT"):
        """Generate an SFTP receiver message flow template."""
        definition = f'''<bpmn2:messageFlow id="{id}" name="{name}" sourceRef="{source_ref}" targetRef="{target_ref}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>disconnect</key>
            <value>0</value>
        </ifl:property>
        <ifl:property>
            <key>fileName</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>Description</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>maximumReconnectAttempts</key>
            <value>3</value>
        </ifl:property>
        <ifl:property>
            <key>stepwise</key>
            <value>1</value>
        </ifl:property>
        <ifl:property>
            <key>fileExist</key>
            <value>Override</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>autoCreate</key>
            <value>1</value>
        </ifl:property>
        <ifl:property>
            <key>privateKeyAlias</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>location_id</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>Name</key>
            <value>SFTP</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocolVersion</key>
            <value>1.20.1</value>
        </ifl:property>
        <ifl:property>
            <key>flatten</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>sftpSecEnabled</key>
            <value>1</value>
        </ifl:property>
        <ifl:property>
            <key>useTempFile</key>
            <value>0</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVName</key>
            <value>external</value>
        </ifl:property>
        <ifl:property>
            <key>path</key>
            <value>{path}</value>
        </ifl:property>
        <ifl:property>
            <key>proxyPort</key>
            <value>8080</value>
        </ifl:property>
        <ifl:property>
            <key>host</key>
            <value>{host}</value>
        </ifl:property>
        <ifl:property>
            <key>connectTimeout</key>
            <value>10000</value>
        </ifl:property>
        <ifl:property>
            <key>fastExistsCheck</key>
            <value>1</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocol</key>
            <value>File</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVId</key>
            <value>1.20.1</value>
        </ifl:property>
        <ifl:property>
            <key>direction</key>
            <value>Receiver</value>
        </ifl:property>
        <ifl:property>
            <key>authentication</key>
            <value>public_key</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentType</key>
            <value>SFTP</value>
        </ifl:property>
        <ifl:property>
            <key>fileAppendTimeStamp</key>
            <value>0</value>
        </ifl:property>
        <ifl:property>
            <key>credential_name</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>proxyProtocol</key>
            <value>socks5</value>
        </ifl:property>
        <ifl:property>
            <key>proxyType</key>
            <value>none</value>
        </ifl:property>
        <ifl:property>
            <key>proxyAlias</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.13</value>
        </ifl:property>
        <ifl:property>
            <key>reconnectDelay</key>
            <value>1000</value>
        </ifl:property>
        <ifl:property>
            <key>proxyHost</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>system</key>
            <value>{target_ref}</value>
        </ifl:property>
        <ifl:property>
            <key>tempFileName</key>
            <value>${{file:name}}.tmp</value>
        </ifl:property>
        <ifl:property>
            <key>allowDeprecatedAlgorithms</key>
            <value>0</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocol</key>
            <value>SFTP</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::AdapterVariant/cname::sap:SFTP/tp::SFTP/mp::File/direction::Receiver/version::1.13.3</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocolVersion</key>
            <value>1.20.1</value>
        </ifl:property>
        <ifl:property>
            <key>username</key>
            <value>{username}</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>'''

        edge = f'''<bpmndi:BPMNEdge bpmnElement="{id}" id="BPMNEdge_{id}" sourceElement="BPMNShape_{source_ref}" targetElement="BPMNShape_{target_ref}">
    <di:waypoint x="757" xsi:type="dc:Point" y="140"/>
    <di:waypoint x="850" xsi:type="dc:Point" y="170"/>
</bpmndi:BPMNEdge>'''

        return {"definition": definition, "edge": edge}

    # ===== SuccessFactors OData Receiver Components =====

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

    # ===== Request-Reply Service Task Components =====

    def request_reply_template(self, id, name, incoming_flow="{{incoming_flow}}", outgoing_flow="{{outgoing_flow}}"):
        """Generate a request-reply service task template based on SAP sample."""
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

        return definition

    # ===== Process Call Activity Components =====

    def process_call_template(self, id, name, process_id="Process_1", incoming_flow="{{incoming_flow}}", outgoing_flow="{{outgoing_flow}}"):
        """Generate a process call activity template for Local Integration Process."""
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
            <value>ctype::FlowstepVariant/cname::NonLoopingProcess/version::1.0.4</value>
        </ifl:property>
        <ifl:property>
            <key>subActivityType</key>
            <value>NonLoopingProcess</value>
        </ifl:property>
        <ifl:property>
            <key>transactionalHandling</key>
            <value>From Calling Process</value>
        </ifl:property>
        <ifl:property>
            <key>transactionTimeout</key>
            <value>30</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        return definition

    # ===== Local Integration Process Components =====

    def local_integration_process_template(self, id="Process_1", name="Local Integration Process 1"):
        """Generate a local integration process template."""
        definition = f'''<bpmn2:process id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>transactionTimeout</key>
            <value>30</value>
        </ifl:property>
        <ifl:property>
            <key>processType</key>
            <value>directCall</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowElementVariant/cname::LocalIntegrationProcess/version::1.1.3</value>
        </ifl:property>
        <ifl:property>
            <key>transactionalHandling</key>
            <value>From Calling Process</value>
        </ifl:property>
    </bpmn2:extensionElements>
    {{process_content}}
</bpmn2:process>'''

        return definition

    # ===== Enhanced Groovy Script Components =====

    def enhanced_groovy_script_template(self, id, name, script_name="script.groovy", script_function="processMessage", incoming_flow="{{incoming_flow}}", outgoing_flow="{{outgoing_flow}}"):
        """Generate an enhanced Groovy script template for Local Integration Process."""
        definition = f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>scriptFunction</key>
            <value>{script_function}</value>
        </ifl:property>
        <ifl:property>
            <key>scriptBundleId</key>
            <value/>
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
            <value>{script_name}</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
</bpmn2:callActivity>'''

        return definition

    # ===== Enhanced Start Event Components =====

    def enhanced_start_event_template(self, id="StartEvent_1", name="Start 1"):
        """Generate an enhanced start event template for Local Integration Process."""
        definition = f'''<bpmn2:startEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::StartEvent/version::1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>StartEvent</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:outgoing>{{outgoing_flow}}</bpmn2:outgoing>
</bpmn2:startEvent>'''

        return definition

    # ===== Enhanced End Event Components =====

    def enhanced_end_event_template(self, id="EndEvent_1", name="End 1", incoming_flow="{{incoming_flow}}"):
        """Generate an enhanced end event template for Local Integration Process."""
        definition = f'''<bpmn2:endEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::EndEvent/version::1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>EndEvent</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
</bpmn2:endEvent>'''

        return definition
