#!/usr/bin/env python3
"""
Simple HTML to PDF Converter using Free APIs
No installations required - just needs requests library
"""

import os
import requests
import json
from datetime import datetime

def convert_html_to_pdf_free(html_file_path: str) -> str:
    """
    Convert HTML to PDF using html2pdf.app (Free service)
    100 free conversions per month
    """
    
    print(f"🔄 Converting {html_file_path} to PDF using html2pdf.app...")
    
    # Read HTML content
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return None
    
    # API endpoint for html2pdf.app (free service)
    url = "https://html2pdf.app/api/v1/generate"
    
    # Create output filename
    base_name = os.path.splitext(os.path.basename(html_file_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"pdf_outputs/{base_name}_{timestamp}.pdf"
    os.makedirs("pdf_outputs", exist_ok=True)
    
    # Prepare the request
    payload = {
        "html": html_content,
        "options": {
            "format": "A4",
            "printBackground": True,
            "displayHeaderFooter": False,
            "margin": {
                "top": "1cm",
                "bottom": "1cm",
                "left": "1cm", 
                "right": "1cm"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Sending request to conversion API...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            # Save PDF
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Get file size
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            print(f"✅ PDF successfully created!")
            print(f"📄 Output: {output_path}")
            print(f"📊 Size: {size_mb:.2f} MB")
            return output_path
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Large files may take longer.")
        return None
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return None

def convert_with_api2pdf(html_file_path: str, api_key: str) -> str:
    """
    Convert using API2PDF (Paid service - very reliable)
    $0.01 per conversion, very high quality
    """
    
    print(f"🔄 Converting {html_file_path} using API2PDF...")
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    base_name = os.path.splitext(os.path.basename(html_file_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"pdf_outputs/{base_name}_api2pdf_{timestamp}.pdf"
    
    url = "https://v2.api2pdf.com/chrome/pdf/html"
    
    payload = {
        "html": html_content,
        "options": {
            "landscape": False,
            "displayHeaderFooter": True,
            "printBackground": True,
            "format": "A4",
            "margin": {
                "top": "1in",
                "bottom": "1in",
                "left": "1in",
                "right": "1in"
            }
        }
    }
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            pdf_url = result.get('pdf')
            
            # Download the PDF
            pdf_response = requests.get(pdf_url)
            with open(output_path, 'wb') as f:
                f.write(pdf_response.content)
            
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ PDF created: {output_path} ({size_mb:.2f} MB)")
            return output_path
        else:
            print(f"❌ API2PDF failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ API2PDF conversion failed: {e}")
        return None

def main():
    """Convert the enhanced Boomi documentation"""
    
    html_file = "../pepsi/boomi_pepsi_ai_documentaion-enhanced.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return
    
    print("🎯 Converting Enhanced Boomi Documentation to PDF")
    print("=" * 60)
    
    # Method 1: Free conversion (100/month limit)
    print("🆓 Method 1: Free API Conversion")
    pdf_path = convert_html_to_pdf_free(html_file)
    
    if pdf_path:
        print(f"\n✅ Success! Your PDF is ready at: {pdf_path}")
        print(f"📱 Open PDF: start {pdf_path}" if os.name == 'nt' else f"📱 Open PDF: open {pdf_path}")
    else:
        print("\n❌ Free conversion failed. Consider trying a paid API.")
    
    print("\n" + "=" * 60)
    print("💰 PAID API OPTIONS (Higher Quality):")
    print("• API2PDF: $0.01/conversion → api2pdf.com")
    print("• YakPDF: 200 free then $7/month → yakpdf.com") 
    print("• PDFBolt: 100 free then $9.99/month → pdfbolt.com")
    print("• pdfg: $0.002/conversion → pdfg.net")
    
    print("\n🔧 To use paid APIs:")
    print('1. Get API key from the service')
    print('2. Call: convert_with_api2pdf(html_file, "your-api-key")')

if __name__ == "__main__":
    main()

