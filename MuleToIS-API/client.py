"""
Client script for the MuleToIS API.
This script demonstrates how to use the API to generate an iFlow from a markdown file.
"""

import os
import sys
import requests
import json
import time
import argparse

def generate_iflow(api_url, markdown_file, iflow_name=None):
    """
    Generate an iFlow from a markdown file
    
    Args:
        api_url (str): Base URL of the API
        markdown_file (str): Path to the markdown file
        iflow_name (str, optional): Name of the iFlow
        
    Returns:
        str: Job ID if successful, None otherwise
    """
    # Read markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Prepare request data
    data = {
        "markdown": markdown_content
    }
    
    if iflow_name:
        data["iflow_name"] = iflow_name
    
    # Send request
    try:
        response = requests.post(f"{api_url}/api/generate-iflow", json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"iFlow generation started: {result['message']}")
        print(f"Job ID: {result['job_id']}")
        
        return result['job_id']
    except requests.exceptions.RequestException as e:
        print(f"Error generating iFlow: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def check_job_status(api_url, job_id, wait=True, max_attempts=240, interval=5):
    """
    Check the status of a job
    
    Args:
        api_url (str): Base URL of the API
        job_id (str): Job ID
        wait (bool): Whether to wait for the job to complete
        max_attempts (int): Maximum number of attempts
        interval (int): Interval between attempts in seconds
        
    Returns:
        dict: Job status if successful, None otherwise
    """
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{api_url}/api/jobs/{job_id}")
            response.raise_for_status()
            
            result = response.json()
            status = result['status']
            
            print(f"Job status: {status}")
            print(f"Message: {result['message']}")
            
            if status == 'completed' or status == 'failed' or not wait:
                return result
            
            print(f"Waiting {interval} seconds before next check...")
            time.sleep(interval)
            
        except requests.exceptions.RequestException as e:
            print(f"Error checking job status: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        
        attempt += 1
    
    print(f"Job did not complete after {max_attempts} attempts")
    return None

def download_iflow(api_url, job_id, output_file=None):
    """
    Download the generated iFlow
    
    Args:
        api_url (str): Base URL of the API
        job_id (str): Job ID
        output_file (str, optional): Path to save the iFlow ZIP file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.get(f"{api_url}/api/jobs/{job_id}/download", stream=True)
        response.raise_for_status()
        
        # Get filename from Content-Disposition header if available
        if not output_file:
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition and 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
                output_file = filename
            else:
                output_file = f"iflow_{job_id}.zip"
        
        # Save the file
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"iFlow downloaded successfully: {output_file}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading iFlow: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate an iFlow from a markdown file')
    parser.add_argument('--api-url', default='http://localhost:5000', help='Base URL of the API')
    parser.add_argument('--markdown-file', required=True, help='Path to the markdown file')
    parser.add_argument('--iflow-name', help='Name of the iFlow')
    parser.add_argument('--output-file', help='Path to save the iFlow ZIP file')
    parser.add_argument('--no-wait', action='store_true', help='Do not wait for the job to complete')
    
    args = parser.parse_args()
    
    # Generate iFlow
    job_id = generate_iflow(args.api_url, args.markdown_file, args.iflow_name)
    if not job_id:
        return
    
    # Check job status
    job_status = check_job_status(args.api_url, job_id, not args.no_wait)
    if not job_status:
        return
    
    # Download iFlow if job completed successfully
    if job_status['status'] == 'completed':
        download_iflow(args.api_url, job_id, args.output_file)

if __name__ == "__main__":
    main()
