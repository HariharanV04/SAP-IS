# Adding Your Company Logo to the MuleSoft Docs Generator

This document provides instructions for adding your company's logo to the application's user interface.

## Logo Requirements

For optimal display, your logo files should meet the following specifications:

1. **Header Logo** (`company-logo.png`):
   - Recommended dimensions: 180px width × 48px height
   - File format: PNG with transparency
   - File size: < 100KB

2. **Footer Logo** (`company-logo-small.png`):
   - Recommended dimensions: 120px width × 32px height
   - File format: PNG with transparency
   - File size: < 50KB

## Installation Steps

1. Prepare your logo files with the names specified above.

2. Place your logo files in the following directory:
   ```
   /public/static/images/
   ```

3. If the `/public/static/images/` directory doesn't exist, create it with the following commands:
   ```powershell
   # Navigate to the project directory
   cd mule_cf_deployment/project

   # Create the directory structure
   mkdir -p public/static/images
   ```

4. Copy your logo files to the images directory:
   ```powershell
   # Copy your logo files to the directory
   copy path\to\your\logo.png public\static\images\company-logo.png
   copy path\to\your\small-logo.png public\static\images\company-logo-small.png
   ```

## Verifying Logo Integration

1. After placing your logo files in the correct directory, run the application locally:
   ```powershell
   npm run dev
   ```

2. Open your browser and navigate to `http://localhost:5173`

3. Verify that your logo appears in the header and footer of the application.

## Troubleshooting

If your logo doesn't appear:

1. Check file paths: Ensure the logo files are correctly named and placed in the `/public/static/images/` directory.

2. Check file formats: Ensure your logos are in PNG format with proper transparency.

3. Check browser console: Look for any errors related to image loading.

4. Clear cache: Try clearing your browser cache or opening the application in an incognito/private window.

## Deployment

When deploying your application, the logo files will be included in the build. Make sure to follow the standard deployment process as outlined in the project documentation. 