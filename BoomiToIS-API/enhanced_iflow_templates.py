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
                    <value define="true">{address}</value>
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

    def filter_template(self, id, name, xpath_type="Integer", wrap_content="", incoming_flow="{{incoming_flow}}", outgoing_flow="{{outgoing_flow}}"):
        """
        Template for Filter component

        Args:
            id (str): Component ID
            name (str): Component name
            xpath_type (str): XPath type (e.g., "Integer"), defaults to "Integer"
            wrap_content (str): XPath filter expression (e.g., "//Customers[Status = '${property.CustomerStatus}']")
            incoming_flow (str): Incoming sequence flow ID, defaults to placeholder
            outgoing_flow (str): Outgoing sequence flow ID, defaults to placeholder

        Returns:
            str: XML template for Filter
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
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

    def message_digest_template(self, id, name, filter_value="", canonicalization_method="xml-c14n", target_header="SAPMessageDigest", digest_algorithm="SHA-512", incoming_flow="{{incoming_flow}}", outgoing_flow="{{outgoing_flow}}"):
        """
        Template for Message Digest component

        Args:
            id (str): Component ID
            name (str): Component name
            filter_value (str): Optional filter expression to select content for digest
            canonicalization_method (str): Canonicalization method (e.g., "xml-c14n")
            target_header (str): Header to store digest (e.g., "SAPMessageDigest")
            digest_algorithm (str): Digest algorithm (e.g., "SHA-512")
            incoming_flow (str): Incoming sequence flow ID, defaults to placeholder
            outgoing_flow (str): Outgoing sequence flow ID, defaults to placeholder

        Returns:
            str: XML template for Message Digest
        """
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>filter</key>
                    <value>{filter_value}</value>
                </ifl:property>
                <ifl:property>
                    <key>canonicalizationMethod</key>
                    <value>{canonicalization_method}</value>
                </ifl:property>
                <ifl:property>
                    <key>targetHeader</key>
                    <value>{target_header}</value>
                </ifl:property>
                <ifl:property>
                    <key>digestAlgorithm</key>
                    <value>{digest_algorithm}</value>
                </ifl:property>
                <ifl:property>
                    <key>componentVersion</key>
                    <value>1.1</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>MessageDigest</value>
                </ifl:property>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::MessageDigest/version::1.1.1</value>
                </ifl:property>
            </bpmn2:extensionElements>
            <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
            <bpmn2:outgoing>{outgoing_flow}</bpmn2:outgoing>
        </bpmn2:callActivity>'''

    def router_template(self, id, name, default_flow_id=None):
        """
        Template for Router (Exclusive Gateway) component.
        
        Generates BPMN2 ExclusiveGateway XML with SAP Integration Suite properties.
        Supports default route specification for exclusive gateways.
        
        Args:
            id (str): Component ID (e.g., "gateway_1")
            name (str): Component name (e.g., "RateLimitExceeded")
            default_flow_id (str, optional): Sequence flow ID for default route when default=true in routing_conditions
            
        Returns:
            str: XML template for Exclusive Gateway
        """
        default_attr = f' default="{default_flow_id}"' if default_flow_id else ""
        
        return f'''<bpmn2:exclusiveGateway{default_attr} id="{id}" name="{name}">
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

    def router_condition_template(self, id, name, source_ref, target_ref, expression="", expression_type="XML", raw_condition_xml: str = None):
        """
        Template for Router Condition (Gateway Route sequence flow).
        
        Generates BPMN2 sequence flow XML with GatewayRoute metadata for router branching.
        Supports explicit XPath expressions from JSON metadata routing_conditions.
        
        Args:
            id (str): Sequence flow ID (e.g., "flow_gateway_1_to_script_2_0")
            name (str): Route name (e.g., "Route 1")
            source_ref (str): Router component ID (e.g., "gateway_1")
            target_ref (str): Target component ID (e.g., "script_2")
            expression (str): XPath expression from JSON condition field (e.g., "${property.rate_limit_exceeded == false}")
            expression_type (str): Expression type, defaults to "XML"
            raw_condition_xml (str): Optional raw <bpmn2:conditionExpression .../> XML to embed verbatim
            
        Returns:
            str: XML template for Gateway Route sequence flow
        """
        import time
        
        # Build conditionExpression element:
        # Priority 1: If raw_condition_xml provided by metadata, embed verbatim
        # Priority 2: If expression provided (conditional), include EMPTY conditionExpression element (match reference)
        # Priority 3: Default route (no expression) → omit conditionExpression entirely
        condition_expr = ""
        if raw_condition_xml and raw_condition_xml.strip():
            # Insert raw XML as-is, ensuring it appears on a new line with proper indentation
            condition_expr = f"\n            {raw_condition_xml.strip()}"
        elif expression and expression.strip():
            # Conditional route with expression from metadata → include expression content inside conditionExpression
            # Escape XML special characters in expression (only &, <, > as XPath expressions may contain these)
            expression_content = expression.strip()
            # Escape XML special characters: & < >
            expression_content = expression_content.replace("&", "&amp;")
            expression_content = expression_content.replace("<", "&lt;")
            expression_content = expression_content.replace(">", "&gt;")
            expression_id = f"FormalExpression_{id}_{int(time.time() * 1000)}"
            condition_expr = f"\n            <bpmn2:conditionExpression id=\"{expression_id}\" xsi:type=\"bpmn2:tFormalExpression\">{expression_content}</bpmn2:conditionExpression>"
        # else: Default route → no conditionExpression
        
        # Build sequence flow XML
        xml_content = f'''<bpmn2:sequenceFlow id="{id}" name="{name}" sourceRef="{source_ref}" targetRef="{target_ref}">
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
            </bpmn2:extensionElements>{condition_expr}
        </bpmn2:sequenceFlow>'''
        
        return xml_content

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
            <ifl:property>
                <key>isTransactional</key>
                <value>false</value>
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

    def message_start_event_template(self, id="StartEvent_1", name="Start 1"):
        """Generate a message start event template for Integration Process with message event definition."""
        definition = f'''<bpmn2:startEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::MessageStartEvent</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:outgoing>{{outgoing_flow}}</bpmn2:outgoing>
    <bpmn2:messageEventDefinition/>
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

    def message_end_event_template(self, id="EndEvent_1", name="End 1", incoming_flow="{{incoming_flow}}"):
        """Generate a message end event template for Integration Process with message event definition."""
        definition = f'''<bpmn2:endEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''

        return definition

    # ===== Additional Templates from Supabase Activity Types =====

    def variables_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>activityType</key><value>Variables</value></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::Variables/version::1.0.0</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

    def gather_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>activityType</key><value>Gather</value></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::Gather/version::1.0.0</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

    def dbstorage_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>activityType</key><value>DBstorage</value></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::DBstorage/version::1.0.0</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

    def xml_modifier_template(self, id, name):
        return f'''<bpmn2:callActivity id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>activityType</key><value>XmlModifier</value></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.0</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::XmlModifier/version::1.0.0</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:callActivity>'''

    def start_error_event_template(self, id="StartEvent_Error_1", name="Error Start 1"):
        return f'''<bpmn2:startEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::ErrorStartEvent</value></ifl:property>
        <ifl:property><key>activityType</key><value>StartErrorEvent</value></ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:errorEventDefinition/>
</bpmn2:startEvent>'''

    def end_error_event_template(self, id="EndEvent_Error_1", name="Error End 1", incoming_flow="{{incoming_flow}}"):
        return f'''<bpmn2:endEvent id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value></ifl:property>
        <ifl:property><key>activityType</key><value>EndErrorEvent</value></ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>{incoming_flow}</bpmn2:incoming>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>'''

    def direct_call_process_template(self, id="Process_Direct", name="Direct Call Process"):
        return f'''<bpmn2:process id="{id}" name="{name}">
    <bpmn2:extensionElements>
        <ifl:property><key>transactionTimeout</key><value>30</value></ifl:property>
        <ifl:property><key>processType</key><value>directCall</value></ifl:property>
        <ifl:property><key>componentVersion</key><value>1.1</value></ifl:property>
        <ifl:property><key>cmdVariantUri</key><value>ctype::FlowElementVariant/cname::LocalIntegrationProcess/version::1.1.3</value></ifl:property>
    </bpmn2:extensionElements>
</bpmn2:process>'''
