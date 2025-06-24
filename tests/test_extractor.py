"""
Comprehensive tests for the extractor module.
Tests URL, arXiv, and DOI extraction functionality.
"""

import pytest
from linkrot import extractor


class TestURLExtraction:
    """Test URL extraction functionality."""

    def test_extract_simple_urls(self):
        """Test extraction of simple HTTP and HTTPS URLs."""
        text = "Visit https://example.com and http://test.org"
        result = extractor.extract_urls(text)
        assert "https://example.com" in result
        assert "http://test.org" in result
        assert len(result) == 2

    def test_extract_complex_urls(self):
        """Test extraction of complex URLs with paths and parameters."""
        text = """
        Check out https://example.com/path/to/resource?param=value&other=123
        Also see http://subdomain.example.org/file.pdf
        And https://www.github.com/user/repo/blob/main/file.py
        """
        result = extractor.extract_urls(text)
        assert "https://example.com/path/to/resource?param=value&other=123" in result
        assert "http://subdomain.example.org/file.pdf" in result
        assert "https://www.github.com/user/repo/blob/main/file.py" in result

    def test_extract_urls_empty_text(self):
        """Test URL extraction from empty text."""
        result = extractor.extract_urls("")
        assert len(result) == 0

    def test_extract_urls_no_urls(self):
        """Test text with no URLs."""
        text = "This is just plain text with no URLs at all."
        result = extractor.extract_urls(text)
        assert len(result) == 0


class TestArxivExtraction:
    """Test arXiv extraction functionality."""

    def test_extract_arxiv_colon_format(self):
        """Test extraction of arXiv references in 'arxiv:' format."""
        text = "See arxiv:1234.5678 for details"
        result = extractor.extract_arxiv(text)
        assert "1234.5678" in result

    def test_extract_arxiv_url_format(self):
        """Test extraction of arXiv references in URL format."""
        text = "Available at http://arxiv.org/abs/2023.12345"
        result = extractor.extract_arxiv(text)
        assert "2023.12345" in result

    def test_extract_arxiv_empty_text(self):
        """Test arXiv extraction from empty text."""
        result = extractor.extract_arxiv("")
        assert len(result) == 0


class TestDOIExtraction:
    """Test DOI extraction functionality."""

    def test_extract_doi_simple(self):
        """Test extraction of simple DOI references."""
        text = "DOI:10.1234/example.doi"
        result = extractor.extract_doi(text)
        assert "10.1234/example.doi" in result

    def test_extract_doi_with_spaces(self):
        """Test DOI extraction with spaces after colon."""
        text = "DOI: 10.1234/example.doi"
        result = extractor.extract_doi(text)
        assert "10.1234/example.doi" in result

    def test_extract_doi_empty_text(self):
        """Test DOI extraction from empty text."""
        result = extractor.extract_doi("")
        assert len(result) == 0


if __name__ == '__main__':
    pytest.main([__file__])
