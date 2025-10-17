"""
AWS S3 Direct Setup Script for IS-Migration
Configure your existing AWS S3 bucket with the application
"""

import os
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

def get_aws_credentials():
    """Get AWS credentials from user input"""
    print("🔑 AWS S3 Configuration Setup")
    print("-" * 40)
    
    # Your bucket details
    bucket_name = "is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias"
    region = "us-east-1"  # Default, can be changed
    
    print(f"Bucket Name: {bucket_name}")
    print(f"AWS Account: 830858425934")
    
    # Get credentials
    access_key = input("\nEnter your AWS Access Key ID: ").strip()
    secret_key = input("Enter your AWS Secret Access Key: ").strip()
    
    # Confirm region
    region_input = input(f"Enter AWS Region (default: {region}): ").strip()
    if region_input:
        region = region_input
    
    return {
        'access_key_id': access_key,
        'secret_access_key': secret_key,
        'bucket_name': bucket_name,
        'region': region
    }

def test_s3_connection(credentials):
    """Test S3 connection with provided credentials"""
    print("\n🔍 Testing S3 Connection...")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=credentials['access_key_id'],
            aws_secret_access_key=credentials['secret_access_key'],
            region_name=credentials['region']
        )
        
        # Test bucket access
        response = s3_client.head_bucket(Bucket=credentials['bucket_name'])
        print("✅ S3 connection successful!")
        print(f"✅ Bucket '{credentials['bucket_name']}' is accessible")
        
        # Test list objects (optional)
        try:
            objects = s3_client.list_objects_v2(
                Bucket=credentials['bucket_name'],
                MaxKeys=1
            )
            print(f"✅ Bucket permissions verified")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                print(f"❌ Bucket '{credentials['bucket_name']}' does not exist")
                return False
            else:
                print(f"⚠️ Limited bucket access: {e}")
        
        return True
        
    except NoCredentialsError:
        print("❌ Invalid AWS credentials")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidAccessKeyId':
            print("❌ Invalid Access Key ID")
        elif error_code == 'SignatureDoesNotMatch':
            print("❌ Invalid Secret Access Key")
        elif error_code == 'AccessDenied':
            print("❌ Access denied - check your permissions")
        else:
            print(f"❌ AWS Error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def update_env_file(credentials):
    """Update .env file with AWS S3 credentials"""
    print("\n📝 Updating .env file...")
    
    try:
        # Read existing .env file
        env_content = ""
        env_file_path = ".env"
        
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                env_content = f.read()
        
        # Prepare S3 configuration
        s3_config = f"""
# AWS S3 Direct Configuration for IS-Migration
AWS_ACCESS_KEY_ID={credentials['access_key_id']}
AWS_SECRET_ACCESS_KEY={credentials['secret_access_key']}
S3_BUCKET_NAME={credentials['bucket_name']}
AWS_REGION={credentials['region']}

# Optional S3 settings
LOCAL_STORAGE_PATH=storage
"""
        
        # Remove existing S3 configuration if present
        lines = env_content.split('\n')
        filtered_lines = []
        skip_s3_section = False
        
        for line in lines:
            if any(line.strip().startswith(comment) for comment in [
                '# AWS S3', '# Cloud Foundry ObjectStore', '# S3 Configuration'
            ]):
                skip_s3_section = True
                continue
            elif line.strip().startswith('#') and skip_s3_section:
                skip_s3_section = False
            elif skip_s3_section and any(line.startswith(key) for key in [
                'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME', 
                'AWS_REGION', 'S3_ENDPOINT_URL', 'LOCAL_STORAGE_PATH'
            ]):
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

def test_upload_download(credentials):
    """Test file upload and download"""
    print("\n🧪 Testing File Operations...")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=credentials['access_key_id'],
            aws_secret_access_key=credentials['secret_access_key'],
            region_name=credentials['region']
        )
        
        # Test file content
        test_content = f"IS-Migration S3 test file created at {datetime.now()}"
        test_key = f"test/s3-connection-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Upload test file
        print(f"📤 Uploading test file: {test_key}")
        s3_client.put_object(
            Bucket=credentials['bucket_name'],
            Key=test_key,
            Body=test_content.encode(),
            ContentType='text/plain',
            Metadata={
                'test': 'true',
                'created_by': 'is-migration-setup'
            }
        )
        print("✅ File uploaded successfully")
        
        # Download test file
        print("📥 Downloading test file...")
        response = s3_client.get_object(
            Bucket=credentials['bucket_name'],
            Key=test_key
        )
        downloaded_content = response['Body'].read().decode()
        
        if test_content == downloaded_content:
            print("✅ File download and content verification successful")
        else:
            print("❌ Content verification failed")
            return False
        
        # Generate presigned URL
        print("🔗 Generating presigned URL...")
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': credentials['bucket_name'], 'Key': test_key},
            ExpiresIn=3600
        )
        print(f"✅ Presigned URL generated: {presigned_url[:80]}...")
        
        # Clean up test file
        print("🗑️ Cleaning up test file...")
        s3_client.delete_object(
            Bucket=credentials['bucket_name'],
            Key=test_key
        )
        print("✅ Test file deleted successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {str(e)}")
        return False

def create_bucket_policy_suggestion(credentials):
    """Suggest bucket policy for IS-Migration application"""
    print("\n📋 Suggested S3 Bucket Policy")
    print("-" * 40)
    
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ISMigrationAppAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{credentials.get('account_id', '830858425934')}:root"
                },
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{credentials['bucket_name']}",
                    f"arn:aws:s3:::{credentials['bucket_name']}/*"
                ]
            }
        ]
    }
    
    print("Copy this policy to your S3 bucket permissions:")
    print(json.dumps(bucket_policy, indent=2))
    
    print("\nTo apply this policy:")
    print("1. Go to AWS S3 Console")
    print(f"2. Select bucket: {credentials['bucket_name']}")
    print("3. Go to Permissions tab")
    print("4. Edit Bucket Policy")
    print("5. Paste the above JSON")

def setup_cf_environment_variables(credentials):
    """Show how to set environment variables in Cloud Foundry"""
    print("\n☁️ Cloud Foundry Environment Variables Setup")
    print("-" * 40)
    
    apps = [
        "it-resonance-main-api",
        "mule-to-is-api", 
        "boomi-to-is-api",
        "mulesoft-iflow-api-gemma3"
    ]
    
    print("Run these commands to set S3 credentials in your CF applications:")
    print()
    
    for app in apps:
        print(f"# Set S3 credentials for {app}")
        print(f"cf set-env {app} AWS_ACCESS_KEY_ID '{credentials['access_key_id']}'")
        print(f"cf set-env {app} AWS_SECRET_ACCESS_KEY '{credentials['secret_access_key']}'")
        print(f"cf set-env {app} S3_BUCKET_NAME '{credentials['bucket_name']}'")
        print(f"cf set-env {app} AWS_REGION '{credentials['region']}'")
        print(f"cf restart {app}")
        print()

def main():
    """Main setup function"""
    print("🚀 AWS S3 Direct Setup for IS-Migration")
    print("=" * 50)
    print("Setting up your existing AWS S3 bucket:")
    print(f"Bucket: is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias")
    print(f"Account: 830858425934")
    print()
    
    # Get credentials
    credentials = get_aws_credentials()
    
    # Test connection
    if not test_s3_connection(credentials):
        print("\n❌ S3 connection failed. Please check your credentials and try again.")
        return False
    
    # Update .env file
    if not update_env_file(credentials):
        print("\n❌ Failed to update .env file.")
        return False
    
    # Test file operations
    if not test_upload_download(credentials):
        print("\n❌ File operations test failed.")
        return False
    
    # Show bucket policy suggestion
    create_bucket_policy_suggestion(credentials)
    
    # Show CF environment setup
    setup_cf_environment_variables(credentials)
    
    print("\n🎉 AWS S3 setup completed successfully!")
    print("\nNext steps:")
    print("1. Apply the suggested bucket policy (if needed)")
    print("2. Set environment variables in your CF applications")
    print("3. Test the integration with your database system")
    print("4. Deploy and test your applications")
    
    print(f"\nYour S3 bucket '{credentials['bucket_name']}' is ready for IS-Migration! 🎯")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
