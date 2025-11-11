"""
Metadata Template Loader

Loads and indexes the components.json metadata template to provide
component definitions, default values, and type mappings.
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class MetadataTemplateLoader:
    """Loads and indexes component metadata from components.json"""
    
    def __init__(self, metadata_path: Optional[str] = None):
        """
        Initialize the metadata loader
        
        Args:
            metadata_path: Path to components.json. If None, uses default location
        """
        if metadata_path is None:
            # Default to metadata_template/components.json relative to this file
            base_dir = Path(__file__).parent.parent
            metadata_path = str(base_dir / "metadata_template" / "components.json")
        
        self.metadata_path = metadata_path
        self.metadata = self._load_metadata()
        self.component_templates = self._extract_component_templates()
        self.type_mapping = self._build_type_mapping()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load the components.json metadata file"""
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in metadata file: {e}")
    
    def _extract_component_templates(self) -> Dict[str, Dict[str, Any]]:
        """Extract component templates from metadata"""
        component_templates = {}
        
        if "component_templates" in self.metadata:
            for key, value in self.metadata["component_templates"].items():
                # Skip comment entries
                if key.startswith("//"):
                    continue
                
                # Extract component info
                if isinstance(value, dict) and "type" in value:
                    comp_type = value.get("type", "")
                    component_templates[comp_type] = value
        
        return component_templates
    
    def _build_type_mapping(self) -> Dict[str, str]:
        """
        Build mapping from component type to template method name
        
        Returns:
            Dict mapping component type to method name (e.g., "message_mapping" -> "message_mapping_template")
        """
        mapping = {}
        for comp_type, template_def in self.component_templates.items():
            # Convert type to method name: "message_mapping" -> "message_mapping_template"
            method_name = f"{comp_type}_template"
            mapping[comp_type] = method_name
        return mapping
    
    def get_component_template(self, component_type: str) -> Optional[Dict[str, Any]]:
        """
        Get component template definition by type
        
        Args:
            component_type: Component type (e.g., "message_mapping", "router")
            
        Returns:
            Component template definition or None if not found
        """
        return self.component_templates.get(component_type)
    
    def get_template_method_name(self, component_type: str) -> Optional[str]:
        """
        Get template method name for component type
        
        Args:
            component_type: Component type
            
        Returns:
            Method name (e.g., "message_mapping_template") or None
        """
        return self.type_mapping.get(component_type)
    
    def get_all_component_types(self) -> List[str]:
        """Get list of all supported component types"""
        return list(self.component_templates.keys())
    
    def get_default_config(self, component_type: str) -> Dict[str, Any]:
        """
        Get default configuration for a component type
        
        Args:
            component_type: Component type
            
        Returns:
            Default config dictionary with placeholder values
        """
        template = self.get_component_template(component_type)
        if template and "config" in template:
            return template["config"].copy()
        return {}
    
    def get_sap_activity_type(self, component_type: str) -> Optional[str]:
        """
        Get SAP activity type for a component
        
        Args:
            component_type: Component type
            
        Returns:
            SAP activity type (e.g., "MessageMapping", "ExclusiveGateway") or None
        """
        template = self.get_component_template(component_type)
        if template:
            return template.get("sap_activity_type")
        return None




