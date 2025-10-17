# Complete Implementation Guide - IS-Migration Platform
*Consolidated from all documentation modified after August 10th, 2025*

---

## Table of Contents

1. [Environment Setup Guide](#environment-setup-guide)
2. [Deployment Fixes & Solutions](#deployment-fixes--solutions)
3. [Technical Architecture](#technical-architecture)
4. [Functional Design](#functional-design)
5. [How to Run Guide](#how-to-run-guide)
6. [Feature Documentation](#feature-documentation)
7. [Environment Configuration](#environment-configuration)
8. [System Architecture Reference](#system-architecture-reference)
9. [API Implementation Details](#api-implementation-details)
10. [Project Documentation](#project-documentation)

---

# Environment Setup Guide

This guide explains how to set up environment variables for both local development and Cloud Foundry deployment.

## 🚀 Cloud Foundry Environment Setup

We've created scripts to handle the special characters and escaping issues when setting CF environment variables.

### Option 1: Python Script (Recommended)

The Python script handles all edge cases and provides better error handling:

```bash
# Navigate to the IMigrate directory
cd IMigrate

# Run the Python setup script
python setup_cf_env.py
```

**Features:**
- ✅ Handles special characters properly
- ✅ Checks CF CLI installation and login status
- ✅ Provides progress feedback
- ✅ Option to restart applications automatically
- ✅ Environment variable verification
- ✅ Cross-platform compatible

### Option 2: Windows Batch Script

For Windows users who prefer batch files:

```cmd
cd IMigrate
setup_cf_env.bat
```

### Option 3: Manual PowerShell (Use Separate Commands)

If you need to set individual variables:

```powershell
# Set variables one by one to avoid escaping issues
cf set-env it-resonance-main-api SAP_BTP_CLIENT_ID "sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895|it!b410334"
cf set-env it-resonance-main-api SAP_BTP_CLIENT_SECRET "5813ca83-4ba6-4231-96e1-1a48a80eafec`$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w="
# ... etc
```

## 🏠 Local Development Environment Setup

### Quick Setup Script

```bash
cd IMigrate
python setup-local-env.ps1
```

This will copy the environment template files to the correct locations:

### Manual Setup

1. **Copy Environment Files:**
   ```bash
   # Main API
   cp environment-setup/main-api.env app/.env
   
   # MuleToIS API  
   cp environment-setup/mulesoft-api.env MuleToIS-API/.env
   
   # BoomiToIS API
   cp environment-setup/boomi-api.env BoomiToIS-API/.env
   
   # Frontend
   cp environment-setup/frontend.env IFA-Project/frontend/.env
   ```

2. **Update API Keys:**
   Edit each `.env` file and replace `your-key-here` with your actual API keys.

## 🔑 Required API Keys

### Anthropic Claude API
- Required for: Main API, MuleToIS API, BoomiToIS API
- Get from: https://console.anthropic.com/
- Set in: `ANTHROPIC_API_KEY`

### RunPod API (Optional - for Gemma-3)
- Required for: Gemma-3 API only
- Get from: https://runpod.io/
- Set in: `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID`

## 🏢 SAP BTP Credentials

The SAP BTP credentials are already configured with working values:

- **Client ID:** `sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895|it!b410334`
- **Client Secret:** `5813ca83-4ba6-4231-96e1-1a48a80eafec$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w=`
- **OAuth URL:** `https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token`
- **Tenant URL:** `https://itr-internal-2hco92jx.it-cpi034.cfapps.us10-002.hana.ondemand.com`
- **Default Package:** `ConversionPackages`

## 🔍 Verification

### Check CF Environment Variables
```bash
cf env it-resonance-main-api
cf env it-resonance-mule-api
cf env it-resonance-boomi-api
```

### Test Local Setup
```bash
# Test MuleToIS API
cd MuleToIS-API
python app.py

# Test unified deployment (in another terminal)
cd ..
python test_unified_deployment.py
```

## 🔄 Restart Applications

After setting environment variables, restart all CF applications:

```bash
cf restart it-resonance-main-api
cf restart it-resonance-mule-api  
cf restart it-resonance-boomi-api
cf restart it-resonance-gemma3-api
cf restart ifa-project
```

## 🐛 Troubleshooting

### PowerShell Special Character Issues
- **Problem:** `&&` not recognized, special characters in environment values
- **Solution:** Use the Python script instead of PowerShell

### CF CLI Not Found
- **Problem:** `cf` command not recognized
- **Solution:** Install CF CLI from https://github.com/cloudfoundry/cli/releases

### Not Logged In to CF
- **Problem:** CF commands fail with authentication error
- **Solution:** Run `cf login` first

### Environment Variables Not Applied
- **Problem:** Applications don't see new environment variables
- **Solution:** Restart the applications with `cf restart <app-name>`

## 📂 File Structure

```
IMigrate/
├── setup_cf_env.py              # Python script for CF env setup
├── setup_cf_env.bat             # Windows batch script for CF env setup  
├── setup-local-env.ps1          # PowerShell script for local env setup
├── environment-setup/           # Template environment files
│   ├── main-api.env
│   ├── mulesoft-api.env
│   ├── boomi-api.env
│   └── frontend.env
└── ENVIRONMENT_SETUP_GUIDE.md   # This file
```

## ✅ Success Indicators

Your environment is properly set up when:

1. ✅ All CF applications show environment variables with `cf env <app-name>`
2. ✅ MuleToIS API starts without errors on port 5001
3. ✅ Unified deployment test passes: `python test_unified_deployment.py`
4. ✅ Frontend can connect to all backend APIs
5. ✅ SAP BTP deployment works from the frontend deploy button

---

# Deployment Fixes & Solutions

## 🚀 **MuleSoft Deployment Fix - Quick Summary**

### 🎯 **Problem Solved**
MuleSoft iFlow deployment was failing due to **job ID mapping issues** between workflow stages, while Boomi deployment worked perfectly.

### ✅ **Solution**
**Smart platform-aware deployment** that leverages the **working direct deployment methods**:

#### **For Boomi Platform:**
- ✅ **Uses existing direct-deploy logic** (already working)
- ✅ **No changes needed** - keeps working as before

#### **For MuleSoft Platform:**  
- ✅ **Uses direct-deploy FIRST** (proven to work)
- ✅ **Enhanced fallback logic** when job IDs are lost
- ✅ **Smart file finding** to locate available ZIP files

### 🔧 **Frontend Fix (One Line Change)**

Replace your deployment button handler:

```javascript
// OLD (broken for MuleSoft)
await deployIflowToSap(jobId, packageId, description, 'mulesoft');

// NEW (works for both platforms)  
await unifiedDeployIflowToSap(jobId, 'ConversionPackages', null, null, 'mulesoft');
```

### 📁 **Files Modified**

1. **`IMigrate/MuleToIS-API/unified_deployment.py`** - Enhanced deployment logic
2. **`IMigrate/MuleToIS-API/app.py`** - New unified endpoints
3. **`IMigrate/IFA-Project/frontend/src/services/api.js`** - Smart deployment function

### 🧪 **Testing**

```bash
# Start MuleToIS API
cd IMigrate/MuleToIS-API && python app.py

# Test the fix
cd IMigrate && python test_unified_deployment.py
```

### 🎉 **Result**

- ✅ **MuleSoft deployments now work** like Boomi deployments
- ✅ **Uses proven direct deployment method first**
- ✅ **Smart fallback** handles job ID mapping issues  
- ✅ **Platform-aware routing** preserves working Boomi logic
- ✅ **Minimal frontend changes** required

**Your "Deploy iFlow" button will now work reliably for both platforms!** 🚀

## 🛠️ MuleSoft iFlow Deployment Fix - Detailed Implementation

### 🎯 **Problem Statement**

The MuleSoft platform iFlow deployment was failing due to **job ID mapping issues** during the workflow transition between:
- Document upload → Documentation generation → iFlow generation → **Deployment** ❌

While the BoomiToIS API deployment worked perfectly, MuleToIS API deployment failed because job IDs were getting lost or mismatched during the multi-stage process.

### ✅ **Solution Overview**

I've implemented a **unified deployment system** that uses the **working direct deployment methods** and solves the job ID mapping problem by:

1. **Direct Deployment First**: Uses the proven `direct-deploy` endpoints that work for both platforms
2. **Smart File Finding**: Multiple strategies to locate iFlow ZIP files when job IDs are lost
3. **Platform-Aware Routing**: MuleToIS uses new unified endpoints, Boomi uses existing working logic
4. **Robust Fallback**: If direct deployment fails, falls back to enhanced unified deployment
5. **Working Credentials**: Uses the same SAP BTP credentials that are proven to work

### 🔧 **Implementation Details**

#### **New Files Created:**

##### 1. `IMigrate/MuleToIS-API/unified_deployment.py`
- **Core deployment logic** with robust file finding
- **Multiple search strategies** for locating iFlow ZIP files:
  - Direct job ID match
  - Job ID prefix matching (8-character prefix)
  - Most recent file fallback
  - Current directory search
- **Working SAP BTP integration** using proven credentials

##### 2. **New API Endpoints** in `IMigrate/MuleToIS-API/app.py`:
```python
# Unified deployment with job ID handling
POST /api/jobs/{job_id}/unified-deploy

# Deploy latest iFlow (no job ID required)  
POST /api/deploy-latest-iflow
```

##### 3. **New Frontend Functions** in `IMigrate/IFA-Project/frontend/src/services/api.js`:
```javascript
// Handles job ID mapping issues
unifiedDeployIflowToSap(jobId, packageId, iflowId, iflowName, platform)

// Deploys most recent ZIP file
deployLatestIflow(packageId, platform)
```

### 🚀 **How to Use the Fix**

#### **Option 1: Unified Deployment (Recommended)**
```javascript
import { unifiedDeployIflowToSap } from './services/api.js';

const handleDeploy = async () => {
    try {
        const result = await unifiedDeployIflowToSap(
            jobId,                    // Your job ID (can be wrong/missing)
            'ConversionPackages',     // Package ID  
            null,                     // iFlow ID (auto-generated)
            null,                     // iFlow name (auto-generated)
            'mulesoft'               // Platform
        );
        
        console.log('✅ Deployment successful:', result);
        // Handle success in UI
        
    } catch (error) {
        console.error('❌ Deployment failed:', error);
        // Handle error in UI
    }
};
```

#### **Option 2: Deploy Latest (Simplest)**
```javascript
import { deployLatestIflow } from './services/api.js';

const handleDeployLatest = async () => {
    try {
        const result = await deployLatestIflow(
            'ConversionPackages',     // Package ID
            'mulesoft'               // Platform  
        );
        
        console.log('✅ Latest iFlow deployed:', result);
        
    } catch (error) {
        console.error('❌ Deployment failed:', error);
    }
};
```

### 🔄 **Deployment Flow**

#### **Before (Broken):**
```
Upload → Generate Docs → Generate iFlow → ❌ Deploy (Job ID lost)
```

#### **After (Fixed):**
```
Upload → Generate Docs → Generate iFlow → ✅ Unified Deploy
                                       ↓
                               Platform-Aware Deployment:
                               
                               🟦 Boomi: Uses existing direct-deploy (works)
                               🟩 MuleToIS: Uses direct-deploy → Fallback to unified
                               
                               Smart File Finding (when needed):
                               1. Direct job ID match
                               2. Job ID prefix match  
                               3. Most recent file
                               4. Any available ZIP
```

### 🧪 **Testing the Solution**

#### **1. Start the MuleToIS API:**
```bash
cd IMigrate/MuleToIS-API
python app.py
```

#### **2. Run the test script:**
```bash
cd IMigrate
python test_unified_deployment.py
```

#### **3. Test in Frontend:**
- Replace existing deployment calls with the new unified functions
- Test with both valid and invalid job IDs
- Verify fallback mechanisms work

### 📋 **API Response Format**

#### **Success Response:**
```json
{
    "status": "success",
    "message": "iFlow deployed successfully using unified deployment",
    "iflow_id": "MuleGenerated_IFlow_20250109_143022",
    "package_id": "ConversionPackages",
    "iflow_name": "IFlow_abc12345",
    "file_deployed": "IFlow_abc12345.zip",
    "response_code": 201,
    "method": "Unified Deployment (BoomiToIS Logic)"
}
```

#### **Error Response:**
```json
{
    "status": "error",
    "message": "No iFlow ZIP file found to deploy"
}
```

### 🔍 **File Finding Strategies**

The unified deployment uses **4 cascading strategies**:

1. **Direct Job ID Match**: `results/{job_id}/*.zip`
2. **Prefix Match**: Look for files containing `IFlow_{first_8_chars_of_job_id}`
3. **Most Recent File**: Find the newest ZIP file in any results directory
4. **Current Directory**: Fall back to any ZIP in the current directory

### 🔐 **SAP BTP Configuration**

The solution uses **working SAP BTP credentials** (same as BoomiToIS):

```python
# Working ITR Internal credentials
client_id = "sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895|it!b410334"
client_secret = "5813ca83-4ba6-4231-96e1-1a48a80eafec$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w="
token_url = "https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token"
base_url = "https://itr-internal-2hco92jx.it-cpi034.cfapps.us10-002.hana.ondemand.com"
```

### 🎯 **Frontend Integration**

#### **Minimal Change Required:**
Replace your existing deployment button handler:

```javascript
// OLD (broken)
await deployIflowToSap(jobId, packageId, description, 'mulesoft');

// NEW (working)
await unifiedDeployIflowToSap(jobId, packageId, null, null, 'mulesoft');
```

#### **For Ultimate Simplicity:**
```javascript
// Deploy whatever iFlow is available (no job ID needed)
await deployLatestIflow('ConversionPackages', 'mulesoft');
```

### 🚨 **Key Benefits**

1. ✅ **Solves Job ID Mapping**: No more lost job IDs during workflow transitions
2. ✅ **Backward Compatible**: Works with existing frontend code
3. ✅ **Smart Fallbacks**: Deploys available files even when job tracking fails
4. ✅ **Proven Logic**: Uses the same approach as working BoomiToIS deployment
5. ✅ **Minimal Changes**: Requires only a few lines of frontend code change
6. ✅ **Comprehensive Testing**: Includes test scripts and error handling

### 🎉 **Result**

After implementing this solution:
- **MuleSoft deployments will work** just like Boomi deployments
- **No more job ID mapping issues** 
- **Simple "Deploy iFlow" button** that actually works
- **Robust error handling** and fallback mechanisms

The solution provides **exactly what you requested**: *"when clicking on the deploy iFlow button in the frontend, whatever zipped file is present we simply deploy to integration suite"* - but with intelligent file finding and error handling.

---

# Technical Architecture

## 📋 Document Overview

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Project:** IS-Migration Platform  
**Purpose:** Comprehensive technical design for migrating integration flows from legacy platforms to SAP Integration Suite

## 🏗️ System Architecture

### 1. **High-Level Architecture**

The IS-Migration platform follows a **microservices architecture** with specialized services for different integration platforms:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Main API      │    │  BoomiToIS-API  │
│   (Port 3000)   │◄──►│   (Port 5000)   │◄──►│   (Port 5003)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  MuleToIS-API   │    │ SAP Integration │
                       │   (Port 5001)   │    │     Suite       │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Gemma-3 API     │
                       │   (Port 5002)   │
                       └─────────────────┘
```

### 2. **Core Architecture Principles**

- **Microservices**: Independent, specialized services for each platform
- **API-First**: RESTful APIs with clear contracts
- **Event-Driven**: Asynchronous processing with job queues
- **Cloud-Native**: Designed for Cloud Foundry deployment
- **AI-Powered**: Multiple LLM providers for robust processing

### 3. **Service Responsibilities**

| Service | Port | Primary Responsibility |
|---------|------|----------------------|
| **Frontend** | 3000 | User interface, workflow management, progress tracking |
| **Main API** | 5000 | Orchestration, document processing, job management |
| **BoomiToIS-API** | 5003 | Boomi XML processing, iFlow generation |
| **MuleToIS-API** | 5001 | MuleSoft XML processing, iFlow generation |
| **Gemma-3 API** | 5002 | RunPod Gemma-3 integration, alternative LLM |

## 🔧 Technical Components

### 1. **Technology Stack**

#### **Backend Services**
- **Framework**: Flask (Python 3.9+)
- **Web Server**: Gunicorn (production), Flask dev server (development)
- **HTTP Client**: Requests library
- **File Processing**: python-docx, PyPDF2, BeautifulSoup4
- **AI Integration**: Anthropic Claude, OpenAI, RunPod Gemma-3

#### **Frontend Application**
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **State Management**: React hooks
- **Build Tool**: Vite

#### **Database & Storage**
- **Primary Database**: Supabase (PostgreSQL)
- **File Storage**: Local filesystem (dev), AWS S3/CF Object Store (prod)
- **Caching**: In-memory caching for search results
- **Job Persistence**: JSON files with database fallback

### 2. **AI/LLM Integration**

#### **Primary LLM Provider: Anthropic Claude**
```python
# Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4000
TEMPERATURE = 0.1
```

#### **Secondary LLM Provider: RunPod Gemma-3**
```python
# OpenAI-compatible endpoint
RUNPOD_BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1"
RUNPOD_CHAT_URL = f"{RUNPOD_BASE_URL}/chat/completions"
```

#### **LLM Usage Patterns**
- **Document Processing**: Convert raw text to structured markdown
- **Component Analysis**: Extract integration components from documentation
- **iFlow Generation**: Generate SAP Integration Suite XML
- **Error Recovery**: Retry logic with multiple attempts

## 🗄️ Database Design

### 1. **Database Schema (Supabase PostgreSQL)**

#### **Core Tables**

```sql
-- Jobs table (primary entity)
CREATE TABLE is_migration.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    platform TEXT DEFAULT 'mulesoft',
    user_id TEXT,
    file_info JSONB,
    parsed_details JSONB,
    enhance_with_llm BOOLEAN DEFAULT false,
    llm_service TEXT,
    upload_path TEXT,
    results_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Documents table (file metadata)
CREATE TABLE is_migration.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES is_migration.jobs(id),
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size BIGINT,
    file_path TEXT,
    content_hash TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- iFlow Generations table (generation tracking)
CREATE TABLE is_migration.iflow_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES is_migration.jobs(id),
    iflow_name TEXT,
    generation_status TEXT DEFAULT 'pending',
    ai_model TEXT,
    generation_time_seconds INTEGER,
    component_count INTEGER,
    template_version TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

#### **Database Features**
- **Row-Level Security (RLS)**: User-based data isolation
- **Vector Extension**: pgvector for similarity search
- **Real-time Subscriptions**: Live status updates
- **Audit Trails**: Complete job history tracking

### 2. **Data Flow Architecture**

```
User Upload → File Storage → Database Record → Processing Queue → Results Storage
     ↓              ↓              ↓                ↓                ↓
   Frontend    Local/S3/CF    Supabase Jobs    Background Job    Results Folder
```

## 🔌 API Design

### 1. **Main API Endpoints**

#### **Document Processing**
```http
POST /api/upload-documentation
Content-Type: multipart/form-data

Request:
- file: Document file (Word, PDF, etc.)
- platform: "boomi" | "mulesoft"
- enhance_with_llm: boolean

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "message": "Document uploaded successfully"
}
```

#### **Job Management**
```http
GET /api/jobs/{job_id}
Response:
{
  "job_id": "uuid",
  "status": "completed",
  "platform": "boomi",
  "files": {
    "documentation_json": "path/to/doc.json",
    "markdown": "path/to/doc.md",
    "iflow": "path/to/iflow.zip"
  },
  "created": "2025-01-09T10:00:00Z",
  "completed": "2025-01-09T10:02:30Z"
}
```

#### **iFlow Generation**
```http
POST /api/generate-iflow-from-docs/{job_id}
Response:
{
  "status": "processing",
  "message": "iFlow generation started",
  "estimated_time": "2-5 minutes"
}
```

### 2. **BoomiToIS-API Endpoints**

#### **iFlow Generation**
```http
POST /api/generate-iflow/{job_id}
Content-Type: application/json

Request:
{
  "markdown_content": "# Integration Flow...",
  "platform": "boomi",
  "options": {
    "template_version": "v2.0",
    "include_error_handling": true
  }
}

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "components_identified": 5,
  "estimated_completion": "2025-01-09T10:05:00Z"
}
```

#### **SAP BTP Deployment**
```http
POST /api/jobs/{job_id}/deploy
Content-Type: application/json

Request:
{
  "tenant_url": "https://tenant.integration.hana.ondemand.com",
  "package_id": "MyPackage",
  "credentials": {
    "client_id": "...",
    "client_secret": "..."
  }
}
```

### 3. **Error Handling Standards**

#### **HTTP Status Codes**
- `200 OK`: Successful operation
- `202 Accepted`: Async operation started
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: System errors

#### **Error Response Format**
```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Unsupported file format. Please upload .docx, .pdf, or .txt files.",
    "details": {
      "supported_formats": [".docx", ".pdf", ".txt"],
      "received_format": ".xlsx"
    }
  }
}
```

## 🔐 Security Design

### 1. **Authentication & Authorization**

#### **API Security**
- **CORS Configuration**: Restricted origins for production
- **Environment Variables**: Secure credential storage
- **API Key Management**: Encrypted storage of LLM API keys

#### **Database Security**
- **Row-Level Security (RLS)**: User-based data isolation
- **Connection Encryption**: SSL/TLS for all database connections
- **Credential Rotation**: Regular API key rotation

### 2. **Data Protection**

#### **File Security**
- **Upload Validation**: File type and size restrictions
- **Virus Scanning**: Malware detection for uploads
- **Temporary Cleanup**: Automatic cleanup of processed files
- **Access Control**: User-specific file access

#### **Data Encryption**
- **In Transit**: HTTPS for all API communications
- **At Rest**: Encrypted storage for sensitive data
- **API Keys**: Environment-based secure storage

## 🚀 Deployment Architecture

### 1. **Cloud Foundry Deployment**

#### **Application Manifest Structure**
```yaml
# Main API
applications:
- name: it-resonance-main-api
  memory: 1G
  instances: 2
  buildpacks:
    - python_buildpack
  env:
    ANTHROPIC_API_KEY: ((anthropic-api-key))
    DATABASE_URL: ((database-url))
```

#### **Environment Configuration**
- **Development**: Local services, file storage
- **Staging**: Cloud services, limited resources
- **Production**: Full cloud deployment, auto-scaling

### 2. **Service Dependencies**

```mermaid
graph TD
    A[Frontend] --> B[Main API]
    B --> C[BoomiToIS-API]
    B --> D[MuleToIS-API]
    D --> E[Gemma-3 API]
    B --> F[Supabase DB]
    B --> G[File Storage]
    C --> H[SAP Integration Suite]
    D --> H
```

### 3. **Scaling Strategy**

#### **Horizontal Scaling**
- **Frontend**: CDN distribution
- **APIs**: Multiple instances with load balancing
- **Database**: Read replicas for heavy queries

#### **Performance Optimization**
- **Caching**: In-memory caching for frequent requests
- **Connection Pooling**: Database connection optimization
- **Async Processing**: Background job processing

## 📊 Performance Design

### 1. **Performance Requirements**

| Operation | Target Time | Acceptable Time |
|-----------|-------------|-----------------|
| Document Upload | < 5 seconds | < 10 seconds |
| Document Processing | < 15 seconds | < 30 seconds |
| iFlow Generation | < 60 seconds | < 120 seconds |
| File Download | < 3 seconds | < 5 seconds |

### 2. **Optimization Strategies**

#### **Backend Optimization**
- **Async Processing**: Non-blocking operations
- **Connection Pooling**: Efficient database connections
- **Caching**: Results caching for repeated operations
- **Batch Processing**: Bulk operations where possible

#### **Frontend Optimization**
- **Code Splitting**: Lazy loading of components
- **Asset Optimization**: Compressed images and scripts
- **Progressive Loading**: Incremental content loading
- **Caching**: Browser caching for static assets

## 🔄 Integration Patterns

### 1. **Document Processing Flow**

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant M as Main API
    participant L as LLM Service
    participant B as BoomiToIS-API
    
    U->>F: Upload Document
    F->>M: POST /api/upload-documentation
    M->>M: Extract Content
    M->>L: Convert to Structured Markdown
    L-->>M: Structured Content
    M->>M: Save Documentation JSON
    M-->>F: Status: documentation_ready
    F->>M: POST /api/generate-iflow-from-docs
    M->>B: POST /api/generate-iflow
    B->>L: Analyze Components
    L-->>B: Component JSON
    B->>B: Apply Templates
    B-->>M: iFlow Complete
    M-->>F: Status: completed
```

### 2. **Error Recovery Patterns**

#### **Retry Logic**
- **LLM Failures**: Up to 5 retry attempts with exponential backoff
- **Network Timeouts**: Automatic retry with circuit breaker
- **Template Errors**: Fallback to basic templates

#### **Graceful Degradation**
- **LLM Unavailable**: Basic markdown structure generation
- **Database Offline**: File-based job storage
- **Storage Issues**: Temporary local storage

This technical design document provides the foundation for understanding the IS-Migration platform's architecture, components, and implementation details.

---

# Functional Design

## 📋 Document Overview

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Project:** IS-Migration Platform  
**Purpose:** Comprehensive functional design covering business requirements, user workflows, and system behavior

## 🎯 Business Requirements

### 1. **Primary Business Objectives**

#### **Strategic Goals**
- **Legacy Migration**: Migrate integration flows from Dell Boomi and MuleSoft to SAP Integration Suite
- **Cost Reduction**: Reduce manual migration effort by 80-90%
- **Time Acceleration**: Complete migrations in days instead of months
- **Quality Assurance**: Ensure SAP-compliant iFlow generation
- **Knowledge Transfer**: Preserve integration logic during migration

#### **Business Value Proposition**
- **Automated Migration**: AI-powered conversion of legacy flows
- **Multi-Platform Support**: Handle both Boomi and MuleSoft platforms
- **Documentation Generation**: Automatic technical documentation
- **Direct Deployment**: Seamless deployment to SAP BTP Integration Suite
- **Progress Visibility**: Real-time tracking of migration progress

### 2. **Stakeholder Requirements**

#### **Business Users**
- **Requirement**: Upload business documents and generate integration flows
- **Expectation**: Simple, intuitive interface with clear progress indicators
- **Success Criteria**: Generate working iFlows without technical expertise

#### **Technical Users**
- **Requirement**: Upload XML files and customize iFlow generation
- **Expectation**: Advanced options, debugging capabilities, template customization
- **Success Criteria**: Fine-grained control over migration process

#### **Integration Architects**
- **Requirement**: Review and validate generated iFlows before deployment
- **Expectation**: Detailed technical documentation, component mapping visibility
- **Success Criteria**: Confidence in generated iFlow quality and SAP compliance

#### **Project Managers**
- **Requirement**: Track migration progress across multiple projects
- **Expectation**: Dashboard views, status reporting, timeline estimates
- **Success Criteria**: Clear visibility into migration pipeline and bottlenecks

## 👥 User Personas & Stories

### 1. **Primary Personas**

#### **Sarah - Business Analyst**
- **Background**: 5+ years in integration projects, familiar with business requirements
- **Technical Level**: Low-Medium (understands business flows, limited technical knowledge)
- **Primary Goal**: Convert business requirement documents into working integrations
- **Pain Points**: Technical complexity, long development cycles, communication gaps

**User Stories:**
```
As Sarah, I want to upload a Word document with integration requirements
So that I can generate a working iFlow without involving developers

As Sarah, I want to see real-time progress during iFlow generation
So that I know the system is working and estimate completion time

As Sarah, I want to download generated documentation
So that I can review and share integration details with stakeholders
```

#### **Mike - Integration Developer**
- **Background**: 8+ years in integration development, expert in Boomi/MuleSoft
- **Technical Level**: High (deep technical knowledge, XML expertise)
- **Primary Goal**: Migrate existing integration flows with minimal rework
- **Pain Points**: Manual conversion effort, maintaining complex logic, testing overhead

**User Stories:**
```
As Mike, I want to upload Boomi XML files
So that I can convert existing flows to SAP Integration Suite

As Mike, I want to customize iFlow templates and components
So that I can ensure the generated flow meets specific requirements

As Mike, I want to access debug files and generation logs
So that I can troubleshoot issues and optimize the conversion process
```

#### **Lisa - Integration Architect**
- **Background**: 10+ years in enterprise integration, SAP Integration Suite expert
- **Technical Level**: Expert (deep SAP knowledge, architecture design)
- **Primary Goal**: Ensure generated iFlows follow SAP best practices
- **Pain Points**: Quality assurance, compliance validation, performance optimization

**User Stories:**
```
As Lisa, I want to review generated iFlow components and mappings
So that I can validate SAP Integration Suite compliance

As Lisa, I want to deploy iFlows directly to SAP BTP
So that I can streamline the deployment process

As Lisa, I want to access detailed technical documentation
So that I can understand the conversion logic and validate the results
```

### 2. **Secondary Personas**

#### **David - Project Manager**
- **Goal**: Track migration progress and manage timelines
- **Needs**: Status dashboards, progress reports, resource allocation insights

#### **Emma - Quality Assurance**
- **Goal**: Validate generated iFlows meet functional requirements
- **Needs**: Test scenarios, validation reports, error tracking

## 🔄 User Workflows

### 1. **Primary Workflow: Document Upload & iFlow Generation**

#### **Workflow Steps**
```mermaid
flowchart TD
    A[User Login] --> B[Select Platform]
    B --> C[Upload Document/XML]
    C --> D[Document Processing]
    D --> E[Review Generated Documentation]
    E --> F[Generate iFlow]
    F --> G[Review iFlow Components]
    G --> H[Download/Deploy iFlow]
    H --> I[Validation & Testing]
    
    D --> J[Processing Failed]
    F --> K[Generation Failed]
    J --> L[Error Resolution]
    K --> L
    L --> C
```

#### **Detailed User Journey**

**Step 1: Platform Selection**
- User selects source platform (Boomi/MuleSoft)
- System configures appropriate processing pipeline
- User sees platform-specific upload options

**Step 2: File Upload**
- User uploads document (Word, PDF, XML)
- System validates file format and size
- Real-time upload progress indicator

**Step 3: Document Processing (10-15 seconds)**
- System extracts content from uploaded file
- AI converts raw content to structured markdown
- User sees processing status with detailed messages

**Step 4: Documentation Review**
- User reviews AI-generated documentation
- Option to download intermediate files
- User can proceed to iFlow generation

**Step 5: iFlow Generation (30-60 seconds)**
- System analyzes documentation for integration components
- AI generates SAP Integration Suite XML
- Real-time progress with component identification

**Step 6: Results & Actions**
- User downloads generated iFlow ZIP package
- Option to deploy directly to SAP BTP
- Access to debug files and generation logs

### 2. **Advanced Workflow: XML File Processing**

#### **Technical User Journey**
```mermaid
flowchart TD
    A[Upload XML Files] --> B[XML Parsing & Analysis]
    B --> C[Component Extraction]
    C --> D[Template Mapping]
    D --> E[iFlow Generation]
    E --> F[Customization Options]
    F --> G[Validation & Testing]
    G --> H[Deployment]
    
    B --> I[Parsing Errors]
    D --> J[Template Issues]
    I --> K[Error Resolution]
    J --> K
    K --> A
```

### 3. **Error Recovery Workflows**

#### **Common Error Scenarios**
- **File Format Issues**: Clear error messages with supported formats
- **Processing Timeouts**: Automatic retry with user notification
- **AI Service Unavailable**: Fallback to basic processing
- **Template Errors**: Alternative template selection

## 📋 Functional Requirements

### 1. **Core Functional Requirements**

#### **FR-001: Document Upload & Processing**
- **Description**: System shall accept multiple document formats and extract integration requirements
- **Acceptance Criteria**:
  - Support .docx, .pdf, .txt, .xml file formats
  - Maximum file size: 50MB
  - Processing time: < 30 seconds for typical documents
  - Extract text content with 95%+ accuracy

#### **FR-002: AI-Powered Documentation Generation**
- **Description**: System shall convert raw document content to structured integration documentation
- **Acceptance Criteria**:
  - Generate structured markdown with integration components
  - Identify data flows, transformations, and endpoints
  - Maintain business context and requirements
  - Support multiple AI providers (Anthropic, OpenAI, Gemma-3)

#### **FR-003: iFlow Generation**
- **Description**: System shall generate SAP Integration Suite iFlows from processed documentation
- **Acceptance Criteria**:
  - Generate valid BPMN 2.0 XML format
  - Include all identified integration components
  - Apply SAP Integration Suite best practices
  - Generate deployable ZIP packages

#### **FR-004: Progress Tracking**
- **Description**: System shall provide real-time progress updates during processing
- **Acceptance Criteria**:
  - Show current processing step
  - Display estimated completion time
  - Provide detailed status messages
  - Handle long-running operations gracefully

#### **FR-005: File Management**
- **Description**: System shall manage uploaded files and generated artifacts
- **Acceptance Criteria**:
  - Secure file storage with user isolation
  - Download access to all generated files
  - Automatic cleanup of temporary files
  - File versioning and history tracking

### 2. **Platform-Specific Requirements**

#### **FR-006: Boomi Integration**
- **Description**: System shall process Boomi XML files and generate equivalent SAP iFlows
- **Acceptance Criteria**:
  - Parse Boomi process XML structure
  - Extract connectors, transformations, and routing logic
  - Map Boomi components to SAP Integration Suite equivalents
  - Preserve business logic and data flow

#### **FR-007: MuleSoft Integration**
- **Description**: System shall process MuleSoft XML files and generate equivalent SAP iFlows
- **Acceptance Criteria**:
  - Parse MuleSoft flow XML structure
  - Extract DataWeave transformations and connectors
  - Map MuleSoft components to SAP Integration Suite equivalents
  - Handle complex routing and error handling patterns

### 3. **Quality Requirements**

#### **FR-008: SAP BTP Deployment**
- **Description**: System shall deploy generated iFlows directly to SAP BTP Integration Suite
- **Acceptance Criteria**:
  - Authenticate with SAP BTP using OAuth 2.0
  - Deploy iFlows to specified packages
  - Validate deployment success
  - Provide deployment status and logs

#### **FR-009: Error Handling & Recovery**
- **Description**: System shall handle errors gracefully and provide recovery options
- **Acceptance Criteria**:
  - Clear error messages with resolution guidance
  - Automatic retry for transient failures
  - Fallback options for service unavailability
  - Error logging and debugging support

## 🎨 User Experience Requirements

### 1. **Interface Design Requirements**

#### **UX-001: Intuitive Navigation**
- **Description**: Users shall navigate the application without training
- **Acceptance Criteria**:
  - Clear visual hierarchy and information architecture
  - Consistent navigation patterns across all pages
  - Breadcrumb navigation for complex workflows
  - Responsive design for desktop and tablet devices

#### **UX-002: Progress Visualization**
- **Description**: Users shall see clear progress indicators during long operations
- **Acceptance Criteria**:
  - Animated progress bars with percentage completion
  - Step-by-step workflow indicators
  - Real-time status messages
  - Estimated time remaining

#### **UX-003: File Management Interface**
- **Description**: Users shall easily manage uploaded files and generated artifacts
- **Acceptance Criteria**:
  - Drag-and-drop file upload interface
  - File preview and metadata display
  - Download buttons with clear file descriptions
  - File organization by job/project

### 2. **Accessibility Requirements**

#### **UX-004: Web Accessibility**
- **Description**: Application shall be accessible to users with disabilities
- **Acceptance Criteria**:
  - WCAG 2.1 AA compliance
  - Keyboard navigation support
  - Screen reader compatibility
  - High contrast mode support

## 📊 Performance Requirements

### 1. **Response Time Requirements**

| Operation | Target Response Time | Maximum Acceptable |
|-----------|---------------------|-------------------|
| Page Load | < 2 seconds | < 5 seconds |
| File Upload | < 5 seconds | < 10 seconds |
| Document Processing | < 15 seconds | < 30 seconds |
| iFlow Generation | < 60 seconds | < 120 seconds |
| File Download | < 3 seconds | < 5 seconds |

### 2. **Scalability Requirements**

#### **PERF-001: Concurrent Users**
- **Description**: System shall support multiple concurrent users
- **Acceptance Criteria**:
  - Support 50+ concurrent users
  - Maintain response times under load
  - Queue management for resource-intensive operations
  - Auto-scaling based on demand

#### **PERF-002: File Processing**
- **Description**: System shall handle large files efficiently
- **Acceptance Criteria**:
  - Process files up to 50MB
  - Streaming upload for large files
  - Background processing for time-intensive operations
  - Progress tracking for long-running jobs

## 🔒 Security & Compliance Requirements

### 1. **Data Security Requirements**

#### **SEC-001: Data Protection**
- **Description**: System shall protect user data and uploaded files
- **Acceptance Criteria**:
  - Encrypt data in transit (HTTPS/TLS)
  - Secure file storage with access controls
  - User data isolation and privacy
  - Automatic cleanup of sensitive data

#### **SEC-002: Authentication & Authorization**
- **Description**: System shall control access to features and data
- **Acceptance Criteria**:
  - User authentication for sensitive operations
  - Role-based access control
  - Session management and timeout
  - API key protection for external services

### 2. **Compliance Requirements**

#### **SEC-003: Enterprise Compliance**
- **Description**: System shall meet enterprise security standards
- **Acceptance Criteria**:
  - Audit logging for all operations
  - Data retention and deletion policies
  - Compliance with corporate security policies
  - Regular security assessments and updates

## 🎯 Success Criteria & KPIs

### 1. **Business Success Metrics**

- **Migration Efficiency**: 80%+ reduction in manual effort
- **Time to Value**: Complete migrations in days vs. months
- **Quality Score**: 95%+ generated iFlows deploy successfully
- **User Adoption**: 90%+ user satisfaction rating
- **Cost Savings**: 60%+ reduction in migration costs

### 2. **Technical Success Metrics**

- **System Availability**: 99.5% uptime
- **Processing Success Rate**: 95%+ successful completions
- **Performance**: Meet all response time requirements
- **Error Rate**: < 5% processing failures
- **User Experience**: < 3 clicks to complete primary workflows

This functional design document defines the complete business and user requirements for the IS-Migration platform. Together with the Technical Design Document, it provides comprehensive guidance for development, testing, and deployment of the migration solution.

---

# How to Run Guide

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

---

# Feature Documentation

This document consolidates all feature-specific documentation, implementation guides, and technical references that were previously scattered across multiple markdown files.

## Table of Contents

1. [Documentation Viewing Feature](#documentation-viewing-feature)
2. [Enhanced Process Flow](#enhanced-process-flow)
3. [iFlow Progress Tracking Enhancement](#iflow-progress-tracking-enhancement)
4. [Image Processing Feature](#image-processing-feature)
5. [Mermaid Syntax Fixer Solution](#mermaid-syntax-fixer-solution)
6. [Migration Flow Reference](#migration-flow-reference)
7. [Python Files Inventory](#python-files-inventory)
8. [S3 Database Integration Summary](#s3-database-integration-summary)
9. [SAP iFlow Deployment Visibility](#sap-iflow-deployment-visibility)
10. [Server Scripts Reference](#server-scripts-reference)
11. [Database Schema Setup](#database-schema-setup)
12. [Architecture Diagram](#architecture-diagram)
13. [Gemma-3 Integration](#gemma-3-integration)

## Documentation Viewing Feature

### 🎯 **Overview**

Added the ability to view intermediate processing files (markdown and JSON) in the UI after uploading a technical design document for Boomi. Users can now see exactly what the AI generated during the document processing step.

### 📋 **What Was Added**

#### 1. **Frontend Changes (JobResult.jsx)**

##### New Download State Management
```javascript
const [downloading, setDownloading] = useState({
  html: false,
  markdown: false,
  iflowReport: false,
  iflowSummary: false,
  generatedIflow: false,
  documentationJson: false,        // NEW
  uploadedDocumentation: false     // NEW
})
```

##### New UI Section for Processing Files
Added a new section that appears only for uploaded documentation (`jobInfo.source_type === 'uploaded_documentation'`):

- **AI-Enhanced Markdown**: The structured markdown created by AI for iFlow generation
- **Documentation JSON**: Complete structured data with metadata
- **Original Document Content**: Raw extracted text from the uploaded file

Each file has:
- 👁️ **View in browser** button (opens in new tab)
- 📥 **Download** button (saves file locally)
- 🏷️ **Status badges** explaining the file purpose

##### Enhanced Download Function
Updated `downloadFile()` function to handle new file type mappings:
- `documentation_json` → `documentationJson` state
- `uploaded_documentation` → `uploadedDocumentation` state

#### 2. **Backend Changes (app.py)**

##### Enhanced API Endpoint
Updated `/api/docs/<job_id>/<file_type>` to handle new file types:

```python
# NEW: Documentation JSON endpoint
elif file_type == 'documentation_json':
    file_path = os.path.join(app.config['RESULTS_FOLDER'], job_id, 'documentation.json')
    return send_file(file_path, mimetype='application/json')

# NEW: Original uploaded documentation endpoint  
elif file_type == 'uploaded_documentation':
    file_path = os.path.join(app.config['RESULTS_FOLDER'], job_id, 'uploaded_documentation.md')
    return send_file(file_path, mimetype='text/markdown')

# ENHANCED: AI-enhanced markdown for uploaded docs
elif file_type == 'markdown':
    # Serves the AI-enhanced content from documentation.json
    # Creates temporary file with structured markdown
```

##### Updated Job Data Structure
Added new file references to job data:
```python
'files': {
    'documentation_json': os.path.join('results', job_id, 'documentation.json'),
    'markdown': os.path.join('results', job_id, 'uploaded_documentation.md'),
    'uploaded_documentation': os.path.join('results', job_id, 'uploaded_documentation.md')  # NEW
}
```

### 🔄 **User Workflow**

#### Before (What Users Couldn't See)
1. Upload Boomi document ✅
2. ❓ **Black box processing** - no visibility into AI conversion
3. Get final iFlow ✅

#### After (What Users Can Now See)
1. Upload Boomi document ✅
2. **View intermediate files**:
   - 📄 **AI-Enhanced Markdown**: See how AI structured the content
   - 📋 **Documentation JSON**: View complete metadata and processing info
   - 📝 **Original Content**: Compare with raw extracted text
3. Get final iFlow ✅

### 🎨 **UI Design**

#### Visual Indicators
- **Blue badges**: AI-Enhanced Markdown ("Structured for iFlow Generation")
- **Green badges**: Documentation JSON ("Structured Data + Metadata") 
- **Gray badges**: Original Content ("Raw Extracted Text")

#### File Actions
- **External Link Icon**: Opens file in browser for immediate viewing
- **Download Icon**: Downloads file to local machine
- **Loading Spinner**: Shows during download operations

### 🧪 **Testing**

Created `test_documentation_viewing.py` to verify:
- ✅ Document upload works
- ✅ All three file types are accessible
- ✅ Proper content types are returned
- ✅ File sizes are reasonable

### 📁 **Files Modified**

1. **IFA-Project/frontend/src/pages/common/JobResult.jsx**
   - Added new download states
   - Added Processing Files UI section
   - Enhanced download function

2. **app/app.py**
   - Enhanced `/api/docs/<job_id>/<file_type>` endpoint
   - Added support for `documentation_json` and `uploaded_documentation`
   - Updated job data structure

3. **test_documentation_viewing.py** (NEW)
   - Test script to verify functionality

### 🚀 **How to Use**

1. **Start the application**:
   ```bash
   ./quick-start-fixed.bat
   # Choose option 2: Start Local Development Servers
   ```

2. **Upload a Boomi document**:
   - Go to http://localhost:3000
   - Select "Boomi" platform
   - Upload a Word/PDF/text document
   - Wait for processing to complete

3. **View intermediate files**:
   - Look for the new "Processing Files" section
   - Click the eye icon to view files in browser
   - Click the download icon to save files locally

### 🎯 **Benefits**

- **Transparency**: Users can see exactly what the AI generated
- **Debugging**: Easier to understand why iFlow generation succeeded/failed
- **Quality Control**: Users can verify the AI understood their document correctly
- **Learning**: Users can see how to structure documents for better AI processing

### 🔮 **Future Enhancements**

- **Inline Editing**: Allow users to edit the AI-enhanced markdown before iFlow generation
- **Comparison View**: Side-by-side comparison of original vs AI-enhanced content
- **Processing Metrics**: Show processing time, token usage, confidence scores
- **Version History**: Keep track of multiple processing attempts

## Enhanced Process Flow

This shows how the new enhanced process flow formatting will look:

### **Process Flow Overview**

#### **Flow Steps**

##### **Step 5: Transform SAP Response to SF Update (shape10)**

**Component Type:** Map/Transform

**Purpose:** Transforms the SAP BAPI response JSON into Salesforce Account update XML format, mapping SAP customer number to Salesforce Account fields for the update operation.

**Configuration Details:**

- **Input Profile:** SAP BAPI Customer Creation Response
- **Output Profile:** Salesforce Account Update Request
- **Transformation Logic:** Maps SAP customer number to Salesforce Account fields
- **Function Steps:** Data type conversions and field mapping transformations

**Input Data Structure:**

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| CustomerNumber | String | SAP-generated customer number from BAPI response |
| CreationStatus | String | Success/failure status of customer creation |
| ResponseMessage | String | Detailed response message from SAP |

**Output Data Structure:**

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| Account.Id | String | Salesforce Account unique identifier |
| Account.CustomerNumber__c | String | Custom field to store SAP customer number |
| Account.SAPStatus__c | String | Integration status tracking field |

**Field Mappings:**

| Source Field | Target Field | Data Type | Business Purpose |
|--------------|--------------|-----------|------------------|
| Customer.CompanyName | BAPI_CUSTOMER.NAME | String | Maps company name from Salesforce to SAP customer master |
| Customer.BillingStreet | BAPI_CUSTOMER.STREET | String | Maps billing street address for customer creation |
| Customer.BillingCity | BAPI_CUSTOMER.CITY | String | Maps billing city for customer address |
| Customer.BillingState | BAPI_CUSTOMER.REGION | String | Maps billing state/region for customer address |
| Customer.BillingPostalCode | BAPI_CUSTOMER.POSTAL_CODE | String | Maps billing postal code for customer address |
| Customer.BillingCountry | BAPI_CUSTOMER.COUNTRY | String | Maps billing country for customer address |

**Data Flow:**

- **Input:** SAP BAPI response JSON containing customer number and status
- **Processing:** Field mapping and data transformation from JSON to XML format
- **Output:** Salesforce Account update XML with mapped customer data

##### **Step 6: Check If New Account (shape25)**

> **Component Type:** Decision

**Purpose:** Evaluates if the account is new based on account status and routes flow accordingly to either create new account or update existing account.

**Configuration Details:**
- **Decision Criteria:** Account status field evaluation
- **Branch Logic:** Routes to create path for new accounts, update path for existing
- **Routing Rules:** Based on account existence and status flags

**Data Flow:**
- **Input:** Transformed Salesforce update data with account information
- **Processing:** Decision logic applied to determine account status
- **Output:** Routing decision directing flow to appropriate next step

##### **Step 7a: Update Salesforce Account (shape5)**

> **Component Type:** Connector Action

**Purpose:** Updates existing Salesforce Account with SAP customer number and integration status information.

**Configuration Details:**
- **Connector Type:** Salesforce
- **Operation:** Update
- **Target Object:** Account
- **Authentication:** OAuth 2.0 with refresh token
- **Error Handling:** Retry logic with exponential backoff

**Data Flow:**
- **Input:** Salesforce Account update XML with customer data
- **Processing:** Salesforce update operation performed via REST API
- **Output:** Salesforce update response with success/failure status

##### **Step 7b: Handle Existing Account (shape21)**

> **Component Type:** Information

**Purpose:** Handles the case when account already exists, providing information about existing account and logging the duplicate scenario.

**Configuration Details:**
- **Information Type:** Account existence notification
- **Logging Level:** INFO
- **Message Format:** Structured log entry with account details

**Data Flow:**
- **Input:** Account data for existing account scenario
- **Processing:** Information logging and duplicate handling logic
- **Output:** Information message and process continuation signal

##### **Step 8: End Events (shape4 and shape22)**

> **Component Type:** End Event

**Purpose:** Completes the process flow with appropriate success or failure handling based on the integration outcome.

**Configuration Details:**
- **Completion Type:** Multiple end points based on flow path
- **Final Actions:** Process completion logging and cleanup
- **Continuation Settings:** Process stops with status indication

**Data Flow:**
- **Input:** Final processed data from previous steps
- **Processing:** Completion actions and final status determination
- **Output:** Process completion with success/failure status

### Key Improvements:

1. **Clear Purpose Statements** - Each step explains what it accomplishes
2. **Detailed Configuration** - Specific technical details organized clearly
3. **Enhanced Data Flow** - Input/Processing/Output clearly defined
4. **Visual Separation** - Horizontal rules and blockquotes for better readability
5. **Professional Formatting** - Clean, business-appropriate presentation
6. **Comprehensive Context** - Full understanding of each step's role

### Field Mappings: Before vs After

#### ❌ **BEFORE (Broken Format):**
```
Field Mappings: | Source Field | Target Field | Type | Notes | |--------------|--------------|------|-------| | 5 | IMPORT/Object/I_PI_COMPANYDATA/Object/NAME | profile | Company name | | 9 | IMPORT/Object/I_PI_COMPANYDATA/Object/STREET | profile | Street address |
```

#### ✅ **AFTER (Enhanced Format):**

**Field Mappings:**

| Source Field | Target Field | Data Type | Business Purpose |
|--------------|--------------|-----------|------------------|
| Customer.CompanyName | BAPI_CUSTOMER.NAME | String | Maps company name from Salesforce to SAP customer master |
| Customer.BillingStreet | BAPI_CUSTOMER.STREET | String | Maps billing street address for customer creation |
| Customer.BillingCity | BAPI_CUSTOMER.CITY | String | Maps billing city for customer address |
| Customer.BillingState | BAPI_CUSTOMER.REGION | String | Maps billing state/region for customer address |

#### 🎯 **Key Field Mapping Improvements:**
- **Readable Field Names** - "Customer.CompanyName" instead of "5" or long XML paths
- **Proper Table Format** - Multi-line markdown table instead of single-line text
- **Business Context** - "Business Purpose" column explains the mapping logic
- **Clean Target Fields** - "BAPI_CUSTOMER.NAME" instead of "IMPORT/Object/I_PI_COMPANYDATA/Object/NAME"
- **Proper Data Types** - "String", "Integer", "Date" instead of generic "profile"

### Input/Output Profiles: Before vs After

#### ❌ **BEFORE (Technical XML Paths):**
```
Input Profile: SF Account QUERY Response XML
- Account Name: Salesforce account name (String)
- Account Street: Street address (String)

Output Profile: Boomi for SAP BAPI_CUSTOMER_CREATEFROMDATA1 FUNCTION Request JSON
- IMPORT/Object/I_PI_COMPANYDATA/Object/NAME: Company name (String)
- IMPORT/Object/I_PI_COMPANYDATA/Object/STREET: Street address (String)
- IMPORT/Object/I_PI_COMPANYDATA/Object/CITY: City (String)
```

#### ✅ **AFTER (Clean, Business-Friendly Format):**

**Input Data Structure:**

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| Account.Name | String | Salesforce account name |
| Account.BillingStreet | String | Primary billing street address |
| Account.BillingCity | String | Billing address city |

**Output Data Structure:**

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| CompanyName | String | SAP customer company name |
| Street | String | Customer street address |
| City | String | Customer city |

#### 🎯 **Key Profile Improvements:**
- **Clean Field Names** - "CompanyName" instead of "IMPORT/Object/I_PI_COMPANYDATA/Object/NAME"
- **Structured Tables** - Easy-to-scan table format instead of bullet lists
- **Business Descriptions** - Clear, business-friendly field descriptions
- **Logical Grouping** - Related fields grouped together (e.g., address fields)
- **Professional Presentation** - Clean, scannable format for technical documentation

## iFlow Progress Tracking Enhancement

### 🎯 **Overview**

Enhanced the iFlow generation process with detailed progress tracking and status updates to provide users with real-time feedback during the long-running AI analysis and generation process.

### ⏱️ **Why This Was Needed**

iFlow generation can take **2-5 minutes** due to:
- **AI Analysis**: Claude Sonnet-4 analyzing complex integration requirements
- **Component Generation**: Creating SAP Integration Suite components
- **Template Processing**: Converting to BPMN 2.0 XML format
- **Retry Logic**: Up to 5 attempts for AI analysis validation

Users were experiencing:
- ❌ **No feedback** during long processing times
- ❌ **Uncertainty** about whether the process was working
- ❌ **No visibility** into which step was currently running

### ✅ **What Was Enhanced**

#### 1. **🔄 Backend Progress Tracking**

##### **Enhanced GenAI Generator**
```python
def _update_job_status(self, job_id, status, message):
    """Update job status for progress tracking"""
    if job_id:
        # Update global jobs.json file
        jobs[job_id]['status'] = status
        jobs[job_id]['message'] = message
        print(f"📊 Job {job_id[:8]}: {status} - {message}")
```

##### **Detailed Status Updates**
- ✅ **"Starting iFlow generation..."**
- ✅ **"Analyzing integration requirements with AI..."**
- ✅ **"AI Analysis attempt 1/5..."**
- ✅ **"AI analysis successful, parsing components..."**
- ✅ **"Generating iFlow XML and configuration files..."**
- ✅ **"Creating final iFlow package..."**
- ✅ **"iFlow generation completed: [name]"**

##### **Error Handling with Progress**
- ✅ **"Parsing failed, retrying... (2/5)"**
- ✅ **"AI response invalid, retrying... (3/5)"**
- ✅ **"AI analysis failed after 5 attempts"**

#### 2. **🎨 Frontend Progress Display**

##### **Enhanced Progress Tracker**
```jsx
{/* Animated spinner for active processing */}
{(status === "processing" || status === "generating_iflow") && (
  <div className="animate-spin rounded-full h-3 w-3 border-2 border-current border-t-transparent" />
)}

{/* Detailed progress information */}
{status === "generating_iflow" && (
  <div className="mt-2 text-xs">
    <div className="flex items-center gap-1 opacity-80">
      <span>⚡</span>
      <span>AI is analyzing your integration requirements and generating components...</span>
    </div>
    <div className="mt-1 opacity-60">
      This process typically takes 2-5 minutes depending on complexity
    </div>
  </div>
)}
```

##### **Visual Improvements**
- ✅ **Animated spinners** during processing
- ✅ **Color-coded status** (blue=processing, green=success, red=error)
- ✅ **Time estimates** for user expectations
- ✅ **Real-time status messages** from backend

#### 3. **📊 Status Polling Enhancement**

##### **Existing Polling System**
- ✅ **2-second intervals** for status checks
- ✅ **5-minute timeout** with safety cleanup
- ✅ **Error handling** with retry logic
- ✅ **Automatic UI updates** when status changes

##### **Enhanced Status Messages**
The frontend now displays the exact backend status messages:
```javascript
// Before: Generic "Processing..."
// After: "AI Analysis attempt 3/5..."
setIflowGenerationMessage(statusResult.message)
```

### 🔧 **Technical Implementation**

#### **Backend Flow**
```python
# 1. Job starts
self._update_job_status(job_id, "processing", "Starting iFlow generation...")

# 2. AI Analysis begins
self._update_job_status(job_id, "processing", "Analyzing integration requirements with AI...")

# 3. Retry attempts (if needed)
self._update_job_status(job_id, "processing", f"AI Analysis attempt {attempt + 1}/{max_retries}...")

# 4. Success/Failure
self._update_job_status(job_id, "completed", f"iFlow generation completed: {iflow_name}")
```

#### **Frontend Polling**
```javascript
// Poll every 2 seconds
const statusInterval = setInterval(async () => {
  const statusResult = await getIflowGenerationStatus(job_id);

  // Update UI with real-time status
  setIflowGenerationStatus(statusResult.status);
  setIflowGenerationMessage(statusResult.message);

  // Handle completion
  if (statusResult.status === "completed") {
    clearInterval(statusInterval);
    toast.success("iFlow generated successfully!");
  }
}, 2000);
```

### 📱 **User Experience**

#### **Before Enhancement**
```
[Generate iFlow] → "Processing..." → (5 minutes of silence) → "Completed!"
```

#### **After Enhancement**
```
[Generate iFlow]
↓
"Starting iFlow generation..." (0:05)
↓
"Analyzing integration requirements with AI..." (0:10)
↓
"AI Analysis attempt 1/5..." (0:30)
↓
"AI analysis successful, parsing components..." (2:15)
↓
"Generating iFlow XML and configuration files..." (3:45)
↓
"Creating final iFlow package..." (4:20)
↓
"iFlow generation completed: sample_boomi_dd_1_9368caf3" (4:35)
```

### 🎯 **Benefits**

#### **For Users**
- ✅ **Real-time feedback** on generation progress
- ✅ **Clear expectations** with time estimates
- ✅ **Confidence** that the process is working
- ✅ **Detailed error messages** if something fails
- ✅ **Visual indicators** with animations and colors

#### **For Debugging**
- ✅ **Detailed logs** with job ID tracking
- ✅ **Step-by-step progress** in backend logs
- ✅ **Retry attempt tracking** for AI analysis
- ✅ **Error context** with specific failure reasons

### 🔍 **How to Monitor Progress**

#### **1. Frontend UI**
- **Progress bar** shows overall completion
- **Status message** shows current step
- **Animated spinner** indicates active processing
- **Time estimate** sets user expectations

#### **2. Browser Console**
```javascript
// Check detailed status
console.log("iFlow generation status:", statusResult);
```

#### **3. Backend Logs**
```
📊 Job 9368caf3: processing - Starting iFlow generation...
📊 Job 9368caf3: processing - Analyzing integration requirements with AI...
📊 Job 9368caf3: processing - AI Analysis attempt 1/5...
📊 Job 9368caf3: processing - AI analysis successful, parsing components...
📊 Job 9368caf3: completed - iFlow generation completed: sample_boomi_dd_1_9368caf3
```

#### **4. Jobs File**
```json
{
  "9368caf3-30f7-437b-8ef9-84f088162692": {
    "status": "processing",
    "message": "AI Analysis attempt 2/5...",
    "created": "2025-07-15T21:00:00.000Z"
  }
}
```

### 🚀 **Future Enhancements**

#### **Potential Additions**
- **Progress percentage** based on current step
- **Estimated time remaining** calculations
- **Detailed component breakdown** during generation
- **Real-time AI response streaming** (if supported)
- **Cancel operation** functionality
- **Progress history** for completed jobs

#### **Advanced Features**
- **WebSocket connections** for real-time updates
- **Progress notifications** via browser notifications
- **Email alerts** for long-running jobs
- **Batch processing** progress tracking

### 🎉 **Result**

Users now have **complete visibility** into the iFlow generation process with:
- **Real-time status updates** every 2 seconds
- **Detailed progress messages** from the AI analysis
- **Visual feedback** with animations and colors
- **Time expectations** to reduce anxiety
- **Error transparency** with retry information

No more wondering if the system is working - users get **continuous feedback** throughout the entire 2-5 minute generation process! 🎯

---

# Environment Configuration

## 🎯 **Complete .env Configuration Added**

Your `.env` file now includes all essential AWS and application configurations:

### 🔑 **AWS S3 Configuration**
```env
AWS_ACCESS_KEY_ID=AKIA4C4YFOZHDVUW2QU2
AWS_SECRET_ACCESS_KEY=Ol+7ECgiTzRAg3WGFro2qGIarIoNGEenxfJUyDYS
S3_BUCKET_NAME=is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=830858425934
```

### ⚙️ **S3 Advanced Configuration**
```env
S3_SIGNATURE_VERSION=s3v4
S3_ADDRESSING_STYLE=virtual
S3_USE_SSL=true
S3_VERIFY_SSL=true
```

### 📁 **File Upload Configuration**
```env
MAX_FILE_SIZE_MB=100
ALLOWED_FILE_TYPES=txt,doc,docx,pdf,xml,json,md
UPLOAD_TIMEOUT_SECONDS=300
```

### 💾 **Storage Configuration**
```env
LOCAL_STORAGE_PATH=storage
TEMP_STORAGE_PATH=temp
FILE_RETENTION_DAYS=90
CLEANUP_INTERVAL_HOURS=24
```

### 🗄️ **Database Configuration**
```env
DATABASE_SCHEMA=is_migration
ENABLE_ROW_LEVEL_SECURITY=true
```

### 🧠 **Vector Search Configuration**
```env
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
MAX_SEARCH_RESULTS=10
```

### 🚀 **Performance Configuration**
```env
REQUEST_TIMEOUT_SECONDS=300
MAX_CONCURRENT_UPLOADS=5
ENABLE_COMPRESSION=true
```

### 📊 **Logging Configuration**
```env
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_ACCESS_LOGS=true
LOG_RETENTION_DAYS=30
```

### 🔒 **Security Configuration**
```env
ENABLE_CORS=true
CORS_ORIGINS=*
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=100
```

### 🚩 **Feature Flags**
```env
ENABLE_VECTOR_SEARCH=true
ENABLE_FEEDBACK_SYSTEM=true
ENABLE_USER_ACTIVITY_TRACKING=true
ENABLE_METRICS_COLLECTION=true
ENABLE_FILE_VERSIONING=false
```

### 🌐 **Integration URLs**
```env
MAIN_API_URL=https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com
MULE_API_URL=https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com
BOOMI_API_URL=https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com
GEMMA3_API_URL=https://mulesoft-iflow-api-gemma3.cfapps.eu10-005.hana.ondemand.com
FRONTEND_URL=https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com
```

## ✅ **What This Gives You**

### **AWS S3 Integration**
- ✅ Direct connection to your S3 bucket
- ✅ Secure file upload/download
- ✅ Automatic failover to local storage
- ✅ File retention and cleanup policies

### **Database Features**
- ✅ Schema isolation (`is_migration`)
- ✅ Vector search capabilities
- ✅ Row-level security
- ✅ History tracking

### **Performance & Security**
- ✅ File size and type restrictions
- ✅ Request timeouts and rate limiting
- ✅ CORS configuration
- ✅ Comprehensive logging

### **Feature Control**
- ✅ Enable/disable features via flags
- ✅ Vector search toggle
- ✅ Feedback system control
- ✅ Activity tracking options

## 🧪 **Validate Your Configuration**

Run the validation script to check everything:

```bash
python validate_environment.py
```

This will:
- ✅ Check all required environment variables
- ✅ Test database and S3 connections
- ✅ Validate URL configurations
- ✅ Generate CF deployment commands

## ☁️ **Cloud Foundry Deployment**

The validator will generate commands like:

```bash
# For each application
cf set-env it-resonance-main-api AWS_ACCESS_KEY_ID 'AKIA4C4YFOZHDVUW2QU2'
cf set-env it-resonance-main-api AWS_SECRET_ACCESS_KEY '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'
cf set-env it-resonance-main-api S3_BUCKET_NAME 'is-migration-dzassg3x3mde9njpznqo3fwc376waeun1a-s3alias'
cf set-env it-resonance-main-api AWS_REGION 'us-east-1'
cf restart it-resonance-main-api
```

## 🔧 **Next Steps**

1. **Validate Configuration**:
   ```bash
   python validate_environment.py
   ```

2. **Test Database Integration**:
   ```bash
   python database_integration/test_cf_objectstore.py
   ```

3. **Set CF Environment Variables**:
   Use the commands generated by the validator

4. **Deploy Applications**:
   Your applications are now ready with full S3 and database integration!

## 🎉 **You're All Set!**

Your IS-Migration application now has:
- ✅ **Complete AWS S3 integration**
- ✅ **Supabase database with vector search**
- ✅ **Production-ready configuration**
- ✅ **Security and performance optimizations**
- ✅ **Feature flags for easy control**

Everything is configured and ready for deployment! 🚀

---

# System Architecture Reference

## 🏗️ System Overview

The IS-Migration platform is a comprehensive AI-powered solution for migrating integration flows from legacy platforms (Dell Boomi, MuleSoft) to SAP Integration Suite. The platform leverages multiple AI providers and template-based generation to ensure reliable, SAP-compliant iFlow creation.

## 🎯 Core Architecture Principles

### 1. **Microservices Architecture**
- **Main API (Port 5000)**: Orchestration and document processing
- **BoomiToIS-API (Port 5003)**: Boomi-specific processing
- **MuleToIS-API (Port 5001)**: MuleSoft-specific processing  
- **MuleToIS-API-Gemma3 (Port 5002)**: RunPod Gemma-3 integration
- **React Frontend**: User interface and workflow management

### 2. **AI-First Approach**
- **Strategic AI Usage**: AI used only for analysis and understanding
- **Template-Based Generation**: Deterministic XML generation using proven templates
- **Multi-Provider Support**: Anthropic Claude, OpenAI GPT, Azure OpenAI, RunPod Gemma-3
- **Fallback Mechanisms**: Local processing when AI providers are unavailable

### 3. **Data-Driven Processing**
- **Supabase Database**: Job management and progress tracking
- **File Storage**: AWS S3 / Cloud Foundry Object Store
- **Local Processing**: Temporary file handling and debug output

## 🔄 Processing Workflow

### Phase 1: Document Upload & Processing (10-15 seconds)
1. **File Upload**: User uploads Word/PDF/XML documents
2. **Platform Selection**: User selects target platform (Boomi/MuleSoft)
3. **Content Extraction**: Raw text extracted from documents
4. **AI Enhancement**: Optional LLM-powered documentation improvement
5. **Markdown Generation**: Structured documentation created

### Phase 2: Component Analysis (30-60 seconds)
1. **LLM Analysis**: AI analyzes documentation to identify components
2. **JSON Generation**: Structured component definitions created
3. **Validation**: JSON structure validated and cleaned
4. **Enhancement**: Code-based component enhancement using keywords

### Phase 3: iFlow Generation (5-10 seconds)
1. **Template Selection**: Appropriate SAP templates selected
2. **XML Assembly**: BPMN 2.0 XML structure created
3. **Validation**: SAP Integration Suite compliance verified
4. **Package Creation**: Complete deployable ZIP package assembled

### Phase 4: Deployment (Optional)
1. **SAP BTP Integration**: Direct deployment to SAP Integration Suite
2. **Credential Management**: OAuth/Basic authentication handling
3. **Status Monitoring**: Real-time deployment progress tracking

## 🧠 AI Integration Strategy

### LLM Usage Points
1. **Documentation Enhancement** (Optional): Improve human-readable documentation
2. **Component Analysis** (Required): Extract technical components from documentation

### AI Provider Matrix
| Provider | Model | Use Case | Token Limits | Cost |
|----------|-------|----------|--------------|------|
| Anthropic | Claude Sonnet-4 | Primary analysis | 200K input | Premium |
| OpenAI | GPT-4/3.5 | Alternative provider | 128K input | Standard |
| Azure OpenAI | GPT-4 | Enterprise deployment | 128K input | Enterprise |
| RunPod | Gemma-3-4b-it | Cost-effective option | 24K input, 16K output | Budget |

### Template-First Development
- **Templates Drive Prompts**: LLM prompts derived from available templates
- **Deterministic Output**: Same input always produces same output
- **SAP Compliance**: Templates guarantee SAP Integration Suite standards

## 🏢 Deployment Architecture

### Local Development Environment
```
Frontend (Vite Dev Server) → Main API (5000) → Processing APIs (5001/5003)
                                ↓
                           Local File System + SQLite
```

### Cloud Production Environment
```
React Frontend (CF Static) → Main API (CF) → Processing APIs (CF)
                                ↓
                        Supabase DB + S3/Object Store
```

### Environment Configuration
- **Local**: File-based storage, direct API calls
- **Cloud**: Database persistence, object storage, CORS handling

## 🔧 Technical Components

### Frontend (React + Vite)
- **Framework**: React 18 with Vite build system
- **UI Library**: HeroUI + Tailwind CSS
- **State Management**: Redux Toolkit
- **Key Features**: File upload, progress tracking, download management

### Backend APIs (Flask)
- **Framework**: Python Flask with CORS support
- **Authentication**: API key management, SAP BTP integration
- **File Processing**: Document parsing, XML processing
- **Job Management**: Async processing with status tracking

### Database Layer (Supabase)
- **Database**: PostgreSQL with is_migration schema
- **Tables**: Jobs, files, processing_status, deployment_logs
- **Features**: Real-time subscriptions, row-level security

### Storage Layer
- **Local**: File system for development
- **Cloud**: AWS S3 or Cloud Foundry Object Store
- **Purpose**: Document storage, artifact management, debug files

## 🛡️ Security & Authentication

### API Security
- **CORS Configuration**: Proper cross-origin handling
- **API Key Management**: Secure credential storage
- **Environment Variables**: Sensitive data protection

### SAP BTP Integration
- **Authentication**: OAuth 2.0 and Basic Auth support
- **Environment Management**: Trial and production environments
- **Credential Rotation**: Secure credential management

## 📊 Monitoring & Debugging

### Debug System
- **genai_debug/ folders**: Comprehensive debug output
- **Intermediate Files**: Raw responses, parsed JSON, generated XML
- **Error Logging**: Detailed error tracking and recovery

### Performance Monitoring
- **Job Status Tracking**: Real-time progress updates
- **API Response Times**: Performance metrics collection
- **Error Rate Monitoring**: System health tracking

## 🚀 Key Innovations

### 1. **Enhanced Request-Reply Processing**
- Solves "hanging Start Message Event" problem
- Creates complete request-reply patterns with proper connections
- Ensures SAP Integration Suite compliance

### 2. **Multi-LLM Architecture**
- Provider flexibility for cost optimization
- Fallback mechanisms for reliability
- Latest models with high token limits

### 3. **Template-Driven Generation**
- Deterministic, reliable output
- SAP Integration Suite compliance guaranteed
- Fast processing without AI dependency

### 4. **Hybrid AI-Code Architecture**
- AI for understanding, code for generation
- Best of both worlds: intelligence + reliability
- Scalable and maintainable approach

---

## 📈 Future Roadmap

### Short Term
- Enhanced template library expansion
- Additional component mappings
- Performance optimization

### Medium Term
- Batch processing capabilities
- Advanced validation and testing
- Integration pattern library

### Long Term
- Zero-LLM generation (pure template-based)
- Migration assessment tools
- Enterprise-grade monitoring

---

# API Implementation Details

## MuleToIS API for iFlow Generation

This API provides a REST interface for generating SAP Integration Suite iFlows from markdown documentation. It leverages the MuleToIFlow GenAI approach to analyze markdown content and generate iFlow XML files.

### Features

- REST API for generating iFlows from markdown content
- Asynchronous job processing
- Job status tracking
- Download generated iFlow ZIP files
- Access to debug files for troubleshooting

### Prerequisites

- Python 3.8 or higher
- Claude API key (set in `.env` file)
- Access to the MuleToIFlow GenAI Approach code

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Claude API key:
   ```
   CLAUDE_API_KEY=your_api_key_here
   ```

### API Endpoints

#### Generate iFlow

```
POST /api/generate-iflow
```

Request body:
```json
{
  "markdown": "# API Documentation...",
  "iflow_name": "MyIFlow" (optional)
}
```

Response:
```json
{
  "status": "queued",
  "message": "iFlow generation started",
  "job_id": "12345678-1234-5678-1234-567812345678"
}
```

#### Get Job Status

```
GET /api/jobs/{job_id}
```

Response:
```json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "status": "completed",
  "created": "2025-05-15T10:30:00.000Z",
  "message": "iFlow generation completed successfully!",
  "files": {
    "zip": "results/12345678-1234-5678-1234-567812345678/GeneratedIFlow_12345678.zip",
    "debug": {
      "raw_analysis_response.txt": "genai_debug/raw_analysis_response.txt",
      "final_iflow_GeneratedIFlow_12345678.xml": "genai_debug/final_iflow_GeneratedIFlow_12345678.xml"
    }
  },
  "iflow_name": "GeneratedIFlow_12345678"
}
```

#### Download Generated iFlow

```
GET /api/jobs/{job_id}/download
```

Returns the generated iFlow ZIP file.

#### Download Debug File

```
GET /api/jobs/{job_id}/debug/{file_name}
```

Returns the specified debug file.

#### Health Check

```
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "message": "MuleToIS API is running",
  "api_key_configured": true
}
```

### Integration with Frontend

To integrate with the frontend "Generate iFlow" button:

1. Update the frontend API service to call the new endpoints:

```javascript
// Generate iFlow from markdown documentation
export const generateIflow = async (markdown, iflowName = null) => {
  try {
    const response = await api.post('/api/generate-iflow', {
      markdown,
      iflow_name: iflowName
    });
    return response.data;
  } catch (error) {
    console.error("Error generating iFlow:", error);
    throw error;
  }
};

// Get iFlow generation status
export const getIflowGenerationStatus = async (jobId) => {
  try {
    const response = await api.get(`/api/jobs/${jobId}`);
    return response.data;
  } catch (error) {
    console.error("Error getting iFlow generation status:", error);
    throw error;
  }
};

// Download generated iFlow
export const downloadGeneratedIflow = async (jobId) => {
  try {
    const response = await api.get(`/api/jobs/${jobId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error("Error downloading generated iFlow:", error);
    throw error;
  }
};
```

2. Update the "Generate iFlow" button handler to use the new API:

```javascript
const handleGenerateIflow = async () => {
  try {
    setIsGeneratingIflow(true);
    
    // Get the markdown content from the job
    const markdownContent = await getDocumentation(jobInfo.id, 'markdown');
    const markdownText = await markdownContent.text();
    
    // Call the API to generate the iFlow
    const result = await generateIflow(markdownText);
    
    // Start polling for status
    const statusInterval = setInterval(async () => {
      try {
        const statusResult = await getIflowGenerationStatus(result.job_id);
        
        if (statusResult.status === "completed") {
          setIsGeneratingIflow(false);
          setIsIflowGenerated(true);
          setIflowJobId(result.job_id);
          toast.success("iFlow generated successfully!");
          clearInterval(statusInterval);
        } else if (statusResult.status === "failed") {
          setIsGeneratingIflow(false);
          toast.error(`iFlow generation failed: ${statusResult.message}`);
          clearInterval(statusInterval);
        }
      } catch (error) {
        console.error("Error checking iFlow generation status:", error);
      }
    }, 2000);
    
  } catch (error) {
    setIsGeneratingIflow(false);
    toast.error("Failed to generate iFlow");
    console.error("Error generating iFlow:", error);
  }
};
```

---

# Project Documentation

## 🏗️ Technical Architecture

### System Overview
IMigrate is a comprehensive integration migration platform that converts legacy integration solutions (Boomi, MuleSoft) to modern SAP Integration Suite implementations using AI-powered analysis and generation.

### AI-Powered Analysis Pipeline
```
Legacy Platform XML/Metadata 
    ↓
Claude Sonnet-4 Analysis & Parsing
    ↓
Structured JSON Representation
    ↓
SAP Integration Suite iFlow Generation
    ↓
Deployment to SAP BTP
```

### Service Architecture
- **Main API** (Port 5000): Core documentation processing, job management, and workflow orchestration
- **BoomiToIS-API** (Port 5003): Specialized Boomi XML processing and iFlow generation
- **MuleToIS-API** (Port 5001): Specialized MuleSoft XML processing and iFlow generation  
- **Frontend** (React/Vite): User interface for uploads, progress tracking, and workflow management

## 🔧 Technical Components

### 1. Document Processing Engine
- **Word Document Conversion**: Converts .docx files to markdown using Anthropic Claude
- **XML Analysis**: Parses Boomi/MuleSoft XML artifacts to extract integration patterns
- **AI Enhancement**: Uses Claude Sonnet-4 for intelligent documentation generation
- **Progress Tracking**: Real-time status updates with visual progress indicators

### 2. iFlow Generation System
- **Template-Based Generation**: Uses enhanced templates for SAP Integration Suite components
- **Component Mapping**: Maps legacy components to SAP equivalents
- **BPMN Generation**: Creates valid BPMN 2.0 XML for SAP Integration Suite
- **Artifact Alignment**: Manages x,y coordinates for proper visual layout

### 3. SAP BTP Integration
- **Direct Deployment**: Deploys generated iFlows to SAP Integration Suite
- **Authentication**: Supports SAP BTP OAuth and basic authentication
- **Environment Management**: Handles multiple SAP BTP environments (trial, production)

## 📊 Current Status

### ✅ Completed Features
- Document upload and processing (Word, XML)
- AI-powered markdown generation
- Progress tracking with visual indicators
- iFlow generation for Boomi processes
- SAP BTP deployment integration
- Multi-platform support (Boomi, MuleSoft)
- Cloud Foundry deployment pipeline

### 🚧 In Progress
- Enhanced template system optimization
- Error handling improvements
- Performance optimization
- Additional component mappings

### 📋 Planned Features
- Batch processing capabilities
- Advanced validation and testing
- Integration pattern library
- Migration assessment tools

## 🗄️ Database Design

### Database Schema (Supabase PostgreSQL)

#### Core Tables

```sql
-- Jobs table (primary entity)
CREATE TABLE is_migration.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    platform TEXT DEFAULT 'mulesoft',
    user_id TEXT,
    file_info JSONB,
    parsed_details JSONB,
    enhance_with_llm BOOLEAN DEFAULT false,
    llm_service TEXT,
    upload_path TEXT,
    results_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Documents table (file metadata)
CREATE TABLE is_migration.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES is_migration.jobs(id),
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size BIGINT,
    file_path TEXT,
    content_hash TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- iFlow Generations table (generation tracking)
CREATE TABLE is_migration.iflow_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES is_migration.jobs(id),
    iflow_name TEXT,
    generation_status TEXT DEFAULT 'pending',
    ai_model TEXT,
    generation_time_seconds INTEGER,
    component_count INTEGER,
    template_version TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

#### Database Features
- **Row-Level Security (RLS)**: User-based data isolation
- **Vector Extension**: pgvector for similarity search
- **Real-time Subscriptions**: Live status updates
- **Audit Trails**: Complete job history tracking

## ⚠️ Known Issues

### Database Integration
- Supabase integration is disabled (`DATABASE_ENABLED = False`) due to dependency conflicts
- Jobs are stored in memory/file-based storage instead of database
- Job persistence issues when applications restart

### Boomi API Parsing Limitations
- **Critical Issue**: Current Boomi XML parser does NOT extract key API elements:
  - ❌ API endpoints and URLs (ConnectionOverride sections)
  - ❌ Query parameters (pageSize, timeout, batchSize, sleep)
  - ❌ Filter parameters (Filter_LSRD, Filter_company_territory_code, etc.)
  - ❌ SuccessFactors operations (only handles Salesforce)
  - ❌ Object types and operation types (objectType, operationType)
  - ❌ Connection configuration details (connectorType, connection IDs)
- **Impact**: Generated SAP Integration Suite equivalents may miss critical API calls, filters, and operations
- **Location**: `BoomiToIS-API/boomi_xml_processor.py` needs enhancement
- **Required**: Add parsing for ConnectionOverride, OverrideableDefinedProcessPropertyValue, ObjectDefinitions, and GenericOperationConfig sections

### Deployment
- Cloud Foundry deployments require hardcoded values in manifest.yml files
- Environment variables need to be configured for each deployment environment

---

**Consolidated Implementation Guide Completed Successfully** ✅  
**All markdown files from August 10th+ consolidated with comprehensive implementation details** 🚀