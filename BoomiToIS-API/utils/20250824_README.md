# Utils Directory

This directory contains utility scripts and helper modules for the BoomiToIS-API project.

## 📁 Available Utilities

### `run.py`
- **Purpose**: Local development server runner using Waitress WSGI server
- **Usage**: `python utils/run.py`
- **Features**: 
  - Configurable port via environment variable
  - Production-ready WSGI server
  - Automatic host binding

### `setup_dependencies.py`
- **Purpose**: Sets up project dependencies and copies necessary files
- **Usage**: `python utils/setup_dependencies.py`
- **Features**:
  - Copies core files from MuleToIflowGenAI Approach folder
  - Creates required directories
  - Logs all operations

### `nltk_setup.py`
- **Purpose**: Downloads and configures NLTK data packages
- **Usage**: Automatically imported by app.py during startup
- **Features**:
  - Downloads required NLTK packages (punkt, stopwords, wordnet, etc.)
  - Configurable data directory
  - Error handling and logging

### `client.py`
- **Purpose**: Example API client demonstrating how to use the BoomiToIS-API
- **Usage**: `python utils/client.py --markdown-file path/to/file.md`
- **Features**:
  - Command-line interface
  - iFlow generation workflow
  - Job status monitoring
  - Automatic download of generated iFlows

## 🚀 Quick Start

```bash
# Run the development server
python utils/run.py

# Setup dependencies (first time only)
python utils/setup_dependencies.py

# Test the API with a markdown file
python utils/client.py --markdown-file example.md --iflow-name MyFlow
```

## 📋 Dependencies

These utilities depend on:
- `waitress` - WSGI server for production
- `nltk` - Natural language processing
- `requests` - HTTP client for API testing
- `argparse` - Command-line argument parsing

## 🔧 Configuration

Most utilities use environment variables:
- `PORT` - Server port (default: 5000)
- `NLTK_DATA` - NLTK data directory path
- API credentials for client testing

---

**Note**: These utilities are designed to work with the main BoomiToIS-API application and should be run from the project root directory.
