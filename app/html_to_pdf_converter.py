#!/usr/bin/env python3
"""
HTML to PDF Converter with Multiple Options
Supports both free local conversion and paid API services
"""

import os
import requests
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any

class HTMLToPDFConverter:
    """Convert HTML to PDF using various methods"""
    
    def __init__(self):
        self.output_dir = "pdf_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def convert_with_weasyprint(self, html_file_path: str, output_pdf_path: str = None) -> str:
        """
        Convert HTML to PDF using WeasyPrint (FREE - Local Processing)
        
        Args:
            html_file_path: Path to HTML file
            output_pdf_path: Optional output path (auto-generated if None)
        
        Returns:
            Path to generated PDF
        """
        try:
            import weasyprint
            print("✅ WeasyPrint found - using local conversion")
        except ImportError:
            print("❌ WeasyPrint not installed. Installing...")
            subprocess.run(["pip", "install", "weasyprint"], check=True)
            import weasyprint
        
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(html_file_path))[0]
            output_pdf_path = os.path.join(self.output_dir, f"{base_name}_weasyprint.pdf")
        
        try:
            print(f"🔄 Converting {html_file_path} to PDF...")
            
            # Read HTML file
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Convert to PDF
            html_doc = weasyprint.HTML(string=html_content, base_url=os.path.dirname(html_file_path))
            html_doc.write_pdf(output_pdf_path)
            
            print(f"✅ PDF successfully created: {output_pdf_path}")
            return output_pdf_path
            
        except Exception as e:
            print(f"❌ WeasyPrint conversion failed: {e}")
            raise
    
    def convert_with_yakpdf_api(self, html_file_path: str, api_key: str, output_pdf_path: str = None) -> str:
        """
        Convert HTML to PDF using YakPDF API (200 free/month, then $7/month)
        
        Args:
            html_file_path: Path to HTML file
            api_key: YakPDF API key
            output_pdf_path: Optional output path
        
        Returns:
            Path to generated PDF
        """
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(html_file_path))[0]
            output_pdf_path = os.path.join(self.output_dir, f"{base_name}_yakpdf.pdf")
        
        try:
            print(f"🔄 Converting {html_file_path} using YakPDF API...")
            
            # Read HTML file
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # YakPDF API endpoint
            url = "https://yakpdf.com/api/pdf"
            
            payload = {
                "html": html_content,
                "options": {
                    "format": "A4",
                    "margin": {
                        "top": "1cm",
                        "right": "1cm", 
                        "bottom": "1cm",
                        "left": "1cm"
                    },
                    "printBackground": True,
                    "displayHeaderFooter": True,
                    "headerTemplate": "<div style='font-size:10px; text-align:center; width:100%;'>Boomi Integration Documentation</div>",
                    "footerTemplate": "<div style='font-size:10px; text-align:center; width:100%;'>Page <span class='pageNumber'></span> of <span class='totalPages'></span></div>"
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                with open(output_pdf_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ PDF successfully created: {output_pdf_path}")
                return output_pdf_path
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ YakPDF conversion failed: {e}")
            raise
    
    def convert_with_pdfbolt_api(self, html_file_path: str, api_key: str, output_pdf_path: str = None) -> str:
        """
        Convert HTML to PDF using PDFBolt API (100 free/month, then $9.99/month)
        
        Args:
            html_file_path: Path to HTML file
            api_key: PDFBolt API key
            output_pdf_path: Optional output path
        
        Returns:
            Path to generated PDF
        """
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(html_file_path))[0]
            output_pdf_path = os.path.join(self.output_dir, f"{base_name}_pdfbolt.pdf")
        
        try:
            print(f"🔄 Converting {html_file_path} using PDFBolt API...")
            
            # Read HTML file
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # PDFBolt API endpoint
            url = "https://pdfbolt.com/api/v1/pdf"
            
            payload = {
                "html": html_content,
                "options": {
                    "format": "A4",
                    "landscape": False,
                    "margin": {
                        "top": "1cm",
                        "right": "1cm",
                        "bottom": "1cm", 
                        "left": "1cm"
                    },
                    "printBackground": True,
                    "displayHeaderFooter": True
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": api_key
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                with open(output_pdf_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ PDF successfully created: {output_pdf_path}")
                return output_pdf_path
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ PDFBolt conversion failed: {e}")
            raise
    
    def convert_with_pdfg_api(self, html_file_path: str, api_key: str, output_pdf_path: str = None) -> str:
        """
        Convert HTML to PDF using pdfg API (Pay-per-use: $0.002/PDF)
        
        Args:
            html_file_path: Path to HTML file
            api_key: pdfg API key
            output_pdf_path: Optional output path
        
        Returns:
            Path to generated PDF
        """
        if output_pdf_path is None:
            base_name = os.path.splitext(os.path.basename(html_file_path))[0]
            output_pdf_path = os.path.join(self.output_dir, f"{base_name}_pdfg.pdf")
        
        try:
            print(f"🔄 Converting {html_file_path} using pdfg API...")
            
            # Read HTML file
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # pdfg API endpoint
            url = "https://api.pdfg.net/v1/pdf"
            
            payload = {
                "html": html_content,
                "options": {
                    "format": "A4",
                    "printBackground": True,
                    "margin": {
                        "top": "20mm",
                        "right": "20mm",
                        "bottom": "20mm",
                        "left": "20mm"
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                with open(output_pdf_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ PDF successfully created: {output_pdf_path}")
                return output_pdf_path
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ pdfg conversion failed: {e}")
            raise

def main():
    """Demo conversion of enhanced Boomi documentation"""
    
    converter = HTMLToPDFConverter()
    html_file = "../pepsi/boomi_pepsi_ai_documentaion-enhanced.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        print("Please ensure the enhanced documentation exists.")
        return
    
    print("🔄 Converting Enhanced Boomi Documentation to PDF...")
    print("=" * 60)
    
    # Method 1: Free local conversion with WeasyPrint
    try:
        pdf_path = converter.convert_with_weasyprint(html_file)
        print(f"✅ Method 1 (WeasyPrint): {pdf_path}")
        
        # Get file size
        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        print(f"📄 PDF Size: {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"❌ Method 1 (WeasyPrint) failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 For API methods, you need to:")
    print("1. Sign up for an API key from the service")
    print("2. Set the API key and call the respective method")
    print("\n📚 API Service Recommendations:")
    print("• YakPDF: 200 free/month → yakpdf.com")
    print("• PDFBolt: 100 free/month → pdfbolt.com") 
    print("• pdfg: $0.002/PDF → pdfg.net")
    print("\n🔗 Example usage:")
    print('converter.convert_with_yakpdf_api(html_file, "your-api-key")')

if __name__ == "__main__":
    main()

