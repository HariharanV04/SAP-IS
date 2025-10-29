# BoomiToIS-API Architecture

## 🏗️ System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Web UI]
        CLI[Command Line Interface]
        API_Client[REST API Client]
    end
    
    subgraph "API Gateway Layer"
        Flask[Flask Web Server]
        CORS[CORS Configuration]
        Auth[Authentication]
    end
    
    subgraph "Core Processing Layer"
        Generator[Enhanced GenAI iFlow Generator]
        Converter[JSON to iFlow Converter]
        Templates[iFlow Templates]
        BPMN[BPMN Templates]
    end
    
    subgraph "Processing & Utilities"
        Boomi_Processor[Boomi XML Processor]
        iFlow_Fixer[iFlow XML Fixer]
        Validator[Configuration Validator]
        SAP_Integration[SAP BTP Integration]
    end
    
    subgraph "Data & Configuration"
        Config[Configuration Files]
        Env[Environment Variables]
        Jobs[Job Queue]
        Templates_Store[Template Store]
    end
    
    subgraph "Output & Deployment"
        iFlow_Output[iFlow ZIP Files]
        Debug_Files[Debug Outputs]
        SAP_Deploy[SAP BTP Deployment]
        Results[Results Directory]
    end
    
    subgraph "External Systems"
        Boomi[Boomi Platform]
        SAP_IS[SAP Integration Suite]
        Claude[Claude AI API]
        BTP[SAP BTP]
    end
    
    %% Frontend to API Gateway
    UI --> Flask
    CLI --> Flask
    API_Client --> Flask
    
    %% API Gateway to Core Processing
    Flask --> Generator
    Flask --> Converter
    Flask --> Templates
    Flask --> BPMN
    
    %% Core Processing to Utilities
    Generator --> Boomi_Processor
    Generator --> iFlow_Fixer
    Generator --> Validator
    Generator --> SAP_Integration
    
    %% Data Flow
    Config --> Generator
    Config --> Converter
    Env --> Generator
    Jobs --> Generator
    
    %% Output Flow
    Generator --> iFlow_Output
    Generator --> Debug_Files
    Generator --> SAP_Deploy
    Generator --> Results
    
    %% External Integrations
    Boomi --> Boomi_Processor
    SAP_IS --> SAP_Integration
    Claude --> Generator
    BTP --> SAP_Deploy
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef core fill:#e8f5e8
    classDef utils fill:#fff3e0
    classDef data fill:#fce4ec
    classDef output fill:#e0f2f1
    classDef external fill:#f1f8e9
    
    class UI,CLI,API_Client frontend
    class Flask,CORS,Auth api
    class Generator,Converter,Templates,BPMN core
    class Boomi_Processor,iFlow_Fixer,Validator,SAP_Integration utils
    class Config,Env,Jobs,Templates_Store data
    class iFlow_Output,Debug_Files,SAP_Deploy,Results output
    class Boomi,SAP_IS,Claude,BTP external
```

## 🔄 Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Web_UI
    participant Flask_API
    participant Generator
    participant Templates
    participant iFlow_Output
    participant SAP_BTP
    
    User->>Web_UI: Upload Boomi XML/JSON
    Web_UI->>Flask_API: POST /api/generate
    Flask_API->>Generator: Process Blueprint
    Generator->>Templates: Load Templates
    Templates->>Generator: Return Templates
    Generator->>Generator: Generate iFlow XML
    Generator->>iFlow_Output: Create ZIP File
    Flask_API->>Web_UI: Return Job ID
    Web_UI->>Flask_API: Poll Job Status
    Flask_API->>Generator: Check Progress
    Generator->>Flask_API: Return Status
    Flask_API->>Web_UI: Return Status
    Web_UI->>User: Download iFlow ZIP
    User->>SAP_BTP: Import iFlow
```

## 🧩 Component Architecture

```mermaid
graph LR
    subgraph "Core Generator"
        A[enhanced_genai_iflow_generator.py]
        B[json_to_iflow_converter.py]
        C[enhanced_iflow_templates.py]
        D[bpmn_templates.py]
    end
    
    subgraph "Web Interface"
        E[app.py]
        F[iflow_generator_api.py]
        G[cors_config.py]
    end
    
    subgraph "Processing"
        H[boomi_xml_processor.py]
        I[iflow_fixer.py]
        J[config_validation_engine.py]
    end
    
    subgraph "Deployment"
        K[iflow_deployment.py]
        L[sap_btp_integration.py]
        M[direct_iflow_deployment.py]
    end
    
    A --> B
    A --> C
    A --> D
    E --> F
    F --> A
    H --> A
    I --> A
    J --> A
    A --> K
    K --> L
    A --> M
```

## 📊 File Organization Architecture

```mermaid
graph TD
    subgraph "Root Directory"
        Main[Main Application Files]
        Config[Configuration Files]
        Docs[Documentation]
        Scripts[Deployment Scripts]
    end
    
    subgraph "Working Directories"
        GenAI_Debug[genai_debug/]
        GenAI_Output[genai_output/]
        Results[results/]
        Uploads[uploads/]
    end
    
    subgraph "Archive Structure"
        Archive[archive/]
        Test_Results[test_results/]
        Test_Scripts[test_scripts/]
        Debug_Files[debug_files/]
        Sample_Files[sample_files/]
        Old_Versions[old_versions/]
    end
    
    Main --> GenAI_Debug
    Main --> GenAI_Output
    Main --> Results
    Main --> Uploads
    
    Archive --> Test_Results
    Archive --> Test_Scripts
    Archive --> Debug_Files
    Archive --> Sample_Files
    Archive --> Old_Versions
```

## 🔧 Configuration Architecture

```mermaid
graph LR
    subgraph "Environment"
        Dev[.env.development]
        Prod[.env.production]
        Example[.env.example]
    end
    
    subgraph "Configuration"
        Config_Engine[config_validation_engine.py]
        Config_Dir[config/]
        Jobs[jobs.json]
    end
    
    subgraph "Templates"
        Templates[enhanced_iflow_templates.py]
        BPMN[bpmn_templates.py]
        Component_Mapping[COMPONENT_MAPPING_REFERENCE.md]
    end
    
    Dev --> Config_Engine
    Prod --> Config_Engine
    Example --> Config_Engine
    Config_Engine --> Templates
    Config_Engine --> BPMN
    Component_Mapping --> Templates
```

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph "Local Development"
        Local[Local Environment]
        Dev_Config[Development Config]
        Local_Test[Local Testing]
    end
    
    subgraph "Cloud Deployment"
        CloudFoundry[Cloud Foundry]
        Manifest[manifest.yml]
        Procfile[Procfile]
        Runtime[runtime.txt]
    end
    
    subgraph "SAP BTP Integration"
        BTP_Client[SAP BTP Client]
        BTP_Secret[SAP BTP Secret]
        BTP_Tenant[SAP BTP Tenant]
        iFlow_Deploy[iFlow Deployment]
    end
    
    Local --> Dev_Config
    Local --> Local_Test
    Local --> CloudFoundry
    CloudFoundry --> Manifest
    CloudFoundry --> Procfile
    CloudFoundry --> Runtime
    CloudFoundry --> BTP_Client
    BTP_Client --> BTP_Secret
    BTP_Client --> BTP_Tenant
    BTP_Client --> iFlow_Deploy
```

---

## 📋 Architecture Summary

### **Layered Architecture**
- **Frontend Layer**: Web UI, CLI, API clients
- **API Gateway Layer**: Flask server with CORS and auth
- **Core Processing Layer**: Main iFlow generation logic
- **Processing & Utilities**: Supporting processors and validators
- **Data & Configuration**: Configuration management and job queue
- **Output & Deployment**: iFlow generation and SAP deployment

### **Key Design Principles**
1. **Separation of Concerns**: Each component has a single responsibility
2. **Modularity**: Components can be developed and tested independently
3. **Extensibility**: Template system allows easy customization
4. **Scalability**: Job-based processing for handling multiple requests
5. **Maintainability**: Clean separation between core logic and utilities

### **Integration Points**
- **Boomi Platform**: Source of integration processes
- **SAP Integration Suite**: Target for generated iFlows
- **Claude AI API**: AI-powered analysis and generation
- **SAP BTP**: Cloud platform for deployment

### **Data Flow**
1. **Input**: Boomi XML/JSON blueprints
2. **Processing**: AI analysis and template-based generation
3. **Output**: SAP Integration Suite compatible iFlow ZIP files
4. **Deployment**: Direct deployment to SAP BTP (optional)
