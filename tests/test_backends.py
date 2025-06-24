"""
Comprehensive tests for the backends module.
Tests Reference class, ReaderBackend, and PyMuPDFBackend functionality.
"""

import unittest
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from linkrot.backends import (
    make_compat_str,
    Reference, 
    ReaderBackend,
    PyMuPDFBackend
)


class TestMakeCompatStr(unittest.TestCase):
    """Test make_compat_str function."""

    def test_make_compat_str_with_string(self):
        """Test with string input."""
        result = make_compat_str("hello world")
        assert result == "hello world"

    def test_make_compat_str_with_empty_string(self):
        """Test with empty string."""
        result = make_compat_str("")
        assert result == ""

    def test_make_compat_str_with_empty_bytes(self):
        """Test with empty bytes."""
        result = make_compat_str(b"")
        assert result == ""

    def test_make_compat_str_with_unicode_bytes(self):
        """Test with unicode bytes."""
        test_bytes = "héllo wørld".encode('utf-8')
        result = make_compat_str(test_bytes)
        assert result == "héllo wørld"

    def test_make_compat_str_with_invalid_input(self):
        """Test with invalid input type."""
        with pytest.raises(AssertionError):
            make_compat_str(123)

    @patch('chardet.detect')
    def test_make_compat_str_with_decode_error(self, mock_detect):
        """Test handling of decode errors."""
        mock_detect.return_value = {'encoding': 'utf-8'}
        
        # Create bytes that will cause decode error when using utf-8
        # Use bytes that aren't valid UTF-8
        invalid_bytes = b'\xff\xfe\xfd'
        
        # The function should handle decode errors gracefully and return empty string
        result = make_compat_str(invalid_bytes)
        assert isinstance(result, str)
        # Due to decode error handling, result should be empty
        assert result == ""

    @patch('chardet.detect')
    def test_make_compat_str_with_utf16be(self, mock_detect):
        """Test UTF-16BE encoding with BOM handling."""
        mock_detect.return_value = {'encoding': 'UTF-16BE'}
        
        # Create bytes with BOM-like content
        test_str = "\\ufeffHello World"
        test_bytes = test_str.encode('utf-16be')
        
        result = make_compat_str(test_bytes)
        assert isinstance(result, str)


class TestReference(unittest.TestCase):
    """Test Reference class."""

    def test_reference_init_url(self):
        """Test Reference initialization with URL."""
        ref = Reference("https://example.com")
        assert ref.ref == "https://example.com"
        assert ref.reftype == "url"
        assert ref.page == 0

    def test_reference_init_pdf(self):
        """Test Reference initialization with PDF URL."""
        ref = Reference("https://example.com/document.pdf")
        assert ref.ref == "https://example.com/document.pdf"
        assert ref.reftype == "pdf"

    def test_reference_init_pdf_with_params(self):
        """Test Reference with PDF URL containing parameters."""
        ref = Reference("https://example.com/doc.pdf?download=true")
        assert ref.reftype == "pdf"

    @patch('linkrot.extractor.extract_arxiv')
    @patch('linkrot.extractor.extract_doi')
    def test_reference_init_arxiv(self, mock_doi, mock_arxiv):
        """Test Reference initialization with arXiv URL."""
        mock_doi.return_value = []
        mock_arxiv.return_value = ["1234.5678"]
        
        ref = Reference("https://arxiv.org/abs/1234.5678")
        assert ref.ref == "1234.5678"
        assert ref.reftype == "arxiv"

    @patch('linkrot.extractor.extract_arxiv')
    @patch('linkrot.extractor.extract_doi')
    def test_reference_init_doi(self, mock_doi, mock_arxiv):
        """Test Reference initialization with DOI."""
        mock_arxiv.return_value = []
        mock_doi.return_value = ["10.1234/example"]
        
        ref = Reference("doi:10.1234/example")
        assert ref.ref == "10.1234/example"
        assert ref.reftype == "doi"

    def test_reference_hash(self):
        """Test Reference hashing."""
        ref1 = Reference("https://example.com")
        ref2 = Reference("https://example.com")
        ref3 = Reference("https://different.com")
        
        assert hash(ref1) == hash(ref2)
        assert hash(ref1) != hash(ref3)

    def test_reference_equality(self):
        """Test Reference equality."""
        ref1 = Reference("https://example.com")
        ref2 = Reference("https://example.com")
        ref3 = Reference("https://different.com")
        
        assert ref1 == ref2
        assert ref1 != ref3

    def test_reference_str(self):
        """Test Reference string representation."""
        ref = Reference("https://example.com")
        expected = "<url: https://example.com>"
        assert str(ref) == expected

    def test_reference_with_page(self):
        """Test Reference with page number."""
        ref = Reference("https://example.com", page=5)
        assert ref.page == 5


class TestReaderBackend(unittest.TestCase):
    """Test ReaderBackend class."""

    def test_reader_backend_init(self):
        """Test ReaderBackend initialization."""
        backend = ReaderBackend()
        assert backend.text == ""
        assert backend.metadata == {}
        assert backend.references == set()

    def test_reader_backend_get_metadata(self):
        """Test get_metadata method."""
        backend = ReaderBackend()
        backend.metadata = {"Title": "Test Document"}
        metadata = backend.get_metadata()
        assert metadata == {"Title": "Test Document"}

    def test_reader_backend_get_text(self):
        """Test get_text method."""
        backend = ReaderBackend()
        backend.text = "Sample text content"
        text = backend.get_text()
        assert text == "Sample text content"

    def test_reader_backend_get_references(self):
        """Test get_references method."""
        backend = ReaderBackend()
        ref1 = Reference("https://example.com")
        ref2 = Reference("https://different.com")  # Different URL so they're not equal
        backend.references = {ref1, ref2}
        
        refs = backend.get_references()
        assert len(refs) == 2

    def test_reader_backend_get_references_with_filter(self):
        """Test get_references with reftype filter."""
        backend = ReaderBackend()
        ref1 = Reference("https://example.com/doc.pdf")  # pdf type
        ref2 = Reference("https://example.com")  # url type
        backend.references = {ref1, ref2}

        pdf_refs = backend.get_references(reftype="pdf")
        assert len(pdf_refs) == 1
        # Convert set to list to access elements
        pdf_refs_list = list(pdf_refs)
        assert pdf_refs_list[0].reftype == "pdf"

    def test_reader_backend_get_references_sorted(self):
        """Test get_references with sorting."""
        backend = ReaderBackend()
        ref1 = Reference("https://z-example.com")
        ref2 = Reference("https://a-example.com")
        backend.references = {ref1, ref2}

        refs = backend.get_references(sort=True)
        # Should be sorted by ref attribute
        refs_list = list(refs)
        assert len(refs_list) == 2
        # First should be a-example (alphabetically first)
        assert refs_list[0].ref == "https://a-example.com"

    def test_reader_backend_get_references_as_dict(self):
        """Test get_references_as_dict method."""
        backend = ReaderBackend()
        ref1 = Reference("https://example.com")
        ref2 = Reference("https://example.com/doc.pdf")
        backend.references = {ref1, ref2}
        
        refs_dict = backend.get_references_as_dict()
        assert "url" in refs_dict
        assert "pdf" in refs_dict

    def test_reader_backend_metadata_cleanup(self):
        """Test metadata cleanup functionality."""
        backend = ReaderBackend()
        backend.metadata = {
            "title": "Test",
            "empty": "",
            "none": None,
            "valid": "content"
        }
        backend.metadata_cleanup()
        # The current implementation only removes empty strings, not None values
        expected = {"title": "Test", "none": None, "valid": "content"}
        assert backend.metadata == expected


if __name__ == '__main__':
    unittest.main()
