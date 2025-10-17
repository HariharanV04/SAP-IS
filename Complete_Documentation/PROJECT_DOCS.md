# PROJECT DOCUMENTATION - IMigrate Platform

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

## 🔐 Environment Configuration

### Required Environment Variables

#### Main API (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
IFLOW_API_URL=http://localhost:5001
BOOMI_API_URL=http://localhost:5003
RESULTS_FOLDER=./results
UPLOADS_FOLDER=./uploads
```

#### BoomiToIS-API (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
SAP_BTP_BASE_URL=https://your-tenant.it-cpi.cfapps.eu10.hana.ondemand.com
SAP_BTP_USERNAME=your-username
SAP_BTP_PASSWORD=your-password
```

#### Frontend (.env)
```
VITE_MAIN_API_PROTOCOL=http
VITE_MAIN_API_HOST=localhost:5000
VITE_IFLOW_API_PROTOCOL=http
VITE_IFLOW_API_HOST=localhost:5003
```

## 🚀 Deployment Architecture

### Local Development
- All services run on localhost with different ports
- Hot reload enabled for frontend development
- Direct API communication between services

### Production (Cloud Foundry)
- Each service deployed as separate CF application
- Environment-specific configurations
- CORS enabled for cross-origin requests
- Health checks and monitoring enabled

### Cloud Foundry Apps
```
├── mule2is-api.cfapps.eu10.hana.ondemand.com     # Main API
├── boomitois-api.cfapps.eu10.hana.ondemand.com   # BoomiToIS API  
├── muletois-api.cfapps.eu10.hana.ondemand.com    # MuleToIS API
└── ifa-project.cfapps.eu10.hana.ondemand.com     # Frontend
```

## 🧪 Testing & Quality Assurance

### Test Coverage
- Unit tests for core processing functions
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Performance tests for large file processing

### Quality Gates
- Code review requirements
- Automated testing in CI/CD pipeline
- Security scanning for dependencies
- Performance monitoring

## 📈 Performance Metrics

### Processing Capabilities
- **Document Processing**: ~60 seconds for typical Word documents
- **iFlow Generation**: ~30-120 seconds depending on complexity
- **Concurrent Jobs**: Supports multiple parallel processing jobs
- **File Size Limits**: Up to 50MB for document uploads

### Scalability Considerations
- Stateless service design for horizontal scaling
- Job queue system for handling peak loads
- Caching for frequently accessed data
- Database optimization for job tracking

## 🔍 Monitoring & Logging

### Application Logs
- Structured logging with timestamps and severity levels
- Request/response logging for API calls
- Error tracking with stack traces
- Performance metrics collection

### Health Monitoring
- Service health check endpoints
- Database connectivity monitoring
- External API dependency checks
- Resource utilization tracking

## 🛡️ Security Considerations

### Authentication & Authorization
- API key management for external services
- Environment variable protection
- Secure credential storage
- Access control for sensitive operations

### Data Protection
- Temporary file cleanup
- Secure file upload handling
- Data encryption in transit
- Privacy compliance measures

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

For setup and usage instructions, see [HOW_TO_RUN_GUIDE.md](./HOW_TO_RUN_GUIDE.md).
