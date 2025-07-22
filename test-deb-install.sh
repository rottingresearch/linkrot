#!/bin/bash

# Test script for verifying linkrot Debian package installation
# Usage: ./test-deb-install.sh

echo "Testing linkrot Debian package installation..."
echo "=" * 50

# Test 1: Check if linkrot command is available
echo "Test 1: Checking linkrot command..."
if command -v linkrot &> /dev/null; then
    echo "✓ linkrot command found"
    linkrot --version
else
    echo "✗ linkrot command not found in PATH"
    echo "Make sure the linkrot package is installed:"
    echo "  sudo dpkg -i ../linkrot_*.deb"
    exit 1
fi

# Test 2: Check if Python module can be imported
echo -e "\nTest 2: Checking Python module import..."
if python3 -c "import linkrot; print('✓ linkrot module imported successfully')" 2>/dev/null; then
    python3 -c "import linkrot; print(f'✓ Version: {linkrot.__version__}')"
else
    echo "✗ Failed to import linkrot Python module"
    echo "Make sure the python3-linkrot package is installed:"
    echo "  sudo dpkg -i ../python3-linkrot_*.deb"
    exit 1
fi

# Test 3: Check help output
echo -e "\nTest 3: Checking help output..."
if linkrot --help | head -5 | grep -q "linkrot"; then
    echo "✓ Help output looks correct"
else
    echo "✗ Help output appears malformed"
fi

# Test 4: Check dependencies
echo -e "\nTest 4: Checking Python dependencies..."
deps=("requests" "chardet" "lxml" "fitz")  # fitz is PyMuPDF
all_deps_ok=true

for dep in "${deps[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo "✓ $dep is available"
    else
        echo "✗ $dep is missing"
        all_deps_ok=false
    fi
done

if $all_deps_ok; then
    echo "✓ All dependencies are satisfied"
else
    echo "✗ Some dependencies are missing"
    echo "Try: sudo apt-get install -f"
fi

# Test 5: Test with a real PDF (if available)
echo -e "\nTest 5: Testing with sample PDF..."
if [ -f "tests/pdfs/valid.pdf" ]; then
    echo "Testing with tests/pdfs/valid.pdf..."
    if linkrot tests/pdfs/valid.pdf | head -10 | grep -q "Document info"; then
        echo "✓ PDF processing works"
    else
        echo "✗ PDF processing failed"
    fi
else
    echo "ℹ No test PDF found, skipping real PDF test"
fi

# Test 6: Test retraction checking feature
echo -e "\nTest 6: Testing retraction checking feature..."
if linkrot --help | grep -q "\-r.*retraction"; then
    echo "✓ Retraction checking option is available"
else
    echo "✗ Retraction checking option not found in help"
fi

# Test 7: Check man page
echo -e "\nTest 7: Checking man page..."
if man linkrot 2>/dev/null | head -5 | grep -q "linkrot"; then
    echo "✓ Man page is installed and accessible"
else
    echo "⚠ Man page not found or not accessible"
fi

# Test 8: Check file permissions
echo -e "\nTest 8: Checking file permissions..."
if [ -x "$(command -v linkrot)" ]; then
    echo "✓ linkrot executable has correct permissions"
else
    echo "✗ linkrot executable permissions issue"
fi

echo -e "\n" + "=" * 50
echo "Installation test complete!"

# Summary
echo -e "\nPackage Status Summary:"
dpkg -l | grep linkrot || echo "No linkrot packages found in dpkg list"

echo -e "\nTo uninstall:"
echo "  sudo apt-get remove linkrot python3-linkrot"

echo -e "\nTo reinstall:"
echo "  sudo dpkg -i ../python3-linkrot_*.deb ../linkrot_*.deb"
