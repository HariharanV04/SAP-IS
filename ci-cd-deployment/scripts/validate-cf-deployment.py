#!/usr/bin/env python3
"""
Validate Cloud Foundry deployment readiness
Checks all prerequisites for successful CF deployment
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime

class CFDeploymentValidator:
    """Validate Cloud Foundry deployment readiness"""
    
    def __init__(self):
        """Initialize validator"""
        self.root_dir = Path.cwd()
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log_success(self, message):
        """Log a success"""
        self.successes.append(message)
        print(f"✅ {message}")
    
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(message)
        print(f"⚠️ {message}")
    
    def log_issue(self, message):
        """Log an issue"""
        self.issues.append(message)
        print(f"❌ {message}")
    
    def run_command(self, command, check_output=True):
        """Run a command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            
            if check_output and result.returncode != 0:
                return None, result.stderr
            
            return result.stdout.strip(), None
            
        except Exception as e:
            return None, str(e)
    
    def check_cf_cli(self):
        """Check if CF CLI is installed and logged in"""
        print("\n🔧 Checking Cloud Foundry CLI...")
        
        # Check if CF CLI is installed
        output, error = self.run_command("cf --version", check_output=False)
        if error or not output:
            self.log_issue("Cloud Foundry CLI not installed")
            self.log_issue("Install with: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html")
            return False
        
        self.log_success(f"CF CLI installed: {output}")
        
        # Check if logged in
        output, error = self.run_command("cf target", check_output=False)
        if error or "Not logged in" in output:
            self.log_issue("Not logged into Cloud Foundry")
            self.log_issue("Login with: cf login -a https://api.cf.eu10-005.hana.ondemand.com")
            return False
        
        self.log_success("Logged into Cloud Foundry")
        
        # Show current target
        lines = output.split('\n')
        for line in lines:
            if 'API endpoint:' in line or 'User:' in line or 'Org:' in line or 'Space:' in line:
                print(f"   {line.strip()}")
        
        return True
    
    def check_app_manifests(self):
        """Check if all app manifests exist and are valid"""
        print("\n📋 Checking application manifests...")
        
        apps = {
            'Main API': 'app/manifest.yml',
            'MuleToIS API': 'MuleToIS-API/manifest.yml',
            'BoomiToIS API': 'BoomiToIS-API/manifest.yml',
            'Frontend': 'IFA-Project/frontend/manifest.yml'
        }
        
        all_valid = True
        
        for app_name, manifest_path in apps.items():
            if os.path.exists(manifest_path):
                self.log_success(f"{app_name} manifest exists: {manifest_path}")
                
                # Check manifest content
                try:
                    with open(manifest_path, 'r') as f:
                        content = f.read()
                        if 'name:' in content and 'memory:' in content:
                            self.log_success(f"{app_name} manifest appears valid")
                        else:
                            self.log_warning(f"{app_name} manifest may be incomplete")
                except Exception as e:
                    self.log_issue(f"Error reading {app_name} manifest: {str(e)}")
                    all_valid = False
            else:
                self.log_issue(f"{app_name} manifest missing: {manifest_path}")
                all_valid = False
        
        return all_valid
    
    def check_dependencies(self):
        """Check if all dependencies are properly configured"""
        print("\n📦 Checking dependencies...")
        
        # Check Python requirements
        python_apps = ['app', 'MuleToIS-API', 'BoomiToIS-API']
        
        for app in python_apps:
            requirements_path = f"{app}/requirements.txt"
            if os.path.exists(requirements_path):
                self.log_success(f"{app} requirements.txt exists")
            else:
                self.log_issue(f"{app} requirements.txt missing")
        
        # Check frontend dependencies
        frontend_package = "IFA-Project/frontend/package.json"
        if os.path.exists(frontend_package):
            self.log_success("Frontend package.json exists")
        else:
            self.log_issue("Frontend package.json missing")
        
        return True
    
    def check_environment_config(self):
        """Check environment configuration"""
        print("\n🔧 Checking environment configuration...")
        
        config_file = "deployment/config/environments.json"
        if os.path.exists(config_file):
            self.log_success("Environment configuration exists")
            
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Check required sections
                required_sections = ['shared', 'production', 'cf_apps']
                for section in required_sections:
                    if section in config:
                        self.log_success(f"Environment config has {section} section")
                    else:
                        self.log_issue(f"Environment config missing {section} section")
                
                # Check credentials
                if 'shared' in config and 'credentials' in config['shared']:
                    creds = config['shared']['credentials']
                    required_creds = ['ANTHROPIC_API_KEY', 'SAP_BTP_CLIENT_ID', 'SAP_BTP_CLIENT_SECRET']
                    
                    for cred in required_creds:
                        if cred in creds and creds[cred]:
                            self.log_success(f"Credential {cred} is configured")
                        else:
                            self.log_issue(f"Credential {cred} is missing or empty")
                
            except Exception as e:
                self.log_issue(f"Error reading environment config: {str(e)}")
        else:
            self.log_issue("Environment configuration missing")
        
        return True
    
    def check_github_workflow(self):
        """Check GitHub Actions workflow"""
        print("\n🔄 Checking GitHub Actions workflow...")
        
        workflow_file = ".github/workflows/deploy.yml"
        if os.path.exists(workflow_file):
            self.log_success("GitHub Actions workflow exists")
            
            try:
                with open(workflow_file, 'r') as f:
                    content = f.read()
                
                # Check for required elements
                required_elements = [
                    'on:', 'jobs:', 'cf login', 'python deployment/deploy.py'
                ]
                
                for element in required_elements:
                    if element in content:
                        self.log_success(f"Workflow contains: {element}")
                    else:
                        self.log_warning(f"Workflow may be missing: {element}")
                        
            except Exception as e:
                self.log_issue(f"Error reading workflow file: {str(e)}")
        else:
            self.log_issue("GitHub Actions workflow missing")
        
        return True
    
    def check_deployment_scripts(self):
        """Check deployment automation scripts"""
        print("\n🚀 Checking deployment scripts...")
        
        scripts = {
            'Python deployment script': 'deployment/deploy.py',
            'Local setup script': 'deployment/scripts/deploy-local.bat',
            'Production deployment script': 'deployment/scripts/deploy-production.bat',
            'Management script': 'deployment/scripts/manage-env.bat'
        }
        
        for script_name, script_path in scripts.items():
            if os.path.exists(script_path):
                self.log_success(f"{script_name} exists")
            else:
                self.log_issue(f"{script_name} missing: {script_path}")
        
        return True
    
    def test_api_health(self):
        """Test if deployed APIs are responding"""
        print("\n🏥 Testing API health (if deployed)...")
        
        api_urls = [
            "https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com/api/health",
            "https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health",
            "https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health"
        ]
        
        for url in api_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log_success(f"API responding: {url}")
                else:
                    self.log_warning(f"API not responding (status {response.status_code}): {url}")
            except requests.exceptions.RequestException:
                self.log_warning(f"API not reachable: {url}")
        
        return True
    
    def check_git_status(self):
        """Check Git repository status"""
        print("\n📝 Checking Git repository status...")
        
        # Check if we're in a git repo
        output, error = self.run_command("git status", check_output=False)
        if error:
            self.log_issue("Not in a Git repository")
            return False
        
        self.log_success("In a Git repository")
        
        # Check for uncommitted changes
        output, error = self.run_command("git status --porcelain")
        if output:
            self.log_warning("Uncommitted changes detected")
            print(f"   Uncommitted files: {len(output.split())}")
        else:
            self.log_success("No uncommitted changes")
        
        # Check remote
        output, error = self.run_command("git remote -v")
        if output:
            self.log_success("Git remotes configured")
            for line in output.split('\n'):
                if 'imigrate' in line:
                    print(f"   {line}")
        else:
            self.log_warning("No Git remotes configured")
        
        return True
    
    def run_validation(self):
        """Run complete validation"""
        print("========================================")
        print("Cloud Foundry Deployment Validation")
        print("========================================")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Working Directory: {self.root_dir}")
        
        # Run all checks
        self.check_git_status()
        self.check_cf_cli()
        self.check_app_manifests()
        self.check_dependencies()
        self.check_environment_config()
        self.check_github_workflow()
        self.check_deployment_scripts()
        self.test_api_health()
        
        # Summary
        print(f"\n{'='*50}")
        print("VALIDATION SUMMARY")
        print(f"{'='*50}")
        
        print(f"✅ Successes: {len(self.successes)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")
        
        if self.issues:
            print(f"\n❌ CRITICAL ISSUES TO FIX:")
            for issue in self.issues:
                print(f"   - {issue}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS TO CONSIDER:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        # Overall assessment
        if len(self.issues) == 0:
            print(f"\n🎉 VALIDATION PASSED!")
            print(f"✅ Your project is ready for Cloud Foundry deployment!")
            print(f"\n🚀 Next steps:")
            print(f"   1. Set up GitHub Secrets (CF credentials)")
            print(f"   2. Push to main branch to trigger deployment")
            print(f"   3. Monitor GitHub Actions for deployment status")
            return True
        else:
            print(f"\n💥 VALIDATION FAILED!")
            print(f"❌ Fix the critical issues above before deploying.")
            return False

def main():
    """Main function"""
    validator = CFDeploymentValidator()
    
    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
