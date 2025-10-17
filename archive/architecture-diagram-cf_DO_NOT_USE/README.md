# React Architecture Diagram Cloud Foundry Deployment

This directory contains the deployment configuration and scripts for deploying the React.js architecture diagram to Cloud Foundry.

## 📋 Prerequisites

1. **Cloud Foundry CLI** installed and configured
2. **Node.js** (version 14 or higher)
3. **npm** (comes with Node.js)
4. **Access to SAP BTP Cloud Foundry** environment

## 🚀 Quick Deployment

### Windows
```bash
deploy-complete.bat
```

### Linux/Mac
```bash
chmod +x *.sh
./deploy-complete.sh
```

## 📁 What Gets Deployed

The deployment includes:

1. **React.js Interactive Architecture Diagram** - Built from `../architecture-diagram/`
   - Interactive components with drag & drop
   - Zoom, pan, and minimap controls
   - Component details on click
   - Responsive design
   - Professional styling with animations

## 🔧 Manual Deployment Steps

If you prefer to deploy manually:

### 1. Navigate to React app directory
```bash
cd ../architecture-diagram
```

### 2. Install dependencies (if needed)
```bash
npm install
```

### 3. Build React app
```bash
npm run build
```

### 4. Copy build files and deploy
```bash
cd ../architecture-diagram-cf
cp -r ../architecture-diagram/build .
cf push
```

## 🌐 Deployed URL

After successful deployment, the React architecture diagram will be available at:

- **React.js Interactive Diagram**: https://architecture-diagram.cfapps.us10-001.hana.ondemand.com

## ⚙️ Configuration Files

- `manifest.yml` - Cloud Foundry application configuration
- `Staticfile` - Static buildpack configuration
- `build/` - Built React files directory (created during deployment)

## 🔍 Architecture Flow

The deployed React diagram shows the updated architecture with:

1. **Documentation API** → **Anthropic API (Docs)** → **Generated Document**
2. **Generated Document** → **SAP Matcher API** & **iFlow Generator**
3. **SAP Matcher API** → **ML Pattern Matcher** (NLTK + ML) → **GitHub API**
4. **iFlow Generator** → **Anthropic API (iFlow)** → **iFlow Code**
5. **iFlow Code** → **SAP Integration Suite** (Deployment)

## 🛠️ Troubleshooting

### Build Issues
- Ensure Node.js is installed for React.js build
- Check that all source directories exist
- Verify npm dependencies are installed

### Deployment Issues
- Confirm CF CLI is logged in: `cf login`
- Check available memory and disk quota
- Verify route is available: `cf routes`

### Memory/Resource Issues
- Current allocation: 128M memory, 512M disk
- Increase in `manifest.yml` if needed for larger React apps

## 📝 Customization

### Change Route
Edit `manifest.yml`:
```yaml
routes:
  - route: your-custom-route.cfapps.us10-001.hana.ondemand.com
```

### Increase Resources
Edit `manifest.yml`:
```yaml
memory: 256M
disk_quota: 1G
```

## 🔄 Updates

To update the deployed React diagram:

1. Make changes to React source files in `../architecture-diagram/`
2. Run deployment script again: `deploy-complete.bat` or `./deploy-complete.sh`
3. Changes will be automatically built and deployed

## 📊 Monitoring

Check application status:
```bash
cf apps
cf logs architecture-diagram --recent
```

## 🎯 Features of Deployed React App

- **Interactive Components**: Drag and drop architecture components
- **Zoom & Pan**: Navigate large diagrams easily
- **Minimap**: Overview of entire architecture
- **Component Details**: Click components for detailed information
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Professional Styling**: Clean, modern interface
- **Real-time Updates**: Smooth animations and transitions
