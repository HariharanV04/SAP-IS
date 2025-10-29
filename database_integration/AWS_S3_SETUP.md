# AWS S3 Direct Setup for IS-Migration

## 📊 Your S3 Bucket Details

- **Bucket Name**: `is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias`
- **AWS Account**: `830858425934`
- **Type**: Direct AWS S3 (not BTP ObjectStore)

## 🚀 Quick Setup (Automated)

Run the setup script with your AWS credentials:

```bash
python database_integration/setup_aws_s3.py
```

This will:
- ✅ Test your S3 connection
- ✅ Update your `.env` file
- ✅ Test file upload/download
- ✅ Show CF environment variable commands

## 📋 Manual Setup Steps

### 1. Get Your AWS Credentials

You'll need:
- **AWS Access Key ID**
- **AWS Secret Access Key**
- **Region** (likely `us-east-1`)

### 2. Update Your .env File

Add these to your `.env` file:

```env
# AWS S3 Direct Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias
AWS_REGION=us-east-1

# Local storage fallback
LOCAL_STORAGE_PATH=storage
```

### 3. Set Cloud Foundry Environment Variables

For each of your deployed applications, run:

```bash
# Main API
cf set-env it-resonance-main-api AWS_ACCESS_KEY_ID 'your_access_key'
cf set-env it-resonance-main-api AWS_SECRET_ACCESS_KEY 'your_secret_key'
cf set-env it-resonance-main-api S3_BUCKET_NAME 'is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias'
cf set-env it-resonance-main-api AWS_REGION 'us-east-1'
cf restart it-resonance-main-api

# MuleToIS API
cf set-env mule-to-is-api AWS_ACCESS_KEY_ID 'your_access_key'
cf set-env mule-to-is-api AWS_SECRET_ACCESS_KEY 'your_secret_key'
cf set-env mule-to-is-api S3_BUCKET_NAME 'is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias'
cf set-env mule-to-is-api AWS_REGION 'us-east-1'
cf restart mule-to-is-api

# BoomiToIS API
cf set-env boomi-to-is-api AWS_ACCESS_KEY_ID 'your_access_key'
cf set-env boomi-to-is-api AWS_SECRET_ACCESS_KEY 'your_secret_key'
cf set-env boomi-to-is-api S3_BUCKET_NAME 'is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias'
cf set-env boomi-to-is-api AWS_REGION 'us-east-1'
cf restart boomi-to-is-api

# Gemma3 API
cf set-env mulesoft-iflow-api-gemma3 AWS_ACCESS_KEY_ID 'your_access_key'
cf set-env mulesoft-iflow-api-gemma3 AWS_SECRET_ACCESS_KEY 'your_secret_key'
cf set-env mulesoft-iflow-api-gemma3 S3_BUCKET_NAME 'is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias'
cf set-env mulesoft-iflow-api-gemma3 AWS_REGION 'us-east-1'
cf restart mulesoft-iflow-api-gemma3
```

### 4. Test the Setup

```bash
python database_integration/test_cf_objectstore.py
```

## 🔒 S3 Bucket Permissions

### Required IAM Permissions

Your AWS user/role needs these S3 permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias",
                "arn:aws:s3:::is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias/*"
            ]
        }
    ]
}
```

### Bucket Policy (Optional)

If you want to restrict access to your application only:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ISMigrationAppAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::830858425934:root"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias",
                "arn:aws:s3:::is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias/*"
            ]
        }
    ]
}
```

## 🧪 Testing Your Setup

### Test S3 Connection
```python
from database_integration.s3_manager import s3_manager

if s3_manager.test_connection():
    print("✅ S3 connection successful!")
else:
    print("❌ S3 connection failed")
```

### Test File Upload
```python
import io
from database_integration.integrated_manager import integrated_manager

# Test file upload
file_content = b"Test file for IS-Migration"
file_obj = io.BytesIO(file_content)

file_url = integrated_manager.storage.upload_file(
    file_obj, 
    "test/sample.txt",
    {"test": "true"}
)

print(f"File uploaded: {file_url}")
```

## 📁 File Organization

Your files will be organized in the S3 bucket like this:

```
is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias/
├── jobs/
│   ├── {job-id}/
│   │   ├── uploads/
│   │   │   └── original_document.txt
│   │   └── results/
│   │       ├── generated_iflow.xml
│   │       └── documentation.md
├── test/
│   └── connection_tests.txt
└── temp/
    └── processing_files.tmp
```

## 🔍 Monitoring and Troubleshooting

### Check S3 Usage
- Go to AWS S3 Console
- Select your bucket
- Check the "Metrics" tab for usage statistics

### Common Issues

1. **Access Denied Errors**
   - Check your AWS credentials
   - Verify IAM permissions
   - Ensure bucket policy allows access

2. **Region Mismatch**
   - Verify your bucket region in AWS Console
   - Update `AWS_REGION` in your configuration

3. **Bucket Not Found**
   - Double-check the bucket name
   - Ensure it exists in your AWS account

### Useful Commands

```bash
# Check CF app environment
cf env it-resonance-main-api

# Check CF app logs
cf logs it-resonance-main-api --recent

# Test S3 access with AWS CLI
aws s3 ls s3://is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias/
```

## 💰 Cost Optimization

### S3 Storage Classes
Consider using different storage classes for cost optimization:
- **Standard**: For frequently accessed files
- **Standard-IA**: For infrequently accessed files (30+ days)
- **Glacier**: For archival (90+ days)

### Lifecycle Policies
Set up lifecycle policies to automatically move old files to cheaper storage classes.

## 🎉 Next Steps

1. **Run the setup script**: `python database_integration/setup_aws_s3.py`
2. **Set CF environment variables** for all your applications
3. **Test the integration** with your database system
4. **Deploy and test** your applications
5. **Monitor usage** in AWS S3 Console

Your IS-Migration application now has direct AWS S3 storage! 🚀
