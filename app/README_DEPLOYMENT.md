# MuleSoft Documentation Generator - Deployment Guide

## Overview

This application generates technical documentation for MuleSoft applications and provides a web interface for uploading, processing, and visualizing MuleSoft XML files. It can optionally enhance the documentation using LLM services (Anthropic Claude or OpenAI).

## Core Components

### Web Application
- **app.py**: Main Flask application that handles web requests, file uploads, and documentation generation
- **run_app.py**: Entry point script that sets up environment and starts the Flask app
- **templates/upload.html**: Main upload page for the web interface
- **templates/api_docs.html**: API documentation page

### Documentation Generation
- **enhanced_doc_generator.py**: Extended documentation generator for multiple file types
- **additional_file_parser.py**: Parser for additional file types (DWL, YAML, RAML, etc.)
- **use_anthropic.py**: Utility for using Anthropic API for documentation enhancement

### Core Modules (in ../final/)
- **documentation_enhancer.py**: LLM-based documentation enhancement using OpenAI or Anthropic
- **mule_flow_documentation.py**: Core MuleSoft flow documentation generator
- **md_to_html_with_mermaid.py**: Converts Markdown to HTML with Mermaid diagrams

### Utility Scripts
- **fix_llm_stuck.py**: Utility to fix stuck LLM enhancement jobs
- **check_llm.py**: Check LLM service availability
- **fix_stuck_jobs.py**: Fix stuck processing jobs
- **debug_xml_parsing.py**: Debug tools for XML parsing issues

## Deployment Structure

The application should be deployed with the following directory structure:

```
mulesoft-documentation-generator/
├── app.py                     # Main Flask application
├── run_app.py                 # Entry point script
├── requirements.txt           # Dependencies
├── Procfile                   # CF deployment command
├── runtime.txt                # Python version
├── enhanced_doc_generator.py  # Documentation generator
├── additional_file_parser.py  # File parser
├── use_anthropic.py           # Anthropic integration
├── static/                    # Static assets
│   └── ...
├── templates/                 # HTML templates
│   ├── upload.html
│   └── api_docs.html
├── uploads/                   # Upload directory
│   └── .gitkeep
└── results/                   # Results directory
    └── .gitkeep
```

## Dependencies on Parent Directory

The application references modules in the parent directory (`../final/`):

- **documentation_enhancer.py**
- **mule_flow_documentation.py**
- **md_to_html_with_mermaid.py**

For Cloud Foundry deployment, you need to ensure these dependencies are properly included or resolved.

## Installation Options

### Option 1: Include Parent Directory Modules

Copy the necessary files from `../final/` into the app directory before deployment:

```bash
# Create final directory inside the app directory
mkdir -p mule_to_iflow/documentation/api/final

# Copy necessary files
cp mule_to_iflow/documentation/final/documentation_enhancer.py mule_to_iflow/documentation/api/final/
cp mule_to_iflow/documentation/final/mule_flow_documentation.py mule_to_iflow/documentation/api/final/
cp mule_to_iflow/documentation/final/md_to_html_with_mermaid.py mule_to_iflow/documentation/api/final/
```

### Option 2: Modify Import Paths

Modify `app.py` and other files to use relative imports instead of using sys.path.append:

```python
# Instead of
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from final.mule_flow_documentation import MuleFlowParser

# Use
from .final.mule_flow_documentation import MuleFlowParser
```

### Option 3: Package as Python Package

Create a proper Python package structure and use setuptools to handle dependencies.

## Environment Configuration

The application requires the following environment variables:

- **ANTHROPIC_API_KEY**: API key for Anthropic Claude (for LLM enhancement)
- **OPENAI_API_KEY**: API key for OpenAI (alternative for LLM enhancement)

Set these in Cloud Foundry using:

```bash
cf set-env mulesoft-documentation-generator ANTHROPIC_API_KEY your-api-key
cf set-env mulesoft-documentation-generator OPENAI_API_KEY your-api-key
cf restage mulesoft-documentation-generator
```

## Deployment Workflow

1. **Prepare the application** using one of the installation options above
2. **Deploy to Cloud Foundry** using the manifest.yml
3. **Configure environment variables** for the LLM services
4. **Verify the application** is working properly

## File Structure for Deployment

Here's the full list of files and scripts required for deployment:

1. **Core Application Files:**
   - app.py
   - run_app.py
   - requirements.txt
   - Procfile
   - runtime.txt
   - templates/*
   - static/*

2. **Documentation Generation Files:**
   - enhanced_doc_generator.py
   - additional_file_parser.py
   - final/documentation_enhancer.py
   - final/mule_flow_documentation.py
   - final/md_to_html_with_mermaid.py

3. **Helper Scripts:**
   - use_anthropic.py

4. **Storage Directories:**
   - uploads/
   - results/ 