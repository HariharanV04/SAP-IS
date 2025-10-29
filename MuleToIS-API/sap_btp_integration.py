"""
SAP BTP Integration module for deploying integration flows to SAP Integration Suite.
"""

import os
import requests
import json
import logging
import base64
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SapBtpIntegration:
    """
    Class for interacting with SAP BTP Integration Suite APIs
    """
    
    def __init__(self, tenant_url, client_id, client_secret, oauth_url=None):
        """
        Initialize the SAP BTP Integration client
        
        Args:
            tenant_url (str): The URL of the SAP Integration Suite tenant
            client_id (str): OAuth client ID
            client_secret (str): OAuth client secret
            oauth_url (str, optional): OAuth token URL. If not provided, will use default path
        """
        self.tenant_url = tenant_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Set OAuth URL
        if oauth_url:
            self.oauth_url = oauth_url
        else:
            # Default OAuth URL pattern for SAP BTP
            self.oauth_url = f"{self.tenant_url}/oauth/token"
        
        # API endpoints
        self.api_base = f"{self.tenant_url}/api/v1"
        self.integration_packages_api = f"{self.api_base}/IntegrationPackages"
        self.integration_designs_api = f"{self.api_base}/IntegrationDesigntimeArtifacts"
        
        # Token cache
        self.access_token = None
        self.token_expiry = 0
    
    def get_auth_token(self):
        """
        Get OAuth token for API authentication
        
        Returns:
            str: Access token
        """
        try:
            # Basic auth for token request
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_header = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(
                self.oauth_url,
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                return self.access_token
            else:
                logger.error(f"Failed to get auth token: {response.status_code} - {response.text}")
                raise Exception(f"Failed to get auth token: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting auth token: {str(e)}")
            raise
    
    def get_headers(self):
        """
        Get headers with auth token for API requests
        
        Returns:
            dict: Headers with auth token
        """
        if not self.access_token:
            self.get_auth_token()
            
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def list_integration_packages(self):
        """
        List all integration packages
        
        Returns:
            list: List of integration packages
        """
        try:
            headers = self.get_headers()
            response = requests.get(
                self.integration_packages_api,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to list integration packages: {response.status_code} - {response.text}")
                raise Exception(f"Failed to list integration packages: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error listing integration packages: {str(e)}")
            raise
    
    def deploy_integration_flow(self, package_id, iflow_name, iflow_zip_path, iflow_id=None, description=None):
        """
        Deploy an integration flow to SAP Integration Suite
        
        Args:
            package_id (str): ID of the integration package
            iflow_name (str): Name of the integration flow
            iflow_zip_path (str): Path to the integration flow ZIP file
            iflow_id (str, optional): ID for the integration flow. If not provided, will use iflow_name
            description (str, optional): Description for the integration flow
            
        Returns:
            dict: Deployment result
        """
        try:
            # If no iflow_id provided, use the iflow_name (with spaces replaced by underscores)
            if not iflow_id:
                iflow_id = iflow_name.replace(' ', '_')
            
            # Step 1: Create or update the integration flow design time artifact
            headers = self.get_headers()
            headers['Content-Type'] = 'application/zip'
            
            # Read the ZIP file
            with open(iflow_zip_path, 'rb') as zip_file:
                zip_content = zip_file.read()
            
            # Create/update the integration flow
            design_api_url = f"{self.integration_designs_api}(Id='{iflow_id}',Version='active')/Content"
            
            # Check if the integration flow already exists
            check_url = f"{self.integration_designs_api}(Id='{iflow_id}',Version='active')"
            check_response = requests.get(check_url, headers=self.get_headers())
            
            if check_response.status_code == 200:
                # Update existing integration flow
                response = requests.put(
                    design_api_url,
                    headers=headers,
                    data=zip_content
                )
            else:
                # Create new integration flow metadata first
                create_metadata_url = f"{self.integration_designs_api}"
                metadata_headers = self.get_headers()
                metadata_headers['Content-Type'] = 'application/json'
                
                metadata = {
                    "Name": iflow_name,
                    "Id": iflow_id,
                    "PackageId": package_id,
                    "Description": description or f"Integration flow generated for {iflow_name}"
                }
                
                metadata_response = requests.post(
                    create_metadata_url,
                    headers=metadata_headers,
                    json=metadata
                )
                
                if metadata_response.status_code not in [201, 200]:
                    logger.error(f"Failed to create integration flow metadata: {metadata_response.status_code} - {metadata_response.text}")
                    raise Exception(f"Failed to create integration flow metadata: {metadata_response.status_code}")
                
                # Now upload the content
                response = requests.put(
                    design_api_url,
                    headers=headers,
                    data=zip_content
                )
            
            if response.status_code not in [200, 201, 202]:
                logger.error(f"Failed to upload integration flow: {response.status_code} - {response.text}")
                raise Exception(f"Failed to upload integration flow: {response.status_code}")
            
            # Step 2: Deploy the integration flow
            deploy_url = f"{self.integration_designs_api}(Id='{iflow_id}',Version='active')/Configurations/Deploy"
            deploy_response = requests.post(
                deploy_url,
                headers=self.get_headers()
            )
            
            if deploy_response.status_code not in [200, 201, 202]:
                logger.error(f"Failed to deploy integration flow: {deploy_response.status_code} - {deploy_response.text}")
                raise Exception(f"Failed to deploy integration flow: {deploy_response.status_code}")
            
            return {
                "status": "success",
                "message": "Integration flow deployed successfully",
                "iflow_id": iflow_id,
                "package_id": package_id
            }
                
        except Exception as e:
            logger.error(f"Error deploying integration flow: {str(e)}")
            raise
