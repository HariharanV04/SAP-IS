"""
Deployment Diagnostic Script
Check for common Cloud Foundry deployment issues
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_sizes():
    """Check for files that might be too large"""
    print("📁 Checking File Sizes")
    print("-" * 40)
    
    large_files = []
    total_size = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', '.env']):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                total_size += size
                
                # Flag files larger than 10MB
                if size > 10 * 1024 * 1024:
                    large_files.append((file_path, size / (1024 * 1024)))
                    
            except OSError:
                continue
    
    print(f"Total app size: {total_size / (1024 * 1024):.1f} MB")
    
    if large_files:
        print("⚠️ Large files found:")
        for file_path, size_mb in large_files:
            print(f"   {file_path}: {size_mb:.1f} MB")
    else:
        print("✅ No unusually large files found")
    
    # Check if total size is too large (CF has limits)
    if total_size > 1024 * 1024 * 1024:  # 1GB
        print("❌ App size exceeds 1GB - this will cause deployment failure")
        return False
    elif total_size > 512 * 1024 * 1024:  # 512MB
        print("⚠️ App size is quite large - consider cleanup")
    
    return True

def check_requirements():
    """Check requirements.txt for issues"""
    print("\n📦 Checking requirements.txt")
    print("-" * 40)
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    
    print(f"✅ requirements.txt found ({len(lines)} dependencies)")
    
    # Check for problematic dependencies
    problematic = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Check for version conflicts
        if '==' not in line and '>=' not in line and line.count('=') == 0:
            problematic.append(f"No version specified: {line}")
        
        # Check for known problematic packages
        if any(pkg in line.lower() for pkg in ['tensorflow', 'torch', 'opencv']):
            problematic.append(f"Heavy package detected: {line}")
    
    if problematic:
        print("⚠️ Potential issues:")
        for issue in problematic:
            print(f"   {issue}")
    else:
        print("✅ requirements.txt looks good")
    
    return True

def check_python_version():
    """Check Python version compatibility"""
    print("\n🐍 Checking Python Version")
    print("-" * 40)
    
    if os.path.exists('runtime.txt'):
        with open('runtime.txt', 'r') as f:
            runtime = f.read().strip()
        print(f"✅ runtime.txt found: {runtime}")
        
        # Check if it's a supported version
        if 'python-3.9' in runtime or 'python-3.10' in runtime or 'python-3.11' in runtime:
            print("✅ Python version is supported")
        else:
            print("⚠️ Python version might not be supported")
            return False
    else:
        print("⚠️ runtime.txt not found - CF will use default Python")
    
    return True

def check_procfile():
    """Check Procfile configuration"""
    print("\n⚙️ Checking Procfile")
    print("-" * 40)
    
    if not os.path.exists('Procfile'):
        print("❌ Procfile not found")
        return False
    
    with open('Procfile', 'r') as f:
        content = f.read().strip()
    
    print(f"✅ Procfile found: {content}")
    
    # Check for common issues
    if 'gunicorn' not in content:
        print("⚠️ Procfile doesn't use gunicorn")
    
    if 'app:app' not in content:
        print("⚠️ Procfile might not reference the correct Flask app")
    
    return True

def check_manifest():
    """Check manifest.yml"""
    print("\n📋 Checking manifest.yml")
    print("-" * 40)
    
    if not os.path.exists('manifest.yml'):
        print("⚠️ manifest.yml not found")
        return True  # Not required
    
    with open('manifest.yml', 'r') as f:
        content = f.read()
    
    print("✅ manifest.yml found")
    
    # Check for common issues
    issues = []
    if 'memory:' not in content:
        issues.append("No memory limit specified")
    
    if 'disk_quota:' not in content:
        issues.append("No disk quota specified")
    
    if 'buildpacks:' not in content and 'buildpack:' not in content:
        issues.append("No buildpack specified")
    
    if issues:
        print("⚠️ Potential issues:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ manifest.yml looks good")
    
    return True

def check_sensitive_files():
    """Check for files that shouldn't be deployed"""
    print("\n🔒 Checking for Sensitive Files")
    print("-" * 40)
    
    sensitive_patterns = [
        '.env',
        '.env.local',
        '.env.development',
        '*.key',
        '*.pem',
        'id_rsa',
        'secrets.json'
    ]
    
    found_sensitive = []
    
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            for pattern in sensitive_patterns:
                if pattern.replace('*', '') in file or file.endswith(pattern.replace('*', '')):
                    found_sensitive.append(file_path)
    
    if found_sensitive:
        print("⚠️ Sensitive files found (should be in .cfignore):")
        for file_path in found_sensitive:
            print(f"   {file_path}")
    else:
        print("✅ No sensitive files found")
    
    return len(found_sensitive) == 0

def check_cfignore():
    """Check .cfignore file"""
    print("\n🚫 Checking .cfignore")
    print("-" * 40)
    
    if not os.path.exists('.cfignore'):
        print("⚠️ .cfignore not found - all files will be uploaded")
        return False
    
    with open('.cfignore', 'r') as f:
        content = f.read()
    
    print("✅ .cfignore found")
    
    # Check for common exclusions
    recommended = ['.env', '__pycache__', '*.pyc', '.git', 'node_modules', 'tests/']
    missing = []
    
    for item in recommended:
        if item not in content:
            missing.append(item)
    
    if missing:
        print("⚠️ Consider adding to .cfignore:")
        for item in missing:
            print(f"   {item}")
    
    return True

def main():
    """Run all diagnostic checks"""
    print("🔍 Cloud Foundry Deployment Diagnostic")
    print("=" * 60)
    
    checks = [
        check_file_sizes,
        check_requirements,
        check_python_version,
        check_procfile,
        check_manifest,
        check_sensitive_files,
        check_cfignore
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append(False)
    
    print("\n📊 Diagnostic Summary")
    print("-" * 40)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All checks passed! Deployment should succeed.")
    elif passed >= total - 1:
        print("⚠️ Minor issues found. Deployment might succeed.")
    else:
        print("❌ Multiple issues found. Fix these before deploying.")
    
    print("\n💡 To get detailed CF logs:")
    print("   cf logs it-resonance-main-api --recent")
    print("   cf events it-resonance-main-api")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
