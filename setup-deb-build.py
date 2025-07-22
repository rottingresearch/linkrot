#!/usr/bin/env python3
"""
Setup script for preparing linkrot Debian package build environment.
This script helps ensure all dependencies are in place and files are properly configured.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_command(command):
    """Check if a command exists in PATH."""
    return shutil.which(command) is not None

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Main setup function."""
    print("Linkrot Debian Package Build Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("Error: pyproject.toml not found.")
        print("Please run this script from the linkrot project root directory.")
        sys.exit(1)
    
    if not os.path.exists("debian"):
        print("Error: debian directory not found.")
        print("Please ensure the debian packaging files are present.")
        sys.exit(1)
    
    print("✓ Found project files")
    
    # Check for required build tools
    required_commands = [
        ("dpkg-buildpackage", "dpkg-dev"),
        ("dh", "debhelper"),
        ("python3", "python3"),
        ("pip3", "python3-pip")
    ]
    
    missing_packages = []
    
    for command, package in required_commands:
        if check_command(command):
            print(f"✓ Found {command}")
        else:
            print(f"✗ Missing {command} (package: {package})")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with:")
        print(f"  sudo apt-get install {' '.join(missing_packages)}")
        
        # Ask if user wants to install automatically
        response = input("\nInstall missing packages automatically? [y/N]: ")
        if response.lower().startswith('y'):
            print("Installing packages...")
            cmd = f"sudo apt-get update && sudo apt-get install -y {' '.join(missing_packages)}"
            result = run_command(cmd)
            if result and result.returncode == 0:
                print("✓ Packages installed successfully")
            else:
                print("✗ Package installation failed")
                sys.exit(1)
        else:
            print("Please install the missing packages manually.")
            sys.exit(1)
    
    # Check Python dependencies
    print("\nChecking Python build dependencies...")
    python_deps = ["build", "setuptools", "wheel"]
    
    missing_python_deps = []
    for dep in python_deps:
        try:
            __import__(dep)
            print(f"✓ Found python3-{dep}")
        except ImportError:
            print(f"✗ Missing python3-{dep}")
            missing_python_deps.append(dep)
    
    if missing_python_deps:
        print(f"\nMissing Python packages: {', '.join(missing_python_deps)}")
        print("Install them with:")
        print(f"  pip3 install {' '.join(missing_python_deps)}")
        
        response = input("\nInstall missing Python packages? [y/N]: ")
        if response.lower().startswith('y'):
            cmd = f"pip3 install {' '.join(missing_python_deps)}"
            result = run_command(cmd)
            if result and result.returncode == 0:
                print("✓ Python packages installed successfully")
            else:
                print("✗ Python package installation failed")
                sys.exit(1)
    
    # Make scripts executable
    print("\nSetting up build scripts...")
    
    scripts = ["debian/rules", "build-deb.sh"]
    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"✓ Made {script} executable")
    
    # Verify package metadata
    print("\nVerifying package metadata...")
    
    try:
        # Read version from __init__.py
        init_file = Path("linkrot/__init__.py")
        if init_file.exists():
            content = init_file.read_text()
            for line in content.split('\n'):
                if line.startswith('__version__'):
                    version = line.split('=')[1].strip().strip('"\'')
                    print(f"✓ Found version: {version}")
                    break
    except Exception as e:
        print(f"⚠ Could not verify version: {e}")
    
    # Check changelog
    changelog = Path("debian/changelog")
    if changelog.exists():
        try:
            first_line = changelog.read_text().split('\n')[0]
            print(f"✓ Changelog entry: {first_line}")
        except Exception as e:
            print(f"⚠ Could not read changelog: {e}")
    
    print("\nSetup complete!")
    print("\nTo build the Debian package:")
    print("  ./build-deb.sh")
    print("\nOr manually:")
    print("  dpkg-buildpackage -us -uc -b")
    
    print("\nBuild requirements summary:")
    print("- All required tools are installed")
    print("- Build scripts are executable")
    print("- Debian packaging files are present")
    print("- Ready to build!")

if __name__ == "__main__":
    main()
