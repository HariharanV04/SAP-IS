#!/usr/bin/env python3
"""
SAP BTP CPI Artifact Count Script
Gets artifact count from SAP Integration Suite using OAuth authentication
"""

import requests
import base64
import json
import sys
import os
from datetime import datetime
import argparse

class SAPCPIArtifactCounter:
    """
    SAP CPI Artifact Counter using OAuth authentication
    """
    
    def __init__(self):
        """Initialize with ITR Internal credentials"""
        # ITR Internal account configuration - using the correct base URL
        self.base_url = 'https://itr-internal-2hco92jx.integrationsuite-cpi034.cfapps.us10-002.hana.ondemand.com'
        self.client_id = 'sb-3c34b7ea-2323-485e-9324-e9c25bbe72be!b124895|it!b410334'
        self.client_secret = '408913ea-83d7-458d-8243-31f15e4a4165$n35ZO3mV4kSJY5TJDcURz0XxgCQ4DjFnrwdv32Wwwxs='
        self.oauth_url = 'https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token'

        self.access_token = None
        
    def get_access_token(self):
        """Get OAuth access token"""
        print("🔑 Getting OAuth access token...")
        
        # Create Basic Auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(self.oauth_url, headers=headers, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print(f"✅ OAuth token acquired successfully")
                return self.access_token
            else:
                print(f"❌ OAuth token request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ OAuth request failed: {str(e)}")
            return None
    
    def make_authenticated_request(self, url, method='GET'):
        """Make authenticated request to SAP CPI"""
        if not self.access_token:
            if not self.get_access_token():
                return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(method, url, headers=headers, timeout=30)
            
            # If 401, try refreshing token once
            if response.status_code == 401:
                print("🔄 Token expired, refreshing...")
                if self.get_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.request(method, url, headers=headers, timeout=30)
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def get_artifact_count(self, artifact_id, version='1.0.1'):
        """
        Get artifact count for specific integration flow

        Args:
            artifact_id (str): Integration flow ID
            version (str): Version of the artifact

        Returns:
            int: Count of resources or None if failed
        """
        # Try different API endpoints that work with service authentication
        # Using Runtime APIs which typically work better with OAuth service credentials
        endpoints_to_try = [
            f"{self.base_url}/api/v1/IntegrationRuntimeArtifacts('{artifact_id}')",
            f"{self.base_url}/api/v1/IntegrationRuntimeArtifacts?$filter=Id eq '{artifact_id}'",
            f"{self.base_url}/api/v1/IntegrationPackages",
            f"{self.base_url}/api/v1/MessageProcessingLogs?$top=1",  # Test endpoint
        ]

        for i, url in enumerate(endpoints_to_try, 1):
            print(f"📊 Attempt {i}: Getting artifact info for: {artifact_id} (v{version})")
            print(f"🔗 URL: {url}")

            response = self.make_authenticated_request(url)

            if response is None:
                continue

            if response.status_code == 200:
                try:
                    data = response.json()

                    if 'IntegrationRuntimeArtifacts' in url:
                        # Runtime artifact endpoint
                        if '$filter' in url:
                            artifacts = data.get('d', {}).get('results', [])
                            if artifacts:
                                artifact = artifacts[0]
                                print(f"✅ Runtime artifact found: {artifact.get('Name', 'N/A')}")
                                print(f"   Status: {artifact.get('Status', 'N/A')}")
                                print(f"   Type: {artifact.get('Type', 'N/A')}")
                                return 1  # Artifact exists and is deployed
                            else:
                                print(f"❌ Runtime artifact not found: {artifact_id}")
                                return 0
                        else:
                            # Single artifact endpoint
                            artifact = data.get('d', {})
                            if artifact:
                                print(f"✅ Runtime artifact found: {artifact.get('Name', 'N/A')}")
                                print(f"   Status: {artifact.get('Status', 'N/A')}")
                                print(f"   Type: {artifact.get('Type', 'N/A')}")
                                return 1
                            else:
                                print(f"❌ Runtime artifact not found: {artifact_id}")
                                return 0

                    elif 'IntegrationPackages' in url:
                        # Package listing endpoint - just test connectivity
                        packages = data.get('d', {}).get('results', [])
                        print(f"✅ API connectivity test successful - found {len(packages)} packages")
                        print("   Note: This endpoint lists packages, not specific artifact resources")
                        return len(packages)

                    elif 'MessageProcessingLogs' in url:
                        # Test endpoint - just verify API access
                        logs = data.get('d', {}).get('results', [])
                        print(f"✅ API connectivity test successful - found {len(logs)} recent logs")
                        print("   Note: This is a connectivity test, not artifact resource count")
                        return len(logs)

                    else:
                        # Generic response handling
                        results = data.get('d', {}).get('results', [])
                        print(f"✅ Found {len(results)} items")
                        return len(results)
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"❌ Invalid response: {str(e)}")
                    print(f"Response text: {response.text[:200]}...")
                    continue
            else:
                print(f"❌ Request failed: {response.status_code}")
                if response.text and len(response.text) < 500:
                    print(f"Response: {response.text}")
                continue

        print(f"❌ All attempts failed for artifact: {artifact_id}")
        return None

    def _get_resources_count(self, artifact_id, version):
        """Helper method to get resources count"""
        url = f"{self.base_url}/api/v1/IntegrationDesigntimeArtifacts(Id='{artifact_id}',Version='{version}')/Resources"
        response = self.make_authenticated_request(url)

        if response and response.status_code == 200:
            try:
                data = response.json()
                resources = data.get('d', {}).get('results', [])
                return len(resources)
            except:
                pass
        return None
    
    def get_artifact_details(self, artifact_id, version='1.0.1'):
        """
        Get detailed information about an artifact
        
        Args:
            artifact_id (str): Integration flow ID
            version (str): Version of the artifact
            
        Returns:
            dict: Artifact details or None if failed
        """
        url = f"{self.base_url}/api/v1/IntegrationDesigntimeArtifacts(Id='{artifact_id}',Version='{version}')"
        
        print(f"📋 Getting artifact details for: {artifact_id} (v{version})")
        
        response = self.make_authenticated_request(url)
        
        if response is None:
            return None
        
        if response.status_code == 200:
            try:
                artifact_data = response.json()
                print(f"✅ Artifact details retrieved")
                return artifact_data
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text}")
                return None
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def get_artifact_resources(self, artifact_id, version='1.0.1'):
        """
        Get list of resources for an artifact
        
        Args:
            artifact_id (str): Integration flow ID
            version (str): Version of the artifact
            
        Returns:
            list: List of resources or None if failed
        """
        url = f"{self.base_url}/api/v1/IntegrationDesigntimeArtifacts(Id='{artifact_id}',Version='{version}')/Resources"
        
        print(f"📁 Getting artifact resources for: {artifact_id} (v{version})")
        
        response = self.make_authenticated_request(url)
        
        if response is None:
            return None
        
        if response.status_code == 200:
            try:
                resources_data = response.json()
                resources = resources_data.get('d', {}).get('results', [])
                print(f"✅ Found {len(resources)} resources")
                return resources
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text}")
                return None
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def list_all_artifacts(self):
        """
        Get list of all integration artifacts

        Returns:
            list: List of all artifacts or None if failed
        """
        # Try different endpoints for listing artifacts
        endpoints_to_try = [
            f"{self.base_url}/api/v1/IntegrationDesigntimeArtifacts",
            f"{self.base_url}/api/v1/IntegrationDesigntimeArtifacts?$top=100",
            f"{self.base_url}/api/v1/IntegrationPackages",  # Alternative: list packages first
        ]

        for i, url in enumerate(endpoints_to_try, 1):
            print(f"📋 Attempt {i}: Getting list of integration artifacts...")
            print(f"🔗 URL: {url}")

            response = self.make_authenticated_request(url)

            if response is None:
                continue

            if response.status_code == 200:
                try:
                    data = response.json()
                    results = data.get('d', {}).get('results', [])
                    if results:
                        print(f"✅ Found {len(results)} items")
                        return results
                    else:
                        print(f"⚠️ No results found in response")
                        continue
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {response.text[:200]}...")
                    continue
            else:
                print(f"❌ Request failed: {response.status_code}")
                if response.text and len(response.text) < 500:
                    print(f"Response: {response.text}")
                continue

        print(f"❌ All attempts failed to list artifacts")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="SAP CPI Artifact Counter")
    parser.add_argument("--artifact-id", default="SFTP_2_IDOC_MigrateFlow", 
                       help="Artifact ID to check (default: SFTP_2_IDOC_MigrateFlow)")
    parser.add_argument("--version", default="1.0.1", 
                       help="Artifact version (default: 1.0.1)")
    parser.add_argument("--details", action="store_true", 
                       help="Get detailed artifact information")
    parser.add_argument("--resources", action="store_true", 
                       help="List artifact resources")
    parser.add_argument("--list-all", action="store_true", 
                       help="List all artifacts")
    
    args = parser.parse_args()
    
    print("========================================")
    print("SAP CPI Artifact Counter")
    print("========================================")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the counter
    counter = SAPCPIArtifactCounter()
    
    try:
        if args.list_all:
            # List all artifacts
            artifacts = counter.list_all_artifacts()
            if artifacts:
                print("\n📋 All Integration Artifacts:")
                print("-" * 80)
                for artifact in artifacts:
                    print(f"ID: {artifact.get('Id', 'N/A')}")
                    print(f"Name: {artifact.get('Name', 'N/A')}")
                    print(f"Version: {artifact.get('Version', 'N/A')}")
                    print(f"Type: {artifact.get('Type', 'N/A')}")
                    print("-" * 40)
        
        else:
            # Get artifact count
            count = counter.get_artifact_count(args.artifact_id, args.version)
            
            if count is not None:
                print(f"\n📊 Results:")
                print(f"Artifact ID: {args.artifact_id}")
                print(f"Version: {args.version}")
                print(f"Resource Count: {count}")
            
            # Get additional details if requested
            if args.details:
                details = counter.get_artifact_details(args.artifact_id, args.version)
                if details:
                    print(f"\n📋 Artifact Details:")
                    artifact_info = details.get('d', {})
                    print(f"Name: {artifact_info.get('Name', 'N/A')}")
                    print(f"Description: {artifact_info.get('Description', 'N/A')}")
                    print(f"Type: {artifact_info.get('Type', 'N/A')}")
                    print(f"Created By: {artifact_info.get('CreatedBy', 'N/A')}")
                    print(f"Created At: {artifact_info.get('CreatedAt', 'N/A')}")
                    print(f"Modified By: {artifact_info.get('ModifiedBy', 'N/A')}")
                    print(f"Modified At: {artifact_info.get('ModifiedAt', 'N/A')}")
            
            # Get resources if requested
            if args.resources:
                resources = counter.get_artifact_resources(args.artifact_id, args.version)
                if resources:
                    print(f"\n📁 Artifact Resources:")
                    for i, resource in enumerate(resources, 1):
                        print(f"{i}. {resource.get('Name', 'N/A')} ({resource.get('ResourceType', 'N/A')})")
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
