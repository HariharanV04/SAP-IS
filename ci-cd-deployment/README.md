# 🚀 IFA Project Deployment Automation

Complete deployment automation system for local development and Cloud Foundry production deployments.

## 📋 Quick Start

### **Local Development**
```bash
# Setup local environment (creates .env files)
deployment\scripts\deploy-local.bat

# Start all development servers
deployment\scripts\start-local.bat

# Or use the management script
deployment\scripts\manage-env.bat setup-local
deployment\scripts\manage-env.bat start-local
```

### **Production Deployment**
```bash
# Deploy all applications to Cloud Foundry
deployment\scripts\deploy-production.bat

# Deploy single application
deployment\scripts\deploy-single.bat frontend

# Or use the management script
deployment\scripts\manage-env.bat deploy-all
deployment\scripts\manage-env.bat deploy-single main_api
```

## 🛠️ Available Commands

### **Management Script (Recommended)**
```bash
# All-in-one management script
deployment\scripts\manage-env.bat [command]

Commands:
  setup-local     - Setup local development environment
  deploy-all      - Deploy all apps to production
  deploy-single   - Deploy single app [app_name]
  status          - Show deployment status
  restart         - Restart all CF apps
  clean           - Clean deployment artifacts
  start-local     - Start all local development servers
```

### **Python Script (Advanced)**
```bash
# Direct Python script usage
python deployment/deploy.py [command] [options]

Commands:
  local           - Setup local development environment
  deploy          - Deploy single app (requires --app)
  deploy-all      - Deploy all applications
  status          - Show deployment status
  restart         - Restart all CF applications
  clean           - Clean deployment artifacts

Options:
  --app [name]    - Specify app: main_api, mule_api, boomi_api, frontend
  --config [path] - Custom configuration file path
```

## 🏗️ Architecture

### **Applications**
- **Main API** (`it-resonance-main-api`) - Core documentation API
- **MuleToIS API** (`mule-to-is-api`) - MuleSoft to SAP Integration Suite
- **BoomiToIS API** (`boomi-to-is-api`) - Boomi to SAP Integration Suite  
- **Frontend** (`ifa-frontend`) - React/Vite frontend application

### **Environment Configuration**
- **Local**: Uses localhost URLs and development settings
- **Production**: Uses Cloud Foundry URLs and production settings
- **Shared**: Common credentials and SAP BTP configuration

## 🔧 Configuration

### **Environment Variables**
All environment variables are managed through `deployment/config/environments.json`:

```json
{
  "shared": {
    "credentials": {
      "ANTHROPIC_API_KEY": "...",
      "SAP_BTP_CLIENT_ID": "...",
      // ... other shared credentials
    }
  },
  "local": {
    "main_api": {
      "API_HOST": "localhost",
      "API_PORT": "5000",
      // ... local-specific settings
    }
  },
  "production": {
    "main_api": {
      "API_HOST": "it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com",
      // ... production-specific settings
    }
  }
}
```

### **Local Development**
- Creates `.env` files for each application
- Uses localhost URLs for inter-service communication
- Same credentials as production for external services

### **Production Deployment**
- Sets environment variables using `cf set-env`
- Uses Cloud Foundry URLs for inter-service communication
- Automatically builds frontend before deployment

## 🌐 URLs

### **Local Development**
- Frontend: http://localhost:3000
- Main API: http://localhost:5000
- MuleToIS API: http://localhost:5001
- BoomiToIS API: http://localhost:5002

### **Production**
- Frontend: https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com
- Main API: https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com
- MuleToIS API: https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com
- BoomiToIS API: https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com

## 🔄 CI/CD Pipeline

### **GitHub Actions**
Automated deployment pipeline in `.github/workflows/deploy.yml`:

- **Triggers**: Push to main, manual workflow dispatch
- **Tests**: Python and frontend build tests
- **Deploy**: Automatic deployment to Cloud Foundry
- **Verify**: Health check verification

### **Required Secrets**
Set these in GitHub repository secrets:
```
CF_ORG=your-cf-org
CF_SPACE=your-cf-space
CF_USERNAME=your-cf-username
CF_PASSWORD=your-cf-password
```

## 🧹 Maintenance

### **Clean Up**
```bash
# Remove .env files and build artifacts
deployment\scripts\manage-env.bat clean
```

### **Restart Applications**
```bash
# Restart all Cloud Foundry applications
deployment\scripts\manage-env.bat restart
```

### **Check Status**
```bash
# Show deployment status and test health endpoints
deployment\scripts\manage-env.bat status
```

## 🚨 Troubleshooting

### **Common Issues**

1. **CF Login Required**
   ```bash
   cf login -a https://api.cf.eu10-005.hana.ondemand.com
   ```

2. **Environment Variables Not Set**
   - Check `deployment/config/environments.json`
   - Run `deployment\scripts\manage-env.bat clean` and retry

3. **Frontend Build Fails**
   ```bash
   cd IFA-Project/frontend
   npm install
   npm run build
   ```

4. **API Health Check Fails**
   - Check application logs: `cf logs [app-name] --recent`
   - Restart applications: `deployment\scripts\manage-env.bat restart`

### **Logs**
```bash
# View application logs
cf logs it-resonance-main-api --recent
cf logs mule-to-is-api --recent
cf logs boomi-to-is-api --recent
cf logs ifa-frontend --recent
```

## 📝 Development Workflow

### **Local Development**
1. Run `deployment\scripts\manage-env.bat setup-local`
2. Run `deployment\scripts\manage-env.bat start-local`
3. Develop and test locally
4. Commit changes to Git

### **Production Deployment**
1. Push changes to main branch (triggers CI/CD)
2. Or manually deploy: `deployment\scripts\manage-env.bat deploy-all`
3. Verify deployment: `deployment\scripts\manage-env.bat status`

This automation system eliminates the pain points of manual deployment and ensures consistent, reliable deployments across environments!
