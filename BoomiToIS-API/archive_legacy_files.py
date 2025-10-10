#!/usr/bin/env python3
"""
Legacy Files Archiving Script for BoomiToIS-API

This script archives legacy, deprecated, and unused files that are no longer needed
for the core application functionality but are preserved for reference.

Usage:
    python archive_legacy_files.py [--dry-run] [--archive-dir ARCHIVE_DIR]

Options:
    --dry-run          Show what would be archived without actually moving files
    --archive-dir      Specify custom archive directory (default: archive/legacy_files)
"""

import os
import shutil
import argparse
import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Files and directories to archive
LEGACY_ITEMS_TO_ARCHIVE = [
    "create_proper_iflow_zip.py",
    "template_based_converter.py", 
    "config_driven_generator.py",
    "config_validation_engine.py",
    "config/"
]

# Test output files to archive
TEST_OUTPUT_FILES_TO_ARCHIVE = [
    "bpmn_test_output.iflw",
    "enhanced_template_test_output.iflw",
    "problematic_sanitized.iflw",
    "sanitizer_test_output_sanitized.iflw",
    "sanitizer_test_output.iflw",
    "simple_test_output.xml",
    "test_enhanced_templates_output.xml",
    "test_iflow_output.xml",
    "simple_test.json",
    "test_markdown_content.md"
]

def create_archive_directory(archive_base_dir="archive"):
    """Create the archive directory with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, f"legacy_files_{timestamp}")
    
    try:
        os.makedirs(archive_dir, exist_ok=True)
        logger.info(f"Created archive directory: {archive_dir}")
        return archive_dir
    except Exception as e:
        logger.error(f"Failed to create archive directory: {e}")
        return None

def archive_item(source_path, archive_dir, dry_run=False):
    """Archive a single file or directory"""
    if not os.path.exists(source_path):
        logger.warning(f"Source item does not exist: {source_path}")
        return False
    
    # Calculate size before moving
    total_size = 0
    if os.path.isfile(source_path):
        try:
            total_size = os.path.getsize(source_path)
        except OSError:
            pass
    elif os.path.isdir(source_path):
        for dirpath, dirnames, filenames in os.walk(source_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
    
    size_mb = total_size / (1024 * 1024)
    item_type = "directory" if os.path.isdir(source_path) else "file"
    
    destination = os.path.join(archive_dir, os.path.basename(source_path))
    
    if dry_run:
        logger.info(f"[DRY RUN] Would archive {item_type}: {source_path} -> {destination} ({size_mb:.2f} MB)")
        return True
    
    try:
        # Move the file or directory
        shutil.move(source_path, destination)
        logger.info(f"Archived {item_type}: {source_path} -> {destination} ({size_mb:.2f} MB)")
        return True
    except Exception as e:
        logger.error(f"Failed to archive {source_path}: {e}")
        return False

def create_archive_readme(archive_dir, archived_items):
    """Create a README file documenting what was archived"""
    readme_path = os.path.join(archive_dir, "README.md")
    
    content = f"""# Archived Legacy Files

**Archive Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Archived Items

The following legacy files and directories were archived from the BoomiToIS-API project:

"""
    
    for item_name in archived_items:
        content += f"- `{item_name}`\n"
    
    content += f"""
## Purpose

These files were legacy, deprecated, or unused components that were cluttering the main project directory. They have been preserved for reference but are no longer needed for the core application functionality.

## File Descriptions

### `create_proper_iflow_zip.py`
- **Status**: Replaced by integrated functionality
- **Replacement**: ZIP creation is now integrated into `enhanced_genai_iflow_generator.py`
- **Reason**: Standalone utility script that was superseded by the main generator

### `template_based_converter.py`
- **Status**: Replaced by enhanced template system
- **Replacement**: `enhanced_iflow_templates.py` + `bpmn_templates.py`
- **Reason**: Legacy converter replaced by more comprehensive template system

### `config_driven_generator.py`
- **Status**: Deprecated approach
- **Replacement**: Main GenAI-based generation approach
- **Reason**: Configuration-driven approach was superseded by AI-powered generation

### `config_validation_engine.py`
- **Status**: Deprecated validation engine
- **Replacement**: Built-in validation in main generator
- **Reason**: Standalone validation replaced by integrated validation

### `config/` directory
- **Status**: Legacy template files
- **Replacement**: `enhanced_iflow_templates.py`
- **Reason**: Old template files replaced by enhanced template system

## Test Output Files

The following test output files were also archived as they are no longer needed:

### iFlow Test Outputs
- `bpmn_test_output.iflw` - BPMN test output
- `enhanced_template_test_output.iflw` - Enhanced template test output
- `problematic_sanitized.iflw` - Problematic sanitized test file
- `sanitizer_test_output_sanitized.iflw` - Sanitizer test output
- `sanitizer_test_output.iflw` - Sanitizer test output

### XML Test Outputs
- `simple_test_output.xml` - Simple test XML output
- `test_enhanced_templates_output.xml` - Enhanced templates test output
- `test_iflow_output.xml` - iFlow test output

### JSON and Markdown Test Files
- `simple_test.json` - Simple test JSON file
- `test_markdown_content.md` - Test markdown content

**Reason**: These are all test output files generated during development and testing phases. They are no longer needed for the core application functionality.

## Core Application Files (Not Archived)

The following files remain in the main project as they are actively used:
- `app.py` - Main Flask application
- `enhanced_genai_iflow_generator.py` - Core generator engine
- `enhanced_iflow_templates.py` - Active template system
- `bpmn_templates.py` - BPMN generation
- `iflow_generator_api.py` - API wrapper
- `iflow_fixer.py` - Post-generation fixing
- `boomi_xml_processor.py` - Boomi processing (REQUIRED)
- `json_to_iflow_converter.py` - JSON-based generation (REQUIRED)
- `cors_config.py` - CORS configuration
- `sap_btp_integration.py` - SAP deployment
- `direct_iflow_deployment.py` - Direct deployment

## Restoration

If you need to restore any of these files, simply move them back to the main
BoomiToIS-API directory from this archive location.

## Archive Structure

```
{os.path.basename(archive_dir)}/
├── README.md (this file)
{chr(10).join([f"├── {item_name}" for item_name in archived_items])}
```

## Impact Assessment

Archiving these files will:
- ✅ Clean up the main project directory
- ✅ Remove unused dependencies
- ✅ Improve project navigation
- ✅ Reduce confusion about which files are active
- ❌ No impact on core functionality
- ❌ No impact on API endpoints
- ❌ No impact on iFlow generation
"""
    
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Created archive README: {readme_path}")
    except Exception as e:
        logger.error(f"Failed to create README: {e}")

def main():
    parser = argparse.ArgumentParser(description="Archive legacy and deprecated files")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be archived without actually moving files")
    parser.add_argument("--archive-dir", default="archive", 
                       help="Base archive directory (default: archive)")
    
    args = parser.parse_args()
    
    # Get the script directory (BoomiToIS-API)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    logger.info("=" * 60)
    logger.info("BoomiToIS-API Legacy Files Archiving Script")
    logger.info("=" * 60)
    logger.info(f"Working directory: {script_dir}")
    logger.info(f"Dry run mode: {args.dry_run}")
    
    # Create archive directory
    archive_dir = create_archive_directory(args.archive_dir)
    if not archive_dir:
        logger.error("Failed to create archive directory. Exiting.")
        return 1
    
    # Archive each item
    archived_items = []
    failed_items = []
    
    # Archive legacy files and directories
    logger.info("Archiving legacy files and directories...")
    for item_name in LEGACY_ITEMS_TO_ARCHIVE:
        source_path = os.path.join(script_dir, item_name)
        
        if archive_item(source_path, archive_dir, args.dry_run):
            archived_items.append(item_name)
        else:
            failed_items.append(item_name)
    
    # Archive test output files
    logger.info("Archiving test output files...")
    for file_name in TEST_OUTPUT_FILES_TO_ARCHIVE:
        source_path = os.path.join(script_dir, file_name)
        
        if archive_item(source_path, archive_dir, args.dry_run):
            archived_items.append(file_name)
        else:
            failed_items.append(file_name)
    
    # Create README if not dry run
    if not args.dry_run and archived_items:
        create_archive_readme(archive_dir, archived_items)
    
    # Summary
    logger.info("=" * 60)
    logger.info("LEGACY FILES ARCHIVING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Successfully archived: {len(archived_items)} items")
    logger.info(f"Failed to archive: {len(failed_items)} items")
    
    if archived_items:
        logger.info("\nArchived items:")
        for item_name in archived_items:
            logger.info(f"  ✓ {item_name}")
    
    if failed_items:
        logger.info("\nFailed items:")
        for item_name in failed_items:
            logger.info(f"  ✗ {item_name}")
    
    if not args.dry_run and archived_items:
        logger.info(f"\nArchive location: {archive_dir}")
        logger.info("Archive README created with detailed descriptions.")
        logger.info("\n🎉 Project cleanup completed! Core functionality preserved.")
    
    return 0 if not failed_items else 1

if __name__ == "__main__":
    exit(main())
