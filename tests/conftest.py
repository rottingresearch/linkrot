"""
Pytest configuration and shared fixtures for linkrot tests.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_pdf_file(temp_directory):
    """Create a mock PDF file for testing."""
    pdf_path = os.path.join(temp_directory, "test.pdf")
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 0\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF")
    return pdf_path


@pytest.fixture
def mock_invalid_pdf_file(temp_directory):
    """Create an invalid PDF file for testing."""
    pdf_path = os.path.join(temp_directory, "invalid.pdf")
    with open(pdf_path, "wb") as f:
        f.write(b"This is not a valid PDF file")
    return pdf_path


@pytest.fixture
def sample_references():
    """Create sample reference objects for testing."""
    refs = []
    
    # PDF references
    for i in range(3):
        ref = Mock()
        ref.ref = f"http://example.com/paper{i}.pdf"
        ref.reftype = "pdf"
        ref.page = i + 1
        refs.append(ref)
    
    # URL references
    for i in range(2):
        ref = Mock()
        ref.ref = f"http://website{i}.com"
        ref.reftype = "url"
        ref.page = i + 1
        refs.append(ref)
    
    # arXiv references
    ref = Mock()
    ref.ref = "1234.5678"
    ref.reftype = "arxiv"
    ref.page = 3
    refs.append(ref)
    
    # DOI reference
    ref = Mock()
    ref.ref = "10.1234/example.doi"
    ref.reftype = "doi"
    ref.page = 4
    refs.append(ref)
    
    return refs


@pytest.fixture
def sample_metadata():
    """Create sample PDF metadata for testing."""
    return {
        "Title": "Sample Research Paper",
        "Author": "Dr. Test Author",
        "Subject": "Computer Science Research",
        "Creator": "LaTeX with hyperref package",
        "Producer": "pdfTeX-1.40.21",
        "CreationDate": "D:20231201120000Z",
        "ModDate": "D:20231201120000Z",
        "Pages": 15
    }


@pytest.fixture
def sample_text():
    """Create sample PDF text content for testing."""
    return """
Abstract

This is a sample research paper that contains various types of references.
The paper discusses important topics in computer science and provides
comprehensive analysis of the subject matter.

Introduction

Recent work by Smith et al. (2023) available at http://example.com/smith2023.pdf
demonstrates the importance of this research area. Additional information
can be found at https://research-portal.org and in the arXiv preprint
arxiv:2023.12345.

For more details, see DOI:10.1234/example.2023.research.

References

1. Smith, J. et al. "Important Research" http://example.com/smith2023.pdf
2. Johnson, A. "Another Paper" https://journal.org/paper.pdf  
3. Brown, B. "Third Paper" arxiv:2023.54321
4. Wilson, C. "Fourth Paper" DOI:10.5678/another.example
"""


@pytest.fixture
def mock_successful_http_response():
    """Create a mock successful HTTP response."""
    response = Mock()
    response.status_code = 200
    response.headers = {'Content-Type': 'application/pdf'}
    response.content = b"Mock PDF content"
    return response


@pytest.fixture
def mock_failed_http_response():
    """Create a mock failed HTTP response."""
    response = Mock()
    response.status_code = 404
    response.headers = {}
    response.content = b"Not Found"
    return response


@pytest.fixture
def download_pdfs():
    """Fixture for download_pdfs tests - ensures cleanup."""
    # This fixture can be used to ensure proper cleanup
    # after download tests
    yield
    # Cleanup code if needed


@pytest.fixture(autouse=True)
def reset_imports():
    """Reset any module-level state between tests."""
    # This can be useful if modules have global state
    yield
    # Reset any global state if needed


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Custom test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark slow tests
        if "slow" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name or "workflow" in item.name:
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests (everything else)
        if not any(marker.name in ["slow", "integration"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
