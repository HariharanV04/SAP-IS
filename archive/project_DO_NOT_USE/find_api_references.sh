#!/bin/bash

echo "===== Searching for API URL References ====="

echo "Searching for \"mulesoft-docs-api\" in all files..."
grep -r --include="*.*" -l "mulesoft-docs-api" .
echo ""

echo "Searching for \"mulesoft\" in all files..."
grep -r --include="*.*" -l "mulesoft" .
echo ""

echo "Searching for \"cfapps.us10-001.hana.ondemand.com\" in all files..."
grep -r --include="*.*" -l "cfapps.us10-001.hana.ondemand.com" .
echo ""

echo "Searching for hardcoded URLs in JavaScript files..."
grep -r --include="*.js" -l "http://" .
grep -r --include="*.js" -l "https://" .
echo ""

echo "Searching for axios API calls..."
grep -r --include="*.js" -l "axios" .
echo ""

echo "Searching for fetch API calls..."
grep -r --include="*.js" -l "fetch(" .
echo ""

echo "Searching for XMLHttpRequest..."
grep -r --include="*.js" -l "XMLHttpRequest" .
echo ""

echo "Searching for environment variables..."
grep -r --include="*.js" -l "process.env" .
grep -r --include="*.js" -l "import.meta.env" .
echo ""

echo "Searching for API configuration..."
grep -r --include="*.js" -l "baseURL" .
echo ""

echo "Searching in build artifacts..."
if [ -d "dist" ]; then
  echo "Searching in dist directory..."
  grep -r --include="*.*" -l "mulesoft-docs-api" dist/
  echo ""
fi

echo "Search completed!"
