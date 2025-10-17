# MuleToIS iFlow Generator API - Deployment Guide

## Overview

This API service generates SAP Integration Suite iFlows from MuleSoft documentation. It provides a REST API for generating iFlows from markdown content and optionally deploying them to SAP BTP Integration Suite.

## Core Components

- **app.py**: Main Flask application that handles API requests
- **iflow_generator_api.py**: Core module for generating iFlows from markdown
- **enhanced_genai_iflow_generator.py**: Enhanced iFlow generation using GenAI
- **sap_btp_integration.py**: Integration with SAP BTP for deployment

## Deployment to Cloud Foundry

### Prerequisites

1. Cloud Foundry CLI installed
2. Access to a Cloud Foundry environment (SAP BTP, IBM Cloud, etc.)
3. Python 3.9 or higher

### Required Files for Deployment

The following files are essential for deployment:

1. **Core Application Files:**
   - app.py
   - iflow_generator_api.py
   - enhanced_genai_iflow_generator.py
   - enhanced_iflow_templates.py
   - enhanced_prompt_generator.py
   - bpmn_templates.py
   - json_to_iflow_converter.py
   - sap_btp_integration.py
   - requirements.txt
   - Procfile
   - runtime.txt
   - manifest.yml

2. **Storage Directories:**
   - uploads/
   - results/

### Deployment Steps

1. **Login to Cloud Foundry:**
   ```bash
   cf login -a https://api.cf.us10-001.hana.ondemand.com
   ```

   Cloud Foundry Environment Details:
   - API Endpoint: https://api.cf.us10-001.hana.ondemand.com
   - Organization: IT Resonance Inc_itr-internal-2hco92jx
   - Org ID: 7a456e2e-ca6b-41b6-9770-f03a9b88f105
   - Org Memory Limit: 4,096MB

2. **Deploy the application:**
   ```bash
   # On Windows
   deploy.bat

   # On Linux/macOS
   chmod +x deploy.sh
   ./deploy.sh
   ```

   Alternatively, you can deploy manually:
   ```bash
   cf push
   ```

3. **Environment Variables:**

   The application uses environment variables defined in the manifest.yml file:

   ```yaml
   env:
     FLASK_ENV: production
     FLASK_DEBUG: false
     CLAUDE_API_KEY: ${CLAUDE_API_KEY}
     MAIN_API_URL: https://it-resonance-api.cfapps.us10-001.hana.ondemand.com

   routes:
   - route: mulesoft-iflow-api.cfapps.us10-001.hana.ondemand.com
   ```

   The `CLAUDE_API_KEY` is read from your local environment during deployment.

   If you need to update environment variables after deployment:

   ```bash
   # For SAP BTP Integration (optional)
   cf set-env mulesoft-iflow-api SAP_BTP_TENANT_URL your-tenant-url
   cf set-env mulesoft-iflow-api SAP_BTP_CLIENT_ID your-client-id
   cf set-env mulesoft-iflow-api SAP_BTP_CLIENT_SECRET your-client-secret
   cf set-env mulesoft-iflow-api SAP_BTP_OAUTH_URL your-oauth-url
   cf set-env mulesoft-iflow-api SAP_BTP_DEFAULT_PACKAGE your-default-package

   # Restage the application to apply changes
   cf restage mulesoft-iflow-api
   ```

## API Endpoints

- **GET /api/health**: Health check endpoint
- **POST /api/generate-iflow**: Generate an iFlow from markdown content
- **POST /api/generate-iflow/{job_id}**: Generate an iFlow using markdown from a previous job
- **GET /api/jobs/{job_id}**: Get job status
- **GET /api/jobs/{job_id}/download**: Download the generated iFlow ZIP file
- **POST /api/jobs/{job_id}/deploy**: Deploy the generated iFlow to SAP BTP Integration Suite

## Troubleshooting

- If the application fails to start, check the logs with `cf logs mulesoft-iflow-api --recent`
- Ensure all required environment variables are set
- Verify that the Python buildpack is available in your Cloud Foundry environment
