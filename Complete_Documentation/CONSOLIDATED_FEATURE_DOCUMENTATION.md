# IS-Migration Project - Consolidated Feature Documentation

This document consolidates all feature-specific documentation, implementation guides, and technical references that were previously scattered across multiple markdown files.

---

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

---

# Documentation Viewing Feature

## 🎯 **Overview**

Added the ability to view intermediate processing files (markdown and JSON) in the UI after uploading a technical design document for Boomi. Users can now see exactly what the AI generated during the document processing step.

## 📋 **What Was Added**

### 1. **Frontend Changes (JobResult.jsx)**

#### New Download State Management
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

#### New UI Section for Processing Files
Added a new section that appears only for uploaded documentation (`jobInfo.source_type === 'uploaded_documentation'`):

- **AI-Enhanced Markdown**: The structured markdown created by AI for iFlow generation
- **Documentation JSON**: Complete structured data with metadata
- **Original Document Content**: Raw extracted text from the uploaded file

Each file has:
- 👁️ **View in browser** button (opens in new tab)
- 📥 **Download** button (saves file locally)
- 🏷️ **Status badges** explaining the file purpose

#### Enhanced Download Function
Updated `downloadFile()` function to handle new file type mappings:
- `documentation_json` → `documentationJson` state
- `uploaded_documentation` → `uploadedDocumentation` state

### 2. **Backend Changes (app.py)**

#### Enhanced API Endpoint
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

#### Updated Job Data Structure
Added new file references to job data:
```python
'files': {
    'documentation_json': os.path.join('results', job_id, 'documentation.json'),
    'markdown': os.path.join('results', job_id, 'uploaded_documentation.md'),
    'uploaded_documentation': os.path.join('results', job_id, 'uploaded_documentation.md')  # NEW
}
```

## 🔄 **User Workflow**

### Before (What Users Couldn't See)
1. Upload Boomi document ✅
2. ❓ **Black box processing** - no visibility into AI conversion
3. Get final iFlow ✅

### After (What Users Can Now See)
1. Upload Boomi document ✅
2. **View intermediate files**:
   - 📄 **AI-Enhanced Markdown**: See how AI structured the content
   - 📋 **Documentation JSON**: View complete metadata and processing info
   - 📝 **Original Content**: Compare with raw extracted text
3. Get final iFlow ✅

## 🎨 **UI Design**

### Visual Indicators
- **Blue badges**: AI-Enhanced Markdown ("Structured for iFlow Generation")
- **Green badges**: Documentation JSON ("Structured Data + Metadata") 
- **Gray badges**: Original Content ("Raw Extracted Text")

### File Actions
- **External Link Icon**: Opens file in browser for immediate viewing
- **Download Icon**: Downloads file to local machine
- **Loading Spinner**: Shows during download operations

## 🧪 **Testing**

Created `test_documentation_viewing.py` to verify:
- ✅ Document upload works
- ✅ All three file types are accessible
- ✅ Proper content types are returned
- ✅ File sizes are reasonable

## 📁 **Files Modified**

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

## 🚀 **How to Use**

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

## 🎯 **Benefits**

- **Transparency**: Users can see exactly what the AI generated
- **Debugging**: Easier to understand why iFlow generation succeeded/failed
- **Quality Control**: Users can verify the AI understood their document correctly
- **Learning**: Users can see how to structure documents for better AI processing

## 🔮 **Future Enhancements**

- **Inline Editing**: Allow users to edit the AI-enhanced markdown before iFlow generation
- **Comparison View**: Side-by-side comparison of original vs AI-enhanced content
- **Processing Metrics**: Show processing time, token usage, confidence scores
- **Version History**: Keep track of multiple processing attempts

# Enhanced Process Flow

This shows how the new enhanced process flow formatting will look:

---

## **Process Flow Overview**

### **Flow Steps**

---

#### **Step 5: Transform SAP Response to SF Update (shape10)**

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

---

#### **Step 6: Check If New Account (shape25)**

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

---

#### **Step 7a: Update Salesforce Account (shape5)**

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

---

#### **Step 7b: Handle Existing Account (shape21)**

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

---

#### **Step 8: End Events (shape4 and shape22)**

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

---

## Key Improvements:

1. **Clear Purpose Statements** - Each step explains what it accomplishes
2. **Detailed Configuration** - Specific technical details organized clearly
3. **Enhanced Data Flow** - Input/Processing/Output clearly defined
4. **Visual Separation** - Horizontal rules and blockquotes for better readability
5. **Professional Formatting** - Clean, business-appropriate presentation
6. **Comprehensive Context** - Full understanding of each step's role

---

## Field Mappings: Before vs After

### ❌ **BEFORE (Broken Format):**
```
Field Mappings: | Source Field | Target Field | Type | Notes | |--------------|--------------|------|-------| | 5 | IMPORT/Object/I_PI_COMPANYDATA/Object/NAME | profile | Company name | | 9 | IMPORT/Object/I_PI_COMPANYDATA/Object/STREET | profile | Street address |
```

### ✅ **AFTER (Enhanced Format):**

**Field Mappings:**

| Source Field | Target Field | Data Type | Business Purpose |
|--------------|--------------|-----------|------------------|
| Customer.CompanyName | BAPI_CUSTOMER.NAME | String | Maps company name from Salesforce to SAP customer master |
| Customer.BillingStreet | BAPI_CUSTOMER.STREET | String | Maps billing street address for customer creation |
| Customer.BillingCity | BAPI_CUSTOMER.CITY | String | Maps billing city for customer address |
| Customer.BillingState | BAPI_CUSTOMER.REGION | String | Maps billing state/region for customer address |

### 🎯 **Key Field Mapping Improvements:**
- **Readable Field Names** - "Customer.CompanyName" instead of "5" or long XML paths
- **Proper Table Format** - Multi-line markdown table instead of single-line text
- **Business Context** - "Business Purpose" column explains the mapping logic
- **Clean Target Fields** - "BAPI_CUSTOMER.NAME" instead of "IMPORT/Object/I_PI_COMPANYDATA/Object/NAME"
- **Proper Data Types** - "String", "Integer", "Date" instead of generic "profile"

---

## Input/Output Profiles: Before vs After

### ❌ **BEFORE (Technical XML Paths):**
```
Input Profile: SF Account QUERY Response XML
- Account Name: Salesforce account name (String)
- Account Street: Street address (String)

Output Profile: Boomi for SAP BAPI_CUSTOMER_CREATEFROMDATA1 FUNCTION Request JSON
- IMPORT/Object/I_PI_COMPANYDATA/Object/NAME: Company name (String)
- IMPORT/Object/I_PI_COMPANYDATA/Object/STREET: Street address (String)
- IMPORT/Object/I_PI_COMPANYDATA/Object/CITY: City (String)
```

### ✅ **AFTER (Clean, Business-Friendly Format):**

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

### 🎯 **Key Profile Improvements:**
- **Clean Field Names** - "CompanyName" instead of "IMPORT/Object/I_PI_COMPANYDATA/Object/NAME"
- **Structured Tables** - Easy-to-scan table format instead of bullet lists
- **Business Descriptions** - Clear, business-friendly field descriptions
- **Logical Grouping** - Related fields grouped together (e.g., address fields)
- **Professional Presentation** - Clean, scannable format for technical documentation

# iFlow Progress Tracking Enhancement

## 🎯 **Overview**

Enhanced the iFlow generation process with detailed progress tracking and status updates to provide users with real-time feedback during the long-running AI analysis and generation process.

## ⏱️ **Why This Was Needed**

iFlow generation can take **2-5 minutes** due to:
- **AI Analysis**: Claude Sonnet-4 analyzing complex integration requirements
- **Component Generation**: Creating SAP Integration Suite components
- **Template Processing**: Converting to BPMN 2.0 XML format
- **Retry Logic**: Up to 5 attempts for AI analysis validation

Users were experiencing:
- ❌ **No feedback** during long processing times
- ❌ **Uncertainty** about whether the process was working
- ❌ **No visibility** into which step was currently running

## ✅ **What Was Enhanced**

### 1. **🔄 Backend Progress Tracking**

#### **Enhanced GenAI Generator**
```python
def _update_job_status(self, job_id, status, message):
    """Update job status for progress tracking"""
    if job_id:
        # Update global jobs.json file
        jobs[job_id]['status'] = status
        jobs[job_id]['message'] = message
        print(f"📊 Job {job_id[:8]}: {status} - {message}")
```

#### **Detailed Status Updates**
- ✅ **"Starting iFlow generation..."**
- ✅ **"Analyzing integration requirements with AI..."**
- ✅ **"AI Analysis attempt 1/5..."**
- ✅ **"AI analysis successful, parsing components..."**
- ✅ **"Generating iFlow XML and configuration files..."**
- ✅ **"Creating final iFlow package..."**
- ✅ **"iFlow generation completed: [name]"**

#### **Error Handling with Progress**
- ✅ **"Parsing failed, retrying... (2/5)"**
- ✅ **"AI response invalid, retrying... (3/5)"**
- ✅ **"AI analysis failed after 5 attempts"**

### 2. **🎨 Frontend Progress Display**

#### **Enhanced Progress Tracker**
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

#### **Visual Improvements**
- ✅ **Animated spinners** during processing
- ✅ **Color-coded status** (blue=processing, green=success, red=error)
- ✅ **Time estimates** for user expectations
- ✅ **Real-time status messages** from backend

### 3. **📊 Status Polling Enhancement**

#### **Existing Polling System**
- ✅ **2-second intervals** for status checks
- ✅ **5-minute timeout** with safety cleanup
- ✅ **Error handling** with retry logic
- ✅ **Automatic UI updates** when status changes

#### **Enhanced Status Messages**
The frontend now displays the exact backend status messages:
```javascript
// Before: Generic "Processing..."
// After: "AI Analysis attempt 3/5..."
setIflowGenerationMessage(statusResult.message)
```

## 🔧 **Technical Implementation**

### **Backend Flow**
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

### **Frontend Polling**
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

## 📱 **User Experience**

### **Before Enhancement**
```
[Generate iFlow] → "Processing..." → (5 minutes of silence) → "Completed!"
```

### **After Enhancement**
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

## 🎯 **Benefits**

### **For Users**
- ✅ **Real-time feedback** on generation progress
- ✅ **Clear expectations** with time estimates
- ✅ **Confidence** that the process is working
- ✅ **Detailed error messages** if something fails
- ✅ **Visual indicators** with animations and colors

### **For Debugging**
- ✅ **Detailed logs** with job ID tracking
- ✅ **Step-by-step progress** in backend logs
- ✅ **Retry attempt tracking** for AI analysis
- ✅ **Error context** with specific failure reasons

## 🔍 **How to Monitor Progress**

### **1. Frontend UI**
- **Progress bar** shows overall completion
- **Status message** shows current step
- **Animated spinner** indicates active processing
- **Time estimate** sets user expectations

### **2. Browser Console**
```javascript
// Check detailed status
console.log("iFlow generation status:", statusResult);
```

### **3. Backend Logs**
```
📊 Job 9368caf3: processing - Starting iFlow generation...
📊 Job 9368caf3: processing - Analyzing integration requirements with AI...
📊 Job 9368caf3: processing - AI Analysis attempt 1/5...
📊 Job 9368caf3: processing - AI analysis successful, parsing components...
📊 Job 9368caf3: completed - iFlow generation completed: sample_boomi_dd_1_9368caf3
```

### **4. Jobs File**
```json
{
  "9368caf3-30f7-437b-8ef9-84f088162692": {
    "status": "processing",
    "message": "AI Analysis attempt 2/5...",
    "created": "2025-07-15T21:00:00.000Z"
  }
}
```

## 🚀 **Future Enhancements**

### **Potential Additions**
- **Progress percentage** based on current step
- **Estimated time remaining** calculations
- **Detailed component breakdown** during generation
- **Real-time AI response streaming** (if supported)
- **Cancel operation** functionality
- **Progress history** for completed jobs

### **Advanced Features**
- **WebSocket connections** for real-time updates
- **Progress notifications** via browser notifications
- **Email alerts** for long-running jobs
- **Batch processing** progress tracking

## 🎉 **Result**

Users now have **complete visibility** into the iFlow generation process with:
- **Real-time status updates** every 2 seconds
- **Detailed progress messages** from the AI analysis
- **Visual feedback** with animations and colors
- **Time expectations** to reduce anxiety
- **Error transparency** with retry information

No more wondering if the system is working - users get **continuous feedback** throughout the entire 2-5 minute generation process! 🎯

---
