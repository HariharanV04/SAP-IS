"""
Direct iFlow deployment module for deploying integration flows to SAP Integration Suite.
This module uses a direct API approach to deploy iFlows to SAP Integration Suite.
"""

import os
import requests
import base64
import json
import time
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectIflowDeployment:
    """
    Class for directly deploying iFlows to SAP Integration Suite
    """
    
    def __init__(self, client_id=None, client_secret=None, token_url=None, base_url=None):
        """
        Initialize the direct iFlow deployment client
        
        Args:
            client_id (str): OAuth client ID
            client_secret (str): OAuth client secret
            token_url (str): OAuth token URL
            base_url (str): Base URL of the SAP Integration Suite tenant
        """
        # Load environment variables if not provided
        load_dotenv()
        
        # Use WORKING ITR Internal credentials (from working script)
        self.client_id = client_id or "sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895|it!b410334"
        self.client_secret = client_secret or "5813ca83-4ba6-4231-96e1-1a48a80eafec$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w="
        self.token_url = token_url or "https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token"
        self.base_url = base_url or "https://itr-internal-2hco92jx.it-cpi034.cfapps.us10-002.hana.ondemand.com"
        
        # Validate required parameters
        if not all([self.client_id, self.client_secret, self.token_url, self.base_url]):
            missing = []
            if not self.client_id: missing.append("SAP_BTP_CLIENT_ID")
            if not self.client_secret: missing.append("SAP_BTP_CLIENT_SECRET")
            if not self.token_url: missing.append("SAP_BTP_OAUTH_URL")
            if not self.base_url: missing.append("SAP_BTP_TENANT_URL")
            
            error_msg = f"Missing required parameters: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def log(self, message):
        """Print a log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        logger.info(f"[{timestamp}] {message}")
        # Force output to be displayed immediately
        sys.stdout.flush()

    def deploy_iflow(self, iflow_path, iflow_id=None, iflow_name=None, package_id="ConversionPackages"):
        """
        Deploy an iFlow to SAP Integration Suite
        
        Args:
            iflow_path (str): Path to the iFlow ZIP file
            iflow_id (str, optional): Technical ID for the iFlow. If None, derived from filename
            iflow_name (str, optional): Display name for the iFlow. If None, derived from filename
            package_id (str, optional): ID of the package where the iFlow will be deployed
            
        Returns:
            dict: Deployment result with status and message
        """
        self.log("Starting iFlow deployment using WORKING method...")

        # Validate file
        if not os.path.exists(iflow_path):
            error_msg = f"File not found: {iflow_path}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}

        # Set defaults using working approach
        if not iflow_name:
            iflow_name = os.path.splitext(os.path.basename(iflow_path))[0]
        if not iflow_id:
            iflow_id = f"Generated_{iflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.log(f"Deploying: {iflow_name} (ID: {iflow_id}) to package: {package_id}")

        file_size = os.path.getsize(iflow_path)
        self.log(f"Found iFlow file: {iflow_path} ({file_size} bytes)")
        
        try:
            # Step 1: Get OAuth token using WORKING method
            self.log("Getting OAuth token...")
            response = requests.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )

            if response.status_code != 200:
                error_msg = f"OAuth failed: {response.status_code} - {response.text}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}

            oauth_token = response.json()["access_token"]
            self.log("✅ OAuth token obtained")

            # Step 2: Read and encode iFlow file using WORKING method
            self.log("Reading and encoding iFlow file...")
            with open(iflow_path, "rb") as f:
                iflow_content = f.read()

            base64_content = base64.b64encode(iflow_content).decode("utf-8")
            self.log(f"File encoded: {len(base64_content)} characters")

            # Step 3: Create payload using WORKING method
            payload = {
                "Name": iflow_name,
                "Id": iflow_id,
                "PackageId": package_id,
                "ArtifactContent": base64_content
            }

            # Step 4: Deploy with WORKING headers (Bearer + Minimal)
            self.log("Deploying with working headers...")
            headers = {
                "Authorization": f"Bearer {oauth_token}",
                "Content-Type": "application/json"
            }

            url = f"{self.base_url}/api/v1/IntegrationDesigntimeArtifacts"
            self.log(f"POST to: {url}")

            response = requests.post(url, headers=headers, json=payload, timeout=120)

            self.log(f"Response status: {response.status_code}")

            if response.status_code in [200, 201, 202]:
                self.log("✅ Deployment successful!")

                return {
                    "status": "success",
                    "message": "iFlow deployed successfully",
                    "iflow_id": iflow_id,
                    "package_id": package_id,
                    "iflow_name": iflow_name,
                    "response_code": response.status_code,
                    "method": "Bearer + Minimal Headers"
                }
            elif response.status_code == 500 and "already exists" in response.text:
                return {
                    "status": "error",
                    "message": f"iFlow with ID '{iflow_id}' already exists. Use a different ID or delete the existing one."
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:300]}"
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Unexpected error during iFlow deployment: {str(e)}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}

# Function to deploy an iFlow directly
def deploy_iflow(iflow_path, iflow_id=None, iflow_name=None, package_id="ConversionPackages"):
    """
    Deploy an iFlow to SAP Integration Suite
    
    Args:
        iflow_path (str): Path to the iFlow ZIP file
        iflow_id (str, optional): Technical ID for the iFlow. If None, derived from filename
        iflow_name (str, optional): Display name for the iFlow. If None, derived from filename
        package_id (str, optional): ID of the package where the iFlow will be deployed
        
    Returns:
        dict: Deployment result with status and message
    """
    deployment = DirectIflowDeployment()
    return deployment.deploy_iflow(iflow_path, iflow_id, iflow_name, package_id)

# Test function
def test_deploy_iflow():
    """Test the direct iFlow deployment"""
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Deploy the iFlow
    result = deploy_iflow("sap_generated_iflow.zip")
    print(f"Deployment result: {result}")

if __name__ == "__main__":
    test_deploy_iflow()
