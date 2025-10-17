# HOW TO RUN GUIDE - IS-Migration Platform

## 🚀 Quick Start Options

### Option 1: Python Launcher (Recommended)
```bash
# Primary launcher - Cross-platform
python platform_launcher.py

# Or use simple wrapper scripts
./start.bat        # Windows
./start.sh         # Linux/Mac
```
This provides an interactive menu with all operations including development, monitoring, and deployment.

### Option 2: Legacy Quick Start
```bash
./quick-start-fixed.bat    # Redirects to Python launcher
```

### Option 3: Direct Python Execution
```bash
# Install launcher dependencies first
pip install -r launcher_requirements.txt

# Then run the launcher
python platform_launcher.py
```

## 🌐 Service URLs

### Local Development
- **Frontend**: http://localhost:5173 (Vite dev server)
- **Main API**: http://localhost:5000
- **MuleToIS API**: http://localhost:5001
- **Gemma-3 API**: http://localhost:5002
- **BoomiToIS API**: http://localhost:5003

### Production (Cloud Foundry)
- **Frontend**: https://ifa-project.cfapps.eu10.hana.ondemand.com
- **Main API**: https://it-resonance-main-api.cfapps.eu10.hana.ondemand.com
- **MuleToIS API**: https://it-resonance-mule-api.cfapps.eu10.hana.ondemand.com
- **Gemma-3 API**: https://it-resonance-gemma3-api.cfapps.eu10.hana.ondemand.com
- **BoomiToIS API**: https://it-resonance-boomi-api.cfapps.eu10.hana.ondemand.com

## 📋 Prerequisites

### Local Development
1. **Python** (3.9+) - Required for all APIs and the launcher
2. **Node.js** (v18+) - Required for frontend
3. **Git** - For version control
4. **pip** - Python package manager (usually comes with Python)

### Launcher Dependencies
```bash
# Install launcher dependencies
pip install -r launcher_requirements.txt

# Or install manually
pip install psutil requests
```

### Production Deployment
1. **Cloud Foundry CLI** - Installed and configured
2. **SAP BTP account** - With appropriate permissions
3. **Environment variables** - Configured (see TECHNICAL_DESIGN.md)

## 🔧 Python Launcher Menu Options

### 🚀 DEVELOPMENT
1. **Setup Development Environment** - Installs all dependencies for all services
2. **Start All Servers (Local)** - Starts all services with logging
3. **Start Individual Service** - Start a single service for debugging
4. **Stop All Servers** - Gracefully stops all running services

### 📊 MONITORING
5. **Check Server Status** - Shows which services are running on which ports
6. **View Service Logs** - View recent log files from services
7. **Health Check All Services** - HTTP health checks for all services

### 🌐 DEPLOYMENT
8. **Deploy to Production (All)** - Deploy all apps to Cloud Foundry
9. **Deploy Single App** - Deploy individual app to Cloud Foundry
10. **Check Deployment Status** - Check Cloud Foundry deployment status

### 🔧 UTILITIES
11. **Clean Environment** - Clean up logs and temporary files
12. **Install Dependencies** - Install launcher dependencies (psutil, requests)
13. **Show Help** - Display help information
14. **Exit** - Gracefully exit and stop all services

## 🔧 Manual Setup Instructions (Alternative)

### 1. Launcher Dependencies
```bash
pip install -r launcher_requirements.txt
```

### 2. Frontend Setup
```bash
cd IFA-Project/frontend
npm install
npm run dev    # Runs on port 5173
```

### 3. Main API Setup
```bash
cd app
pip install -r requirements.txt
python app.py  # Runs on port 5000
```

### 4. BoomiToIS API Setup
```bash
cd BoomiToIS-API
pip install -r requirements.txt
python app.py  # Runs on port 5003
```

### 5. MuleToIS API Setup
```bash
cd MuleToIS-API
pip install -r requirements.txt
python app.py  # Runs on port 5001
```

### 6. Gemma-3 API Setup
```bash
cd MuleToIS-API-Gemma3
pip install -r requirements.txt
python app.py  # Runs on port 5002
```

## 🔍 Testing & Verification

### Using Python Launcher
```bash
# Start the launcher
python platform_launcher.py

# Then use menu options:
# Option 5: Check Server Status
# Option 7: Health Check All Services
# Option 6: View Service Logs
```

### Health Checks
```bash
# Using the launcher (Option 7)
python platform_launcher.py
# Select: 7. Health Check All Services

# Manual health checks
curl http://localhost:5000/api/health    # Main API
curl http://localhost:5001/api/health    # MuleToIS API
curl http://localhost:5002/api/health    # Gemma-3 API
curl http://localhost:5003/api/health    # BoomiToIS API
curl http://localhost:5173/             # Frontend
```

### Manual Testing Workflow
1. **Start Services**: Use launcher option 2 (Start All Servers)
2. **Check Status**: Use launcher option 5 (Check Server Status)
3. **Upload Document**: Use frontend at http://localhost:5173
4. **Generate Documentation**: Verify markdown generation works
5. **Generate iFlow**: Test iFlow generation from documentation
6. **Deploy to SAP**: Test SAP BTP integration (production only)
7. **View Logs**: Use launcher option 6 if issues occur

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Conflicts
**Problem**: Services won't start due to port conflicts
**Solution**:
```bash
# Check which ports are in use
python platform_launcher.py
# Select: 5. Check Server Status

# Or manually check ports
netstat -an | findstr "5000 5001 5002 5003 5173"  # Windows
lsof -i :5000,:5001,:5002,:5003,:5173              # Linux/Mac
```

#### 2. Python Dependencies
**Problem**: Import errors or missing modules
**Solution**:
```bash
# Use launcher to install all dependencies
python platform_launcher.py
# Select: 1. Setup Development Environment

# Or install manually for each service
cd app && pip install -r requirements.txt
cd BoomiToIS-API && pip install -r requirements.txt
cd MuleToIS-API && pip install -r requirements.txt
cd MuleToIS-API-Gemma3 && pip install -r requirements.txt
```

#### 3. Launcher Dependencies
**Problem**: Launcher fails to start
**Solution**:
```bash
# Install launcher dependencies
pip install -r launcher_requirements.txt

# Or use the launcher's built-in installer
python platform_launcher.py
# Select: 12. Install Dependencies
```

#### 4. Node.js Dependencies
**Problem**: Frontend won't start
**Solution**:
```bash
cd IFA-Project/frontend
npm install
npm run dev
```

#### 5. Environment Variables
**Problem**: Services fail with configuration errors
**Solution**: Check .env files in each service directory and ensure all required variables are set

### Logs & Debugging

#### Using Python Launcher
```bash
python platform_launcher.py
# Select: 6. View Service Logs
```

#### Manual Log Access
- **Launcher logs**: `logs/` directory (created when using launcher)
- **Frontend logs**: Browser developer console
- **API logs**: Terminal output where services are running
- **Production logs**: `cf logs [app-name]` for Cloud Foundry

#### Log File Locations
```
logs/
├── main-api_YYYYMMDD_HHMMSS.log
├── boomi-api_YYYYMMDD_HHMMSS.log
├── mule-api_YYYYMMDD_HHMMSS.log
├── gemma-api_YYYYMMDD_HHMMSS.log
└── frontend_YYYYMMDD_HHMMSS.log
```

## 📁 Project Structure Reference

```
├── platform_launcher.py       # 🚀 MAIN LAUNCHER (Python)
├── launcher_requirements.txt   # Launcher dependencies
├── start.bat / start.sh       # Simple wrapper scripts
├── quick-start-fixed.bat      # Legacy launcher (redirects)
├── stop-all-servers.bat/.sh   # Stop services scripts
│
├── app/                       # Main API (Port 5000)
│   ├── app.py                # Main application
│   ├── requirements.txt      # Python dependencies
│   └── .env                 # Environment variables
│
├── BoomiToIS-API/            # Boomi API (Port 5003)
│   ├── app.py               # Boomi processing service
│   └── requirements.txt     # Dependencies
│
├── MuleToIS-API/             # MuleSoft API (Port 5001)
│   ├── app.py               # MuleSoft processing service
│   └── requirements.txt     # Dependencies
│
├── MuleToIS-API-Gemma3/      # Gemma-3 API (Port 5002)
│   ├── app.py               # Gemma-3 integration service
│   └── requirements.txt     # Dependencies
│
├── IFA-Project/frontend/     # React Frontend (Port 5173)
│   ├── package.json         # Node.js dependencies
│   └── src/                # React source code
│
├── ci-cd-deployment/         # Deployment scripts & configs
├── database_integration/     # Database setup scripts
├── architecture/            # Architecture documentation
├── logs/                   # Service logs (created by launcher)
└── archive/               # Archived files (ignore)
```

## 📚 Documentation References

- **[README.md](./README.md)** - Project overview and quick start
- **[TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md)** - Complete technical architecture
- **[FUNCTIONAL_DESIGN.md](./FUNCTIONAL_DESIGN.md)** - Business requirements and workflows
- **[PROJECT_DOCS.md](./PROJECT_DOCS.md)** - Technical details and status
- **[CONSOLIDATED_FEATURE_DOCUMENTATION.md](./CONSOLIDATED_FEATURE_DOCUMENTATION.md)** - All feature implementations

## 🎯 Quick Reference Commands

```bash
# 🚀 Start everything (recommended)
python platform_launcher.py

# 🔧 Install launcher dependencies
pip install -r launcher_requirements.txt

# 📊 Check what's running
python platform_launcher.py  # Then select option 5

# 🛑 Stop everything
python platform_launcher.py  # Then select option 4

# 🌐 Access frontend
http://localhost:5173

# 📋 View logs
python platform_launcher.py  # Then select option 6
```
