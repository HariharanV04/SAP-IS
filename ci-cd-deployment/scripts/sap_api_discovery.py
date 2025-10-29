#!/usr/bin/env python3
"""
SAP API Discovery Script
Tries different base URLs and authentication methods to find working endpoints
"""

import requests
import base64
import json
import sys
from datetime import datetime

class SAPAPIDiscovery:
    """Discover working SAP API endpoints"""
    
    def __init__(self):
        """Initialize with ITR Internal credentials"""
        self.client_id = 'sb-3c34b7ea-2323-485e-9324-e9c25bbe72be!b124895|it!b410334'
        self.client_secret = '408913ea-83d7-458d-8243-31f15e4a4165$n35ZO3mV4kSJY5TJDcURz0XxgCQ4DjFnrwdv32Wwwxs='
        self.oauth_url = 'https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token'
        self.access_token = None
        
        # Different possible base URLs for SAP Integration Suite
        self.base_urls = [
            'https://itr-internal-2hco92jx.integrationsuite-cpi034.cfapps.us10-002.hana.ondemand.com',
            'https://itr-internal-2hco92jx.it-cpi034-rt.cfapps.us10-002.hana.ondemand.com',
            'https://itr-internal-2hco92jx.it-cpi034.cfapps.us10-002.hana.ondemand.com',
            'https://itr-internal-2hco92jx-api.cfapps.us10-002.hana.ondemand.com',
        ]
        
    def get_access_token(self):
        """Get OAuth access token"""
        if self.access_token:
            return True
            
        print("🔑 Getting OAuth access token...")
        
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        try:
            response = requests.post(self.oauth_url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print(f"✅ OAuth token acquired successfully")
                return True
            else:
                print(f"❌ OAuth token request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ OAuth request failed: {str(e)}")
            return False
    
    def test_endpoint(self, base_url, endpoint, description):
        """Test a specific endpoint with OAuth token"""
        if not self.access_token:
            return False
            
        url = f"{base_url}/api/v1{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        print(f"\n🔍 Testing: {description}")
        print(f"🔗 URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        results = data.get('d', {}).get('results', [])
                        print(f"✅ SUCCESS - JSON response with {len(results)} items")
                        
                        if results and len(results) > 0:
                            first_item = results[0]
                            print(f"   Sample item: {first_item.get('Id', first_item.get('Name', 'N/A'))}")
                        
                        return True
                        
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON in response")
                        return False
                        
                elif 'text/html' in content_type:
                    print(f"❌ HTML response (likely redirect) - length: {len(response.text)}")
                    return False
                    
                else:
                    print(f"✅ SUCCESS - Non-JSON response: {content_type}")
                    return True
                    
            elif response.status_code == 401:
                print(f"❌ UNAUTHORIZED - Token rejected")
                return False
                
            elif response.status_code == 403:
                print(f"❌ FORBIDDEN - Insufficient permissions")
                return False
                
            elif response.status_code == 404:
                print(f"❌ NOT FOUND - Endpoint doesn't exist")
                return False
                
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            return False
    
    def test_basic_auth_endpoint(self, base_url, endpoint, description):
        """Test endpoint with Basic Authentication instead of OAuth"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        url = f"{base_url}/api/v1{endpoint}"
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Accept': 'application/json'
        }
        
        print(f"\n🔍 Testing with Basic Auth: {description}")
        print(f"🔗 URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        results = data.get('d', {}).get('results', [])
                        print(f"✅ SUCCESS - JSON response with {len(results)} items")
                        return True
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON in response")
                        return False
                else:
                    print(f"✅ SUCCESS - Non-JSON response: {content_type}")
                    return True
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            return False
    
    def discover_working_endpoints(self):
        """Discover which endpoints and base URLs work"""
        print("========================================")
        print("SAP API Discovery")
        print("========================================")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get OAuth token
        if not self.get_access_token():
            print("❌ Failed to get OAuth token. Cannot proceed.")
            return
        
        # Test endpoints to try
        endpoints_to_test = [
            ("/IntegrationDesigntimeArtifacts", "Design Time Artifacts"),
            ("/IntegrationRuntimeArtifacts", "Runtime Artifacts"),
            ("/IntegrationPackages", "Integration Packages"),
            ("/MessageProcessingLogs", "Message Processing Logs"),
            ("/IntegrationDesigntimeArtifacts?$top=5", "Design Time Artifacts (Limited)"),
        ]
        
        working_combinations = []
        
        # Test each base URL with OAuth
        for base_url in self.base_urls:
            print(f"\n{'='*60}")
            print(f"Testing Base URL: {base_url}")
            print(f"{'='*60}")
            
            for endpoint, description in endpoints_to_test:
                if self.test_endpoint(base_url, endpoint, description):
                    working_combinations.append((base_url, endpoint, description, "OAuth"))
        
        # Also try Basic Auth with the main base URL
        main_base_url = self.base_urls[0]
        print(f"\n{'='*60}")
        print(f"Testing Basic Auth with: {main_base_url}")
        print(f"{'='*60}")
        
        for endpoint, description in endpoints_to_test:
            if self.test_basic_auth_endpoint(main_base_url, endpoint, description):
                working_combinations.append((main_base_url, endpoint, description, "Basic Auth"))
        
        # Summary
        print(f"\n{'='*60}")
        print("DISCOVERY SUMMARY")
        print(f"{'='*60}")
        
        if working_combinations:
            print(f"✅ Found {len(working_combinations)} working combinations:")
            for base_url, endpoint, description, auth_type in working_combinations:
                print(f"\n🎯 {description}")
                print(f"   URL: {base_url}/api/v1{endpoint}")
                print(f"   Auth: {auth_type}")
        else:
            print(f"❌ No working combinations found")
            print(f"💡 Possible issues:")
            print(f"   - API credentials may not have the required permissions")
            print(f"   - Different authentication method required")
            print(f"   - API endpoints may be different than expected")
            print(f"   - Network connectivity issues")
        
        return working_combinations

def main():
    """Main function"""
    discovery = SAPAPIDiscovery()
    
    try:
        working_endpoints = discovery.discover_working_endpoints()
        
        if working_endpoints:
            print(f"\n🎉 Discovery successful!")
            print(f"💡 Use the working combinations above for your API calls.")
        else:
            print(f"\n💥 Discovery failed - no working endpoints found.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Discovery cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Discovery failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
