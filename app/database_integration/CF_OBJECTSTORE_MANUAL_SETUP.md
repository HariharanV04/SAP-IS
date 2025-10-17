# Cloud Foundry ObjectStore Manual Setup Guide

## 🚀 Automated Setup (Recommended)

Run the automated setup script:
```bash
python database_integration/setup_cf_objectstore.py
```

## 📋 Manual Setup Steps

If you prefer to set up manually, follow these steps:

### 1. Check CF Login Status
```bash
cf target
```

### 2. Check Marketplace for ObjectStore Service
```bash
cf marketplace
```
Look for `objectstore` service with `standard` plan.

### 3. Create ObjectStore Service Instance
```bash
cf create-service objectstore standard is-migration-storage
```

### 4. Wait for Service Creation (Check Status)
```bash
cf services
```
Wait until you see `create succeeded` for `is-migration-storage`.

### 5. Create Service Key for Credentials
```bash
cf create-service-key is-migration-storage is-migration-key
```

### 6. Get Service Credentials
```bash
cf service-key is-migration-storage is-migration-key
```

This will output JSON credentials like:
```json
{
  "credentials": {
    "access_key_id": "your_access_key_id",
    "bucket": "your_bucket_name", 
    "host": "s3.region.amazonaws.com",
    "region": "us-east-1",
    "secret_access_key": "your_secret_access_key",
    "uri": "s3://...",
    "username": "your_username"
  }
}
```

### 7. Update Your .env File

Add these credentials to your `.env` file:
```env
# Cloud Foundry ObjectStore S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=your_bucket_name
AWS_REGION=us-east-1
S3_ENDPOINT_URL=s3.region.amazonaws.com
S3_USERNAME=your_username
```

### 8. Bind Service to Your Applications

Bind the objectstore service to each of your deployed applications:

```bash
# Bind to main API
cf bind-service it-resonance-main-api is-migration-storage

# Bind to MuleToIS API  
cf bind-service mule-to-is-api is-migration-storage

# Bind to BoomiToIS API
cf bind-service boomi-to-is-api is-migration-storage

# Bind to Gemma3 API
cf bind-service mulesoft-iflow-api-gemma3 is-migration-storage
```

### 9. Restart Applications (Optional)

If you want the applications to immediately pick up the new environment variables:
```bash
cf restart it-resonance-main-api
cf restart mule-to-is-api  
cf restart boomi-to-is-api
cf restart mulesoft-iflow-api-gemma3
```

### 10. Verify Service Binding

Check that the service is bound to your applications:
```bash
cf env it-resonance-main-api
```

You should see the objectstore credentials under `VCAP_SERVICES`.

## 🔧 Testing the Setup

### Test S3 Connection
```python
from database_integration.s3_manager import s3_manager

# Test connection
if s3_manager.test_connection():
    print("✅ S3 ObjectStore connection successful!")
else:
    print("❌ S3 ObjectStore connection failed")
```

### Test File Upload
```python
import io
from database_integration.integrated_manager import integrated_manager

# Test file upload
file_content = b"Test file content"
file_obj = io.BytesIO(file_content)

file_url = integrated_manager.storage.upload_file(
    file_obj, 
    "test/sample.txt",
    {"test": "true"}
)

if file_url:
    print(f"✅ File uploaded successfully: {file_url}")
else:
    print("❌ File upload failed")
```

## 🔍 Troubleshooting

### Common Issues:

1. **Service creation takes time**
   - ObjectStore service creation can take 5-10 minutes
   - Check status with `cf services` periodically

2. **Service binding limit**
   - CF has a limit of 5 service bindings per service instance
   - Use service keys if you need more than 5 applications

3. **Credentials not working**
   - Verify the credentials format in your .env file
   - Check that the endpoint URL is correct
   - Ensure the bucket name matches exactly

4. **Applications not picking up credentials**
   - Restart applications after binding: `cf restart <app-name>`
   - Check environment variables: `cf env <app-name>`

### Useful Commands:

```bash
# List all services
cf services

# List all service keys
cf service-keys is-migration-storage

# Check application environment
cf env <app-name>

# Check application logs
cf logs <app-name> --recent

# Unbind service (if needed)
cf unbind-service <app-name> is-migration-storage

# Delete service key (if needed)
cf delete-service-key is-migration-storage is-migration-key

# Delete service instance (if needed)
cf delete-service is-migration-storage
```

## 📊 Service Details

After setup, you'll have:

- **Service Name**: `is-migration-storage`
- **Service Plan**: `objectstore/standard`
- **Service Key**: `is-migration-key`
- **S3-Compatible Storage**: Ready for file uploads/downloads
- **Automatic Failover**: Falls back to local storage if S3 unavailable

## 🎉 Next Steps

1. **Test the integration** with your database system
2. **Upload some files** through your application
3. **Verify files are stored** in the CF ObjectStore
4. **Monitor usage** through CF dashboard
5. **Scale as needed** for production workloads

Your IS-Migration application now has enterprise-grade object storage through Cloud Foundry! 🚀
