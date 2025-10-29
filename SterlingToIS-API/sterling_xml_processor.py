#!/usr/bin/env python3
"""
Sterling B2B XML Processor
Extracts integration logic from Sterling BPML and MXL files
NO HARDCODED VALUES - All data extracted from actual files
"""

import os
import xml.etree.ElementTree as ET
import json
from typing import List, Dict, Any
from pathlib import Path
import argparse
from datetime import datetime


class SterlingXMLProcessor:
    """Process Sterling B2B XML files and extract integration logic"""
    
    def __init__(self, output_dir: str = "sterling_parsed_outputs"):
        self.components = []
        self.output_dir = Path(output_dir)
        self.stats = {
            'total_files': 0,
            'bpml_files': 0,
            'mxl_files': 0,
            'successful': 0,
            'failed': 0,
            'patterns': {}
        }
        self._setup_directories()
    
    def _setup_directories(self):
        """Create output directory structure"""
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "individual_markdown" / "bpml").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "individual_markdown" / "mxl").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "json" / "bpml").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "json" / "mxl").mkdir(parents=True, exist_ok=True)
    
    def process_directory(self, directory_path: str, save_outputs: bool = True) -> str:
        """Process all BPML and MXL files in a directory"""
        print("=" * 80)
        print("🚀 Sterling B2B XML Processor")
        print("=" * 80)
        print()
        print(f"📦 Processing directory: {directory_path}")
        print()
        
        source_path = Path(directory_path)
        if not source_path.exists():
            print(f"❌ Error: Directory not found: {directory_path}")
            return ""
        
        # Find all BPML and MXL files
        bpml_files = list(source_path.rglob("*.bpml"))
        mxl_files = list(source_path.rglob("*.mxl"))
        
        print("🔍 Scanning for files...")
        print(f"   Found {len(bpml_files)} BPML files")
        print(f"   Found {len(mxl_files)} MXL files")
        print()
        
        self.stats['total_files'] = len(bpml_files) + len(mxl_files)
        self.stats['bpml_files'] = len(bpml_files)
        self.stats['mxl_files'] = len(mxl_files)
        
        # Process BPML files
        if bpml_files:
            print("=" * 80)
            print("📝 Processing BPML Files...")
            print("=" * 80)
            print()
            
            for idx, bpml_path in enumerate(bpml_files, 1):
                print(f"[{idx}/{len(bpml_files)}] {bpml_path.name}")
                self._process_bpml_file(str(bpml_path), save_outputs)
                print()
        
        # Process MXL files
        if mxl_files:
            print("=" * 80)
            print("🗺️  Processing MXL Files...")
            print("=" * 80)
            print()
            
            for idx, mxl_path in enumerate(mxl_files, 1):
                print(f"[{idx}/{len(mxl_files)}] {mxl_path.name}")
                self._process_mxl_file(str(mxl_path), save_outputs)
                print()
        
        # Generate combined documentation
        print("=" * 80)
        print("📄 Generating Documentation...")
        print("=" * 80)
        print()
        
        markdown = self._generate_markdown()
        
        if save_outputs:
            # Save combined markdown
            combined_md_path = self.output_dir / "combined_documentation.md"
            with open(combined_md_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"✅ Saved combined documentation: {combined_md_path.name}")
            
            # Save all components JSON
            all_components_path = self.output_dir / "all_components.json"
            with open(all_components_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_components': len(self.components),
                    'bpml_count': self.stats['bpml_files'],
                    'mxl_count': self.stats['mxl_files'],
                    'components': self.components
                }, f, indent=2)
            print(f"✅ Saved all components JSON: {all_components_path.name}")
            
            # Generate summary report
            self._generate_summary_report()
            print(f"✅ Saved summary report: summary_report.txt")
        
        print()
        print("=" * 80)
        print("✅ PROCESSING COMPLETE")
        print("=" * 80)
        print()
        print("📊 Statistics:")
        print(f"   Total Files: {self.stats['total_files']}")
        print(f"   ✅ Successful: {self.stats['successful']}")
        print(f"   ❌ Failed: {self.stats['failed']}")
        success_rate = (self.stats['successful'] / self.stats['total_files'] * 100) if self.stats['total_files'] > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if self.stats['patterns']:
            print("🎯 Integration Patterns:")
            for pattern, count in sorted(self.stats['patterns'].items(), key=lambda x: x[1], reverse=True):
                pattern_name = pattern.replace('_', ' ').title()
                print(f"   {pattern_name}: {count}")
            print()
        
        print(f"📁 Output Location: {self.output_dir.absolute()}")
        print(f"   📄 Combined markdown: combined_documentation.md")
        print(f"   📊 All components: all_components.json")
        print(f"   📝 Individual markdown: individual_markdown/ ({len(self.components)} files)")
        print(f"   📊 Individual JSON: json/ ({len(self.components)} files)")
        print(f"   📋 Summary: summary_report.txt")
        print()
        print("🎉 All done! Check 'sterling_parsed_outputs' folder for results.")
        print()
        
        return markdown
    
    def _process_bpml_file(self, bpml_path: str, save_outputs: bool):
        """Process a single BPML file"""
        try:
            with open(bpml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            root = ET.fromstring(content)
            
            # Extract component information
            process_info = self._extract_bpml_info(root, content, bpml_path)
            
            if process_info:
                self.components.append(process_info)
                print(f"   ✅ Processed component: {process_info['name']} ({process_info['type']})")
                
                if save_outputs:
                    # Save individual JSON
                    json_path = self._get_output_path(bpml_path, "json/bpml", ".json")
                    json_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(process_info, f, indent=2)
                    
                    # Save individual markdown
                    md_path = self._get_output_path(bpml_path, "individual_markdown/bpml", ".md")
                    md_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(self._generate_individual_bpml_markdown(process_info))
                
                self.stats['successful'] += 1
            else:
                print(f"   ⚠️  No process found in file")
                self.stats['failed'] += 1
                
        except Exception as e:
            print(f"   ❌ Error processing {bpml_path}: {e}")
            self.stats['failed'] += 1
    
    def _process_mxl_file(self, mxl_path: str, save_outputs: bool):
        """Process a single MXL file"""
        try:
            with open(mxl_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            root = ET.fromstring(content)
            
            # Extract component information
            map_info = self._extract_mxl_info(root, content, mxl_path)
            
            if map_info:
                self.components.append(map_info)
                print(f"   ✅ Processed component: {map_info['name']} ({map_info['type']})")
                
                if save_outputs:
                    # Save individual JSON
                    json_path = self._get_output_path(mxl_path, "json/mxl", ".json")
                    json_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(map_info, f, indent=2)
                    
                    # Save individual markdown
                    md_path = self._get_output_path(mxl_path, "individual_markdown/mxl", ".md")
                    md_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(self._generate_individual_mxl_markdown(map_info))
                
                self.stats['successful'] += 1
            else:
                print(f"   ⚠️  No map found in file")
                self.stats['failed'] += 1
                
        except Exception as e:
            print(f"   ❌ Error processing {mxl_path}: {e}")
            self.stats['failed'] += 1
    
    def _extract_bpml_info(self, root: ET.Element, raw_content: str, file_path: str) -> Dict[str, Any]:
        """Extract information from BPML file - ACTUAL VALUES ONLY, NO HARDCODING"""
        process_name = root.get('name', Path(file_path).stem)
        
        component_info = {
            'id': Path(file_path).stem,
            'name': process_name,
            'type': 'sterling.process',
            'subtype': 'bpml',
            'description': f'Sterling B2B Business Process: {process_name}',
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'rules': [],
            'operations': [],
            'assignments': [],
            'sequences': [],
            'patterns': [],
            'raw_content': raw_content[:5000]
        }
        
        # Extract business rules - ACTUAL VALUES
        for rule in root.findall('.//rule'):
            rule_info = {
                'name': rule.get('name', ''),
                'condition': rule.get('condition', ''),
                'type': 'business_rule'
            }
            if rule_info['name'] or rule_info['condition']:
                component_info['rules'].append(rule_info)
        
        # Extract operations - ACTUAL VALUES FROM FILE
        for operation in root.findall('.//operation'):
            op_name = operation.get('name', '')
            participant = operation.get('participant', '')
            
            op_info = {
                'name': op_name,
                'participant': participant,
                'type': self._identify_operation_type(operation),
                'config': {}
            }
            
            # Extract ACTUAL assignment values from output message
            output_msg = operation.find('.//output')
            if output_msg is not None:
                for assign in output_msg.findall('.//assign'):
                    assign_to = assign.get('to', '')
                    assign_value = assign.text
                    if assign_value is None or not assign_value.strip():
                        from_attr = assign.get('from', '')
                        if from_attr:
                            assign_value = {'from': from_attr}
                    if assign_to and assign_value:
                        op_info['config'][assign_to] = assign_value
            
            component_info['operations'].append(op_info)
        
        # Extract sequences
        for sequence in root.findall('.//sequence'):
            seq_info = {
                'name': sequence.get('name', ''),
                'type': 'sequential_flow'
            }
            component_info['sequences'].append(seq_info)
        
        # Identify patterns from ACTUAL content
        patterns = self._identify_bpml_patterns(root)
        component_info['patterns'] = patterns
        
        for pattern in patterns:
            self.stats['patterns'][pattern] = self.stats['patterns'].get(pattern, 0) + 1
        
        return component_info
    
    def _extract_mxl_info(self, root: ET.Element, raw_content: str, file_path: str) -> Dict[str, Any]:
        """Extract information from MXL file - ACTUAL VALUES ONLY, NO HARDCODING"""
        map_details = root.find('.//MapDetails')
        map_name = map_details.get('MapName', Path(file_path).stem) if map_details is not None else Path(file_path).stem
        author = map_details.get('Author', '') if map_details is not None else ''
        description = map_details.get('Description', '') if map_details is not None else ''
        
        component_info = {
            'id': Path(file_path).stem,
            'name': map_name,
            'type': 'sterling.map',
            'subtype': 'mxl',
            'description': description,
            'author': author,
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'mappings': [],
            'functions': [],
            'input_fields': [],
            'output_fields': [],
            'raw_content': raw_content[:5000]
        }
        
        # Extract input fields - ACTUAL FIELD DEFINITIONS
        input_card = root.find('.//INPUT')
        if input_card is not None:
            for field in input_card.findall('.//Field'):
                field_info = {
                    'id': field.get('ID', ''),
                    'name': field.get('FieldName', ''),
                    'type': field.get('FieldType', ''),
                    'length': field.get('Length', ''),
                    'start_pos': field.get('StartPos', ''),
                    'format': field.get('Format', ''),
                    'direction': 'input'
                }
                component_info['input_fields'].append(field_info)
        
        # Extract output fields - ACTUAL FIELD DEFINITIONS
        output_card = root.find('.//OUTPUT')
        if output_card is not None:
            for field in output_card.findall('.//Field'):
                field_info = {
                    'id': field.get('ID', ''),
                    'name': field.get('FieldName', ''),
                    'type': field.get('FieldType', ''),
                    'format': field.get('Format', ''),
                    'direction': 'output'
                }
                component_info['output_fields'].append(field_info)
        
        # Extract field mappings - ACTUAL FIELD MAPPINGS FROM FILE
        for link in root.findall('.//Link'):
            from_id = link.get('From', '')
            to_id = link.get('To', '')
            from_field = self._find_field_by_id(component_info['input_fields'], from_id)
            to_field = self._find_field_by_id(component_info['output_fields'], to_id)
            
            mapping_info = {
                'from_key': from_id,
                'from_field': from_field,
                'from_type': 'field',
                'to_key': to_id,
                'to_field': to_field,
                'to_type': self._find_field_type(component_info['output_fields'], to_id),
                'mapping_type': 'direct'
            }
            component_info['mappings'].append(mapping_info)
        
        # Extract transformation rules - ACTUAL TRANSFORMATION EXPRESSIONS
        for explicit_rule in root.findall('.//ExplicitRule'):
            target_id = explicit_rule.get('Target', '')
            rule_text = explicit_rule.text or ''
            target_field = self._find_field_by_id(component_info['output_fields'], target_id)
            
            mapping_info = {
                'from_key': 'explicit_rule',
                'from_type': 'transformation',
                'to_key': target_id,
                'to_field': target_field,
                'to_type': self._find_field_type(component_info['output_fields'], target_id),
                'mapping_type': 'transformation',
                'transformation': rule_text.strip()
            }
            component_info['mappings'].append(mapping_info)
            
            function_info = {
                'name': f'Transform_{target_field}',
                'type': 'transformation',
                'category': 'explicit_rule',
                'target_field': target_field,
                'expression': rule_text.strip(),
                'language': 'sterling_rule'
            }
            component_info['functions'].append(function_info)
        
        return component_info
    
    def _find_field_by_id(self, fields: List[Dict], field_id: str) -> str:
        """Find field name by ID"""
        for field in fields:
            if field.get('id') == field_id:
                return field.get('name', field_id)
        return field_id
    
    def _find_field_type(self, fields: List[Dict], field_id: str) -> str:
        """Find field type by ID"""
        for field in fields:
            if field.get('id') == field_id:
                return field.get('type', 'string')
        return 'string'
    
    def _identify_operation_type(self, operation: ET.Element) -> str:
        """Identify operation type based on participant name"""
        participant = operation.get('participant', '').lower()
        
        if 'ftpclient' in participant and 'sftp' not in participant:
            return 'ftp_adapter'
        elif 'sftpclient' in participant:
            return 'sftp_adapter'
        elif 'restapiclient' in participant or 'restapi' in participant:
            return 'rest_adapter'
        elif 'httpclient' in participant or 'httprespond' in participant:
            return 'http_adapter'
        elif 'mailbox' in participant:
            return 'message_queue'
        elif 'translation' in participant:
            return 'message_mapping'
        elif 'xapiservice' in participant or 'xapi' in participant:
            return 'soap_adapter'
        elif 'assign' in participant:
            return 'content_modifier'
        elif 'xmljsontransformer' in participant or 'jsontoxmltransformer' in participant:
            return 'json_xml_converter'
        else:
            return 'service'
    
    def _identify_bpml_patterns(self, root: ET.Element) -> List[str]:
        """Identify integration patterns based on actual content"""
        patterns = []
        
        if root.find('.//operation[@participant="FTPClientBeginSession"]') is not None or \
           root.find('.//operation[@participant="SFTPClientBeginSession"]') is not None:
            patterns.append('ftp_file_transfer')
        
        if root.find('.//operation[@participant="RESTAPIClient"]') is not None:
            patterns.append('rest_api_integration')
        
        if root.find('.//operation[@participant="Translation"]') is not None:
            patterns.append('data_transformation')
        
        if root.find('.//operation[@participant="MailboxAdd"]') is not None or \
           root.find('.//operation[@participant="MailboxGet"]') is not None:
            patterns.append('mailbox_operations')
        
        if root.find('.//repeat') is not None:
            patterns.append('batch_processing')
        
        if root.find('.//choice') is not None or root.find('.//rule') is not None:
            patterns.append('conditional_logic')
        
        if root.find('.//operation[@participant="XAPIService"]') is not None:
            patterns.append('xapi_operations')
        
        if root.find('.//operation[@participant="HTTPClient"]') is not None or \
           root.find('.//operation[@participant="HttpRespond"]') is not None:
            patterns.append('http_operations')
        
        return patterns
    
    def _generate_individual_bpml_markdown(self, process_info: Dict) -> str:
        """Generate markdown for a single BPML process"""
        md = f"# {process_info['name']}\n\n"
        md += f"**Type**: {process_info['type']}\n"
        md += f"**File**: {process_info['file_name']}\n\n"
        md += "## Description\n\n"
        md += f"{process_info['description']}\n\n"
        
        if process_info['patterns']:
            md += "## Integration Patterns\n\n"
            for pattern in process_info['patterns']:
                md += f"- {pattern.replace('_', ' ').title()}\n"
            md += "\n"
        
        if process_info['rules']:
            md += "## Business Rules\n\n"
            for rule in process_info['rules']:
                md += f"### {rule['name']}\n"
                md += f"- **Condition**: `{rule['condition']}`\n\n"
        
        if process_info['operations']:
            md += "## Operations\n\n"
            for idx, op in enumerate(process_info['operations'], 1):
                md += f"### {idx}. {op['name']}\n"
                md += f"- **Participant**: {op['participant']}\n"
                md += f"- **Type**: {op['type']}\n"
                if op['config']:
                    md += f"- **Configuration**:\n"
                    for key, value in op['config'].items():
                        md += f"  - `{key}`: {value}\n"
                md += "\n"
        
        return md
    
    def _generate_individual_mxl_markdown(self, map_info: Dict) -> str:
        """Generate markdown for a single MXL map"""
        md = f"# {map_info['name']}\n\n"
        md += f"**Type**: {map_info['type']}\n"
        md += f"**File**: {map_info['file_name']}\n"
        md += f"**Author**: {map_info['author']}\n\n"
        md += "## Description\n\n"
        md += f"{map_info['description']}\n\n"
        
        if map_info['input_fields']:
            md += "## Input Fields\n\n"
            for field in map_info['input_fields']:
                md += f"- **{field['name']}** ({field['type']})"
                if field.get('length'):
                    md += f" - Length: {field['length']}"
                if field.get('start_pos'):
                    md += f", Position: {field['start_pos']}"
                md += "\n"
            md += "\n"
        
        if map_info['output_fields']:
            md += "## Output Fields\n\n"
            for field in map_info['output_fields']:
                md += f"- **{field['name']}** ({field['type']})\n"
            md += "\n"
        
        if map_info['mappings']:
            md += "## Field Mappings\n\n"
            for mapping in map_info['mappings']:
                if mapping['mapping_type'] == 'direct':
                    md += f"- **{mapping['from_field']}** → **{mapping['to_field']}**\n"
                else:
                    md += f"- **{mapping['to_field']}**: `{mapping.get('transformation', '')}`\n"
            md += "\n"
        
        return md
    
    def _generate_markdown(self) -> str:
        """Generate combined markdown for all components"""
        if not self.components:
            return "# Sterling B2B Integration\n\nNo components found.\n"
        
        md = "# Sterling B2B Integration Documentation\n\n"
        md += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += "## Overview\n\n"
        md += f"This documentation covers {len(self.components)} Sterling B2B components:\n"
        md += f"- BPML Processes: {self.stats['bpml_files']}\n"
        md += f"- MXL Maps: {self.stats['mxl_files']}\n\n"
        
        bpml_components = [c for c in self.components if c['type'] == 'sterling.process']
        if bpml_components:
            md += "## Business Processes (BPML)\n\n"
            for comp in bpml_components:
                md += f"### {comp['name']}\n\n"
                md += self._generate_individual_bpml_markdown(comp)
                md += "\n---\n\n"
        
        mxl_components = [c for c in self.components if c['type'] == 'sterling.map']
        if mxl_components:
            md += "## Data Maps (MXL)\n\n"
            for comp in mxl_components:
                md += f"### {comp['name']}\n\n"
                md += self._generate_individual_mxl_markdown(comp)
                md += "\n---\n\n"
        
        return md
    
    def _generate_summary_report(self):
        """Generate a summary report"""
        report_path = self.output_dir / "summary_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("STERLING B2B XML PROCESSOR - SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Files: {self.stats['total_files']}\n")
            f.write(f"BPML Files: {self.stats['bpml_files']}\n")
            f.write(f"MXL Files: {self.stats['mxl_files']}\n")
            f.write(f"Successful: {self.stats['successful']}\n")
            f.write(f"Failed: {self.stats['failed']}\n")
            success_rate = (self.stats['successful'] / self.stats['total_files'] * 100) if self.stats['total_files'] > 0 else 0
            f.write(f"Success Rate: {success_rate:.1f}%\n\n")
            
            if self.stats['patterns']:
                f.write("INTEGRATION PATTERNS\n")
                f.write("-" * 80 + "\n")
                for pattern, count in sorted(self.stats['patterns'].items(), key=lambda x: x[1], reverse=True):
                    pattern_name = pattern.replace('_', ' ').title()
                    f.write(f"{pattern_name}: {count}\n")
                f.write("\n")
            
            f.write("OUTPUT FILES\n")
            f.write("-" * 80 + "\n")
            f.write(f"Combined Documentation: combined_documentation.md\n")
            f.write(f"All Components JSON: all_components.json\n")
            f.write(f"Individual Markdown Files: individual_markdown/ ({len(self.components)} files)\n")
            f.write(f"Individual JSON Files: json/ ({len(self.components)} files)\n\n")
            f.write("COMPONENTS\n")
            f.write("-" * 80 + "\n")
            for idx, comp in enumerate(self.components, 1):
                f.write(f"{idx}. {comp['name']} ({comp['type']})\n")
                f.write(f"   File: {comp['file_name']}\n")
                if comp.get('patterns'):
                    f.write(f"   Patterns: {', '.join(comp['patterns'])}\n")
                f.write("\n")
    
    def _get_output_path(self, source_path: str, output_subdir: str, new_ext: str) -> Path:
        """Get output path preserving directory structure"""
        source = Path(source_path)
        try:
            if 'sterling-b2b-samples' in str(source):
                rel_path = str(source).split('sterling-b2b-samples')[1].lstrip(os.sep)
                rel_path = Path(rel_path).with_suffix(new_ext)
                return self.output_dir / output_subdir / rel_path
        except:
            pass
        return self.output_dir / output_subdir / source.with_suffix(new_ext).name


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Sterling B2B XML Processor')
    parser.add_argument('--source', default='sterling-b2b-samples', help='Source directory')
    parser.add_argument('--output', default='sterling_parsed_outputs', help='Output directory')
    parser.add_argument('--clean', action='store_true', help='Clean output directory first')
    
    args = parser.parse_args()
    
    if args.clean:
        import shutil
        output_path = Path(args.output)
        if output_path.exists():
            print(f"🗑️  Cleaning output directory: {output_path}")
            shutil.rmtree(output_path)
            print("✅ Clean complete\n")
    
    processor = SterlingXMLProcessor(args.output)
    processor.process_directory(args.source)


if __name__ == "__main__":
    main()





