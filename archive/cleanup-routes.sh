#!/bin/bash

echo "===== IT Resonance Integration Flow Analyzer - Route Cleanup ====="

# Login to Cloud Foundry
echo "Logging in to Cloud Foundry..."
cf login -a https://api.cf.us10-001.hana.ondemand.com

if [ $? -ne 0 ]; then
  echo "Cloud Foundry login failed! Aborting cleanup."
  exit 1
fi

# List all routes
echo "Current routes in your space:"
cf routes

# Delete orphaned routes (routes not mapped to any app)
echo "Cleaning up orphaned routes..."
cf delete-orphaned-routes -f

# List routes again to confirm cleanup
echo "Routes after cleanup:"
cf routes

# Check route quota
echo "Checking route quota..."
cf space dev | grep routes

echo "===== Route cleanup completed! ====="
echo "If you still have route quota issues, you may need to manually delete some routes."
echo "To delete a specific route, use: cf delete-route DOMAIN --hostname HOSTNAME"
echo "Example: cf delete-route cfapps.us10-001.hana.ondemand.com --hostname it-resonance-ui"
