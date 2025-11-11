"""
Enhanced iFlow Generator

Generates SAP Integration Suite iFlow packages from JSON metadata.
Uses enhanced_json_to_iflow_converter.py and enhanced_component_templates.py.
Supports all 76+ component types from components.json metadata template.
"""

import os
import json
import zipfile
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .enhanced_json_to_iflow_converter import EnhancedJSONToIFlowConverter


class EnhancedIFlowGenerator:
    """
    Generates complete SAP Integration Suite iFlow packages from JSON metadata.
    Creates ZIP files with proper folder structure, including scripts, mappings, and schemas.
    """
    
    def __init__(self):
        """Initialize the generator"""
        self.converter = EnhancedJSONToIFlowConverter()
    
    def generate_iflow(self, input_file: str, output_dir: str, iflow_name: str) -> str:
        """
        Generate complete iFlow package from JSON metadata file
        
        Args:
            input_file: Path to JSON metadata file
            output_dir: Directory to save the iFlow package
            iflow_name: Name of the iFlow
        
        Returns:
            Path to generated ZIP file
        """
        try:
            # Convert JSON to iFlow XML
            print(f"Reading metadata from: {input_file}")
            result = self.converter.convert(input_file)
            
            iflow_xml = result['iflow_xml']
            script_files = result['script_files']
            mapping_files = result['mapping_files']
            schema_files = result['schema_files']
            wsd_files = result.get('wsd_files', {})
            
            # Read JSON to get iflow_info
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            iflow_info = data.get("iflow_info", {})
            iflow_name = iflow_info.get("name", iflow_name)
            
            # Log package creation info
            print(f"\nCreating iFlow Package:")
            print(f"   iFlow Name: {iflow_name}")
            print(f"   Script files: {len(script_files)}")
            print(f"   Mapping files: {len(mapping_files)}")
            print(f"   Schema files: {len(schema_files)}")
            print(f"   WSD files: {len(wsd_files)}")
            
            # Create iFlow package
            zip_path = self._create_iflow_package(
                iflow_xml=iflow_xml,
                script_files=script_files,
                mapping_files=mapping_files,
                schema_files=schema_files,
                wsd_files=wsd_files,
                output_dir=output_dir,
                iflow_name=iflow_name,
                iflow_info=iflow_info
            )
            
            print(f"\n✅ iFlow package created: {zip_path}")
            return zip_path
            
        except Exception as e:
            raise Exception(f"Failed to generate iFlow: {str(e)}")
    
    def _create_iflow_package(self, iflow_xml: str, script_files: Dict[str, str], 
                              mapping_files: Dict[str, str], schema_files: Dict[str, str],
                              wsd_files: Dict[str, str], output_dir: str, iflow_name: str, iflow_info: Dict[str, Any]) -> str:
        """
        Create complete iFlow ZIP package with all required files
        
        Args:
            iflow_xml: Generated iFlow XML content
            script_files: Dictionary of script filenames to content
            mapping_files: Dictionary of mapping filenames to content
            schema_files: Dictionary of schema filenames to content
            wsd_files: Dictionary of WSD filenames to content
            output_dir: Output directory
            iflow_name: iFlow name (may contain spaces for display)
            iflow_info: iFlow info from JSON
        
        Returns:
            Path to ZIP file
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize iflow name for file paths (no spaces)
        sanitized_iflow_name = self._sanitize_name(iflow_name)
        
        # Create ZIP file (use sanitized name for file)
        zip_path = os.path.join(output_dir, f"{sanitized_iflow_name}.zip")
        
        print(f"   Creating ZIP file: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # META-INF/MANIFEST.MF
            print(f"   Adding: META-INF/MANIFEST.MF")
            manifest_content = self._generate_manifest_content(iflow_name, iflow_info)
            zipf.writestr("META-INF/MANIFEST.MF", manifest_content)
            
            # metainfo.prop
            print(f"   Adding: metainfo.prop")
            metainfo_content = self._generate_metainfo_content(iflow_name, iflow_info)
            zipf.writestr("metainfo.prop", metainfo_content)
            
            # .project file
            print(f"   Adding: .project")
            project_content = self._generate_project_content(iflow_name)
            zipf.writestr(".project", project_content)
            
            # src/main/resources/scenarioflows/integrationflow/{sanitized_iflow_name}.iflw
            iflow_filename = f"{sanitized_iflow_name}.iflw"
            iflow_dir = f"src/main/resources/scenarioflows/integrationflow"
            print(f"   Adding: {iflow_dir}/{iflow_filename}")
            zipf.writestr(f"{iflow_dir}/{iflow_filename}", iflow_xml)
            
            # parameters.prop
            print(f"   Adding: src/main/resources/parameters.prop")
            parameters_content = self._generate_parameters_content()
            zipf.writestr("src/main/resources/parameters.prop", parameters_content)
            
            # parameters.propdef
            print(f"   Adding: src/main/resources/parameters.propdef")
            propdef_content = self._generate_propdef_content()
            zipf.writestr("src/main/resources/parameters.propdef", propdef_content)
            
            # Script files: src/main/resources/script/*.groovy
            if script_files:
                print(f"   Adding {len(script_files)} script file(s):")
                for script_filename, script_content in script_files.items():
                    # Ensure .groovy extension
                    if not script_filename.endswith('.groovy'):
                        script_filename = f"{script_filename}.groovy"
                    print(f"      - src/main/resources/script/{script_filename}")
                    zipf.writestr(f"src/main/resources/script/{script_filename}", script_content)
            
            # Mapping files: src/main/resources/mappings/*.mmap or xslt/*.xsl
            if mapping_files:
                print(f"   Adding {len(mapping_files)} mapping file(s):")
                for mapping_path, mapping_content in mapping_files.items():
                    print(f"      - src/main/resources/{mapping_path}")
                    zipf.writestr(f"src/main/resources/{mapping_path}", mapping_content)
            
            # Schema files: src/main/resources/schemas/*.xsd
            if schema_files:
                print(f"   Adding {len(schema_files)} schema file(s):")
                for schema_filename, schema_content in schema_files.items():
                    if not schema_filename.endswith('.xsd'):
                        schema_filename = f"{schema_filename}.xsd"
                    print(f"      - src/main/resources/schemas/{schema_filename}")
                    zipf.writestr(f"src/main/resources/schemas/{schema_filename}", schema_content)
            
            # WSD files: src/main/resources/wsd/*.wsdl
            if wsd_files:
                print(f"   Adding {len(wsd_files)} WSD file(s):")
                for wsd_filename, wsd_content in wsd_files.items():
                    if not wsd_filename.endswith('.wsdl'):
                        wsd_filename = f"{wsd_filename}.wsdl"
                    print(f"      - src/main/resources/wsd/{wsd_filename}")
                    zipf.writestr(f"src/main/resources/wsd/{wsd_filename}", wsd_content)
        
        return zip_path
    
    def _generate_project_content(self, iflow_name: str) -> str:
        """Generate .project file content"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
\t<name>{iflow_name}</name>
\t<comment></comment>
\t<projects>
\t</projects>
\t<buildSpec>
\t</buildSpec>
\t<natures>
\t</natures>
</projectDescription>
"""
    
    def _generate_parameters_content(self) -> str:
        """Generate parameters.prop file content"""
        current_date = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        return f"""#Store parameters
#{current_date}
"""
    
    def _generate_propdef_content(self) -> str:
        """Generate parameters.propdef file content"""
        return """<?xml version="1.0" encoding="UTF-8" standalone="no"?><parameters><param_references/></parameters>"""
    
    def _generate_manifest_content(self, iflow_name: str, iflow_info: Dict[str, Any]) -> str:
        """Generate MANIFEST.MF content with proper line wrapping (72 chars max per line)"""
        bundle_version = iflow_info.get("version", "1.0.0")
        # Sanitize symbolic name: remove spaces and special chars
        bundle_symbolic_name = self._sanitize_name(iflow_name)
        
        # Use exact same Import-Package format as working generator (72 chars per line with space continuation)
        return f"""Manifest-Version: 1.0
Bundle-ManifestVersion: 2
Bundle-Name: {iflow_name}
Bundle-SymbolicName: {bundle_symbolic_name}; singleton:=true
Bundle-Version: {bundle_version}
SAP-BundleType: IntegrationFlow
SAP-NodeType: IFLMAP
SAP-RuntimeProfile: iflmap
Import-Package: com.sap.esb.application.services.cxf.interceptor,com.sap
 .esb.security,com.sap.it.op.agent.api,com.sap.it.op.agent.collector.cam
 el,com.sap.it.op.agent.collector.cxf,com.sap.it.op.agent.mpl,javax.jms,
 javax.jws,javax.wsdl,javax.xml.bind.annotation,javax.xml.namespace,java
 x.xml.ws,org.apache.camel;version="2.8",org.apache.camel.builder;versio
 n="2.8",org.apache.camel.builder.xml;version="2.8",org.apache.camel.com
 ponent.cxf,org.apache.camel.model;version="2.8",org.apache.camel.proces
 sor;version="2.8",org.apache.camel.processor.aggregate;version="2.8",or
 g.apache.camel.spring.spi;version="2.8",org.apache.commons.logging,org.
 apache.cxf.binding,org.apache.cxf.binding.soap,org.apache.cxf.binding.s
 oap.spring,org.apache.cxf.bus,org.apache.cxf.bus.resource,org.apache.cx
 f.bus,org.apache.cxf.bus.spring,org.apache.cxf.buslifecycle,org.apache.cxf.catalog,org.apa
 che.cxf.configuration.jsse;version="2.5",org.apache.cxf.configuration.s
 pring,org.apache.cxf.endpoint,org.apache.cxf.headers,org.apache.cxf.int
 erceptor,org.apache.cxf.management.counters;version="2.5",org.apache.cx
 f.message,org.apache.cxf.phase,org.apache.cxf.resource,org.apache.cxf.s
 ervice.factory,org.apache.cxf.service.model,org.apache.cxf.transport,or
 g.apache.cxf.transport.common.gzip,org.apache.cxf.transport.http,org.ap
 ache.cxf.transport.http.policy,org.apache.cxf.workqueue,org.apache.cxf.
 ws.rm.persistence,org.apache.cxf.wsdl11,org.osgi.framework;version="1.6
 .0",org.slf4j;version="1.6",org.springframework.beans.factory.config;ve
 rsion="3.0",com.sap.esb.camel.security.cms,org.apache.camel.spi,com.sap
 .esb.webservice.audit.log,com.sap.esb.camel.endpoint.configurator.api,c
 om.sap.esb.camel.jdbc.idempotency.reorg,javax.sql,org.apache.camel.proc
 essor.idempotent.jdbc,org.osgi.service.blueprint;version="[1.0.0,2.0.0)
 "
Origin-Bundle-Name: {iflow_name}
Origin-Bundle-SymbolicName: {bundle_symbolic_name}
"""
    
    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize name for SAP IS compatibility (remove spaces, special chars).
        Used for component IDs, file names, Bundle-SymbolicName, etc.
        
        Args:
            name: Original name (may contain spaces/special chars)
            
        Returns:
            Sanitized name with spaces replaced by underscores, special chars removed
        """
        if not name:
            return "Default"
        # Replace multiple spaces/hyphens with single underscore, then collapse
        import re
        # First replace spaces and hyphens with single underscore
        sanitized = re.sub(r'[\s\-]+', '_', name)
        # Remove special characters (keep alphanumeric, underscore)
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', sanitized)
        # Collapse multiple underscores to single
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = "IFlow_" + sanitized
        # Ensure it's not empty
        if not sanitized:
            sanitized = "IFlow"
        return sanitized
    
    def _generate_metainfo_content(self, iflow_name: str, iflow_info: Dict[str, Any]) -> str:
        """Generate metainfo.prop content"""
        description = iflow_info.get("description", f"{iflow_name} Integration Flow")
        current_date = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        
        return f"""#Store metainfo properties
#{current_date}
description={description}
"""


def main():
    """Command-line interface for iFlow generation"""
    parser = argparse.ArgumentParser(
        description="Generate SAP Integration Suite iFlow from JSON metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python enhanced_iflow_generator.py --input_file sample_1.json --output_dir output_sample1 --iflow_name Sample1
  python enhanced_iflow_generator.py --input_file "BoomiToIS-API/sample_metadata_jsons/sample_1.json" --output_dir "output" --iflow_name "MyIFlow"
        """
    )
    
    parser.add_argument(
        "--input_file",
        required=True,
        help="Path to JSON metadata file (following components.json template structure)"
    )
    
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Directory to save the generated iFlow ZIP package"
    )
    
    parser.add_argument(
        "--iflow_name",
        help="Name of the iFlow (optional, will use name from iflow_info if not provided)"
    )
    
    args = parser.parse_args()
    
    # Generate iFlow
    generator = EnhancedIFlowGenerator()
    
    try:
        # Read JSON to get iflow_name if not provided
        iflow_name = args.iflow_name
        if not iflow_name:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            iflow_info = data.get("iflow_info", {})
            iflow_name = iflow_info.get("name", "GeneratedIFlow")
        
        print(f"🚀 Generating iFlow: {iflow_name}")
        print(f"📂 Input: {args.input_file}")
        print(f"📦 Output: {args.output_dir}")
        
        zip_path = generator.generate_iflow(
            input_file=args.input_file,
            output_dir=args.output_dir,
            iflow_name=iflow_name
        )
        
        print(f"\n✅ Success! iFlow package created at: {zip_path}")
        print(f"📋 You can now import this ZIP file into SAP Integration Suite")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

