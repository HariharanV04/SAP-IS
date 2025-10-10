# Directory Archiving Guide

This guide explains how to clean up the BoomiToIS-API project by archiving test output directories and other non-essential files.

## 🗂️ What Gets Archived

The following directories are safe to archive as they contain test outputs and sample files that are not needed for the core application:

- `Complete_Workflow_Test_output/`
- `Enhanced_Complete_Package_Test_output/`
- `Single_IFlow_Test_output/`
- `Template_Test_Integration_output/`
- `minimal_sap_package_output/`
- `proper_iflow_output/`
- `sap_package_output/`
- `test_empty/`
- `test_step_1/`
- `test_output/`

## 🚀 How to Archive

### Option 1: Using the Python Script (Recommended)

```bash
# Dry run to see what would be archived
python archive_directories.py --dry-run

# Actually archive the directories
python archive_directories.py
```

### Option 2: Using the Batch Script (Windows)

```cmd
archive_test_outputs.bat
```

### Option 3: Using the Shell Script (Linux/Mac)

```bash
./archive_test_outputs.sh
```

## 📁 Archive Structure

After archiving, the directories will be moved to:
```
archive/
└── test_outputs_YYYYMMDD_HHMMSS/
    ├── README.md
    ├── Complete_Workflow_Test_output/
    ├── Enhanced_Complete_Package_Test_output/
    ├── Single_IFlow_Test_output/
    ├── Template_Test_Integration_output/
    ├── minimal_sap_package_output/
    ├── proper_iflow_output/
    ├── sap_package_output/
    ├── test_empty/
    ├── test_step_1/
    └── test_output/
```

## 🔧 What Remains in Main Directory

The following directories and files are **NOT archived** as they are essential for the application:

### Core Application Files
- `app.py` - Main Flask application
- `enhanced_genai_iflow_generator.py` - Core generator engine
- `enhanced_iflow_templates.py` - Template system
- `iflow_generator_api.py` - API wrapper
- `iflow_fixer.py` - Post-generation fixing
- `cors_config.py` - CORS configuration
- `sap_btp_integration.py` - SAP deployment
- `direct_iflow_deployment.py` - Direct deployment

### Active Directories
- `genai_debug/` - **ACTIVE** - Contains runtime debug files
- `results/` - **ACTIVE** - Contains job results
- `uploads/` - **ACTIVE** - Contains uploaded files
- `utils/` - **ACTIVE** - Contains utility functions and NLTK data

### Configuration Files
- `.env*` - Environment configurations
- `requirements.txt` - Python dependencies
- `manifest.yml` - Cloud Foundry deployment
- `Procfile` - Process configuration
- `runtime.txt` - Python version

## 🔄 Restoration

If you need to restore any archived directories:

1. Navigate to the archive directory: `archive/test_outputs_YYYYMMDD_HHMMSS/`
2. Copy the desired directory back to the main BoomiToIS-API directory
3. The directory will be immediately available for use

## 📊 Space Savings

The archiving process typically saves significant disk space:
- Test output directories: ~0.1-0.5 MB each
- Total space saved: ~1-5 MB (depending on test outputs)
- Main benefit: Cleaner project structure and easier navigation

## ⚠️ Important Notes

1. **Always run with `--dry-run` first** to see what will be archived
2. **The `genai_debug/` directory is NOT archived** - it contains active debug files
3. **The `genai_output/` directory contents can be archived** but the directory structure is preserved
4. **Archived files are moved, not copied** - they are no longer in the main directory
5. **The archive includes a README** explaining what was archived and how to restore

## 🛠️ Customization

You can customize the archiving process by modifying `archive_directories.py`:

- Add more directories to `DIRECTORIES_TO_ARCHIVE`
- Change the archive location with `--archive-dir`
- Modify the README template in the `create_archive_readme()` function

## 📝 Logs

The archiving script provides detailed logging:
- Shows which directories are being processed
- Displays file sizes
- Reports success/failure status
- Creates a summary at the end

All operations are logged with timestamps for easy tracking.
