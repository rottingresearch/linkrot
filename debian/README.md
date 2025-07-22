# Building Debian Package for Linkrot

This directory contains all the necessary files to build a Debian package for linkrot.

## Prerequisites

### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install dpkg-dev debhelper dh-python python3-setuptools python3-build python3-pip
```

### On Windows (using WSL):
1. Install WSL and a Ubuntu/Debian distribution
2. Run the above commands in your WSL environment

## Quick Build

### Method 1: Use the setup script (recommended)
```bash
# Make sure you're in the linkrot project root directory
python3 setup-deb-build.py
./build-deb.sh
```

### Method 2: Manual build
```bash
# Make sure you're in the linkrot project root directory
chmod +x debian/rules
dpkg-buildpackage -us -uc -b
```

### Method 3: Windows batch file (uses WSL)
```cmd
build-deb.bat
```

## Package Information

This will create two packages:

1. **python3-linkrot** - The Python library package
   - Contains the linkrot Python module
   - Can be imported with `import linkrot`
   - Dependencies: python3-pymupdf, python3-chardet, python3-lxml, python3-requests

2. **linkrot** - The command-line tool package
   - Contains the `linkrot` command
   - Depends on python3-linkrot
   - Installed to `/usr/bin/linkrot`

## Installation

After building, install both packages:
```bash
# Install from the parent directory where .deb files are created
sudo dpkg -i ../python3-linkrot_*.deb ../linkrot_*.deb

# Fix any dependency issues if they occur
sudo apt-get install -f
```

## Testing Installation

```bash
# Test command-line tool
linkrot --help
linkrot --version

# Test Python import
python3 -c "import linkrot; print(linkrot.__version__)"

# Test with a PDF (example)
linkrot example.pdf -r -c
```

## Package Structure

```
debian/
├── changelog          # Package version history
├── compat            # Debhelper compatibility level
├── control           # Package dependencies and descriptions
├── copyright         # Copyright information
├── rules             # Build rules (Makefile)
├── source/
│   └── format        # Source package format
├── linkrot.install   # Files to install for linkrot package
├── linkrot.1         # Manual page for linkrot command
└── linkrot.manpages  # Manual page installation
```

## Customization

### Version Updates
Update the version in:
1. `linkrot/__init__.py` (main version)
2. `debian/changelog` (add new entry at top)

### Dependencies
Update dependencies in:
1. `pyproject.toml` (Python dependencies)
2. `debian/control` (Debian package dependencies)

### Build Rules
Modify `debian/rules` for custom build behavior.

## Troubleshooting

### Common Issues

1. **Missing build dependencies**
   ```bash
   sudo apt-get install dpkg-dev debhelper dh-python
   ```

2. **Python module not found during build**
   ```bash
   pip3 install build setuptools wheel
   ```

3. **Permission denied on scripts**
   ```bash
   chmod +x debian/rules build-deb.sh
   ```

4. **Package conflicts**
   ```bash
   sudo apt-get remove python3-linkrot linkrot
   # Then reinstall
   ```

### Build Logs
Check build logs if the build fails:
```bash
# The build process will show detailed output
# Look for specific error messages about missing dependencies or build failures
```

### Clean Build
To start fresh:
```bash
# Clean build artifacts
rm -rf debian/python3-linkrot/ debian/linkrot/ debian/.debhelper/
rm -f debian/files debian/*substvars debian/debhelper-build-stamp

# Rebuild
dpkg-buildpackage -us -uc -b
```

## Distribution

The built packages can be:
1. Installed locally with `dpkg -i`
2. Added to a personal APT repository
3. Submitted to Debian/Ubuntu repositories (with proper sponsorship)
4. Distributed as standalone .deb files

## Notes

- The packages follow Debian packaging standards
- They are built for "all" architectures (pure Python)
- GPLv3 license is properly declared
- Man page is included for the command-line tool
- Both library and CLI tool are packaged separately for flexibility
