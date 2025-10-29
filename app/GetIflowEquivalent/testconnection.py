
import requests
import base64
import json

def test_btp_authentication():
    # BTP OAuth token URL
    token_url = "https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token"
    
    # Your client credentials
    client_id = "sb-9192486c-93cf-4f8c-b678-b70179f525d2!b124895|it-rt-itr-internal-2hco92jx!b56186"
    client_secret = "93374dee-1b82-4c54-b948-63f7fc94e096$KqvXtSNXE_j-rSWxjLtGkUAwzfo0czbobxSOGT4l1ts="  # Update with your client secret
    
    # API endpoint for testing after authentication
    api_base_url = "https://itr-internal-2hco92jx.integrationsuite.cfapps.us10-002.hana.ondemand.com"
    test_endpoint = f"{api_base_url}/api/v1/DiscoveryContent?$top=1"  # Just get one result to test
    
    try:
        # Standard OAuth client credentials flow
        auth_string = f"{client_id}:{client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = "grant_type=client_credentials"
        
        print(f"Requesting token from: {token_url}")
        response = requests.post(token_url, headers=headers, data=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("Token received successfully!")
            print(f"Token type: {token_data.get('token_type')}")
            print(f"Expires in: {token_data.get('expires_in')} seconds")
            
            # Test using the token to access an API endpoint
            access_token = token_data.get('access_token')
            print("\nTesting API access with the token...")
            
            api_headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            api_response = requests.get(test_endpoint, headers=api_headers)
            print(f"API Status: {api_response.status_code}")
            
            if api_response.status_code == 200:
                print("API access successful!")
                result = api_response.json()
                if 'value' in result and len(result['value']) > 0:
                    print(f"Found {len(result['value'])} item(s)")
                    print(f"First item name: {result['value'][0].get('Name')}")
                else:
                    print("API returned successfully but no items found")
            else:
                print(f"API access failed: {api_response.text}")
        else:
            print(f"Failed to get token: {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_btp_authentication()