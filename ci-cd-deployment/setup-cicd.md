# 🔄 CI/CD Pipeline Setup Guide

## 📋 Prerequisites

1. **GitHub Repository** with the code
2. **Cloud Foundry Account** with deployment permissions
3. **GitHub Repository Admin Access** to set secrets

## 🔐 Step 1: Get Your Cloud Foundry Details

Run these commands to get your CF details:

```bash
# Login to Cloud Foundry (if not already logged in)
cf login -a https://api.cf.eu10-005.hana.ondemand.com

# Get your organization
cf orgs

# Get your space
cf spaces

# Get your username (from cf target output)
cf target
```

**Example Output:**
```
API endpoint:   https://api.cf.eu10-005.hana.ondemand.com
User:           your-username@domain.com
Org:            your-org-name
Space:          your-space-name
```

## 🔑 Step 2: Add GitHub Secrets

1. **Go to your GitHub repository**
2. **Click Settings** → **Secrets and variables** → **Actions**
3. **Click "New repository secret"** and add each of these:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `CF_ORG` | Your CF organization name | `your-org-name` |
| `CF_SPACE` | Your CF space name | `development` or `production` |
| `CF_USERNAME` | Your CF username/email | `your-email@domain.com` |
| `CF_PASSWORD` | Your CF password | `your-cf-password` |

## 🚀 Step 3: Test the Pipeline

### **Option A: Push to Main Branch**
```bash
# Make any small change and push to main
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```

### **Option B: Manual Trigger**
1. Go to **GitHub** → **Actions** tab
2. Click **"Deploy to Cloud Foundry"** workflow
3. Click **"Run workflow"**
4. Choose deployment target (all apps or specific app)
5. Click **"Run workflow"**

## 📊 Step 4: Monitor Deployment

1. **Go to GitHub Actions tab** in your repository
2. **Click on the running workflow**
3. **Watch the deployment progress** in real-time
4. **Check the logs** for any issues

## ✅ Step 5: Verify Deployment

After successful deployment, the pipeline will automatically test these URLs:
- https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com/api/health
- https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health  
- https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health

## 🔄 Workflow Behavior

### **Automatic Deployment (Push to Main)**
```
Push to main → Run Tests → Deploy All Apps → Verify Health → ✅ Done
```

### **Manual Deployment (Workflow Dispatch)**
```
Manual Trigger → Choose Target → Deploy → Verify Health → ✅ Done
```

### **Pull Request (Testing Only)**
```
PR to main → Run Tests → Build Frontend → ✅ No Deployment
```

## 🚨 Troubleshooting

### **Common Issues:**

1. **"CF Login Failed"**
   - Check CF_USERNAME and CF_PASSWORD secrets
   - Verify your CF account has deployment permissions

2. **"App Not Found"**
   - Ensure apps exist in CF: `cf apps`
   - Check CF_ORG and CF_SPACE are correct

3. **"Build Failed"**
   - Check the build logs in GitHub Actions
   - Test locally first: `npm run build`

4. **"Health Check Failed"**
   - Apps deployed but not responding
   - Check CF logs: `cf logs [app-name] --recent`

### **Debug Commands:**
```bash
# Check CF target
cf target

# Check app status
cf apps

# Check app logs
cf logs it-resonance-main-api --recent
cf logs mule-to-is-api --recent
cf logs boomi-to-is-api --recent
cf logs ifa-frontend --recent

# Restart apps if needed
cf restart it-resonance-main-api
cf restart mule-to-is-api
cf restart boomi-to-is-api
cf restart ifa-frontend
```

## 🎯 Expected Results

After setup, you'll have:

✅ **Automatic deployment** on every push to main  
✅ **Manual deployment** option for specific apps  
✅ **Automatic testing** before deployment  
✅ **Health verification** after deployment  
✅ **Deployment notifications** (success/failure)  

## 📝 Next Steps

1. **Complete the secret setup** (most important!)
2. **Test with a small change** to main branch
3. **Monitor the first deployment** in GitHub Actions
4. **Verify all apps are working** after deployment

Once configured, every push to main will automatically deploy to Cloud Foundry! 🚀
