# BoomiToIS-API Cloud Foundry Deployment Guide

## 🚀 **Deployment Overview**

This guide covers deploying the BoomiToIS-API to SAP Cloud Foundry, similar to the MuleToIS-API deployment.

### **📋 Prerequisites**

1. **Cloud Foundry CLI** installed and configured
2. **SAP BTP Account** with Cloud Foundry access
3. **Environment Variables** configured (see .env file)
4. **API Keys** for Anthropic and SAP BTP

### **🔧 Configuration**

#### **Application Details:**
- **Name**: `boomi-to-is-api`
- **Route**: `https://boomi-to-is-api.cfapps.us10-001.hana.ondemand.com`
- **Memory**: 512M
- **Disk**: 1G
- **Stack**: cflinuxfs4

#### **Environment Variables:**
```bash
ANTHROPIC_API_KEY=<your-anthropic-key>
SAP_BTP_TENANT_URL=https://4728b940trial.it-cpitrial05.cfapps.us10-001.hana.ondemand.com
SAP_BTP_CLIENT_ID=<your-client-id>
SAP_BTP_CLIENT_SECRET=<your-client-secret>
SAP_BTP_OAUTH_URL=https://4728b940trial.authentication.us10.hana.ondemand.com/oauth/token
MAIN_API_URL=https://it-resonance-api-wacky-panther-za.cfapps.us10-001.hana.ondemand.com
CORS_ORIGIN=https://ifa-frontend.cfapps.us10-001.hana.ondemand.com
```

### **🚀 Deployment Steps**

#### **Option 1: Windows Deployment**
```bash
cd BoomiToIS-API
deploy.bat
```

#### **Option 2: Linux/Mac Deployment**
```bash
cd BoomiToIS-API
chmod +x deploy.sh
./deploy.sh
```

#### **Option 3: Manual Deployment**
```bash
cd BoomiToIS-API
cf login -a https://api.cf.us10-001.hana.ondemand.com
cf target -o "IT Resonance Inc_itr-internal-2hco92jx" -s "dev"
cf push
```

### **✅ Verification**

After deployment, verify the API is working:

1. **Health Check**: 
   ```
   GET https://boomi-to-is-api.cfapps.us10-001.hana.ondemand.com/api/health
   ```

2. **Expected Response**:
   ```json
   {
     "status": "ok",
     "message": "BoomiToIS API is running",
     "platform": "Dell Boomi",
     "api_key_configured": true
   }
   ```

### **🔗 API Endpoints**

- **Health Check**: `/api/health`
- **Generate iFlow**: `/api/generate-iflow`
- **Upload Boomi XML**: `/api/upload-boomi-xml`
- **Deploy to SAP**: `/api/deploy-to-sap`

### **🛠️ Troubleshooting**

#### **Common Issues:**

1. **Environment Variables Not Set**:
   - Check .env file exists
   - Verify all required variables are set

2. **Memory Issues**:
   - Increase memory in manifest.yml if needed
   - Monitor app performance

3. **SAP BTP Connection Issues**:
   - Verify SAP BTP credentials
   - Check OAuth URL and tenant URL

4. **CORS Issues**:
   - Verify CORS_ORIGIN is set correctly
   - Check frontend URL matches

### **📊 Monitoring**

- **Logs**: `cf logs boomi-to-is-api --recent`
- **Status**: `cf app boomi-to-is-api`
- **Events**: `cf events boomi-to-is-api`

### **🔄 Updates**

To update the deployed application:
```bash
cf push boomi-to-is-api
```

### **🎯 Integration with Frontend**

The API will be accessible from the IFA Frontend at:
`https://ifa-frontend.cfapps.us10-001.hana.ondemand.com`

Update frontend configuration to point to:
`https://boomi-to-is-api.cfapps.us10-001.hana.ondemand.com`
