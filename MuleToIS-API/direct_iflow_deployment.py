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
        
        # Use WORKING ITR Internal credentials (from working BoomiToIS script)
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

    def deploy_iflow(self, iflow_path, iflow_id=None, iflow_name=None, package_id="WithRequestReply"):
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
        self.log("Starting iFlow upload process using JSON API approach...")
        
        # If iflow_id or iflow_name not provided, derive from filename
        if not iflow_id or not iflow_name:
            # Get the filename without extension
            filename = os.path.basename(iflow_path)
            filename_without_ext = os.path.splitext(filename)[0]
            
            # Set iflow_id and iflow_name if not provided
            if not iflow_id:
                iflow_id = filename_without_ext
                self.log(f"Using iFlow ID derived from filename: {iflow_id}")
            
            if not iflow_name:
                iflow_name = filename_without_ext
                self.log(f"Using iFlow name derived from filename: {iflow_name}")
        
        # Check if file exists
        if not os.path.exists(iflow_path):
            error_msg = f"Error: iFlow file '{iflow_path}' not found in {os.getcwd()}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}
        else:
            file_size = os.path.getsize(iflow_path)
            self.log(f"Found iFlow file: {iflow_path} ({file_size} bytes)")
        
        try:
            # Step 1: Get OAuth token
            self.log("Getting OAuth token...")
            try:
                response = requests.post(
                    self.token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=30
                )
                
                self.log(f"OAuth response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_msg = f"Failed to get OAuth token: {response.text}"
                    self.log(error_msg)
                    return {"status": "error", "message": error_msg}
                
                try:
                    oauth_token = response.json()["access_token"]
                    self.log("OAuth token obtained successfully")
                except (json.JSONDecodeError, KeyError) as e:
                    error_msg = f"Error parsing OAuth response: {e}"
                    self.log(error_msg)
                    self.log(f"Response content: {response.text}")
                    return {"status": "error", "message": error_msg}
            except requests.exceptions.RequestException as e:
                error_msg = f"Network error during OAuth request: {e}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
            
            # Step 2: Try to get CSRF token
            self.log("Getting CSRF token...")
            csrf_token = None
            
            for endpoint in ["/api/v1/IntegrationDesigntimeArtifacts", "/itspaces/api/1.0/workspace"]:
                self.log(f"Trying CSRF endpoint: {self.base_url}{endpoint}")
                try:
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers={
                            "Authorization": f"Bearer {oauth_token}",
                            "X-CSRF-Token": "Fetch"
                        },
                        timeout=30
                    )
                    
                    self.log(f"CSRF request to {endpoint} returned status {response.status_code}")
                    
                    if "X-CSRF-Token" in response.headers:
                        csrf_token = response.headers["X-CSRF-Token"]
                        self.log(f"CSRF token obtained: {csrf_token[:5]}...")
                        break
                    else:
                        self.log(f"No CSRF token in response headers. Headers: {list(response.headers.keys())}")
                except requests.exceptions.RequestException as e:
                    self.log(f"Network error during CSRF request to {endpoint}: {e}")
            
            # Step 3: Read and encode iFlow file
            self.log("Reading and encoding iFlow file...")
            try:
                with open(iflow_path, "rb") as f:
                    iflow_content = f.read()
                
                self.log(f"Read {len(iflow_content)} bytes from file")
                
                base64_content = base64.b64encode(iflow_content).decode("utf-8")
                self.log(f"File encoded as base64 ({len(base64_content)} characters)")
            except Exception as e:
                error_msg = f"Error reading or encoding file: {e}"
                self.log(error_msg)
                return {"status": "error", "message": error_msg}
            
            # Step 4: Create payload
            self.log("Creating payload...")
            payload = {
                "Name": iflow_name,
                "Id": iflow_id,
                "PackageId": package_id,
                "ArtifactContent": base64_content
            }
            self.log("Payload created successfully")
            
            # Step 5: Upload iFlow
            self.log("Uploading iFlow...")
            
            headers = {
                "Authorization": f"Bearer {oauth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "DataServiceVersion": "2.0"
            }
            
            if csrf_token:
                headers["X-CSRF-Token"] = csrf_token
                self.log("Using CSRF token in request")
            else:
                self.log("No CSRF token available, proceeding without it")
            
            success = False
            response_text = ""
            
            for endpoint in ["/api/v1/IntegrationDesigntimeArtifacts", "/itspaces/api/1.0/workspace/content"]:
                self.log(f"Trying upload endpoint: {self.base_url}{endpoint}")
                
                try:
                    # Log that we're about to make the request
                    self.log("Sending upload request...")
                    
                    # Make the request with a longer timeout
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        json=payload,
                        timeout=120  # Longer timeout for the upload
                    )
                    
                    self.log(f"Upload response status: {response.status_code}")
                    response_text = response.text
                    self.log(f"Response content: {response_text[:500]}..." if len(response_text) > 500 else f"Response content: {response_text}")
                    
                    if response.status_code in [200, 201, 202]:
                        self.log("Upload successful!")
                        success = True
                        break
                except requests.exceptions.RequestException as e:
                    self.log(f"Network error during upload to {endpoint}: {e}")
            
            if success:
                return {
                    "status": "success",
                    "message": "iFlow deployed successfully",
                    "iflow_id": iflow_id,
                    "package_id": package_id,
                    "iflow_name": iflow_name
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to deploy iFlow. Response: {response_text}"
                }
                
        except Exception as e:
            error_msg = f"Unexpected error during iFlow deployment: {str(e)}"
            self.log(error_msg)
            return {"status": "error", "message": error_msg}

# Function to deploy an iFlow directly
def deploy_iflow(iflow_path, iflow_id=None, iflow_name=None, package_id="WithRequestReply"):
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
