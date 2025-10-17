import requests
import base64
import os
import json
import time
import sys

# Your credentials
client_id = "sb-09f9c01e-d098-4f72-8b09-b39757ec93a2!b443330|it!b26655"
client_secret = "3a96f9f7-f596-48a8-903c-afd54ad9583e$6wFmr1lu8TWwA8OUI2GnRsL4Vie86YcIiUaMBei8zD0="
token_url = "https://4728b940trial.authentication.us10.hana.ondemand.com/oauth/token"
base_url = "https://4728b940trial.it-cpitrial05.cfapps.us10-001.hana.ondemand.com"

# iFlow details
iflow_path = "sap_generated_iflow.zip"
iflow_id = "SAPGeneratedIFlow"
iflow_name = "SAP Generated IFlow"
package_id = "WithRequestReply"

def log(message):
    """Print a log message with timestamp"""
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{timestamp}] {message}")
    # Force output to be displayed immediately
    sys.stdout.flush()

def upload_iflow_using_json_api():
    log("Starting iFlow upload process using JSON API approach...")
    
    # Check if file exists
    if not os.path.exists(iflow_path):
        log(f"Error: iFlow file '{iflow_path}' not found in {os.getcwd()}")
        return False
    else:
        file_size = os.path.getsize(iflow_path)
        log(f"Found iFlow file: {iflow_path} ({file_size} bytes)")
    
    # Step 1: Get OAuth token
    log("Getting OAuth token...")
    try:
        response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        
        log(f"OAuth response status: {response.status_code}")
        
        if response.status_code != 200:
            log(f"Failed to get OAuth token: {response.text}")
            return False
        
        try:
            oauth_token = response.json()["access_token"]
            log("OAuth token obtained successfully")
        except (json.JSONDecodeError, KeyError) as e:
            log(f"Error parsing OAuth response: {e}")
            log(f"Response content: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        log(f"Network error during OAuth request: {e}")
        return False
    
    # Step 2: Try to get CSRF token
    log("Getting CSRF token...")
    csrf_token = None
    
    for endpoint in ["/api/v1/IntegrationDesigntimeArtifacts", "/itspaces/api/1.0/workspace"]:
        log(f"Trying CSRF endpoint: {base_url}{endpoint}")
        try:
            response = requests.get(
                f"{base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {oauth_token}",
                    "X-CSRF-Token": "Fetch"
                },
                timeout=30
            )
            
            log(f"CSRF request to {endpoint} returned status {response.status_code}")
            
            if "X-CSRF-Token" in response.headers:
                csrf_token = response.headers["X-CSRF-Token"]
                log(f"CSRF token obtained: {csrf_token[:5]}...")
                break
            else:
                log(f"No CSRF token in response headers. Headers: {list(response.headers.keys())}")
        except requests.exceptions.RequestException as e:
            log(f"Network error during CSRF request to {endpoint}: {e}")
    
    # Step 3: Read and encode iFlow file
    log("Reading and encoding iFlow file...")
    try:
        with open(iflow_path, "rb") as f:
            iflow_content = f.read()
        
        log(f"Read {len(iflow_content)} bytes from file")
        
        base64_content = base64.b64encode(iflow_content).decode("utf-8")
        log(f"File encoded as base64 ({len(base64_content)} characters)")
    except Exception as e:
        log(f"Error reading or encoding file: {e}")
        return False
    
    # Step 4: Create payload
    log("Creating payload...")
    payload = {
        "Name": iflow_name,
        "Id": iflow_id,
        "PackageId": package_id,
        "ArtifactContent": base64_content
    }
    log("Payload created successfully")
    
    # Step 5: Upload iFlow
    log("Uploading iFlow...")
    
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "DataServiceVersion": "2.0"
    }
    
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token
        log("Using CSRF token in request")
    else:
        log("No CSRF token available, proceeding without it")
    
    for endpoint in ["/api/v1/IntegrationDesigntimeArtifacts", "/itspaces/api/1.0/workspace/content"]:
        log(f"Trying upload endpoint: {base_url}{endpoint}")
        
        try:
            # Log that we're about to make the request
            log("Sending upload request...")
            
            # Make the request with a longer timeout
            response = requests.post(
                f"{base_url}{endpoint}",
                headers=headers,
                json=payload,
                timeout=120  # Longer timeout for the upload
            )
            
            log(f"Upload response status: {response.status_code}")
            log(f"Response content: {response.text[:500]}..." if len(response.text) > 500 else f"Response content: {response.text}")
            
            if response.status_code in [200, 201, 202]:
                log("Upload successful!")
                return True
        except requests.exceptions.RequestException as e:
            log(f"Network error during upload to {endpoint}: {e}")
    
    log("All upload attempts failed")
    return False

# Run the upload function
log("Script started")
result = upload_iflow_using_json_api()
log(f"Script finished with result: {'SUCCESS' if result else 'FAILURE'}")