#!/usr/bin/env python3
"""
Cloud Foundry Environment Variables Setup Script
This script sets all environment variables for CF deployment across all APIs.
Handles special characters and escaping properly.
"""

import subprocess
import sys
import os
import time
from typing import Dict, List

class CFEnvSetup:
    def __init__(self):
        # Working SAP BTP Credentials (from BoomiToIS direct deployment)
        self.sap_credentials = {
            'SAP_BTP_CLIENT_ID': 'sb-5e4b1b9b-d22f-427d-a6ae-f33c83513c0f!b124895|it!b410334',
            'SAP_BTP_CLIENT_SECRET': '5813ca83-4ba6-4231-96e1-1a48a80eafec$kmhNJINpEbcsXgBQJn9vvaAHGgMegiM_-FB7EC_SF9w=',
            'SAP_BTP_OAUTH_URL': 'https://itr-internal-2hco92jx.authentication.us10.hana.ondemand.com/oauth/token',
            'SAP_BTP_TENANT_URL': 'https://itr-internal-2hco92jx.it-cpi034.cfapps.us10-002.hana.ondemand.com',
            'SAP_BTP_DEFAULT_PACKAGE': 'ConversionPackages'
        }
        
        # Application configurations
        self.app_configs = {
            'it-resonance-main-api': {
                **self.sap_credentials,
                'ANTHROPIC_API_KEY': 'sk-ant-api03-yTb9vL3wgKQrUjKrEuFGPtCg9R5uPGAUAy1MzZK5sBHhMgQmyPr7kl0nLU2Q8xZ_',
                'IFLOW_API_URL': 'https://mule-to-is-api.cfapps.eu10.hana.ondemand.com',
                'BOOMI_API_URL': 'https://boomi-to-is-api.cfapps.eu10.hana.ondemand.com',
                'MULE_API_URL': 'https://mule-to-is-api.cfapps.eu10.hana.ondemand.com',
                'LLM_SERVICE': 'anthropic',
                'DATABASE_ENABLED': 'false',
                'FLASK_ENV': 'production'
            },
            'mule-to-is-api': {
                **self.sap_credentials,
                'ANTHROPIC_API_KEY': 'sk-ant-api03-yTb9vL3wgKQrUjKrEuFGPtCg9R5uPGAUAy1MzZK5sBHhMgQmyPr7kl0nLU2Q8xZ_',
                'MAIN_API_URL': 'https://it-resonance-main-api.cfapps.eu10.hana.ondemand.com',
                'FLASK_ENV': 'production',
                'PORT': '5001'
            },
            'boomi-to-is-api': {
                **self.sap_credentials,
                'ANTHROPIC_API_KEY': 'sk-ant-api03-yTb9vL3wgKQrUjKrEuFGPtCg9R5uPGAUAy1MzZK5sBHhMgQmyPr7kl0nLU2Q8xZ_',
                'MAIN_API_URL': 'https://it-resonance-main-api.cfapps.eu10.hana.ondemand.com',
                'FLASK_ENV': 'production',
                'PORT': '5003'
            }
        }

    def run_cf_command(self, command: List[str]) -> bool:
        """
        Run a CF CLI command and return success status
        """
        try:
            print(f"   Executing: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   ✅ Success")
                return True
            else:
                print(f"   ❌ Failed: {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout: Command took too long")
            return False
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False

    def check_cf_cli(self) -> bool:
        """
        Check if CF CLI is installed and user is logged in
        """
        print("🔍 Checking CF CLI status...")
        
        # Check if cf command exists
        try:
            result = subprocess.run(['cf', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ CF CLI not found. Please install it first.")
                return False
            print(f"✅ CF CLI found: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ CF CLI not found. Please install it first.")
            return False
        
        # Check if user is logged in
        try:
            result = subprocess.run(['cf', 'target'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Not logged in to CF. Please run 'cf login' first.")
                return False
            print("✅ Logged in to CF")
            return True
        except Exception as e:
            print(f"❌ Error checking CF status: {str(e)}")
            return False

    def set_env_vars_for_app(self, app_name: str, env_vars: Dict[str, str]) -> bool:
        """
        Set environment variables for a specific CF application
        """
        print(f"\n🔧 Configuring {app_name}...")
        success_count = 0
        total_count = len(env_vars)
        
        for key, value in env_vars.items():
            command = ['cf', 'set-env', app_name, key, value]
            if self.run_cf_command(command):
                success_count += 1
            time.sleep(0.5)  # Small delay to avoid rate limiting
        
        print(f"   📊 Set {success_count}/{total_count} environment variables")
        return success_count == total_count

    def setup_all_environments(self):
        """
        Set up environment variables for all applications
        """
        print("🚀 Setting up Cloud Foundry Environment Variables for All APIs")
        print("=" * 65)
        
        if not self.check_cf_cli():
            return False
        
        all_success = True
        
        for app_name, env_vars in self.app_configs.items():
            success = self.set_env_vars_for_app(app_name, env_vars)
            if not success:
                all_success = False
        
        return all_success

    def restart_all_apps(self):
        """
        Restart all applications to apply environment variables
        """
        print(f"\n🔄 Restarting all applications...")
        
        apps = list(self.app_configs.keys())
        success_count = 0
        
        for app_name in apps:
            print(f"   🔄 Restarting {app_name}...")
            command = ['cf', 'restart', app_name]
            if self.run_cf_command(command):
                success_count += 1
        
        print(f"   📊 Restarted {success_count}/{len(apps)} applications")
        return success_count == len(apps)

    def verify_env_vars(self, app_name: str):
        """
        Verify environment variables for an application
        """
        print(f"\n🔍 Verifying environment variables for {app_name}...")
        command = ['cf', 'env', app_name]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                # Look for our SAP BTP variables in the output
                output = result.stdout
                if 'SAP_BTP_CLIENT_ID' in output and 'SAP_BTP_TENANT_URL' in output:
                    print(f"   ✅ SAP BTP environment variables found")
                else:
                    print(f"   ⚠️  SAP BTP environment variables may not be set")
            else:
                print(f"   ❌ Failed to get environment variables")
        except Exception as e:
            print(f"   ❌ Error verifying environment: {str(e)}")

def main():
    """
    Main function
    """
    print("Cloud Foundry Environment Setup Script")
    print("======================================")
    
    setup = CFEnvSetup()
    
    # Setup environment variables
    if setup.setup_all_environments():
        print("\n✅ All environment variables have been set successfully!")
        
        # Ask user if they want to restart applications
        restart = input("\n🔄 Would you like to restart all applications now? (y/N): ").strip().lower()
        if restart in ['y', 'yes']:
            if setup.restart_all_apps():
                print("\n✅ All applications have been restarted successfully!")
            else:
                print("\n⚠️  Some applications failed to restart. Check CF status manually.")
        
        # Ask user if they want to verify environment variables
        verify = input("\n🔍 Would you like to verify environment variables for an app? (y/N): ").strip().lower()
        if verify in ['y', 'yes']:
            app_name = input("Enter app name (e.g., it-resonance-main-api): ").strip()
            if app_name:
                setup.verify_env_vars(app_name)
        
        print("\n📝 Next Steps:")
        print("1. ✅ ANTHROPIC_API_KEY is already set with the correct key")
        print("2. Test your deployment at the frontend URL")
        print("3. Restart all applications:")
        print("   cf restart it-resonance-main-api")
        print("   cf restart mule-to-is-api")
        print("   cf restart boomi-to-is-api")
        
    else:
        print("\n❌ Some environment variables failed to set. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
