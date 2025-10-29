#!/usr/bin/env python3
"""
Directory Archiving Script for BoomiToIS-API

This script archives test output directories and other non-essential folders
to clean up the main project directory while preserving the files for future reference.

Usage:
    python archive_directories.py [--dry-run] [--archive-dir ARCHIVE_DIR]

Options:
    --dry-run          Show what would be archived without actually moving files
    --archive-dir      Specify custom archive directory (default: archive/test_outputs)
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

# Directories to archive
DIRECTORIES_TO_ARCHIVE = [
    "Complete_Workflow_Test_output",
    "Enhanced_Complete_Package_Test_output", 
    "Single_IFlow_Test_output",
    "Template_Test_Integration_output",
    "minimal_sap_package_output",
    "proper_iflow_output",
    "sap_package_output",
    "test_empty",
    "test_step_1",
    "test_output"
]

def create_archive_directory(archive_base_dir="archive"):
    """Create the archive directory with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, f"test_outputs_{timestamp}")
    
    try:
        os.makedirs(archive_dir, exist_ok=True)
        logger.info(f"Created archive directory: {archive_dir}")
        return archive_dir
    except Exception as e:
        logger.error(f"Failed to create archive directory: {e}")
        return None

def archive_directory(source_dir, archive_dir, dry_run=False):
    """Archive a single directory"""
    if not os.path.exists(source_dir):
        logger.warning(f"Source directory does not exist: {source_dir}")
        return False
    
    if not os.path.isdir(source_dir):
        logger.warning(f"Source is not a directory: {source_dir}")
        return False
    
    # Calculate size before moving
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                pass
    
    size_mb = total_size / (1024 * 1024)
    
    destination = os.path.join(archive_dir, os.path.basename(source_dir))
    
    if dry_run:
        logger.info(f"[DRY RUN] Would archive: {source_dir} -> {destination} ({size_mb:.2f} MB)")
        return True
    
    try:
        # Move the directory
        shutil.move(source_dir, destination)
        logger.info(f"Archived: {source_dir} -> {destination} ({size_mb:.2f} MB)")
        return True
    except Exception as e:
        logger.error(f"Failed to archive {source_dir}: {e}")
        return False

def create_archive_readme(archive_dir, archived_dirs):
    """Create a README file documenting what was archived"""
    readme_path = os.path.join(archive_dir, "README.md")
    
    content = f"""# Archived Test Outputs

**Archive Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Archived Directories

The following directories were archived from the BoomiToIS-API project:

"""
    
    for dir_name in archived_dirs:
        content += f"- `{dir_name}/`\n"
    
    content += f"""
## Purpose

These directories contained test outputs, sample integrations, and other non-essential files
that were cluttering the main project directory. They have been preserved for reference
but are no longer needed for the core application functionality.

## Core Application Files (Not Archived)

The following directories and files remain in the main project:
- `app.py` - Main Flask application
- `enhanced_genai_iflow_generator.py` - Core generator engine
- `enhanced_iflow_templates.py` - Template system
- `iflow_generator_api.py` - API wrapper
- `genai_debug/` - Active debug files (required for runtime)
- `results/` - Active job results
- `uploads/` - Active upload directory
- `utils/` - Utility functions and NLTK data

## Restoration

If you need to restore any of these directories, simply move them back to the main
BoomiToIS-API directory from this archive location.

## Archive Structure

```
{os.path.basename(archive_dir)}/
├── README.md (this file)
{chr(10).join([f"├── {dir_name}/" for dir_name in archived_dirs])}
```
"""
    
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Created archive README: {readme_path}")
    except Exception as e:
        logger.error(f"Failed to create README: {e}")

def main():
    parser = argparse.ArgumentParser(description="Archive test output directories")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be archived without actually moving files")
    parser.add_argument("--archive-dir", default="archive", 
                       help="Base archive directory (default: archive)")
    
    args = parser.parse_args()
    
    # Get the script directory (BoomiToIS-API)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    logger.info("=" * 60)
    logger.info("BoomiToIS-API Directory Archiving Script")
    logger.info("=" * 60)
    logger.info(f"Working directory: {script_dir}")
    logger.info(f"Dry run mode: {args.dry_run}")
    
    # Create archive directory
    archive_dir = create_archive_directory(args.archive_dir)
    if not archive_dir:
        logger.error("Failed to create archive directory. Exiting.")
        return 1
    
    # Archive each directory
    archived_dirs = []
    failed_dirs = []
    
    for dir_name in DIRECTORIES_TO_ARCHIVE:
        source_path = os.path.join(script_dir, dir_name)
        
        if archive_directory(source_path, archive_dir, args.dry_run):
            archived_dirs.append(dir_name)
        else:
            failed_dirs.append(dir_name)
    
    # Create README if not dry run
    if not args.dry_run and archived_dirs:
        create_archive_readme(archive_dir, archived_dirs)
    
    # Summary
    logger.info("=" * 60)
    logger.info("ARCHIVING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Successfully archived: {len(archived_dirs)} directories")
    logger.info(f"Failed to archive: {len(failed_dirs)} directories")
    
    if archived_dirs:
        logger.info("\nArchived directories:")
        for dir_name in archived_dirs:
            logger.info(f"  ✓ {dir_name}")
    
    if failed_dirs:
        logger.info("\nFailed directories:")
        for dir_name in failed_dirs:
            logger.info(f"  ✗ {dir_name}")
    
    if not args.dry_run and archived_dirs:
        logger.info(f"\nArchive location: {archive_dir}")
        logger.info("Archive README created with restoration instructions.")
    
    return 0 if not failed_dirs else 1

if __name__ == "__main__":
    exit(main())







