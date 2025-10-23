#!/usr/bin/env python3
"""
Convert Excel file with multiple tabs to separate CSV files
"""
import pandas as pd
import os
import sys

def convert_excel_to_csvs(excel_path, output_dir):
    """Convert each sheet in Excel file to separate CSV files"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read all sheets from Excel file
        print(f"📖 Reading Excel file: {excel_path}")
        excel_file = pd.ExcelFile(excel_path)
        
        print(f"📋 Found {len(excel_file.sheet_names)} sheets:")
        for i, sheet_name in enumerate(excel_file.sheet_names, 1):
            print(f"   {i}. {sheet_name}")
        
        # Convert each sheet to CSV
        for sheet_name in excel_file.sheet_names:
            try:
                print(f"\n🔄 Converting sheet: {sheet_name}")
                
                # Read the sheet
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                # Clean sheet name for filename (remove special characters)
                clean_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_name = clean_name.replace(' ', '_')
                
                # Create CSV filename
                csv_filename = f"{clean_name}.csv"
                csv_path = os.path.join(output_dir, csv_filename)
                
                # Save to CSV
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
                print(f"   ✅ Saved: {csv_filename}")
                print(f"   📊 Rows: {len(df)}, Columns: {len(df.columns)}")
                
                # Show column names
                if len(df.columns) > 0:
                    print(f"   📝 Columns: {', '.join(df.columns[:5])}" + 
                          (f" ... +{len(df.columns)-5} more" if len(df.columns) > 5 else ""))
                
            except Exception as e:
                print(f"   ❌ Error converting sheet '{sheet_name}': {str(e)}")
        
        print(f"\n🎉 Conversion complete! CSV files saved to: {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    # File paths
    excel_file = "EC372-EC to NAVEX (OB) FMD.xlsx"
    output_directory = "csv_exports"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        print("📁 Current directory contents:")
        for item in os.listdir('.'):
            print(f"   {item}")
        sys.exit(1)
    
    # Convert Excel to CSVs
    success = convert_excel_to_csvs(excel_file, output_directory)
    
    if success:
        print(f"\n📂 CSV files location: {os.path.abspath(output_directory)}")
        print("\n🔍 Next steps:")
        print("1. Review the generated CSV files")
        print("2. Compare content with enhanced HTML documentation")
        print("3. Identify any missing information")
    else:
        print("\n❌ Conversion failed. Please check the error messages above.")

