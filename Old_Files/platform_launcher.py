#!/usr/bin/env python3
"""
IS-Migration Platform Launcher
A unified Python script to manage the IS-Migration platform across all environments.
"""

import os
import sys
import subprocess
import time
import json
import platform
import signal
import psutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class PlatformLauncher:
    def __init__(self):
        self.root_dir = Path(__file__).parent.absolute()
        self.is_windows = platform.system() == "Windows"
        self.processes = {}
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration for services"""
        return {
            "services": {
                "main_api": {
                    "name": "Main API",
                    "port": 5000,
                    "path": "app",
                    "command": ["python", "app.py"],
                    "health_endpoint": "/api/health"
                },
                "boomi_api": {
                    "name": "BoomiToIS API", 
                    "port": 5003,
                    "path": "BoomiToIS-API",
                    "command": ["python", "app.py"],
                    "health_endpoint": "/api/health"
                },
                "mule_api": {
                    "name": "MuleToIS API",
                    "port": 5001, 
                    "path": "MuleToIS-API",
                    "command": ["python", "app.py"],
                    "health_endpoint": "/api/health"
                },
                "gemma3_api": {
                    "name": "Gemma-3 API",
                    "port": 5002,
                    "path": "MuleToIS-API-Gemma3", 
                    "command": ["python", "app.py"],
                    "health_endpoint": "/api/health"
                },
                "frontend": {
                    "name": "Frontend",
                    "port": 5173,
                    "path": "IFA-Project/frontend",
                    "command": ["npm", "run", "dev"],
                    "health_endpoint": "/"
                }
            },
            "deployment": {
                "script_path": "ci-cd-deployment/deploy.py",
                "apps": ["main_api", "boomi_api", "mule_api", "gemma3_api", "frontend"]
            }
        }

    def print_header(self):
        """Print the application header"""
        print(f"\n{Colors.CYAN}{'='*60}")
        print(f"{Colors.CYAN}IS-Migration Platform - Python Launcher")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

    def print_menu(self):
        """Print the main menu"""
        print(f"{Colors.YELLOW}What would you like to do?{Colors.RESET}\n")
        
        print(f"{Colors.BLUE}🚀 DEVELOPMENT{Colors.RESET}")
        print("  1. Setup Development Environment")
        print("  2. Start All Servers (Local)")
        print("  3. Start Individual Service")
        print("  4. Stop All Servers")
        print()
        
        print(f"{Colors.BLUE}📊 MONITORING{Colors.RESET}")
        print("  5. Check Server Status")
        print("  6. View Service Logs")
        print("  7. Health Check All Services")
        print()
        
        print(f"{Colors.BLUE}🌐 DEPLOYMENT{Colors.RESET}")
        print("  8. Deploy to Production (All)")
        print("  9. Deploy Single App")
        print("  10. Check Deployment Status")
        print()
        
        print(f"{Colors.BLUE}🔧 UTILITIES{Colors.RESET}")
        print("  11. Clean Environment")
        print("  12. Install Dependencies")
        print("  13. Show Help")
        print("  14. Exit")
        print()

    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        print(f"{Colors.YELLOW}Checking prerequisites...{Colors.RESET}")

        # Try different command variations for better compatibility
        required_tools = [
            ("python", ["python", "--version"]),
            ("node", ["node", "--version"]),
            ("npm", ["npm", "--version"])
        ]

        missing_tools = []
        node_installed = False

        for tool_name, command in required_tools:
            tool_found = False

            # Try the primary command
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10, shell=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    if version:  # Make sure we got actual output
                        print(f"  ✅ {tool_name}: {version}")
                        tool_found = True
                        if tool_name == "node":
                            node_installed = True
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                pass

            # If npm failed, try alternative approaches
            if not tool_found and tool_name == "npm":
                # Try with cmd /c on Windows
                if self.is_windows:
                    try:
                        result = subprocess.run(["cmd", "/c", "npm", "--version"],
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0 and result.stdout.strip():
                            version = result.stdout.strip()
                            print(f"  ✅ {tool_name}: {version}")
                            tool_found = True
                    except:
                        pass

                # Try npx npm --version as fallback
                if not tool_found:
                    try:
                        result = subprocess.run(["npx", "npm", "--version"],
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0 and result.stdout.strip():
                            version = result.stdout.strip()
                            print(f"  ✅ {tool_name}: {version} (via npx)")
                            tool_found = True
                    except:
                        pass

            if not tool_found:
                missing_tools.append(tool_name)

        if missing_tools:
            print(f"\n{Colors.RED}❌ Missing required tools: {', '.join(missing_tools)}{Colors.RESET}")

            # Special handling for npm when node is installed
            if "npm" in missing_tools and node_installed:
                print(f"\n{Colors.YELLOW}🔧 Node.js is installed but npm is missing.{Colors.RESET}")
                print(f"{Colors.CYAN}Possible solutions:{Colors.RESET}")
                print("1. Reinstall Node.js from https://nodejs.org/ (includes npm)")
                print("2. Install npm separately:")
                if self.is_windows:
                    print("   - Download npm from https://www.npmjs.com/get-npm")
                    print("   - Or use: winget install OpenJS.NodeJS")
                else:
                    print("   - Ubuntu/Debian: sudo apt install npm")
                    print("   - macOS: brew install npm")
                    print("   - Or reinstall Node.js with npm included")

                # Try to continue without npm for backend-only setup
                print(f"\n{Colors.YELLOW}Would you like to continue with backend-only setup? (y/n){Colors.RESET}")
                choice = input().strip().lower()
                if choice == 'y':
                    print(f"{Colors.YELLOW}⚠️  Continuing without npm - Frontend will not be available{Colors.RESET}")
                    return True

            print(f"\n{Colors.YELLOW}Please install the missing tools and try again.{Colors.RESET}")
            return False

        print(f"\n{Colors.GREEN}✅ All prerequisites satisfied!{Colors.RESET}")
        return True

    def setup_environment(self):
        """Setup development environment"""
        print(f"\n{Colors.CYAN}🏠 Setting up development environment...{Colors.RESET}\n")
        
        if not self.check_prerequisites():
            return
        
        services_to_setup = ["main_api", "boomi_api", "mule_api", "gemma3_api"]
        
        for service_key in services_to_setup:
            service = self.config["services"][service_key]
            print(f"{Colors.YELLOW}Installing {service['name']} dependencies...{Colors.RESET}")
            
            service_path = self.root_dir / service["path"]
            requirements_file = service_path / "requirements.txt"
            
            if requirements_file.exists():
                try:
                    subprocess.run(
                        ["pip", "install", "-r", "requirements.txt"],
                        cwd=service_path,
                        check=True,
                        capture_output=True
                    )
                    print(f"  ✅ {service['name']} dependencies installed")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ Failed to install {service['name']} dependencies: {e}")
            else:
                print(f"  ⚠️  No requirements.txt found for {service['name']}")
        
        # Setup frontend
        print(f"{Colors.YELLOW}Installing Frontend dependencies...{Colors.RESET}")
        frontend_path = self.root_dir / self.config["services"]["frontend"]["path"]

        if (frontend_path / "package.json").exists():
            npm_command = self._get_npm_command()
            if npm_command:
                try:
                    subprocess.run(npm_command + ["install"], cwd=frontend_path, check=True, capture_output=True)
                    print(f"  ✅ Frontend dependencies installed")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ Failed to install Frontend dependencies: {e}")
                    print(f"     You may need to run: cd {frontend_path} && npm install")
            else:
                print(f"  ⚠️  npm not found - skipping Frontend dependencies")
                print(f"     Install npm and run this setup again to enable Frontend")
        else:
            print(f"  ⚠️  No package.json found for Frontend")

        print(f"\n{Colors.GREEN}✅ Development environment setup completed!{Colors.RESET}")

        # Check if npm is available for final message
        try:
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"{Colors.YELLOW}Note: Frontend dependencies may not be installed due to missing npm{Colors.RESET}")
            print(f"{Colors.CYAN}To enable Frontend: Install npm and run setup again{Colors.RESET}")

    def _get_npm_command(self) -> Optional[List[str]]:
        """Get the working npm command"""
        # Try different npm command variations
        npm_commands = [
            ["npm"],
            ["cmd", "/c", "npm"] if self.is_windows else ["npm"],
            ["npx", "npm"]
        ]

        for cmd in npm_commands:
            try:
                result = subprocess.run(cmd + ["--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    return cmd
            except:
                continue

        return None

    def _check_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        try:
            if tool_name == "npm":
                return self._get_npm_command() is not None
            elif tool_name == "node":
                subprocess.run(["node", "--version"], capture_output=True, check=True)
            elif tool_name == "python":
                subprocess.run(["python", "--version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def start_all_servers(self):
        """Start all services locally"""
        print(f"\n{Colors.CYAN}🚀 Starting all servers locally...{Colors.RESET}\n")
        
        if not self.check_prerequisites():
            return
        
        # Create logs directory
        logs_dir = self.root_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for service_key, service in self.config["services"].items():
            print(f"{Colors.BLUE}Starting {service['name']} (Port {service['port']})...{Colors.RESET}")

            # Special handling for frontend (npm dependency)
            if service_key == "frontend":
                npm_command = self._get_npm_command()
                if not npm_command:
                    print(f"  ⚠️  Skipping {service['name']} - npm not available")
                    continue
                # Use the detected npm command
                command = npm_command + ["run", "dev"]
            else:
                command = service["command"]

            service_path = self.root_dir / service["path"]
            log_file = logs_dir / f"{service_key}_{timestamp}.log"

            try:
                # Open log file for writing
                log_handle = open(log_file, 'w')

                # Start the process
                process = subprocess.Popen(
                    command,
                    cwd=service_path,
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                self.processes[service_key] = {
                    "process": process,
                    "log_file": log_file,
                    "log_handle": log_handle,
                    "service": service
                }

                print(f"  ✅ {service['name']} started (PID: {process.pid})")
                time.sleep(2)  # Give service time to start

            except Exception as e:
                print(f"  ❌ Failed to start {service['name']}: {e}")
        
        print(f"\n{Colors.GREEN}{'='*50}")
        print(f"{Colors.GREEN}All servers started!{Colors.RESET}")
        print(f"{Colors.GREEN}{'='*50}{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}Service URLs:{Colors.RESET}")
        for service_key, service in self.config["services"].items():
            print(f"  {Colors.BLUE}{service['name']:<15}{Colors.RESET} http://localhost:{service['port']}")
        
        print(f"\n{Colors.YELLOW}Log files created in: {logs_dir}{Colors.RESET}")
        print(f"{Colors.YELLOW}Use option 5 to check server status{Colors.RESET}")

    def start_individual_service(self):
        """Start a single service"""
        print(f"\n{Colors.CYAN}🚀 Start Individual Service{Colors.RESET}\n")
        
        services = list(self.config["services"].items())
        
        print("Available services:")
        for i, (key, service) in enumerate(services, 1):
            print(f"  {i}. {service['name']} (Port {service['port']})")
        print(f"  {len(services) + 1}. Back to main menu")
        
        try:
            choice = int(input(f"\nEnter your choice (1-{len(services) + 1}): "))
            if choice == len(services) + 1:
                return
            if 1 <= choice <= len(services):
                service_key, service = services[choice - 1]
                self._start_single_service(service_key, service)
            else:
                print(f"{Colors.RED}Invalid choice{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.RESET}")

    def _start_single_service(self, service_key: str, service: Dict):
        """Start a single service"""
        print(f"\n{Colors.BLUE}Starting {service['name']}...{Colors.RESET}")

        # Special handling for frontend (npm dependency)
        if service_key == "frontend":
            npm_command = self._get_npm_command()
            if not npm_command:
                print(f"❌ Cannot start {service['name']} - npm not available")
                print(f"Please install npm and try again")
                return
            command = npm_command + ["run", "dev"]
        else:
            command = service["command"]

        service_path = self.root_dir / service["path"]

        try:
            process = subprocess.Popen(
                command,
                cwd=service_path
            )

            print(f"✅ {service['name']} started (PID: {process.pid})")
            print(f"🌐 URL: http://localhost:{service['port']}")
            print(f"📁 Path: {service_path}")
            print(f"\n{Colors.YELLOW}Press Ctrl+C to stop the service{Colors.RESET}")

            # Wait for the process
            process.wait()

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Stopping {service['name']}...{Colors.RESET}")
            process.terminate()
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")

    def stop_all_servers(self):
        """Stop all running servers"""
        print(f"\n{Colors.CYAN}🛑 Stopping all servers...{Colors.RESET}\n")
        
        # Stop processes started by this script
        for service_key, proc_info in self.processes.items():
            try:
                process = proc_info["process"]
                service = proc_info["service"]
                
                if process.poll() is None:  # Process is still running
                    print(f"{Colors.BLUE}Stopping {service['name']}...{Colors.RESET}")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                        print(f"  ✅ {service['name']} stopped gracefully")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        print(f"  ⚠️  {service['name']} force killed")
                
                # Close log file handle
                if "log_handle" in proc_info:
                    proc_info["log_handle"].close()
                    
            except Exception as e:
                print(f"  ❌ Error stopping {service_key}: {e}")
        
        # Clear the processes dict
        self.processes.clear()
        
        # Also kill any processes running on our ports
        ports = [service["port"] for service in self.config["services"].values()]
        self._kill_processes_on_ports(ports)
        
        print(f"\n{Colors.GREEN}✅ All servers stopped!{Colors.RESET}")

    def _kill_processes_on_ports(self, ports: List[int]):
        """Kill processes running on specified ports"""
        for port in ports:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    try:
                        connections = proc.info['connections']
                        if connections:
                            for conn in connections:
                                if conn.laddr.port == port:
                                    print(f"  🔪 Killing process {proc.info['pid']} on port {port}")
                                    proc.kill()
                                    break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                print(f"  ⚠️  Could not check port {port}: {e}")

    def check_server_status(self):
        """Check the status of all servers"""
        print(f"\n{Colors.CYAN}📊 Checking server status...{Colors.RESET}\n")
        
        for service_key, service in self.config["services"].items():
            port = service["port"]
            name = service["name"]
            
            # Check if port is in use
            port_in_use = False
            try:
                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    try:
                        connections = proc.info['connections']
                        if connections:
                            for conn in connections:
                                if conn.laddr.port == port:
                                    port_in_use = True
                                    print(f"{Colors.GREEN}✅ {name:<15} - Running (Port {port}, PID {proc.info['pid']}){Colors.RESET}")
                                    break
                        if port_in_use:
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception:
                pass
            
            if not port_in_use:
                print(f"{Colors.RED}❌ {name:<15} - Not running (Port {port}){Colors.RESET}")

    def view_service_logs(self):
        """View logs for services"""
        print(f"\n{Colors.CYAN}📊 Service Logs{Colors.RESET}\n")
        
        logs_dir = self.root_dir / "logs"
        if not logs_dir.exists():
            print(f"{Colors.RED}No logs directory found. Start services first.{Colors.RESET}")
            return
        
        log_files = list(logs_dir.glob("*.log"))
        if not log_files:
            print(f"{Colors.RED}No log files found.{Colors.RESET}")
            return
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print("Available log files:")
        for i, log_file in enumerate(log_files[:10], 1):  # Show last 10 files
            print(f"  {i}. {log_file.name}")
        
        try:
            choice = int(input(f"\nEnter your choice (1-{min(10, len(log_files))}): "))
            if 1 <= choice <= len(log_files):
                log_file = log_files[choice - 1]
                print(f"\n{Colors.YELLOW}Showing last 50 lines of {log_file.name}:{Colors.RESET}\n")
                
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        for line in lines[-50:]:
                            print(line.rstrip())
                except Exception as e:
                    print(f"{Colors.RED}Error reading log file: {e}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid choice{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.RESET}")

    def health_check_all(self):
        """Perform health check on all services"""
        print(f"\n{Colors.CYAN}🏥 Health Check - All Services{Colors.RESET}\n")
        
        try:
            import requests
        except ImportError:
            print(f"{Colors.RED}requests library not installed. Run: pip install requests{Colors.RESET}")
            return
        
        for service_key, service in self.config["services"].items():
            url = f"http://localhost:{service['port']}{service['health_endpoint']}"
            
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✅ {service['name']:<15} - Healthy{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⚠️  {service['name']:<15} - Responding but status {response.status_code}{Colors.RESET}")
            except requests.exceptions.ConnectionError:
                print(f"{Colors.RED}❌ {service['name']:<15} - Not responding{Colors.RESET}")
            except requests.exceptions.Timeout:
                print(f"{Colors.YELLOW}⚠️  {service['name']:<15} - Timeout{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}❌ {service['name']:<15} - Error: {e}{Colors.RESET}")

    def deploy_to_production(self):
        """Deploy all apps to production"""
        print(f"\n{Colors.CYAN}🌐 Deploy to Production (All Apps){Colors.RESET}\n")
        
        deploy_script = self.root_dir / self.config["deployment"]["script_path"]
        
        if not deploy_script.exists():
            print(f"{Colors.RED}Deployment script not found: {deploy_script}{Colors.RESET}")
            return
        
        confirm = input(f"{Colors.YELLOW}Are you sure you want to deploy to production? (y/N): {Colors.RESET}")
        if confirm.lower() != 'y':
            print("Deployment cancelled.")
            return
        
        print(f"{Colors.BLUE}Starting deployment process...{Colors.RESET}")
        
        try:
            result = subprocess.run(
                ["python", str(deploy_script), "--all"],
                cwd=deploy_script.parent,
                text=True
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Deployment completed successfully!{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Deployment failed with exit code {result.returncode}{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}❌ Deployment error: {e}{Colors.RESET}")

    def deploy_single_app(self):
        """Deploy a single app to production"""
        print(f"\n{Colors.CYAN}🌐 Deploy Single App{Colors.RESET}\n")
        
        apps = self.config["deployment"]["apps"]
        
        print("Available applications:")
        for i, app in enumerate(apps, 1):
            service = self.config["services"][app]
            print(f"  {i}. {service['name']}")
        print(f"  {len(apps) + 1}. Back to main menu")
        
        try:
            choice = int(input(f"\nEnter your choice (1-{len(apps) + 1}): "))
            if choice == len(apps) + 1:
                return
            if 1 <= choice <= len(apps):
                app_key = apps[choice - 1]
                self._deploy_single_app(app_key)
            else:
                print(f"{Colors.RED}Invalid choice{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid input{Colors.RESET}")

    def _deploy_single_app(self, app_key: str):
        """Deploy a single application"""
        service = self.config["services"][app_key]
        deploy_script = self.root_dir / self.config["deployment"]["script_path"]
        
        if not deploy_script.exists():
            print(f"{Colors.RED}Deployment script not found: {deploy_script}{Colors.RESET}")
            return
        
        confirm = input(f"{Colors.YELLOW}Deploy {service['name']} to production? (y/N): {Colors.RESET}")
        if confirm.lower() != 'y':
            print("Deployment cancelled.")
            return
        
        print(f"{Colors.BLUE}Deploying {service['name']}...{Colors.RESET}")
        
        try:
            result = subprocess.run(
                ["python", str(deploy_script), "--app", app_key],
                cwd=deploy_script.parent,
                text=True
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {service['name']} deployed successfully!{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Deployment failed with exit code {result.returncode}{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}❌ Deployment error: {e}{Colors.RESET}")

    def check_deployment_status(self):
        """Check deployment status"""
        print(f"\n{Colors.CYAN}🌐 Checking deployment status...{Colors.RESET}\n")
        
        deploy_script = self.root_dir / self.config["deployment"]["script_path"]
        
        if not deploy_script.exists():
            print(f"{Colors.RED}Deployment script not found: {deploy_script}{Colors.RESET}")
            return
        
        try:
            result = subprocess.run(
                ["python", str(deploy_script), "--status"],
                cwd=deploy_script.parent,
                text=True
            )
            
            if result.returncode != 0:
                print(f"{Colors.RED}❌ Failed to check deployment status{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}❌ Error checking deployment status: {e}{Colors.RESET}")

    def clean_environment(self):
        """Clean up temporary files and logs"""
        print(f"\n{Colors.CYAN}🔧 Cleaning environment...{Colors.RESET}\n")
        
        confirm = input(f"{Colors.YELLOW}This will clean up logs and temporary files. Continue? (y/N): {Colors.RESET}")
        if confirm.lower() != 'y':
            print("Cleanup cancelled.")
            return
        
        # Clean up logs
        logs_dir = self.root_dir / "logs"
        if logs_dir.exists():
            try:
                for log_file in logs_dir.glob("*.log"):
                    log_file.unlink()
                print(f"✅ Cleaned up log files")
            except Exception as e:
                print(f"❌ Error cleaning logs: {e}")
        
        # Clean up Python cache
        for cache_dir in self.root_dir.rglob("__pycache__"):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"✅ Removed {cache_dir}")
            except Exception as e:
                print(f"❌ Error removing {cache_dir}: {e}")
        
        # Clean up temp directories
        temp_dirs = ["temp_extract", "genai_debug"]
        for temp_dir in temp_dirs:
            temp_path = self.root_dir / temp_dir
            if temp_path.exists():
                try:
                    import shutil
                    shutil.rmtree(temp_path)
                    print(f"✅ Removed {temp_dir}")
                except Exception as e:
                    print(f"❌ Error removing {temp_dir}: {e}")
        
        print(f"\n{Colors.GREEN}✅ Environment cleaned up!{Colors.RESET}")

    def install_dependencies(self):
        """Install Python dependencies for the launcher"""
        print(f"\n{Colors.CYAN}📦 Installing launcher dependencies...{Colors.RESET}\n")
        
        dependencies = ["psutil", "requests"]
        
        for dep in dependencies:
            try:
                subprocess.run(["pip", "install", dep], check=True, capture_output=True)
                print(f"✅ Installed {dep}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {dep}: {e}")

    def show_help(self):
        """Show help information"""
        print(f"\n{Colors.CYAN}📖 IS-Migration Platform Help{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}Quick Start:{Colors.RESET}")
        print("1. First time: Run option 12 (Install Dependencies)")
        print("2. Setup: Run option 1 (Setup Development Environment)")
        print("3. Daily use: Run option 2 (Start All Servers)")
        print("4. When done: Run option 4 (Stop All Servers)")
        print()
        
        print(f"{Colors.YELLOW}Server URLs (when running):{Colors.RESET}")
        for service in self.config["services"].values():
            print(f"- {service['name']}: http://localhost:{service['port']}")
        print()
        
        print(f"{Colors.YELLOW}Troubleshooting:{Colors.RESET}")
        print("- If servers won't start: Check if ports are already in use (option 5)")
        print("- If dependencies fail: Ensure Python and Node.js are installed")
        print("- If deployment fails: Check Cloud Foundry CLI is installed")
        print("- For logs: Use option 6 to view service logs")
        print()
        
        print(f"{Colors.YELLOW}For more help, see:{Colors.RESET}")
        print("- README.md")
        print("- HOW_TO_RUN_GUIDE.md") 
        print("- TECHNICAL_DESIGN.md")

    def run(self):
        """Main application loop"""
        # Setup signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print(f"\n{Colors.YELLOW}Shutting down...{Colors.RESET}")
            self.stop_all_servers()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        while True:
            try:
                self.print_header()
                self.print_menu()
                
                choice = input(f"Enter your choice (1-14): ").strip()
                
                if choice == "1":
                    self.setup_environment()
                elif choice == "2":
                    self.start_all_servers()
                elif choice == "3":
                    self.start_individual_service()
                elif choice == "4":
                    self.stop_all_servers()
                elif choice == "5":
                    self.check_server_status()
                elif choice == "6":
                    self.view_service_logs()
                elif choice == "7":
                    self.health_check_all()
                elif choice == "8":
                    self.deploy_to_production()
                elif choice == "9":
                    self.deploy_single_app()
                elif choice == "10":
                    self.check_deployment_status()
                elif choice == "11":
                    self.clean_environment()
                elif choice == "12":
                    self.install_dependencies()
                elif choice == "13":
                    self.show_help()
                elif choice == "14":
                    print(f"\n{Colors.GREEN}Thank you for using IS-Migration Platform!{Colors.RESET}")
                    self.stop_all_servers()
                    break
                else:
                    print(f"{Colors.RED}Invalid choice. Please enter 1-14.{Colors.RESET}")
                
                if choice != "14":
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Shutting down...{Colors.RESET}")
                self.stop_all_servers()
                break
            except Exception as e:
                print(f"{Colors.RED}An error occurred: {e}{Colors.RESET}")
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")

if __name__ == "__main__":
    launcher = PlatformLauncher()
    launcher.run()
