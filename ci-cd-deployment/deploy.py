#!/usr/bin/env python3
"""
Complete Deployment Automation for IFA Project
Handles local development and Cloud Foundry production deployments
"""

import json
import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Any
import time

class DeploymentManager:
    def __init__(self, config_path: str = "ci-cd-deployment/config/environments.json"):
        """Initialize deployment manager with configuration"""
        # Handle being run from different directories
        script_dir = Path(__file__).parent
        self.root_dir = Path.cwd()

        if config_path == "ci-cd-deployment/config/environments.json":
            # Try multiple possible locations for the config file
            possible_paths = [
                "ci-cd-deployment/config/environments.json",  # From root
                "config/environments.json",  # From ci-cd-deployment dir
                script_dir / "config/environments.json",  # Relative to script
                self.root_dir / "ci-cd-deployment/config/environments.json"  # Absolute from root
            ]

            config_found = False
            for path in possible_paths:
                test_path = Path(path) if isinstance(path, str) else path
                if test_path.exists():
                    self.config_path = str(test_path)
                    config_found = True
                    break

            if not config_found:
                self.config_path = config_path  # Fallback to original
        else:
            # Custom config path provided
            self.config_path = config_path

        self.config = self.load_config()

    def resolve_app_path(self, app_name: str) -> str:
        """Resolve app path relative to root directory"""
        app_path = self.config['cf_apps'][app_name]['path']
        if app_path.startswith('./'):
            app_path = app_path[2:]  # Remove './'
        return str(self.root_dir / app_path)

    def load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        try:
            # Use the resolved config path directly
            config_file = Path(self.config_path)
            if not config_file.is_absolute():
                config_file = self.root_dir / self.config_path

            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {config_file}")
            print(f"   Root directory: {self.root_dir}")
            print(f"   Config path: {self.config_path}")
            print(f"   Attempted path: {config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def run_command(self, command: str, cwd: str = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run shell command with error handling"""
        print(f"🔧 Running: {command}")
        if cwd:
            print(f"📁 Working directory: {cwd}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                print(f"✅ Output: {result.stdout.strip()}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {command}")
            print(f"❌ Error: {e.stderr}")
            if check:
                sys.exit(1)
            return e
    
    def create_env_file(self, app_name: str, environment: str) -> None:
        """Create .env file for local development"""
        env_config = {**self.config['shared']['credentials']}
        env_config.update(self.config[environment][app_name])

        app_path = self.resolve_app_path(app_name)
        env_file_path = os.path.join(app_path, '.env')
        
        print(f"📝 Creating .env file for {app_name} at {env_file_path}")
        
        with open(env_file_path, 'w') as f:
            f.write(f"# Auto-generated .env file for {app_name} - {environment}\n")
            f.write(f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Created .env file for {app_name}")
    
    def set_cf_env_vars(self, app_name: str) -> None:
        """Set Cloud Foundry environment variables"""
        cf_app_name = self.config['cf_apps'][app_name]['name']

        # Combine shared credentials with production config
        env_vars = {**self.config['shared']['credentials']}
        env_vars.update(self.config['production'][app_name])

        print(f"🔧 Setting environment variables for {cf_app_name}")

        for key, value in env_vars.items():
            command = f'cf set-env {cf_app_name} {key} "{value}"'
            self.run_command(command)

        print(f"✅ Environment variables set for {cf_app_name}")
    
    def deploy_to_cf(self, app_name: str, build_frontend: bool = False) -> None:
        """Deploy application to Cloud Foundry"""
        app_config = self.config['cf_apps'][app_name]
        app_path = self.resolve_app_path(app_name)
        cf_app_name = app_config['name']
        
        print(f"🚀 Deploying {app_name} to Cloud Foundry...")
        
        # Build frontend if needed
        if build_frontend and app_name == 'frontend':
            print("🔨 Building frontend...")
            # Remove platform-specific lock file to avoid platform conflicts
            lock_file = os.path.join(app_path, 'package-lock.json')
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print("🗑️ Removed platform-specific package-lock.json")

            self.run_command("npm install", cwd=app_path)

            # Install Linux-specific Rollup dependency for CI deployment
            print("🔧 Installing Linux-specific Rollup dependency...")
            self.run_command("npm uninstall @rollup/rollup-win32-x64-msvc || true", cwd=app_path)
            self.run_command("npm install @rollup/rollup-linux-x64-gnu --save-optional", cwd=app_path)

            # Install terser for production builds
            self.run_command("npm install terser --save-dev", cwd=app_path)

            self.run_command("npm run build", cwd=app_path)
        
        # Deploy the app first
        print(f"📦 Pushing {cf_app_name} to Cloud Foundry...")
        self.run_command("cf push", cwd=app_path)

        # Set environment variables after app is created
        self.set_cf_env_vars(app_name)

        # Restart app to apply environment variables
        print(f"🔄 Restarting {cf_app_name} to apply environment variables...")
        self.run_command(f"cf restart {cf_app_name}")

        print(f"✅ Successfully deployed {cf_app_name}")
    
    def setup_local_development(self, apps: List[str] = None) -> None:
        """Setup local development environment"""
        if apps is None:
            apps = list(self.config['cf_apps'].keys())
        
        print("🏠 Setting up local development environment...")
        
        for app_name in apps:
            print(f"\n📋 Setting up {app_name} for local development...")
            self.create_env_file(app_name, 'local')
        
        print("\n✅ Local development environment setup complete!")
        print("\n🚀 To start local development:")
        print("  Main API: cd app && python app.py")
        print("  MuleToIS API: cd MuleToIS-API && python app.py")
        print("  BoomiToIS API: cd BoomiToIS-API && python app.py")
        print("  Frontend: cd IFA-Project/frontend && npm run dev")
    
    def deploy_all_to_cf(self) -> None:
        """Deploy all applications to Cloud Foundry"""
        print("🌐 Starting complete Cloud Foundry deployment...")
        
        # Deploy in order: APIs first, then frontend
        deployment_order = ['main_api', 'mule_api', 'boomi_api', 'gemma3_api', 'frontend']
        
        for app_name in deployment_order:
            print(f"\n{'='*50}")
            print(f"Deploying {app_name}")
            print(f"{'='*50}")
            
            build_frontend = (app_name == 'frontend')
            self.deploy_to_cf(app_name, build_frontend=build_frontend)
            
            # Wait a bit between deployments
            if app_name != 'frontend':
                print("⏳ Waiting 10 seconds before next deployment...")
                time.sleep(10)
        
        print(f"\n{'='*50}")
        print("🎉 All applications deployed successfully!")
        print(f"{'='*50}")
        self.show_deployment_status()
    
    def show_deployment_status(self) -> None:
        """Show deployment status and URLs"""
        print("\n📊 Deployment Status:")
        self.run_command("cf apps")
        
        print("\n🌐 Application URLs:")
        print("  Frontend: https://ifa-frontend.cfapps.eu10-005.hana.ondemand.com")
        print("  Main API: https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com")
        print("  MuleToIS API: https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com")
        print("  BoomiToIS API: https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com")
        
        print("\n🔍 Testing API Health:")
        health_urls = [
            "https://it-resonance-main-api.cfapps.eu10-005.hana.ondemand.com/api/health",
            "https://mule-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health",
            "https://boomi-to-is-api.cfapps.eu10-005.hana.ondemand.com/api/health"
        ]
        
        for url in health_urls:
            self.run_command(f"curl -s {url}", check=False)
    
    def restart_cf_apps(self) -> None:
        """Restart all Cloud Foundry applications"""
        print("🔄 Restarting all Cloud Foundry applications...")

        for app_name in self.config['cf_apps'].keys():
            cf_app_name = self.config['cf_apps'][app_name]['name']
            print(f"🔄 Restarting {cf_app_name}...")
            self.run_command(f"cf restart {cf_app_name}")

        print("✅ All applications restarted!")

    def clean_deployment(self) -> None:
        """Clean up deployment artifacts"""
        print("🧹 Cleaning deployment artifacts...")

        # Remove .env files
        for app_name in self.config['cf_apps'].keys():
            app_path = self.resolve_app_path(app_name)
            env_file = os.path.join(app_path, '.env')
            if os.path.exists(env_file):
                os.remove(env_file)
                print(f"🗑️ Removed {env_file}")

        # Remove frontend build artifacts
        frontend_dist = "IFA-Project/frontend/dist"
        if os.path.exists(frontend_dist):
            shutil.rmtree(frontend_dist)
            print(f"🗑️ Removed {frontend_dist}")

        print("✅ Cleanup complete!")

def main():
    parser = argparse.ArgumentParser(description="IFA Project Deployment Manager")
    parser.add_argument("command", choices=[
        "local", "deploy", "deploy-all", "status", "clean", "restart"
    ], help="Deployment command")
    parser.add_argument("--app", choices=[
        "main_api", "mule_api", "boomi_api", "gemma3_api", "frontend"
    ], help="Specific app to deploy")
    parser.add_argument("--config", default="ci-cd-deployment/config/environments.json",
                       help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    deployer = DeploymentManager(args.config)
    
    try:
        if args.command == "local":
            deployer.setup_local_development()
        
        elif args.command == "deploy":
            if not args.app:
                print("❌ --app parameter required for single app deployment")
                sys.exit(1)
            deployer.deploy_to_cf(args.app, build_frontend=(args.app == 'frontend'))
        
        elif args.command == "deploy-all":
            deployer.deploy_all_to_cf()
        
        elif args.command == "status":
            deployer.show_deployment_status()
        
        elif args.command == "clean":
            deployer.clean_deployment()

        elif args.command == "restart":
            deployer.restart_cf_apps()
    
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
