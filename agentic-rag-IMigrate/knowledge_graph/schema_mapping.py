"""
Schema Mapping for SAP iFlow Neo4j Database.
Maps conceptual table descriptions to actual Neo4j node labels and relationships.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class SchemaMapping:
    """Mapping between conceptual tables and actual Neo4j schema."""
    conceptual_table: str
    actual_node_label: str
    purpose: str
    key_properties: List[str]
    description: str
    sample_query: str


class IFlowSchemaMapper:
    """Maps conceptual iFlow tables to actual Neo4j schema."""
    
    def __init__(self):
        """Initialize schema mappings."""
        self.mappings = {
            # Conceptual Table 1: iflow_packages
            "iflow_packages": SchemaMapping(
                conceptual_table="iflow_packages",
                actual_node_label="Process",  # Maps to Process nodes in Neo4j
                purpose="Package metadata and process definitions",
                key_properties=["id", "name", "type", "folder_id"],
                description="Process nodes represent iFlow packages/processes with their metadata",
                sample_query="MATCH (p:Process) RETURN p.id, p.name, p.type LIMIT 10"
            ),
            
            # Conceptual Table 2: iflow_components ⭐ MAIN DATA
            "iflow_components": SchemaMapping(
                conceptual_table="iflow_components", 
                actual_node_label="Component",  # Maps to Component nodes in Neo4j
                purpose="Individual BPMN components (events, tasks, gateways)",
                key_properties=["id", "name", "type", "folder_id"],
                description="Component nodes represent individual BPMN elements like start events, tasks, gateways",
                sample_query="MATCH (c:Component) RETURN c.id, c.name, c.type, c.folder_id LIMIT 10"
            ),
            
            # Conceptual Table 3: iflow_flows 🔄 CONNECTIONS
            "iflow_flows": SchemaMapping(
                conceptual_table="iflow_flows",
                actual_node_label="RELATIONSHIP",  # Maps to relationships between Component nodes
                purpose="All flow connections (sequence + message flows)",
                key_properties=["FLOWS_TO", "CONNECTS_TO", "INVOKES", "RECEIVES_FROM"],
                description="Relationships between Component nodes represent flow connections",
                sample_query="MATCH (c1:Component)-[r:FLOWS_TO]->(c2:Component) RETURN type(r), c1.name, c2.name LIMIT 10"
            ),
            
            # Conceptual Table 4: iflow_assets 📁 FILES
            "iflow_assets": SchemaMapping(
                conceptual_table="iflow_assets",
                actual_node_label="SubProcess/Protocol",  # Maps to SubProcess and Protocol nodes
                purpose="Scripts, schemas, mappings, properties",
                key_properties=["id", "name", "type"],
                description="SubProcess and Protocol nodes represent different types of assets and configurations",
                sample_query="MATCH (s:SubProcess) RETURN s.id, s.name, s.type LIMIT 5 UNION MATCH (p:Protocol) RETURN p.id, p.name, p.type LIMIT 5"
            ),
            
            # Additional mapping for folders/containers
            "iflow_containers": SchemaMapping(
                conceptual_table="iflow_containers",
                actual_node_label="Folder",  # Maps to Folder nodes
                purpose="Organizational containers for iFlow elements",
                key_properties=["id", "name", "type"],
                description="Folder nodes represent organizational containers that group related iFlow elements",
                sample_query="MATCH (f:Folder) RETURN f.id, f.name, f.type LIMIT 10"
            )
        }
    
    def get_mapping(self, conceptual_table: str) -> SchemaMapping:
        """Get mapping for a conceptual table."""
        return self.mappings.get(conceptual_table)
    
    def get_actual_node_label(self, conceptual_table: str) -> str:
        """Get the actual Neo4j node label for a conceptual table."""
        mapping = self.mappings.get(conceptual_table)
        return mapping.actual_node_label if mapping else None
    
    def get_all_mappings(self) -> Dict[str, SchemaMapping]:
        """Get all schema mappings."""
        return self.mappings
    
    def get_purpose_description(self) -> str:
        """Get a formatted description of the database purpose."""
        description = """
SAP iFlow Neo4j Database Schema Mapping:

🏗️ **DATABASE PURPOSE**: Store and analyze SAP iFlow integration patterns, components, and relationships

📊 **CONCEPTUAL VS ACTUAL SCHEMA**:

**Table 1: iflow_packages** → **Process nodes**
• Purpose: Package metadata and reconstructed process definitions  
• Records: Process definitions and their properties
• Key Fields: id, name, type, folder_id
• Neo4j Query: MATCH (p:Process) RETURN p

**Table 2: iflow_components** ⭐ **Component nodes** (MAIN DATA)
• Purpose: Individual BPMN components (events, tasks, gateways)
• Records: 1,684+ individual components from iFlow processes
• Key Fields: id, name, type, folder_id  
• Neo4j Query: MATCH (c:Component) RETURN c

**Table 3: iflow_flows** 🔄 **Relationships** (CONNECTIONS)  
• Purpose: All flow connections (sequence + message flows)
• Records: 11,439+ relationships between components
• Key Types: FLOWS_TO, CONNECTS_TO, INVOKES, RECEIVES_FROM
• Neo4j Query: MATCH ()-[r]->() RETURN type(r), count(r)

**Table 4: iflow_assets** 📁 **SubProcess/Protocol nodes** (FILES)
• Purpose: Scripts, schemas, mappings, properties
• Records: Additional assets and configuration elements
• Key Fields: id, name, type
• Neo4j Query: MATCH (n) WHERE n:SubProcess OR n:Protocol RETURN n

🎯 **TOTAL DATABASE SIZE**: 2,780 nodes, 11,439 relationships
🏷️ **NODE TYPES**: Component, Process, SubProcess, Protocol, Folder, Participant
"""
        return description.strip()
    
    def validate_schema(self, driver) -> Dict[str, Any]:
        """Validate that the actual schema matches our mappings."""
        # This would be implemented to verify the Neo4j database schema
        pass


# Global instance for easy access
schema_mapper = IFlowSchemaMapper()




