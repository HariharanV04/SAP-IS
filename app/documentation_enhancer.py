"""Documentation enhancer using LLM services."""
import os
import sys
import logging
import json
from typing import Optional
import re
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Mermaid validator and LLM fixer
from mermaid_validator import validate_mermaid_in_documentation
from llm_mermaid_fixer import fix_documentation_with_llm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import OpenAI and Anthropic, but don't fail if not installed
try:
    import openai
except ImportError:
    openai = None
    logger.warning("OpenAI package not installed. OpenAI-based enhancement will not be available.")

try:
    import anthropic
    import httpx
except ImportError:
    anthropic = None
    logger.warning("Anthropic package not installed. Claude-based enhancement will not be available.")

class DocumentationEnhancer:
    def __init__(self, selected_service='openai'):
        """Initialize documentation enhancer with specified LLM service.

        Args:
            selected_service: Service to use ('openai' or 'anthropic')
        """
        self.selected_service = selected_service

        # Load API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Initialize clients if possible
        self.openai_client = None
        self.anthropic_client = None

        if openai and self.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")

        if anthropic and self.anthropic_api_key:
            try:
                # Create a custom HTTP client with extended timeout (600 seconds instead of 300)
                http_client = httpx.Client(timeout=600.0)

                # Initialize Anthropic client with a custom http_client to avoid proxies issue
                self.anthropic_client = anthropic.Anthropic(
                    api_key=self.anthropic_api_key,
                    http_client=http_client
                )
                logger.info("Anthropic client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")

    def enhance_documentation(self, base_documentation: str, generate_json: bool = True, output_dir: str = None, platform: str = 'boomi') -> str:
        """Enhance documentation using the configured LLM service.

        Args:
            base_documentation: Base documentation to enhance
            platform: The platform type ('boomi' or 'mulesoft') - overrides content detection

        Returns:
            Enhanced documentation or original if enhancement fails
        """
        # Modified to use a variable to track enhancement success
        enhancement_successful = False

        # Use platform parameter instead of content detection
        logger.info(f"Using platform-based enhancement: {platform}")

        if platform == 'mulesoft':
            prompt = self._create_mulesoft_enhancement_prompt(base_documentation)
        else:
            prompt = f"""You are a Boomi and SAP Integration Suite specialist. Based on the following technical
    documentation, create comprehensive documentation that includes API details, flow logic,
    and detailed SAP Integration Suite visualization. Use SAP Integration Suite components and connections for
    the visualization.

    IMPORTANT:
    1. Do NOT make assumptions about adapters or systems not explicitly mentioned in the source documentation.
    2. Use ONLY the components and connections present in the original Boomi process.
    3. When describing the SAP Integration Suite implementation, maintain the same integration pattern.
    4. If a connection type is unclear, mark it as a configuration decision.
    5. PRESERVE ALL TECHNICAL EXPRESSIONS EXACTLY AS WRITTEN, especially:
    - All HTTP connector configurations and endpoints
    - All Boomi Map/Transform field mappings and functions
    - All Document Properties and their source values
    - All connector parameters and operation configurations
    - DO NOT simplify, summarize, or rewrite any technical expressions

    CRITICAL BOOMI-SPECIFIC ANALYSIS REQUIREMENTS:
    6. ANALYZE BOOMI XML STRUCTURE THOROUGHLY:
    - Examine ALL <shape> elements and their shapetype attributes
    - Identify ALL <connectoraction> elements and their actionType, connectorType
    - Extract ALL <documentproperties> and their complex source value configurations
    - Analyze ALL <Map> elements with their <Mappings> and <Functions>
    - Identify ALL HTTP connector calls within Document Properties
    - Examine ALL operation configurations and parameters

    7. SEQUENCE OF EVENTS MUST BE ACCURATE:
    - Follow the <dragpoints> to determine the exact flow sequence
    - Map each shape's connections using toShape attributes
    - Preserve the exact order of operations as defined in the Boomi XML
    - Do NOT reorder or assume different sequences than what's in the XML

    8. CAPTURE COMPLEX BOOMI PATTERNS:
    - Document Properties with HTTP connector calls (GET operations to external APIs)
    - Dynamic property calculations using date functions, concatenations
    - Connector parameter mappings from profile elements
    - Field mappings in Map components with fromKey/toKey relationships
    - Function steps in transformations (DocumentPropertyGet, etc.)

    HANDLING LARGE DOCUMENTATION:
    1. First analyze the documentation size and structure. If you determine the content will exceed 20,000 tokens in your response, you should:
       - Focus on the most essential components and flows in your detailed analysis
       - Ensure all flows are at least mentioned, even if some details are summarized
       - Prioritize accuracy over comprehensive detail for very large applications
    2. Your final output must include a complete and accurate mapping of all components, even if you need to be more concise in your explanations.

    Here is the source documentation:

    {base_documentation}

    Please structure your response in Markdown with these sections:

    # [Descriptive Title Based on the API/Integration Purpose]

    ## Table of Contents
    Create a detailed table of contents with hyperlinks to all sections and subsections in the document. Use Markdown link syntax like [Section Name](#section-name) to create clickable links to each section. Include ALL sections and subsections.

    ## API Overview
    - Comprehensive description of what this API does and its business purpose
    - Base URL/endpoint pattern
    - Authentication mechanisms
    - Rate limiting information (if available)
    - General response format

    ## Endpoints
    For each endpoint, provide a detailed breakdown:
    - HTTP Method and full path
    - Purpose of the endpoint
    - Request parameters (path, query, headers) with detailed descriptions
    - Request body structure (if applicable) with field descriptions and data types
    - Response format and status codes with detailed descriptions
    - Example request/response if available
    - Error handling for this endpoint

    ## Current Boomi Flow Logic
    ### Process Flow Overview
    Provide a high-level overview of the Boomi process including:
    1. What triggers the process (Start Event configuration)
    2. Main processing steps and their purpose in sequence
    3. Data transformations that occur
    4. External system interactions
    5. Expected outcomes and error scenarios

    ### Step-by-Step Flow Description

    **FORMATTING REQUIREMENTS FOR STEP-BY-STEP FLOW:**
    Use enhanced visual formatting with clear hierarchy and professional structure:

    ## **Process Flow Overview**

    ### **Flow Steps**

    For each step, use this enhanced format:

    ---

    #### **Step 1: Start Event (shape1)**

**Component Type:** [Component Name]

**Purpose:** [Brief description of what this step accomplishes]

**Configuration Details:**

- **Connector Type:** [Specific connector type]
- **Operation:** [Listen/Trigger operation details]
- **Input Profile:** [Data format and structure]
- **Trigger Conditions:** [What initiates this process]

**Data Flow:**

- **Input:** [Detailed input description]
- **Processing:** [What happens to the data]
- **Output:** [Detailed output description]

    ---

    #### **Step 2: Document Properties** *(if present)*

**Component Type:** Document Properties

**Purpose:** [Brief description of property calculations and enhancements]

**Configuration Details:**

- **Dynamic Properties:** [List all dynamic document properties]
- **HTTP Calls:** [Any HTTP connector calls within properties]
- **Calculations:** [Date calculations, concatenations, etc.]
- **Parameter Mappings:** [Source value configurations]

**Data Flow:**

- **Input:** [Previous step output]
- **Processing:** [Property calculations and data enhancement]
- **Output:** [Enhanced data with calculated properties]

    ---

    #### **Step 3: Transform/Map Components**

**Component Type:** Map/Transform

**Purpose:** [Brief description of the transformation being performed]

**Configuration Details:**

- **Input Profile:** [Source data structure name]
- **Output Profile:** [Target data structure name]
- **Transformation Logic:** [Key transformation rules]
- **Function Steps:** [Any special functions used]

**IMPORTANT FORMATTING REQUIREMENTS:**

1. **Error Property Categories:** When documenting error properties, use structured tables:
   ```
   | Category | Property Names | Description |
   |----------|----------------|-------------|
   | Business Rule Errors | RPT_INT_ALL_BRULE_ERR_CNT, RPT_INT_ALL_BRULE_WRN_CNT, RPT_INT_ALL_BRULE_SKP_CNT | Error tracking for business rule violations |
   | Cleanse Errors | RPT_INT_ALL_CLNS_ERR_CNT, RPT_INT_ALL_CLNS_WRN_CNT, RPT_INT_ALL_CLNS_SKP_CNT | Data cleansing error tracking |
   ```

2. **Input Profile Details:** Use structured tables for field mappings:
   ```
   | Field Path | Description | Data Type | Business Purpose |
   |------------|-------------|-----------|------------------|
   | CompoundEmployee/person/person_id_external | Global Person ID | String | Unique employee identifier |
   | CompoundEmployee/person/employment_information/email_address | Corporate email address | String | Employee contact information |
   ```

3. **Output Profile Details:** Use structured tables for target fields:
   ```
   | Target Field | Description | Source Mapping | Business Purpose |
   |--------------|-------------|----------------|------------------|
   | Record/Elements/GPID | Global Person ID | CompoundEmployee/person/person_id_external | Employee identification |
   | Record/Elements/First Name | Employee first name | CompoundEmployee/person/personal_information/first_name | Employee identification |
   ```

4. **Property Lists:** When listing multiple properties, use organized bullet points:
   ```
   **Business Rule Errors:**
   - RPT_INT_ALL_BRULE_ERR_CNT: Error count for business rule violations
   - RPT_INT_ALL_BRULE_WRN_CNT: Warning count for business rule issues
   - RPT_INT_ALL_BRULE_SKP_CNT: Skip count for business rule processing
   ```

5. **Dense Property Sections:** When documenting error property categories, use structured tables instead of dense lists:
   ```
   **Before (Poor Formatting):**
   - **Business Rule Errors:** RPT_INT_ALL_BRULE_ERR_CNT, RPT_INT_ALL_BRULE_WRN_CNT, RPT_INT_ALL_BRULE_SKP_CNT
   - **Cleanse Errors:** RPT_INT_ALL_CLNS_ERR_CNT, RPT_INT_ALL_CLNS_WRN_CNT, RPT_INT_ALL_CLNS_SKP_CNT
   
   **After (Improved Formatting):**
   | Category | Property Names | Description |
   |----------|----------------|-------------|
   | Business Rule Errors | RPT_INT_ALL_BRULE_ERR_CNT, RPT_INT_ALL_BRULE_WRN_CNT, RPT_INT_ALL_BRULE_SKP_CNT | Error tracking for business rule violations |
   | Cleanse Errors | RPT_INT_ALL_CLNS_ERR_CNT, RPT_INT_ALL_CLNS_WRN_CNT, RPT_INT_ALL_CLNS_SKP_CNT | Data cleansing error tracking |
   ```

6. **Input/Output Profile Sections:** Use structured tables for field mappings instead of continuous text:
   ```
   **Before (Poor Formatting):**
   Record/Elements/GPID: Global Person ID - Record/Elements/First Name: Employee first name - Record/Elements/Last Name: Employee last name
   
   **After (Improved Formatting):**
   | Target Field | Description | Source Mapping | Business Purpose |
   |--------------|-------------|----------------|------------------|
   | Record/Elements/GPID | Global Person ID | CompoundEmployee/person/person_id_external | Employee identification |
   | Record/Elements/First Name | Employee first name | CompoundEmployee/person/personal_information/first_name | Employee identification |
   | Record/Elements/Last Name | Employee last name | CompoundEmployee/person/personal_information/last_name | Employee identification |
   ```

7. **Specific Formatting Examples for Common Sections:**
   
   **Error Property Categories (Improved):**
   ```
   | Category | Property Names | Description |
   |----------|----------------|-------------|
   | Business Rule Errors | RPT_INT_ALL_BRULE_ERR_CNT, RPT_INT_ALL_BRULE_WRN_CNT, RPT_INT_ALL_BRULE_SKP_CNT | Error tracking for business rule violations |
   | Cleanse Errors | RPT_INT_ALL_CLNS_ERR_CNT, RPT_INT_ALL_CLNS_WRN_CNT, RPT_INT_ALL_CLNS_SKP_CNT | Data cleansing error tracking |
   | Decision Errors | RPT_INT_ALL_DCN_ERR_CNT, RPT_INT_ALL_DCN_WRN_CNT, RPT_INT_ALL_DCN_SKP_CNT | Decision point error tracking |
   | Route Errors | RPT_INT_ALL_ROUTE_ERR_CNT, RPT_INT_ALL_ROUTE_WRN_CNT, RPT_INT_ALL_ROUTE_SKP_CNT | Routing error tracking |
   | TryCatch Errors | RPT_INT_ALL_TRYCATCH_ERR_CNT, RPT_INT_ALL_TRYCATCH_WRN_CNT, RPT_INT_ALL_TRYCATCH_SKP_CNT | Exception handling tracking |
   | Return Errors | RPT_INT_ALL_RETURN_ERR_CNT, RPT_INT_ALL_RETURN_WRN_CNT, RPT_INT_ALL_RETURN_SKP_CNT | Return value tracking |
   | General Errors | RPT_INT_ALL_ERR_CNT, RPT_INT_INTERFACE_START_TIME, RPT_INT_ALL_WRN_CNT | Overall error tracking |
   ```
   
   **Input Profile (Improved):**
   ```
   | Field Path | Description | Data Type | Business Purpose |
   |------------|-------------|-----------|------------------|
   | CompoundEmployee/person/person_id_external | Global Person ID | String | Unique employee identifier |
   | CompoundEmployee/person/employment_information/email_address | Corporate email address | String | Employee contact information |
   | CompoundEmployee/person/employment_information/employment_status | Employment status code | String | Current employment status |
   | CompoundEmployee/person/employment_information/employee_class | Employee classification | String | Employee role classification |
   | CompoundEmployee/person/employment_information/pay_grade | Pay grade level | String | Compensation hierarchy |
   | CompoundEmployee/person/employment_information/position | Position title | String | Job role description |
   | CompoundEmployee/person/employment_information/location | Location code | String | Work location identifier |
   | CompoundEmployee/person/employment_information/territory | Territory code | String | Geographic territory |
   ```
   
   **Output Profile (Improved):**
   ```
   | Target Field | Description | Source Mapping | Business Purpose |
   |--------------|-------------|----------------|------------------|
   | Record/Elements/GPID | Global Person ID | CompoundEmployee/person/person_id_external | Employee identification |
   | Record/Elements/First Name | Employee first name | CompoundEmployee/person/personal_information/first_name | Employee identification |
   | Record/Elements/Last Name | Employee last name | CompoundEmployee/person/personal_information/last_name | Employee identification |
   | Record/Elements/Email Address | Corporate email address | CompoundEmployee/person/employment_information/email_address | Employee contact information |
   | Record/Elements/emplStatus | Employment status description | CompoundEmployee/person/employment_information/employment_status | Employment status tracking |
   | Record/Elements/employee-class | Employee class description | CompoundEmployee/person/employment_information/employee_class | Employee role tracking |
   | Record/Elements/Country | Country name | CompoundEmployee/person/employment_information/location/country | Geographic information |
   | Record/Elements/Location | Location name | CompoundEmployee/person/employment_information/location/name | Work location information |
   | Record/Elements/Manager name | Manager full name | CompoundEmployee/person/employment_information/manager/name | Organizational hierarchy |
   | Record/Elements/Termination Date | Employment end date | CompoundEmployee/person/employment_information/termination_date | Employment history |
   | Record/Elements/Original Hire Date | First hire date | CompoundEmployee/person/employment_information/hire_date | Employment tenure |
   ```

    **Input Data Structure:**

    | Field Name | Data Type | Description |
    |------------|-----------|-------------|
    | [Clean field names] | [Data types] | [Business description] |

    **Output Data Structure:**

    | Field Name | Data Type | Description |
    |------------|-----------|-------------|
    | [Clean field names] | [Data types] | [Business description] |

    **Field Mappings:**

    | Source Field | Target Field | Data Type | Business Purpose |
    |--------------|--------------|-----------|------------------|
    | [Extract meaningful field names] | [Clean target field names] | [Proper data types] | [Clear business context] |

    **Data Flow:**

    - **Input:** [Source format and structure]
    - **Processing:** [Transformation logic applied]
    - **Output:** [Target format and structure]

    ---

    #### **Step 4: Connector Actions**

**Component Type:** [Connector Type] (Salesforce, HTTP, etc.)

**Purpose:** [Brief description of the external system interaction]

**Configuration Details:**

- **Connector Type:** [Specific connector (Salesforce, HTTP, etc.)]
- **Operation:** [Send, Get, Update, Delete, etc.]
- **Target Object:** [Specific object or endpoint]
- **Authentication:** [Authentication method used]
- **Error Handling:** [How errors are managed]

**Data Flow:**

- **Input:** [Data being sent to external system]
- **Processing:** [External system operation performed]
- **Output:** [Response or result from external system]

    ---

    #### **Step 5: Decision Points** *(if present)*

**Component Type:** Decision

**Purpose:** [Brief description of the decision logic]

**Configuration Details:**

- **Decision Criteria:** [What conditions are evaluated]
- **Branch Logic:** [How different paths are determined]
- **Routing Rules:** [Where data flows based on conditions]

**Data Flow:**

- **Input:** [Data being evaluated]
- **Processing:** [Decision logic applied]
- **Output:** [Routing decision and data direction]

---

#### **Step 6: End Events**

**Component Type:** End Event

**Purpose:** [Brief description of process completion]

**Configuration Details:**

- **Completion Type:** [Success, failure, or conditional completion]
- **Final Actions:** [Any cleanup or notification actions]
- **Continuation Settings:** [Whether process continues or stops]

**Data Flow:**

- **Input:** [Final processed data]
- **Processing:** [Completion actions performed]
- **Output:** [Process completion status and final results]

    ---

    **VISUAL ENHANCEMENT REQUIREMENTS:**
    - Use horizontal rules (---) to separate each step clearly
    - Use blockquotes (>) for component type headers for visual distinction
    - Include detailed Purpose sections explaining what each step accomplishes
    - Break Configuration into specific sub-categories for clarity
    - Provide comprehensive Data Flow sections with Input/Processing/Output
    - Use consistent formatting throughout all steps
    - Number steps clearly and maintain logical sequence
    - Use proper spacing and indentation for readability
    - Highlight important configuration details with bold formatting
    - Make technical details easily scannable with clear section headers
    - Keep formatting clean and professional
    - Include decision points and branching logic where applicable
    - Provide context for each transformation and connector action

    **CRITICAL: FIELD MAPPING TABLE FORMATTING:**
    - NEVER create single-line field mapping text that looks like: "Field Mappings: | Source Field | Target Field | Type | Notes | |--------------|--------------|------|-------| | 5 | IMPORT/Object..."
    - ALWAYS create proper multi-line markdown tables with each row on a separate line
    - ALWAYS extract meaningful field names instead of showing numbers or long XML paths
    - ALWAYS include proper table headers and separators

    **CRITICAL: INPUT/OUTPUT PROFILE FORMATTING:**
    - NEVER show long XML paths like "IMPORT/Object/I_PI_COMPANYDATA/Object/NAME"
    - ALWAYS extract clean field names like "CompanyName" or "Customer.Name"
    - Use structured tables for Input/Output data structures instead of bullet lists
    - Group related fields logically (e.g., Address fields together)
    - Include business-friendly descriptions instead of technical XML paths
    - Format profiles as clean, scannable tables with Field Name, Data Type, Description columns

    **ADDITIONAL FORMATTING GUIDELINES:**
    - Start each major section with a clear heading
    - Use bullet points for configuration details
    - Include code blocks for technical specifications
    - Add summary boxes for complex transformations
    - Use tables for structured data (field mappings, parameters)
    - Include visual separators between different component types

    PAY SPECIAL ATTENTION to these technical details:
    - Include ALL HTTP connector endpoints and parameters
    - Show ALL Boomi Map field mappings with exact fromKey/toKey relationships
    - Preserve ALL Document Property source value configurations
    - Maintain ALL connector parameter mappings and profile element references
    - Document ALL function steps in transformations

    ## Boomi Transformations Explained
    For each Map/Transform component in the Boomi process:
    1. Provide a brief explanation of what the transformation is doing in plain language
    2. Explain the input profile format and expected output profile format
    3. Detail ALL field mappings with their source and target paths
    4. Explain any function steps used (DocumentPropertyGet, etc.)
    5. Include ALL default values and constants
    6. Show the complete mapping configuration from the XML

    **FIELD MAPPINGS OUTPUT FORMAT:**
    For all field mappings, use structured tables instead of paragraph text. Use this EXACT format:

    **Field Mappings:**

    | Source Field | Target Field | Data Type | Business Purpose |
    |--------------|--------------|-----------|------------------|
    | Account.Name | Customer.CompanyName | String | Maps Salesforce account name to SAP customer company name |
    | Account.BillingStreet | Customer.Street | String | Maps billing address street to customer address |

    **CRITICAL REQUIREMENTS for field mapping tables:**
    - ALWAYS use the exact table format shown above with proper markdown table syntax
    - NEVER put field mappings in a single line or paragraph format
    - Use meaningful, readable field names (not XML paths or numbers)
    - Include clear business purpose in the last column
    - For complex XML paths, extract the meaningful field name (e.g., "CompanyName" instead of "IMPORT/Object/I_PI_COMPANYDATA/Object/NAME")
    - Use proper data types (String, Integer, Date, Boolean, etc.)
    - Each row must be on a separate line with proper pipe (|) separators
    - Include the table header exactly as shown
    - Add a blank line before and after the table

    **INPUT/OUTPUT PROFILE FORMAT:**
    For Input Profile and Output Profile descriptions, use structured format:

    **Input Profile:** [Profile name or description]
    - Field 1: Description and data type
    - Field 2: Description and data type

    **Output Profile:** [Profile name or description]
    - Field 1: Description and data type
    - Field 2: Description and data type

    Avoid long paragraph descriptions for profiles. Use bullet points for clarity.

    ## SAP Integration Suite Implementation
    ### Component Mapping

    This section provides a detailed mapping of Boomi components to their SAP Integration Suite equivalents, organized by subprocess for clear implementation guidance.

    Map each Boomi component to its SAP Integration Suite equivalent using this comprehensive mapping:

    **Core Boomi Components:**
    - Start Event (shapetype="start") → Start Message Event
    - Stop Event (shapetype="stop") → End Message Event
    - Connector Action (shapetype="connectoraction") → Request Reply with appropriate adapter
    - Map/Transform (shapetype="map") → Message Mapping or Groovy Script
    - Document Properties (shapetype="documentproperties") → Content Modifier (Set Properties)
    - Decision (shapetype="decision") → Router (Exclusive Gateway)
    - Branch → Parallel Gateway or Exclusive Gateway
    - Error Path → Exception Subprocess

    **Boomi Connector Types to SAP Adapters:**
    - connectorType="wss" (Web Services Server) → HTTPS Adapter (Receiver)
    - connectorType="http" → HTTPS Adapter (Sender)
    - connectorType="salesforce" → Salesforce Adapter or HTTPS Adapter
    - connectorType="sftp" → SFTP Adapter
    - connectorType="database" → JDBC Adapter
    - connectorType="odata" → OData Adapter

    **Mapping Components:**
    - Data Mapping → Message Mapping
    - XSLT Transform → XSLT Mapping
    - Operation Mapping → Operation Mapping

    **Processing Components:**
    - Content Enricher → Content Enricher (with lookup)
    - Filter → Filter
    - Script/Groovy → Groovy Script
    - XML Modifier → XML Modifier
    - Write Variables → Write Variables

    **Gateway Components:**
    - Parallel Processing → Sequential Multicast or Parallel Multicast
    - Join → Join (Parallel Gateway)
    - Exclusive Choice → Router (Exclusive Gateway)

    **Splitter Components:**
    - EDI Splitter → EDI Splitter
    - IDoc Splitter → IDoc Splitter
    - General Splitter → General Splitter

    **Storage Components:**
    - Database Select → Select (DB Storage)
    - Database Write → Write (DB Storage)
    - Database Get → Get (DB Storage)
    - Persist → Persist
    - ID Mapping → ID Mapping

    **Converter Components:**
    - JSON to XML → JSON to XML Converter
    - XML to CSV → XML to CSV Converter
    - CSV to XML → CSV to XML Converter
    - XML to JSON → XML to JSON Converter
    - Base64 Encode → Base64 Encoder
    - Base64 Decode → Base64 Decoder

    **Event Components:**
    - Timer/Scheduler → Timer Start Event
    - Error End → Error End Event
    - Process Call → Process Call

    **Aggregation Components:**
    - Aggregator → Aggregator
    - Gather → Gather

    **EDI Components:**
    - EDI Extractor → EDI Extractor
    - EDI Validator → EDI Validator

    **Adapter Components:**
    - OData Connector → OData Adapter
    - SFTP Connector → SFTP Adapter
    - SuccessFactors Connector → SuccessFactors Adapter
    - Salesforce Connector → Salesforce Adapter

    **COMPONENT MAPPING OUTPUT FORMAT:**
    Create structured tables for component mappings, organized by subprocess. Use this exact format:

    #### [Subprocess Name] Component Mapping
    | Boomi Component | SAP Integration Suite Equivalent | Purpose |
    |-----------------|----------------------------------|---------|
    | Component Name (shape reference) | SAP Equivalent | Clear description of what this component does |

    **Requirements for component mapping tables:**
    - Create separate tables for each subprocess (Main Process, Where Clause Sub-Process, Extract Data Sub-Process, etc.)
    - Include all three columns: Boomi Component, SAP Integration Suite Equivalent, Purpose
    - Preserve the same connection types and patterns
    - Provide clear, concise purpose descriptions for each component
    - Use consistent formatting and spacing
    - Include shape references from the original Boomi process where available

    ### Integration Flow Visualization

    IMPORTANT VISUALIZATION INSTRUCTIONS:
    1. Analyze the complexity of the flows first. If there are multiple complex flows with many endpoints, create separate diagrams. If the flows are simple or closely related, combine them into a single comprehensive diagram.
    2. Each diagram should have a clear, descriptive heading (e.g., "## Order Processing Flow Diagram" or "## Customer Data Integration Flow")
    3. For each diagram, provide a brief introduction explaining what the diagram represents
    4. Use your judgment to determine if multiple diagrams are needed - prefer fewer, more comprehensive diagrams when possible
    5. If you create multiple diagrams, ensure they are logically grouped and clearly labeled
    6. FOLLOW THE EXAMPLE DIAGRAM STRUCTURE PROVIDED BELOW - it shows the correct syntax and formatting

    Create a Mermaid diagram that accurately represents the flows, components, and connections found in the original Boomi process. The diagram should follow this format:
    **IMPORTANT**: Your model output must be *only* the Mermaid code block (```mermaid …```) with no shell prompts or extra text.
    Use real line breaks in labels (or `<br/>`), not `\n` literals.

    STUDY THE EXAMPLE DIAGRAM BELOW CAREFULLY - it shows the proper way to structure your diagram with correct syntax for nodes, connections, and styling.

    ```mermaid
    flowchart TD
    %% Define node styles for Boomi/SAP Integration Suite components
    classDef httpAdapter fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef contentModifier fill:#98FB98,stroke:#333,stroke-width:2px
    classDef mapping fill:#DDA0DD,stroke:#333,stroke-width:2px
    classDef adapter fill:#FFD700,stroke:#333,stroke-width:2px
    classDef event fill:#C0C0C0,stroke:#333,stroke-width:2px
    classDef errorHandler fill:#FFA07A,stroke:#333,stroke-width:2px

    %% Example Boomi diagram structure (use this as a reference)
    %% Start((Start)) --> StripeWebhook[HTTP Adapter: Stripe Webhook Receiver]:::httpAdapter
    %% StripeWebhook --> SetDynamicProps[Content Modifier: Set Dynamic Properties]:::contentModifier
    %% SetDynamicProps --> TransformData[Message Mapping: JSON to XML]:::mapping
    %% TransformData --> SalesforceCreate[Salesforce Adapter: Create Opportunity]:::adapter
    %% SalesforceCreate --> End((End)):::event

    %% %% Error Handling (if present in Boomi process)
    %% StripeWebhook -->|Error| ErrorHandler[(Exception Subprocess)]:::errorHandler
    %% ErrorHandler --> LogError[Write to Log: Error Details]:::contentModifier
    %% LogError --> ErrorEnd((Error End)):::event

    %% %% Document Properties Detail (if complex)
    %% subgraph DynamicProperties["Dynamic Properties Calculation"]
    %%     GetCustomer[HTTP GET: Customer Details]:::httpAdapter
    %%     GetProduct[HTTP GET: Product Details]:::httpAdapter
    %%     ConcatDescription[Concatenate: Customer + Product]:::contentModifier
    %%     CalcCloseDate[Calculate: Close Date - 3 months]:::contentModifier
    %% end

    %% YOUR ACTUAL DIAGRAM NODES AND CONNECTIONS GO HERE
    %% FOLLOW THE EXACT SEQUENCE FROM BOOMI XML DRAGPOINTS
    %% DO NOT INDENT THE FENCES — they must start at column 0

    ```

    %% Add styling based on component types
    class StripeWebhook,GetCustomer,GetProduct httpAdapter
    class SetDynamicProps,ConcatDescription,CalcCloseDate,LogError contentModifier
    class TransformData mapping
    class SalesforceCreate adapter
    class Start,End,ErrorEnd event
    class ErrorHandler errorHandler

    IMPORTANT MERMAID DIAGRAM RULES FOR BOOMI PROCESSES:
    1. Use TD (top-down) direction
    2. Include ALL style definitions exactly as shown above
    3. Group related flows with %% comments
    4. Use these exact node shapes:
       - ((name)) for Start/End events (Boomi Start/Stop shapes)
       - [name] for regular components (Connector Actions, Document Properties)
       - {"name"} for routers/decisions (IMPORTANT: use quotes inside the curly braces)
       - [(name)] for error handlers (Exception Subprocesses)
    5. Use these exact style classes based on Boomi component types:
       - :::httpAdapter for HTTP connectors, Web Services Server, OData adapters
       - :::contentModifier for Document Properties, Content Modifiers
       - :::mapping for Map/Transform components, Message Mappings
       - :::adapter for Salesforce, SFTP, Database connectors
       - :::event for Start/End events
       - :::errorHandler for error handling components
    6. Use -->|label| for labeled connections following Boomi dragpoint sequence
    7. Keep error handlers grouped together (if present in Boomi process)
    8. Maintain exact spacing and indentation as shown
    9. FOLLOW THE EXACT SEQUENCE from Boomi XML dragpoints (toShape attributes)
    10. Include ALL components from the Boomi process, even complex Document Properties
    11. For Document Properties with HTTP calls, show the external API interactions
    12. Use descriptive labels that reflect the actual Boomi component names and purposes

    ### Configuration Details
    For each component in the visualization, provide:
    - All required parameters
    - Default values
    - Placeholder values for missing configurations
    - Connection details between components

    ## Environment Configuration
    Provide a comprehensive breakdown of all configuration details:
    - Important configuration parameters (from source)
    - Environment variables (from source) with descriptions and example values
    - Dependencies on external systems (from source)
    - Security settings and certificates needed
    - Deployment considerations
    - Required resources (memory, CPU, etc.)

    ## API Reference
    Create a detailed API reference section that includes:
    - Complete list of all endpoints with their HTTP methods
    - Request and response schemas for each endpoint
    - Authentication requirements
    - Error codes and their meanings
    - Rate limiting information
    - Pagination details (if applicable)
    - Versioning information
    
    ### Query Parameters Formatting
         For API endpoints with query parameters, format them in organized tables with clear categorization:
     
     #### **Standard OData Parameters**
     | Parameter | Type | Required | Default | Description | Example Value |
     |-----------|------|----------|---------|-------------|---------------|
     | `$filter` | String | No | None | Dynamic WHERE clause with multiple criteria | See filtering examples below |
     | `$select` | String | No | All fields | Employee demographic field selection | `first_name,last_name,email` |
     | `$expand` | String | No | None | Related entity expansion | `PersonalInformation,Employment` |
     | `$top` | Integer | No | 1000 | Maximum number of records to return | `500` |
     | `$skip` | Integer | No | 0 | Number of records to skip for pagination | `1000` |
     | `$orderby` | String | No | None | Sort order for results | `last_modified_on desc` |
     | `$format` | String | No | JSON | Response format specification | `json` |
     
     #### **SuccessFactors-Specific Parameters**
     | Parameter | Type | Required | Description | Example Value |
     |-----------|------|----------|-------------|---------------|
     | `$filter` | String | No | Complex filtering with SuccessFactors syntax | See detailed examples below |
     | `$select` | String | No | Field selection for performance optimization | `person_id_external,first_name,last_name` |
     | `$expand` | String | No | Related entity expansion for nested data | `employment_information,personal_information` |
     
     ### **Advanced Filtering Examples**
     For complex filtering parameters like SuccessFactors `$filter`, organize them clearly with business context:
     
     #### **Entity-Based Filtering**
     | Filter Type | Filter Expression | Business Purpose | Example Values |
     |-------------|-------------------|------------------|----------------|
     | **Legal Entity** | `legal_entity_code in ('entity1','entity2')` | Filter by organizational structure | `'PEP01','PEP02','PEP03'` |
     | **Employee Class** | `employee_class in ('class1','class2')` | Filter by employee role/level | `'REG','CON','TEMP'` |
     | **Territory** | `company_territory_code in ('territory1','territory2')` | Filter by geographic region | `'US','CA','MX'` |
     | **Employment Status** | `employment_status eq 'A'` | Filter active employees only | `'A' (Active), 'T' (Terminated)` |
     
     #### **Date-Based Filtering**
     | Filter Type | Filter Expression | Business Purpose | Example Values |
     |-------------|-------------------|------------------|----------------|
     | **Last Modified** | `last_modified_on gt datetime'2024-01-01T00:00:00'` | Delta processing since last run | `2024-01-01T00:00:00` |
     | **End Date Range** | `end_date ge datetime'2024-01-01' and end_date le datetime'2024-12-31'` | Fiscal year filtering | `2024-01-01 to 2024-12-31` |
     | **Hire Date** | `hire_date ge datetime'2020-01-01'` | New employee filtering | `2020-01-01` |
     | **Termination Date** | `termination_date ne null` | Recently terminated employees | `null` (not terminated) |
     
     #### **Complex Filter Combinations**
     | Business Scenario | Filter Expression | Description |
     |-------------------|-------------------|-------------|
     | **Active US Employees** | `employment_status eq 'A' and company_territory_code eq 'US'` | Filter active employees in US territory |
     | **Recent Changes** | `last_modified_on gt datetime'2024-01-01T00:00:00' and (employment_status eq 'A' or employment_status eq 'T')` | Recent employment status changes |
     | **Specific Departments** | `employee_class in ('REG','CON') and legal_entity_code eq 'PEP01'` | Regular and contract employees in specific entity |
     
     #### **Performance Optimization Tips**
     | Optimization | Description | Example |
     |--------------|-------------|---------|
     | **Field Selection** | Use `$select` to limit returned fields | `$select=person_id_external,first_name,last_name,email` |
     | **Pagination** | Use `$top` and `$skip` for large datasets | `$top=500&$skip=1000` |
     | **Sorting** | Use `$orderby` for consistent data ordering | `$orderby=last_modified_on desc` |
     | **Expansion Control** | Limit `$expand` to required entities only | `$expand=employment_information($select=employee_class,status)` |

    Make sure the final document has:
    1. A descriptive title that reflects the purpose of the Boomi integration
    2. A comprehensive table of contents with hyperlinks to all sections
    3. Clear headings and subheadings for all sections
    4. Properly labeled Mermaid diagrams with descriptive headings that render correctly in HTML
    5. Complete process details including all Boomi components, configurations, and connections
    6. Detailed environment configuration information
    7. Accurate sequence of events based on Boomi XML dragpoint analysis
    8. All HTTP connector endpoints and parameters from Document Properties
    9. Complete field mappings from Boomi Map components
    10. All external system dependencies and API calls

    CRITICAL FINAL REMINDERS:
    - This is a DELL BOOMI process - use Boomi-specific terminology throughout
    - Analyze the XML structure thoroughly to capture ALL technical details
    - Maintain the exact sequence of operations as defined in the Boomi process
    - Include ALL Document Properties calculations and HTTP connector calls
    - Preserve ALL field mappings and transformation logic
    - Ensure Mermaid diagrams follow the exact component flow from the XML"""

        # Try to enhance with selected service
        enhanced_content = None
        if self.selected_service == 'openai':
            enhanced_content = self.enhance_with_openai(prompt)
            if enhanced_content:
                logger.info("Enhancement with OpenAI was successful")
                enhancement_successful = True
            else:
                logger.warning("Enhancement with OpenAI failed")

        elif self.selected_service in ['anthropic', 'claude']:  # Accept both names for compatibility
            enhanced_content = self.enhance_with_anthropic(prompt)
            if enhanced_content:
                logger.info("Enhancement with Anthropic was successful")
                enhancement_successful = True
            else:
                logger.warning("Enhancement with Anthropic failed")

        # Return enhanced content or original if enhancement fails
        if not enhancement_successful:
            logger.warning("LLM enhancement was not successful. Returning original documentation.")
            final_content = base_documentation
        else:
            final_content = enhanced_content

        # Validate and fix Mermaid diagrams
        try:
            # First try basic validation
            final_content = validate_mermaid_in_documentation(final_content)
            logger.info("Basic Mermaid diagram validation completed")

            # If basic validation doesn't work well, try LLM fixing
            if "```mermaid" in final_content:
                logger.info("Attempting LLM-powered Mermaid fixing for better results")
                final_content = fix_documentation_with_llm(final_content)
                logger.info("LLM Mermaid fixing completed")

        except Exception as e:
            logger.warning(f"Mermaid validation failed: {e}")
            # Try LLM fixing as fallback
            try:
                logger.info("Attempting LLM Mermaid fixing as fallback")
                final_content = fix_documentation_with_llm(final_content)
                logger.info("LLM Mermaid fixing fallback completed")
            except Exception as llm_e:
                logger.warning(f"LLM Mermaid fixing also failed: {llm_e}")

        # Normalize markdown tables and improve overall UX (Table of Contents)
        try:
            final_content = self._fix_table_formatting(final_content)
            final_content = self._ensure_table_of_contents(final_content)
        except Exception as e:
            logger.warning(f"Post-processing (tables/ToC) failed: {e}")

        # Generate JSON components if requested
        if generate_json and output_dir and enhancement_successful:
            try:
                self._generate_json_components(final_content, output_dir)
            except Exception as e:
                logger.warning(f"Failed to generate JSON components: {e}")

        return final_content

    def _fix_table_formatting(self, text: str) -> str:
        """Convert markdown tables that were wrapped in code fences into real tables.

        Many LLMs emit markdown tables inside triple backticks, which render as code blocks
        (showing pipes and dashed lines) instead of real tables. This removes the fences for
        blocks that look like tables, while preserving legitimate code blocks (mermaid, json,
        xml, groovy, bash, etc.).
        """
        if not text or "```" not in text:
            return text

        # Match fenced code blocks: ```lang\n...\n```
        fence_pattern = re.compile(r"```([a-zA-Z0-9_-]*)\n([\s\S]*?)\n```", re.MULTILINE)

        def is_table_block(lang: str, body: str) -> bool:
            # Never touch known code languages
            protected_langs = {"mermaid", "json", "xml", "yaml", "yml", "groovy", "java", "python", "bash", "sh", "sql", "javascript", "typescript"}
            if lang in protected_langs:
                return False
            # Heuristic: at least two lines start with '|' and there's a header separator row with dashes
            lines = [ln.rstrip() for ln in body.splitlines() if ln.strip()]
            pipe_lines = [ln for ln in lines if ln.strip().startswith('|') and ln.strip().endswith('|')]
            if len(pipe_lines) < 2:
                return False
            has_header = any(('---' in ln or ':-' in ln or '-:' in ln) and ln.strip().startswith('|') for ln in pipe_lines)
            return has_header

        def replacer(match: re.Match) -> str:
            lang = (match.group(1) or '').strip().lower()
            body = match.group(2)
            if is_table_block(lang, body):
                # Ensure a blank line before and after the table for proper rendering
                cleaned = body.strip("\n")
                return f"\n{cleaned}\n"
            return match.group(0)

        return fence_pattern.sub(replacer, text)

    def _ensure_table_of_contents(self, text: str) -> str:
        """Insert a simple Markdown Table of Contents after the H1 if not present."""
        if not text:
            return text
        if "## Table of Contents" in text:
            return text

        lines = text.splitlines()
        # Find first H1
        insert_idx = 0
        for i, ln in enumerate(lines[:50]):  # search near the top
            if ln.startswith('# '):
                insert_idx = i + 1
                break

        # Collect headings for ToC
        toc_items = []
        for ln in lines:
            if ln.startswith('## '):
                title = ln[3:].strip()
                anchor = re.sub(r"[^a-z0-9 -]", '', title.lower())
                anchor = anchor.replace(' ', '-')
                toc_items.append(f"- [{title}](#{anchor})")
            elif ln.startswith('### '):
                title = ln[4:].strip()
                anchor = re.sub(r"[^a-z0-9 -]", '', title.lower())
                anchor = anchor.replace(' ', '-')
                toc_items.append(f"  - [{title}](#{anchor})")

        if not toc_items:
            return text

        toc_block = ["", "## Table of Contents", "", *toc_items, "", ""]
        return "\n".join(lines[:insert_idx] + toc_block + lines[insert_idx:])

    def enhance_with_openai(self, prompt: str) -> Optional[str]:
        """Enhance documentation using OpenAI.

        Args:
            prompt: Prompt for OpenAI

        Returns:
            Enhanced documentation or None if failed
        """
        if not self.openai_client:
            logger.warning("OpenAI client not available. Cannot enhance documentation.")
            return None

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Updated to latest GPT model
                messages=[
                    {"role": "system", "content": "You are an expert integration specialist helping convert Boomi processes to SAP Integration Suite."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=18000,
                timeout=600  # Set timeout to 600 seconds (increased from 300)
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error using OpenAI for enhancement: {str(e)}")
            return None

    def enhance_with_anthropic(self, prompt: str) -> Optional[str]:
        """Enhance documentation using Anthropic Claude.

        Args:
            prompt: Prompt for Claude

        Returns:
            Enhanced documentation or None if failed
        """
        if not self.anthropic_client:
            logger.error("Anthropic client not available. Cannot enhance documentation.")
            logger.error(f"API Key available: {bool(self.anthropic_api_key)}")
            logger.error(f"Anthropic module available: {bool(anthropic)}")
            return None

        try:
            # Log the API call attempt with prompt size
            logger.info(f"Starting Anthropic Claude API call with prompt size: {len(prompt)} characters")
            logger.info(f"Using model: claude-sonnet-4-20250514 with timeout: 600 seconds")
            logger.info(f"API Key (first 5 chars): {self.anthropic_api_key[:5]}...")

            import time
            start_time = time.time()

            try:
                # Use the Anthropic Messages API with the newer format
                response = self.anthropic_client.messages.create(
                    # model="claude-3-7-sonnet-20250219",  # Using the latest model
                    model="claude-sonnet-4-20250514",
                    max_tokens=20000,
                    # temperature=0.2,
                    temperature=1,
                    timeout=600,  # Set timeout to 600 seconds (increased from 300)
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                )
            except Exception as api_error:
                logger.error(f"Anthropic API call failed with error: {str(api_error)}")
                logger.error(f"Error type: {type(api_error).__name__}")

                # Try with a different model as fallback
                logger.info("Trying fallback to claude-sonnet-4-20250514 model with different settings...")
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=20000,
                        temperature=0.2,
                        timeout=600,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    )
                    logger.info("Fallback to claude-sonnet-4-20250514 model with different settings succeeded")
                except Exception as fallback_error:
                    logger.error(f"Fallback API call also failed: {str(fallback_error)}")
                    raise fallback_error

            elapsed_time = time.time() - start_time
            logger.info(f"Anthropic API call completed in {elapsed_time:.2f} seconds")

            # Get the content from the response - extract text from the first content item
            if hasattr(response, 'content') and len(response.content) > 0:
                # Check if content is a list with text items
                for item in response.content:
                    if hasattr(item, 'text'):
                        logger.info(f"Successfully extracted content from response, length: {len(item.text)} characters")
                        return item.text

                # Fallback for other response structures
                logger.warning("Unexpected response structure. Attempting to extract text directly.")
                if hasattr(response.content[0], 'text'):
                    logger.info(f"Extracted text directly from content[0], length: {len(response.content[0].text)} characters")
                    return response.content[0].text

                # Try to extract content as a string if it's not an object with a text attribute
                logger.warning("Could not find text attribute. Trying to convert content to string.")
                try:
                    content_str = str(response.content[0])
                    logger.info(f"Converted content to string, length: {len(content_str)} characters")
                    return content_str
                except Exception as str_error:
                    logger.error(f"Error converting content to string: {str(str_error)}")

            # Log the full response structure for debugging
            logger.warning("Could not extract text from Anthropic response")
            logger.warning(f"Response type: {type(response)}")
            logger.warning(f"Response attributes: {dir(response)}")
            logger.warning(f"Response content type: {type(response.content) if hasattr(response, 'content') else 'No content attribute'}")

            return None

        except Exception as e:
            logger.error(f"Error using Anthropic Claude for enhancement: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error traceback: {e.__traceback__}")
            return None

    def analyze_image_with_anthropic(self, prompt: str, image_data: str, mime_type: str) -> Optional[str]:
        """Analyze image using Anthropic Claude with vision capabilities.

        Args:
            prompt: Text prompt for image analysis
            image_data: Base64 encoded image data
            mime_type: MIME type of the image (e.g., 'image/png')

        Returns:
            Image analysis result or None if failed
        """
        if not self.anthropic_client:
            logger.error("Anthropic client not available. Cannot analyze image.")
            return None

        try:
            logger.info(f"Starting Anthropic vision analysis with image type: {mime_type}")

            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Vision-capable model
                max_tokens=1000,
                timeout=300,  # 5 minutes for image analysis
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": image_data
                                }
                            }
                        ]
                    }
                ]
            )

            logger.info("Anthropic vision analysis completed successfully")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error using Anthropic for image analysis: {str(e)}")
            return None

    def _generate_json_components(self, enhanced_documentation: str, output_dir: str):
        """Generate JSON components for iFlow generation from enhanced documentation."""
        try:
            import os
            import json
            from datetime import datetime

            # Create a JSON generation prompt
            json_prompt = f"""Based on the following Boomi documentation, generate a JSON structure that represents the SAP Integration Suite components needed for this integration.

CRITICAL ALIGNMENT WITH MERMAID DIAGRAM:
- Generate JSON that matches the complexity and subprocess structure shown in the Mermaid diagram
- Include NESTED subprocesses for complex business logic (e.g., "Where Clause Construction", "Employee Data Extraction")
- Use gateway components for decision routing with multiple branches
- Model PARALLEL processing flows with proper gateway splits and joins
- Include exception handling subprocesses for error flows

RESPONSE FORMAT:
- Respond with ONLY valid JSON in the exact format specified below. No explanations/markdown.
- Use ONLY these component types (lowercase exactly):
  content_modifier, content_enricher, json_to_xml, script, request_reply, odata, gateway, sftp, successfactors, subprocess, exception_subprocess, message_mapping
- Do NOT generate start_event or end_event components (they are added automatically).
- Do NOT include a "sequence" field; component array order dictates flow.
- Populate required config keys for each type as specified below.

{enhanced_documentation}

Generate JSON in this exact format:
{{
    "process_name": "Name of the integration process",
    "description": "Description of what this integration does",
    "endpoints": [
        {{
            "method": "HTTP method (GET, POST, etc.)",
            "path": "Endpoint path (e.g., /api/orders)",
            "purpose": "Purpose of this endpoint",
            "components": [
                {{
                    "type": "One of: content_modifier | content_enricher | json_to_xml | script | request_reply | odata | gateway | sftp | successfactors | subprocess | exception_subprocess | message_mapping",
                    "name": "Component name",
                    "id": "Unique component ID",
                    "config": {{
                        "content": "For content_modifier (string)",
                        "body_type": "For content_modifier/content_enricher (expression|constant)",
                        "header_table": "For content_enricher (optional)",
                        "script": "For script (Groovy content)",
                        "script_type": "For script (default: groovy)",
                        "method": "For request_reply (GET|POST|...)",
                        "url": "For request_reply (full URL)",
                        "operation": "For odata or successfactors (e.g., Query(GET))",
                        "service_url": "For odata (base service URL)",
                        "entity_set": "For odata (entity set/resource path)",
                        "host": "For sftp",
                        "port": "For sftp (default: 22)",
                        "path": "For sftp (remote directory)",
                        "username": "For sftp",
                        "auth_type": "For sftp (Password|Key)",
                        "operation_sftp": "For sftp operation (PUT|GET)",
                        "auth_method": "For successfactors (e.g., OAuth)",
                        "url_sf": "For successfactors (full OData URL)",
                        "branches": [{"to": "component_id", "condition": "${property.value == 'condition'}"}],
                        "components": "For subprocess/exception_subprocess: array of nested components in execution order",
                        "source_format": "For message_mapping (JSON|XML|CSV)",
                        "target_format": "For message_mapping (JSON|XML|CSV)",
                        "mapping_logic": "For message_mapping (transformation description)",
                        "mapping_name": "For message_mapping (name of mapping bundle)",
                        "source_schema": "For message_mapping (source XSD filename)",
                        "target_schema": "For message_mapping (target XSD filename)"
                    }}
                }}
            ]
        }}
    ]
}}

STRICT REQUIREMENTS:
- Use lowercase type names exactly as listed.
- Include only the config keys relevant to the component type.
- For subprocess and exception_subprocess, include a "components" array of nested components using the same schema (one nesting level only).
- Do not include unknown component types or empty components.

COMPLEX FLOW MODELING (match Mermaid diagram complexity):
- Use "gateway" components with "branches" config for decision routing (Router, Parallel Gateway, Join Gateway)
- Create subprocess components for reusable business logic with descriptive names
- Model error handling with exception_subprocess components
- Use multiple endpoints if the integration has different processing paths
- For parallel processing, use gateway with multiple branches followed by a join gateway
- Ensure subprocess components contain their own complete component flows

SUBPROCESS EXAMPLES TO INCLUDE:
- "Where Clause Construction" subprocess for dynamic query building
- "Employee Data Extraction" subprocess for SuccessFactors data retrieval
- "Error Processing" exception_subprocess for error handling flows
- Gateway splits for parallel processing (Delta vs Full, Send to Vendor decision)

RESPOND WITH ONLY JSON:"""

            # Generate JSON using enhanced logic with validation and retry
            components = self._generate_json_with_validation(json_prompt, output_dir)

            if components:
                # Apply the same enhancements as iFlow generation
                components = self._generate_transformation_scripts(components)
                components = self._create_intelligent_connections(components)

                # Save the enhanced JSON to file
                os.makedirs(output_dir, exist_ok=True)
                json_file = os.path.join(output_dir, "iflow_components.json")

                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(components, f, indent=2)

                logger.info(f"✅ Generated enhanced JSON components file: {json_file}")

                # Also save metadata
                metadata = {
                    "generated_at": datetime.now().isoformat(),
                    "source": "documentation_enhancer",
                    "llm_service": self.selected_service,
                    "documentation_length": len(enhanced_documentation),
                    "components_count": len(components.get("endpoints", [])),
                    "has_transformations": len(components.get("endpoints", [{}])[0].get("transformations", [])) > 0 if components.get("endpoints") else False,
                    "has_intelligent_connections": "sequence_flows" in str(components)
                }

                metadata_file = os.path.join(output_dir, "generation_metadata.json")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)

                logger.info(f"✅ Generated metadata file: {metadata_file}")
            else:
                logger.warning("Failed to generate JSON components")

        except Exception as e:
            logger.error(f"Error generating JSON components: {e}")
            raise

    def _generate_json_with_validation(self, json_prompt: str, output_dir: str, max_retries: int = 3):
        """Generate JSON with validation and retry logic."""
        import json

        for attempt in range(max_retries):
            try:
                logger.info(f"JSON generation attempt {attempt + 1}/{max_retries}")

                # Generate JSON response
                json_response = None
                if self.selected_service == 'anthropic' and self.anthropic_client:
                    json_response = self._call_anthropic_for_json(json_prompt)
                elif self.selected_service == 'openai' and self.openai_client:
                    json_response = self._call_openai_for_json(json_prompt)

                if not json_response:
                    logger.warning(f"Attempt {attempt + 1}: No response from LLM")
                    continue

                # Save debug response
                debug_dir = os.path.join(output_dir, "debug")
                os.makedirs(debug_dir, exist_ok=True)
                debug_file = os.path.join(debug_dir, f"json_response_attempt_{attempt + 1}.txt")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(json_response)

                # Validate JSON
                is_valid, message = self._validate_json_response(json_response)
                if not is_valid:
                    logger.warning(f"Attempt {attempt + 1}: Invalid JSON - {message}")
                    continue

                # Parse JSON
                try:
                    components = json.loads(json_response)
                except json.JSONDecodeError as e:
                    logger.warning(f"Attempt {attempt + 1}: JSON decode error - {e}")
                    continue

                # Check for meaningful content
                if not self._has_meaningful_components(components):
                    logger.warning(f"Attempt {attempt + 1}: Components lack meaningful content")
                    continue

                logger.info(f"✅ Successfully generated valid JSON on attempt {attempt + 1}")
                return components

            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Error - {e}")
                continue

        logger.error(f"Failed to generate valid JSON after {max_retries} attempts")
        return None

    def _call_anthropic_for_json(self, prompt: str) -> str:
        """Call Anthropic API specifically for JSON generation."""
        try:
            response = self.anthropic_client.messages.create(
                # model="claude-3-7-sonnet-20250219",
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                temperature=1,  # Lower temperature for more consistent JSON
                timeout=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            # Extract text from response
            if hasattr(response, 'content') and len(response.content) > 0:
                for item in response.content:
                    if hasattr(item, 'text'):
                        return item.text

            return None

        except Exception as e:
            logger.error(f"Error calling Anthropic for JSON: {e}")
            return None

    def _call_openai_for_json(self, prompt: str) -> str:
        """Call OpenAI API specifically for JSON generation."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at converting Boomi processes to SAP Integration Suite JSON configurations. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent JSON
                max_tokens=8000,
                timeout=300
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling OpenAI for JSON: {e}")
            return None

    def _validate_json_response(self, response: str):
        """Validate JSON response format."""
        try:
            import json
            import re

            # Try to extract JSON from response
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Look for JSON structure
                start_brace = response.find('{')
                end_brace = response.rfind('}')
                if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                    json_str = response[start_brace:end_brace + 1]
                else:
                    json_str = response.strip()

            # Parse JSON
            parsed_json = json.loads(json_str)

            # Check structure
            if not isinstance(parsed_json, dict):
                return False, "Response is not a JSON object"

            if "endpoints" not in parsed_json:
                return False, "Missing required 'endpoints' field"

            return True, "Valid JSON response"

        except Exception as e:
            return False, f"JSON validation error: {e}"

    def _has_meaningful_components(self, components):
        """Check if components contain meaningful content."""
        if not isinstance(components, dict):
            return False

        endpoints = components.get("endpoints", [])
        if not endpoints:
            return False

        # Check if at least one endpoint has components (start/end are auto-added by converter)
        for endpoint in endpoints:
            endpoint_components = endpoint.get("components", [])
            if len(endpoint_components) >= 1:
                return True

        return False

    def _generate_transformation_scripts(self, components):
        """Generate transformation scripts for components."""
        try:
            if not isinstance(components, dict) or "endpoints" not in components:
                return components

            for endpoint in components["endpoints"]:
                endpoint_components = endpoint.get("components", [])
                transformations = []

                for component in endpoint_components:
                    if component.get("type") == "message_mapping":
                        # Generate transformation script
                        transformation = {
                            "id": f"transform_{component.get('id', 'unknown')}",
                            "type": "groovy_script",
                            "name": f"Transform for {component.get('name', 'Unknown')}",
                            "script": self._generate_groovy_script(component)
                        }
                        transformations.append(transformation)

                if transformations:
                    endpoint["transformations"] = transformations

            return components

        except Exception as e:
            logger.warning(f"Error generating transformation scripts: {e}")
            return components

    def _generate_groovy_script(self, component):
        """Generate a basic Groovy script for transformation."""
        return """
// Auto-generated transformation script
import com.sap.gateway.ip.core.customdev.util.Message;

def Message processData(Message message) {
    // Get message body
    def body = message.getBody(java.lang.String);

    // Transform data here
    // Add your transformation logic

    message.setBody(body);
    return message;
}
""".strip()

    def _create_intelligent_connections(self, components):
        """Create intelligent connections between components."""
        try:
            if not isinstance(components, dict) or "endpoints" not in components:
                return components

            for endpoint in components["endpoints"]:
                endpoint_components = endpoint.get("components", [])
                sequence_flows = []

                # Create connections based on component sequence
                for i in range(len(endpoint_components) - 1):
                    current_comp = endpoint_components[i]
                    next_comp = endpoint_components[i + 1]

                    flow = {
                        "from": current_comp.get("id"),
                        "to": next_comp.get("id"),
                        "condition": None
                    }
                    sequence_flows.append(flow)

                if sequence_flows:
                    endpoint["sequence_flows"] = sequence_flows

            return components

        except Exception as e:
            logger.warning(f"Error creating intelligent connections: {e}")
            return components

    def _detect_mulesoft_content(self, content: str) -> bool:
        """Detect if the content is MuleSoft-related"""
        mulesoft_indicators = [
            'mule-app', 'mule-config', 'http:listener', 'http:request',
            'transform', 'choice', 'scatter-gather', 'salesforce:',
            'dataweave', 'ee:transform', 'mule-artifact', 'flow name=',
            'sub-flow', 'error-handler', 'apikit:', 'vm:', 'jms:'
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in mulesoft_indicators)

    def _create_mulesoft_enhancement_prompt(self, base_documentation: str) -> str:
        """Create MuleSoft-specific enhancement prompt"""
        return f"""You are a MuleSoft and SAP Integration Suite specialist. Based on the following MuleSoft technical
    documentation, create comprehensive documentation that includes API details, flow logic,
    and detailed SAP Integration Suite visualization. Use SAP Integration Suite components and connections for
    the visualization.

    Transform this MuleSoft documentation into a comprehensive guide that shows:
    1. How MuleSoft components map to SAP Integration Suite equivalents
    2. Complete API reference with tabular format
    3. Proper Mermaid diagrams that render correctly
    4. Detailed flow analysis and component mappings

    Here is the source MuleSoft documentation:

    {base_documentation}

    Please structure your response in Markdown with these sections:

    # [Descriptive Title Based on the MuleSoft Application Purpose]

    ## Table of Contents
    Create a detailed table of contents with hyperlinks to all sections and subsections in the document. Use Markdown link syntax like [Section Name](#section-name) to create clickable links to each section. Include ALL sections and subsections.

    ## API Overview
    - Comprehensive description of what this MuleSoft application does and its business purpose
    - Base URL/endpoint pattern from HTTP listeners
    - Authentication mechanisms used in the flows
    - Rate limiting information (if available)
    - General response format and content types

    ## MuleSoft to SAP Integration Suite Component Mapping
    Create a detailed table showing how each MuleSoft component maps to SAP Integration Suite:

    | MuleSoft Component | SAP Integration Suite Equivalent | Purpose | Configuration Notes |
    |-------------------|----------------------------------|---------|-------------------|
    | HTTP Listener | HTTPS Sender Adapter | Receives HTTP requests | Maps to inbound endpoint |
    | HTTP Request | HTTP Receiver Adapter | Makes HTTP calls | Maps to outbound calls |
    | Transform Message | Groovy Script | Data transformation | DataWeave → Groovy conversion |
    | Choice Router | Router (Exclusive Gateway) | Conditional routing | When/otherwise logic |
    | Scatter-Gather | Multicast | Parallel processing | Concurrent execution |
    | Salesforce Connector | OData Request-Reply | Salesforce integration | Maps to OData operations |
    | Error Handler | Exception Subprocess | Error handling | Try-catch equivalent |

    ## API Reference
    Create a comprehensive API reference in tabular format:

    ### Endpoints
    | Method | Path | Description | Request Body | Response | Authentication |
    |--------|------|-------------|--------------|----------|----------------|
    | GET | /api/customers | Retrieve customer list | None | Customer array | Bearer token |
    | POST | /api/customers | Create new customer | Customer object | Created customer | Bearer token |
    | PUT | /api/customers/{{id}} | Update customer | Customer object | Updated customer | Bearer token |
    | DELETE | /api/customers/{{id}} | Delete customer | None | Success message | Bearer token |
    
    ### Query Parameters
    For endpoints with query parameters, format them in organized tables:
    
    | Parameter | Type | Required | Description | Example |
    |-----------|------|----------|-------------|---------|
    | limit | Integer | No | Maximum number of records to return | 100 |
    | offset | Integer | No | Number of records to skip | 0 |
    | sort | String | No | Sort field and direction | name:asc |
    | filter | String | No | Filter criteria | status='active' |
    
    ### Complex Filter Examples
    For complex filtering parameters, organize them clearly with code blocks:
    
    **Date Range Filtering:**
    ```
    startDate=2023-01-01&endDate=2023-12-31
    ```
    
    **Status Filtering:**
    ```
    status in ('active','pending')
    ```
    
    **Multi-field Filtering:**
    ```
    category=electronics AND price>100
    ```

    ### Request/Response Schemas
    #### Customer Object
    | Field | Type | Required | Description | Example |
    |-------|------|----------|-------------|---------|
    | id | String | No | Unique identifier | "12345" |
    | name | String | Yes | Customer name | "John Doe" |
    | email | String | Yes | Email address | "john@example.com" |
    | phone | String | No | Phone number | "+1-555-0123" |

    ### Error Codes
    | Code | Message | Description | Resolution |
    |------|---------|-------------|------------|
    | 400 | Bad Request | Invalid request format | Check request syntax |
    | 401 | Unauthorized | Missing/invalid auth | Provide valid token |
    | 404 | Not Found | Resource not found | Check resource ID |
    | 500 | Internal Error | Server error | Contact support |

    ## Flow Analysis
    Provide detailed analysis of each MuleSoft flow:

    ### Main Flow: [Flow Name]
    - **Purpose**: What this flow accomplishes
    - **Trigger**: How the flow is initiated (HTTP listener, scheduler, etc.)
    - **Components**: List all components in execution order
    - **Data Transformation**: Describe any DataWeave transformations
    - **External Integrations**: List external systems called
    - **Error Handling**: Describe error handling strategy

    ## Mermaid Flow Diagram
    Create a Mermaid diagram that accurately represents the MuleSoft flows and their SAP Integration Suite equivalents:

    **CRITICAL MERMAID REQUIREMENTS:**
    1. Use `flowchart TD` (top-down direction)
    2. Include ALL style definitions for proper rendering
    3. Use proper node shapes for different component types
    4. Follow exact syntax for connections and labels
    5. Include error handling flows if present

    ```mermaid
    flowchart TD
    %% Define node styles for MuleSoft/SAP Integration Suite components
    classDef httpListener fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef httpRequest fill:#98FB98,stroke:#333,stroke-width:2px
    classDef transform fill:#DDA0DD,stroke:#333,stroke-width:2px
    classDef choice fill:#FFD700,stroke:#333,stroke-width:2px
    classDef salesforce fill:#FF6347,stroke:#333,stroke-width:2px
    classDef event fill:#C0C0C0,stroke:#333,stroke-width:2px
    classDef errorHandler fill:#FFA07A,stroke:#333,stroke-width:2px

    %% MuleSoft Flow Components
    Start((Start)):::event
    HTTPListener[HTTP Listener: /api/customers]:::httpListener
    ValidateInput[Transform: Validate Input]:::transform
    ChoiceRouter{{"Customer Type?"}}:::choice
    PremiumFlow[HTTP Request: Premium Service]:::httpRequest
    StandardFlow[HTTP Request: Standard Service]:::httpRequest
    SalesforceCreate[Salesforce: Create Record]:::salesforce
    ResponseTransform[Transform: Format Response]:::transform
    End((End)):::event

    %% Error Handling
    ErrorHandler[(Error Handler)]:::errorHandler
    LogError[Transform: Log Error]:::transform
    ErrorResponse[Transform: Error Response]:::transform
    ErrorEnd((Error End)):::event

    %% Main Flow Connections
    Start --> HTTPListener
    HTTPListener --> ValidateInput
    ValidateInput --> ChoiceRouter
    ChoiceRouter -->|Premium| PremiumFlow
    ChoiceRouter -->|Standard| StandardFlow
    PremiumFlow --> SalesforceCreate
    StandardFlow --> SalesforceCreate
    SalesforceCreate --> ResponseTransform
    ResponseTransform --> End

    %% Error Flow Connections
    HTTPListener -->|Error| ErrorHandler
    ValidateInput -->|Error| ErrorHandler
    SalesforceCreate -->|Error| ErrorHandler
    ErrorHandler --> LogError
    LogError --> ErrorResponse
    ErrorResponse --> ErrorEnd
    ```

    **MERMAID DIAGRAM RULES FOR MULESOFT:**
    1. Use TD (top-down) direction
    2. Include ALL style definitions exactly as shown above
    3. Use these exact node shapes:
       - ((name)) for Start/End events
       - [name] for regular components (HTTP Listener, Transform, etc.)
       - {{"name"}} for choice routers (IMPORTANT: use quotes inside double curly braces)
       - [(name)] for error handlers
    4. Use these style classes based on MuleSoft component types:
       - :::httpListener for HTTP Listeners
       - :::httpRequest for HTTP Requests
       - :::transform for Transform Message, DataWeave
       - :::choice for Choice routers
       - :::salesforce for Salesforce connectors
       - :::event for Start/End events
       - :::errorHandler for error handling components
    5. Use -->|label| for labeled connections
    6. Group error handlers separately
    7. Follow the exact sequence from MuleSoft flow execution

    ## Technical Implementation Details
    - Configuration properties and their purposes
    - Environment-specific settings
    - Security configurations
    - Performance considerations
    - Monitoring and logging setup

    ## Migration Considerations
    - Key differences between MuleSoft and SAP Integration Suite
    - Required configuration changes
    - Data format considerations
    - Authentication mapping
    - Error handling strategy changes

    Make sure the final document has:
    1. A descriptive title that reflects the purpose of the MuleSoft application
    2. A comprehensive table of contents with hyperlinks to all sections
    3. Clear headings and subheadings for all sections
    4. Properly formatted tables for API reference and component mappings
    5. A working Mermaid diagram that renders correctly in HTML
    6. Complete flow analysis with technical details
    7. Practical migration guidance for SAP Integration Suite

    CRITICAL FINAL REMINDERS:
    - This is a MULESOFT application - use MuleSoft-specific terminology throughout
    - Create tables for API references, component mappings, and schemas
    - Ensure Mermaid diagrams follow the exact syntax and styling shown
    - Include comprehensive error handling documentation
    - Provide practical SAP Integration Suite migration guidance"""