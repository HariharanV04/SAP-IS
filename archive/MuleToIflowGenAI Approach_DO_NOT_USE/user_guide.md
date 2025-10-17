# GenAI iFlow Generator: User Guide

## 1. Introduction

The GenAI iFlow Generator is a powerful tool that uses artificial intelligence to automatically convert MuleSoft API specifications into SAP Integration Suite iFlow configurations. This guide will help you understand how to use the tool effectively.

## 2. Prerequisites

Before using the GenAI iFlow Generator, ensure you have the following:

### 2.1 System Requirements
- Python 3.6 or higher
- Internet connection (for AI provider API calls)
- 100MB+ of free disk space

### 2.2 Required Python Packages
- For OpenAI integration: `pip install openai`
- For Claude integration: `pip install anthropic`

### 2.3 API Keys
- For OpenAI: Obtain an API key from [OpenAI Platform](https://platform.openai.com/)
- For Claude: Obtain an API key from [Anthropic Console](https://console.anthropic.com/)

## 3. Installation

1. Clone or download the GenAI iFlow Generator repository
2. Navigate to the project directory
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 4. Preparing Your Input

### 4.1 Markdown Format
The tool accepts API specifications in markdown format. The markdown should include:
- API overview and description
- Endpoint details (paths, methods, request/response formats)
- Data transformation logic
- Error handling information

### 4.2 Example Markdown Structure
```markdown
# API Overview
Description of the API and its purpose.

# Endpoints

## POST /resource
- **Purpose**: Create a new resource
- **Request Body**: JSON schema
- **Response**: 201 Created with resource details

## GET /resource/{id}
- **Purpose**: Retrieve a resource
- **Path Parameters**: id - The resource identifier
- **Response**: 200 OK with resource details

# Data Transformations
Description of data transformations used in the API.
```

## 5. Running the Tool

### 5.1 Basic Usage
```bash
python genai_iflow_generator.py --markdown <markdown_file> --output <output_path> --name <iflow_name> --provider <provider> --api-key <api_key>
```

### 5.2 Command-Line Arguments
- `--markdown`: Path to the markdown file containing the API specification (required)
- `--output`: Directory where the generated iFlow ZIP file will be saved (required)
- `--name`: Name of the generated iFlow (required)
- `--api-key`: API key for the AI provider (optional for local mode)
- `--model`: AI model to use (default: gpt-4 for OpenAI, claude-3-7-sonnet-20250219 for Claude)
- `--provider`: AI provider to use (openai, claude, or local)

### 5.3 Examples

#### Using OpenAI (GPT-4)
```bash
python genai_iflow_generator.py --markdown api_spec.md --output output_folder --name CustomerAPI --provider openai --api-key sk-your-openai-api-key
```

#### Using Claude
```bash
python genai_iflow_generator.py --markdown api_spec.md --output output_folder --name CustomerAPI --provider claude --api-key sk-your-claude-api-key
```

#### Using Local Mode (No API Key Required)
```bash
python genai_iflow_generator.py --markdown api_spec.md --output output_folder --name CustomerAPI --provider local
```

## 6. Understanding the Output

### 6.1 Output Structure
The tool generates a ZIP file containing all the necessary files for an SAP Integration Suite iFlow:
- Main iFlow configuration file (.iflw)
- Manifest file
- Project configuration files
- Parameter definitions
- Groovy scripts (if complex transformations are needed)

### 6.2 Generated Files
- `src/main/resources/scenarioflows/integrationflow/{iflow_name}.iflw`: Main iFlow configuration
- `META-INF/MANIFEST.MF`: Manifest file
- `.project`: Project configuration
- `.classpath`: Classpath configuration
- `src/main/resources/parameters.prop`: Parameters properties
- `src/main/resources/parameters.propdef`: Parameter definitions
- `src/main/resources/script/*.groovy`: Groovy scripts for complex transformations

## 7. Importing into SAP Integration Suite

1. Log in to your SAP Integration Suite tenant
2. Navigate to the "Design" section
3. Click "Import" and select the generated ZIP file
4. Follow the import wizard to complete the process
5. The imported iFlow will appear in your package

## 8. Customizing the Generated iFlow

After importing the iFlow, you may need to make some adjustments:
1. Review and update endpoint configurations
2. Configure security settings and credentials
3. Test the iFlow with sample data
4. Deploy the iFlow to make it active

## 9. Troubleshooting

### 9.1 Common Issues

#### API Key Issues
- **Error**: "Invalid API key"
- **Solution**: Verify your API key is correct and has not expired

#### Package Installation Issues
- **Error**: "Module not found"
- **Solution**: Ensure you've installed all required packages with `pip install`

#### Generation Issues
- **Error**: "Failed to parse JSON response"
- **Solution**: Try using a different AI provider or simplify your markdown input

### 9.2 Getting Help
If you encounter issues not covered in this guide:
1. Check the project's GitHub repository for known issues
2. Submit a detailed bug report including your input markdown and error messages
3. Contact the development team for support

## 10. Best Practices

### 10.1 Input Preparation
- Keep your markdown clear and well-structured
- Include detailed information about endpoints and data transformations
- Use consistent formatting throughout the document

### 10.2 AI Provider Selection
- OpenAI (GPT-4) generally provides the most detailed analysis
- Claude is a good alternative with similar capabilities
- Local mode is useful for testing but provides simplified results

### 10.3 Output Validation
- Always review the generated iFlow before deploying
- Pay special attention to data transformations and routing logic
- Test the iFlow with representative sample data

## 11. Conclusion

The GenAI iFlow Generator significantly accelerates the process of creating SAP Integration Suite iFlows from MuleSoft API specifications. By following this guide, you can leverage the power of AI to streamline your integration development process.

For more detailed technical information, please refer to the Technical Design Document.
