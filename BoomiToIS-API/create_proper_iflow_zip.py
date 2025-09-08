#!/usr/bin/env python3
"""
Create proper iFlow ZIP package using the existing package_iflow_zip function
"""

import json
import os
import sys
from pathlib import Path

def create_proper_iflow_zip():
    """Create iFlow ZIP package with correct SAP Integration Suite structure"""
    
    print("🚀 Creating Proper iFlow ZIP Package with SAP Integration Suite Structure")
    print("=" * 70)
    
    # Load the JSON file
    json_file = "genai_debug/final_components.json"
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    print(f"📁 Loading JSON from: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f"✅ JSON loaded successfully")
        print(f"📊 Process: {json_data.get('process_name', 'Unknown')}")
        
        # Import the converter
        try:
            from json_to_iflow_converter import EnhancedJSONToIFlowConverter
            print("✅ EnhancedJSONToIFlowConverter imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import converter: {e}")
            return
        
        # Create converter instance
        converter = EnhancedJSONToIFlowConverter()
        
        # Convert JSON to iFlow XML
        print("\n🔄 Converting JSON to iFlow XML...")
        
        try:
            xml_content = converter.convert(json.dumps(json_data))
            print("✅ iFlow XML generated successfully")
            
            # Import the proper ZIP packaging tool
            try:
                # Add tools directory to path
                current_dir = Path(__file__).resolve().parent
                tools_dir = current_dir.parent.parent / "tools"
                sys.path.insert(0, str(tools_dir))
                
                from iflow_generate import package_iflow_zip
                print("✅ package_iflow_zip imported successfully")
                
            except ImportError as e:
                print(f"❌ Failed to import package_iflow_zip: {e}")
                return
            
            # Create output directory
            output_dir = "proper_iflow_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Use the proper package_iflow_zip function
            print("\n📦 Creating proper SAP Integration Suite ZIP package...")
            iflow_name = "StripeSalesforceIntegration"
            
            zip_path = package_iflow_zip(
                iflow_name=iflow_name,
                iflow_xml=xml_content,
                output_dir=output_dir
            )
            
            print(f"✅ Proper iFlow ZIP package created successfully!")
            print(f"📦 ZIP file: {zip_path}")
            print(f"📁 Output directory: {output_dir}")
            
            # List ZIP contents to verify structure
            print(f"\n📋 ZIP package contents (SAP Integration Suite Structure):")
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for file_info in sorted(zipf.filelist, key=lambda x: x.filename):
                    indent = "  " * (file_info.filename.count('/') - 1)
                    print(f"{indent}📄 {file_info.filename} ({file_info.file_size} bytes)")
            
            print(f"\n🎉 Proper iFlow ZIP package ready for SAP Integration Suite!")
            print(f"💡 This ZIP has the correct folder structure for deployment")
            
        except Exception as e:
            print(f"❌ Failed to create proper iFlow ZIP: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_proper_iflow_zip()
