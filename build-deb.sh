#!/bin/bash

# Build script for creating Debian package for linkrot
# Usage: ./build-deb.sh

set -e

echo "Building Debian package for linkrot..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "debian" ]; then
    echo "Error: Please run this script from the linkrot project root directory"
    exit 1
fi

# Check for required tools
if ! command -v dpkg-buildpackage &> /dev/null; then
    echo "Error: dpkg-buildpackage not found. Please install:"
    echo "  sudo apt-get install dpkg-dev"
    exit 1
fi

if ! command -v dh &> /dev/null; then
    echo "Error: debhelper not found. Please install:"
    echo "  sudo apt-get install debhelper"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf debian/python3-linkrot/
rm -rf debian/linkrot/
rm -rf debian/.debhelper/
rm -rf debian/tmp/
rm -f debian/files
rm -f debian/debhelper-build-stamp
rm -f debian/python3-linkrot.substvars
rm -f debian/linkrot.substvars

# Install build dependencies if not present
echo "Checking build dependencies..."
missing_deps=""

if ! dpkg -l | grep -q python3-setuptools; then
    missing_deps="$missing_deps python3-setuptools"
fi

if ! dpkg -l | grep -q python3-build; then
    missing_deps="$missing_deps python3-build"
fi

if ! dpkg -l | grep -q dh-python; then
    missing_deps="$missing_deps dh-python"
fi

if [ -n "$missing_deps" ]; then
    echo "Installing missing build dependencies: $missing_deps"
    sudo apt-get update
    sudo apt-get install -y $missing_deps
fi

# Make debian/rules executable
chmod +x debian/rules

# Build the package
echo "Building package..."
dpkg-buildpackage -us -uc -b

echo ""
echo "Build complete!"
echo "Package files should be in the parent directory:"
ls -la ../*.deb 2>/dev/null || echo "No .deb files found in parent directory"

echo ""
echo "To install the package:"
echo "  sudo dpkg -i ../python3-linkrot_*.deb ../linkrot_*.deb"
echo "  sudo apt-get install -f  # Fix any dependency issues"

echo ""
echo "To test the installation:"
echo "  linkrot --help"
echo "  python3 -c 'import linkrot; print(linkrot.__version__)'"
