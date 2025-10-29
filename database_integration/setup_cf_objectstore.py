"""
Cloud Foundry ObjectStore Setup Script
Automates the creation and configuration of CF objectstore service
"""

import subprocess
import json
import os
import sys
import time
from typing import Dict, Any, Optional

def run_cf_command(command: str) -> tuple[bool, str]:
    """Run a CF CLI command and return success status and output"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def check_cf_login() -> bool:
    """Check if user is logged into CF"""
    success, output = run_cf_command("cf target")
    if success and "api endpoint" in output.lower():
        print("✅ Already logged into Cloud Foundry")
        return True
    else:
        print("❌ Not logged into Cloud Foundry")
        print("Please run: cf login")
        return False

def check_marketplace() -> bool:
    """Check if objectstore service is available"""
    print("🔍 Checking CF marketplace for objectstore service...")
    success, output = run_cf_command("cf marketplace")
    
    if success and "objectstore" in output:
        print("✅ ObjectStore service is available in marketplace")
        return True
    else:
        print("❌ ObjectStore service not found in marketplace")
        print("Available services:")
        print(output)
        return False

def create_objectstore_service(service_name: str = "is-migration-storage") -> bool:
    """Create objectstore service instance"""
    print(f"📦 Creating objectstore service instance: {service_name}")
    
    success, output = run_cf_command(f"cf create-service objectstore standard {service_name}")
    
    if success:
        print(f"✅ Service creation initiated: {service_name}")
        return True
    else:
        if "already exists" in output.lower():
            print(f"ℹ️ Service {service_name} already exists")
            return True
        else:
            print(f"❌ Failed to create service: {output}")
            return False

def wait_for_service_creation(service_name: str, max_wait_minutes: int = 10) -> bool:
    """Wait for service creation to complete"""
    print(f"⏳ Waiting for service {service_name} to be ready...")
    
    max_attempts = max_wait_minutes * 6  # Check every 10 seconds
    
    for attempt in range(max_attempts):
        success, output = run_cf_command("cf services")
        
        if success and service_name in output:
            lines = output.split('\n')
            for line in lines:
                if service_name in line:
                    if "create succeeded" in line.lower():
                        print(f"✅ Service {service_name} is ready!")
                        return True
                    elif "create in progress" in line.lower():
                        print(f"⏳ Still creating... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(10)
                        break
                    elif "create failed" in line.lower():
                        print(f"❌ Service creation failed: {line}")
                        return False
        
        if attempt == max_attempts - 1:
            print(f"⏰ Timeout waiting for service creation")
            return False
    
    return False

def create_service_key(service_name: str, key_name: str = "is-migration-key") -> bool:
    """Create service key for accessing credentials"""
    print(f"🔑 Creating service key: {key_name}")
    
    success, output = run_cf_command(f"cf create-service-key {service_name} {key_name}")
    
    if success:
        print(f"✅ Service key created: {key_name}")
        return True
    else:
        if "already exists" in output.lower():
            print(f"ℹ️ Service key {key_name} already exists")
            return True
        else:
            print(f"❌ Failed to create service key: {output}")
            return False

def get_service_credentials(service_name: str, key_name: str) -> Optional[Dict[str, Any]]:
    """Get service credentials from service key"""
    print(f"📋 Retrieving credentials from service key...")
    
    success, output = run_cf_command(f"cf service-key {service_name} {key_name}")
    
    if success:
        try:
            # Parse the JSON from the output
            # The output usually contains some header text, so we need to find the JSON part
            lines = output.split('\n')
            json_start = -1
            
            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    json_start = i
                    break
            
            if json_start >= 0:
                json_text = '\n'.join(lines[json_start:])
                credentials = json.loads(json_text)
                print("✅ Successfully retrieved credentials")
                return credentials
            else:
                print("❌ Could not find JSON credentials in output")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse credentials JSON: {e}")
            print("Raw output:")
            print(output)
            return None
    else:
        print(f"❌ Failed to get service key: {output}")
        return None

def update_env_file(credentials: Dict[str, Any]) -> bool:
    """Update .env file with S3 credentials"""
    print("📝 Updating .env file with S3 credentials...")
    
    try:
        # Read existing .env file
        env_content = ""
        env_file_path = ".env"
        
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                env_content = f.read()
        
        # Prepare S3 configuration
        s3_config = f"""
# Cloud Foundry ObjectStore S3 Configuration
AWS_ACCESS_KEY_ID={credentials.get('access_key_id', '')}
AWS_SECRET_ACCESS_KEY={credentials.get('secret_access_key', '')}
S3_BUCKET_NAME={credentials.get('bucket', '')}
AWS_REGION={credentials.get('region', 'us-east-1')}
S3_ENDPOINT_URL={credentials.get('host', '')}
S3_USERNAME={credentials.get('username', '')}
"""
        
        # Remove existing S3 configuration if present
        lines = env_content.split('\n')
        filtered_lines = []
        skip_s3_section = False
        
        for line in lines:
            if line.strip().startswith('# Cloud Foundry ObjectStore'):
                skip_s3_section = True
                continue
            elif line.strip().startswith('#') and skip_s3_section:
                skip_s3_section = False
            elif skip_s3_section and any(line.startswith(key) for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME', 'AWS_REGION', 'S3_ENDPOINT_URL', 'S3_USERNAME']):
                continue
            
            if not skip_s3_section:
                filtered_lines.append(line)
        
        # Add new S3 configuration
        updated_content = '\n'.join(filtered_lines).rstrip() + s3_config
        
        # Write back to .env file
        with open(env_file_path, 'w') as f:
            f.write(updated_content)
        
        print("✅ .env file updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def bind_service_to_apps(service_name: str, apps: list = None) -> bool:
    """Bind objectstore service to applications"""
    if apps is None:
        apps = [
            "it-resonance-main-api",
            "mule-to-is-api", 
            "boomi-to-is-api",
            "mulesoft-iflow-api-gemma3"
        ]
    
    print(f"🔗 Binding service {service_name} to applications...")
    
    success_count = 0
    for app in apps:
        print(f"  Binding to {app}...")
        success, output = run_cf_command(f"cf bind-service {app} {service_name}")
        
        if success:
            print(f"  ✅ Successfully bound to {app}")
            success_count += 1
        else:
            if "already bound" in output.lower():
                print(f"  ℹ️ Already bound to {app}")
                success_count += 1
            else:
                print(f"  ❌ Failed to bind to {app}: {output}")
    
    print(f"🔗 Bound to {success_count}/{len(apps)} applications")
    return success_count > 0

def main():
    """Main setup function"""
    print("🚀 Cloud Foundry ObjectStore Setup for IS-Migration")
    print("=" * 60)
    
    service_name = "is-migration-storage"
    key_name = "is-migration-key"
    
    # Step 1: Check CF login
    if not check_cf_login():
        return False
    
    # Step 2: Check marketplace
    if not check_marketplace():
        return False
    
    # Step 3: Create service instance
    if not create_objectstore_service(service_name):
        return False
    
    # Step 4: Wait for service creation
    if not wait_for_service_creation(service_name):
        print("⚠️ Service creation may still be in progress. You can check with: cf services")
        print("Continue with the next steps once the service shows 'create succeeded'")
        return False
    
    # Step 5: Create service key
    if not create_service_key(service_name, key_name):
        return False
    
    # Step 6: Get credentials
    credentials = get_service_credentials(service_name, key_name)
    if not credentials:
        return False
    
    # Step 7: Update .env file
    if not update_env_file(credentials):
        return False
    
    # Step 8: Bind to applications
    bind_service_to_apps(service_name)
    
    print("\n🎉 ObjectStore setup completed successfully!")
    print("\nNext steps:")
    print("1. Restart your applications to pick up the new environment variables")
    print("2. Test the S3 integration with your database system")
    print("3. Your applications now have access to S3-compatible object storage!")
    
    print(f"\nService Details:")
    print(f"  Service Name: {service_name}")
    print(f"  Service Key: {key_name}")
    print(f"  Bucket: {credentials.get('bucket', 'N/A')}")
    print(f"  Region: {credentials.get('region', 'N/A')}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
