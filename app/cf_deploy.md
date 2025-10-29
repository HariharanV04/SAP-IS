# Deploying to Cloud Foundry

This guide provides instructions for deploying the MuleSoft Documentation Generator application to Cloud Foundry.

## Prerequisites

1. Cloud Foundry CLI installed
2. Access to a Cloud Foundry environment (SAP BTP, IBM Cloud, etc.)
3. Python 3.9 or higher

## Files for Deployment

The following files are essential for deployment:

1. **App Structure:**
   - `app.py` - Main Flask application
   - `run_app.py` - Entry point script
   - `requirements.txt` - Dependencies
   - `Procfile` - Specifies how to run the application
   - `runtime.txt` - Specifies Python version
   - `templates/` - HTML templates
   - `static/` - Static assets
   - `.env` - Environment variables (not included in deployment)

2. **Support Modules:**
   - `enhanced_doc_generator.py`
   - `additional_file_parser.py`
   - `use_anthropic.py`
   - Additional modules in the parent directory

## Deployment Steps

1. **Login to Cloud Foundry:**
   ```bash
   cf login -a <API_ENDPOINT>
   ```

2. **Navigate to the project directory:**
   ```bash
   cd path/to/mule_to_iflow
   ```

3. **Create necessary service instances (if required):**
   ```bash
   cf create-service <SERVICE> <PLAN> mulesoft-doc-db
   ```

4. **Deploy the application:**
   ```bash
   cf push
   ```

5. **Set environment variables (LLM API keys):**
   ```bash
   cf set-env mulesoft-documentation-generator ANTHROPIC_API_KEY your-api-key
   cf set-env mulesoft-documentation-generator OPENAI_API_KEY your-api-key
   cf restage mulesoft-documentation-generator
   ```

## Troubleshooting

1. **Application crashes on startup:**
   - Check logs: `cf logs mulesoft-documentation-generator --recent`
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **Missing modules or import errors:**
   - Check that all required modules are properly included in the deployment
   - Update the `sys.path.append()` statements in app.py if needed

3. **File permissions issues:**
   - Ensure uploads/ and results/ directories are writable
   - Use environment variables for file paths instead of hardcoded paths

## Monitoring

- View logs: `cf logs mulesoft-documentation-generator`
- Check app status: `cf app mulesoft-documentation-generator`
- Scale the app: `cf scale mulesoft-documentation-generator -i 2` (increases to 2 instances) 