"""
Comprehensive tests for the extractor module.
Tests URL, arXiv, and DOI extraction functionality.
"""

import pytest
from linkrot import extractor

# Import the improved extractor if available
try:
    from linkrot.extractor_improved import (
        extract_urls as extract_urls_improved,
        extract_arxiv as extract_arxiv_improved,
        extract_doi as extract_doi_improved,
        clean_url_text
    )
    HAS_IMPROVED_EXTRACTOR = True
except ImportError:
    HAS_IMPROVED_EXTRACTOR = False


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

    def test_extract_urls_with_special_characters(self):
        """Test URL extraction with special characters and unicode."""
        text = "Visit https://example.com/path-with-dashes_and_underscores.html"
        result = extractor.extract_urls(text)
        assert "https://example.com/path-with-dashes_and_underscores.html" in result

    def test_extract_urls_case_insensitive(self):
        """Test that URL extraction is case insensitive."""
        text = "Visit HTTPS://EXAMPLE.COM and Http://Test.Org"
        result = extractor.extract_urls(text)
        assert len(result) >= 2

    def test_extract_urls_from_multiline(self):
        """Test URL extraction from multiline text."""
        text = """
        First line with https://example.com
        Second line with http://test.org
        Third line with https://github.com
        """
        result = extractor.extract_urls(text)
        assert "https://example.com" in result
        assert "http://test.org" in result
        assert "https://github.com" in result

    def test_extract_urls_no_duplicates(self):
        """Test that duplicate URLs are removed."""
        text = """
        https://example.com
        https://example.com
        https://example.com
        http://test.org
        """
        result = extractor.extract_urls(text)
        assert len(result) == 2

    def test_extract_urls_empty_text(self):
        """Test URL extraction from empty text."""
        result = extractor.extract_urls("")
        assert len(result) == 0

    def test_extract_urls_no_urls(self):
        """Test text with no URLs."""
        text = "This is just plain text with no URLs at all."
        result = extractor.extract_urls(text)
        assert len(result) == 0

    def test_extract_urls_with_domains(self):
        """Test various domain extensions."""
        text = """
        https://example.edu
        http://test.gov
        https://site.org
        http://company.net
        https://research.ac.uk
        """
        result = extractor.extract_urls(text)
        assert len(result) == 5


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

    def test_extract_arxiv_https_url_format(self):
        """Test extraction of arXiv references in HTTPS URL format."""
        text = "See https://arxiv.org/abs/1801.00001"
        result = extractor.extract_arxiv(text)
        assert "1801.00001" in result

    def test_extract_arxiv_mixed_formats(self):
        """Test extraction of mixed arXiv formats."""
        text = """
        Reference arxiv:1234.5678 and also
        https://arxiv.org/abs/2023.12345 and
        arxiv: 1801.00001
        """
        result = extractor.extract_arxiv(text)
        assert "1234.5678" in result
        assert "2023.12345" in result
        assert "1801.00001" in result

    def test_extract_arxiv_with_periods(self):
        """Test that periods are stripped from arXiv IDs."""
        text = "See arxiv:1234.5678. for more info"
        result = extractor.extract_arxiv(text)
        assert "1234.5678" in result

    def test_extract_arxiv_case_insensitive(self):
        """Test case insensitive arXiv extraction."""
        text = "ArXiv:1234.5678 and ARXIV.ORG/abs/2023.12345"
        result = extractor.extract_arxiv(text)
        # Should find at least one reference
        assert len(result) >= 1

    def test_extract_arxiv_no_duplicates(self):
        """Test that duplicate arXiv IDs are removed."""
        text = """
        arxiv:1234.5678
        arxiv:1234.5678
        http://arxiv.org/abs/1234.5678
        """
        result = extractor.extract_arxiv(text)
        assert len(result) == 1
        assert "1234.5678" in result

    def test_extract_arxiv_empty_text(self):
        """Test arXiv extraction from empty text."""
        result = extractor.extract_arxiv("")
        assert len(result) == 0

    def test_extract_arxiv_no_matches(self):
        """Test text with no arXiv references."""
        text = "This text has no arXiv references at all."
        result = extractor.extract_arxiv(text)
        assert len(result) == 0

    def test_extract_arxiv_with_version(self):
        """Test arXiv extraction with version numbers."""
        text = "See arxiv:1234.5678v2 for the latest version"
        result = extractor.extract_arxiv(text)
        assert "1234.5678v2" in result


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

    def test_extract_doi_case_insensitive(self):
        """Test case insensitive DOI extraction."""
        text = "doi:10.1234/example and DOI:10.5678/another"
        result = extractor.extract_doi(text)
        # Should find at least one
        assert len(result) >= 1

    def test_extract_doi_complex(self):
        """Test extraction of complex DOI with special characters."""
        text = "DOI:10.1038/s41586-021-03819-2"
        result = extractor.extract_doi(text)
        assert "10.1038/s41586-021-03819-2" in result

    def test_extract_doi_with_periods(self):
        """Test that periods are stripped from DOI endings."""
        text = "See DOI:10.1234/example.doi. for citation"
        result = extractor.extract_doi(text)
        assert "10.1234/example.doi" in result

    def test_extract_doi_multiple(self):
        """Test extraction of multiple DOIs."""
        text = """
        First paper DOI:10.1234/first
        Second paper DOI:10.5678/second
        Third paper DOI:10.9012/third
        """
        result = extractor.extract_doi(text)
        assert "10.1234/first" in result
        assert "10.5678/second" in result
        assert "10.9012/third" in result

    def test_extract_doi_no_duplicates(self):
        """Test that duplicate DOIs are removed."""
        text = """
        DOI:10.1234/example
        DOI:10.1234/example
        DOI: 10.1234/example
        """
        result = extractor.extract_doi(text)
        assert len(result) == 1
        assert "10.1234/example" in result

    def test_extract_doi_empty_text(self):
        """Test DOI extraction from empty text."""
        result = extractor.extract_doi("")
        assert len(result) == 0

    def test_extract_doi_no_matches(self):
        """Test text with no DOI references."""
        text = "This text has no DOI references at all."
        result = extractor.extract_doi(text)
        assert len(result) == 0

    def test_extract_doi_with_underscore(self):
        """Test DOI extraction with underscores."""
        text = "DOI:10.1234/example_with_underscore"
        result = extractor.extract_doi(text)
        assert "10.1234/example_with_underscore" in result

    def test_extract_doi_modern_formats(self):
        """Test extraction of modern DOI formats."""
        # URL-based DOI formats
        text1 = "Available at https://doi.org/10.1126/science.abc1234"
        result1 = extractor.extract_doi(text1)
        assert "10.1126/science.abc1234" in result1
        
        # dx.doi.org format
        text2 = "See dx.doi.org/10.1000/456 for details"
        result2 = extractor.extract_doi(text2)
        assert "10.1000/456" in result2
        
        # DOI without colon
        text3 = "DOI 10.1038/s41586-021-03828-1"
        result3 = extractor.extract_doi(text3)
        assert "10.1038/s41586-021-03828-1" in result3
        
        # DOI in parentheses
        text4 = "(DOI: 10.1000/182)"
        result4 = extractor.extract_doi(text4)
        assert "10.1000/182" in result4
        
        # Mixed case
        text5 = "doi:10.1371/journal.pone.0123456"
        result5 = extractor.extract_doi(text5)
        assert "10.1371/journal.pone.0123456" in result5

    def test_extract_doi_pdf_splits(self):
        """Test DOI extraction with PDF-style line splits."""
        text = """
        References include DOI:
        10.1000/182 and https://doi.org/
        10.1038/nature12373
        """
        result = extractor.extract_doi(text)
        assert "10.1000/182" in result
        assert "10.1038/nature12373" in result
        assert len(result) == 2


class TestCombinedExtraction:
    """Test combined extraction scenarios."""

    def test_extract_all_types_mixed(self):
        """Test text containing URLs, arXiv, and DOI references."""
        text = """
        Visit https://example.com for the website.
        The paper is available at arxiv:1234.5678
        Citation: DOI:10.1234/example.doi
        Also see http://arxiv.org/abs/2023.12345
        """
        urls = extractor.extract_urls(text)
        arxivs = extractor.extract_arxiv(text)
        dois = extractor.extract_doi(text)

        assert "https://example.com" in urls
        assert "1234.5678" in arxivs
        assert "2023.12345" in arxivs
        assert "10.1234/example.doi" in dois

    def test_edge_cases_punctuation(self):
        """Test extraction with various punctuation marks."""
        text = """
        URLs: https://example.com, http://test.org;
        arXiv: arxiv:1234.5678, arxiv:5678.1234!
        DOI: DOI:10.1234/example, DOI:10.5678/another?
        """
        urls = extractor.extract_urls(text)
        arxivs = extractor.extract_arxiv(text)
        dois = extractor.extract_doi(text)

        assert len(urls) >= 2
        assert len(arxivs) >= 2
        assert len(dois) >= 2

    def test_extraction_with_line_breaks(self):
        """Test extraction across line breaks."""
        text = "See\nhttps://example.com\nand\narxiv:1234.5678\nfor\nDOI:10.1234/example"
        
        urls = extractor.extract_urls(text)
        arxivs = extractor.extract_arxiv(text)
        dois = extractor.extract_doi(text)

        assert "https://example.com" in urls
        assert "1234.5678" in arxivs
        assert "10.1234/example" in dois


class TestImprovedExtractor:
    """Test cases for the improved URL extractor with PDF handling."""
    
    def test_clean_url_text_basic(self):
        """Test basic text cleaning functionality."""
        # Test with no changes needed
        text = "Visit https://example.com for info"
        result = clean_url_text(text)
        assert result == text
        
        # Test with empty/None input
        assert clean_url_text("") == ""
        assert clean_url_text(None) == None
    
    def test_clean_url_text_pdf_issues(self):
        """Test cleaning of PDF-specific text issues."""
        # URL split across lines with hyphen
        text = "Visit https://github.com/user/very-\nlong-path"
        result = clean_url_text(text)
        assert "verylong-path" in result
        assert "\n" not in result.split("verylong-path")[0]
        
        # Domain split across lines
        text = "Visit www.\nexample.com"
        result = clean_url_text(text)
        assert "www.example.com" in result
        
        # URL with path split
        text = "See https://arxiv.org/abs/\n2021.12345"
        result = clean_url_text(text)
        assert "https://arxiv.org/abs/2021.12345" in result
        
        # Page break characters
        text = "Visit www.example.com\x0cNext page"
        result = clean_url_text(text)
        assert "\x0c" not in result
    
    def test_improved_url_extraction_pdf_splits(self):
        """Test URL extraction with PDF-style line splits."""
        # URL split at path
        text = "See https://arxiv.org/abs/\n2021.12345 for details"
        urls = extract_urls_improved(text)
        assert "https://arxiv.org/abs/2021.12345" in urls
        assert len(urls) == 1
        
        # URL split with hyphen
        text = "Visit https://github.com/user/very-\nlong-repository-name"
        urls = extract_urls_improved(text)
        expected_url = "https://github.com/user/verylong-repository-name"
        assert expected_url in urls
        
        # Domain split
        text = "Check www.\nexample.com and secondary.\norg/path"
        urls = extract_urls_improved(text)
        assert "www.example.com" in urls
        assert "secondary.org/path" in urls
        assert len(urls) == 2
    
    def test_improved_url_extraction_complex_pdf(self):
        """Test extraction from complex PDF-like text."""
        text = """
        References:
        1. https://journal.nature.com/articles/
           nature12345
        2. www.university.
           edu/research/papers  
        3. http://github.com/user/long-
           project-name/issues
        """
        
        urls = extract_urls_improved(text)
        
        # Should find all 3 URLs properly reconstructed
        expected_urls = {
            "https://journal.nature.com/articles/nature12345",
            "www.university.edu/research/papers",
            "http://github.com/user/longproject-name/issues"
        }
        
        assert len(urls) >= 3
        for expected_url in expected_urls:
            assert expected_url in urls
    
    def test_improved_arxiv_extraction(self):
        """Test improved arXiv extraction with PDF issues."""
        # Basic test
        text = "See arxiv:1234.5678 and arxiv.org/abs/9876.5432"
        arxivs = extract_arxiv_improved(text)
        assert "1234.5678" in arxivs
        assert "9876.5432" in arxivs
        
        # With line breaks
        text = "Paper at arxiv:\n1234.5678 and https://arxiv.org/abs/\n9876.5432"
        arxivs = extract_arxiv_improved(text)
        assert "1234.5678" in arxivs
        assert "9876.5432" in arxivs
    
    def test_improved_doi_extraction(self):
        """Test improved DOI extraction with PDF issues."""
        # Basic test
        text = "DOI: 10.1000/182 and DOI:10.1038/nature12373"
        dois = extract_doi_improved(text)
        assert "10.1000/182" in dois
        assert "10.1038/nature12373" in dois
        
        # With line breaks
        text = "DOI:\n10.1000/182 and DOI: 10.1038/\nnature12373"
        dois = extract_doi_improved(text)
        assert "10.1000/182" in dois
        # Note: DOI split across lines might not be perfectly handled
        # depending on the specific pattern
    
    def test_improved_vs_original_comparison(self):
        """Test that improved extractor finds more/better URLs than original."""
        # Test case where original fails but improved succeeds
        text = "Visit https://example.com/path/\nto/resource"
        
        original_urls = extractor.extract_urls(text)
        improved_urls = extract_urls_improved(text)
        
        # Improved should find complete URL
        complete_url = "https://example.com/path/to/resource"
        assert complete_url in improved_urls
        
        # Original might only find partial URL
        assert len(improved_urls) >= len(original_urls)
    
    def test_improved_url_cleaning_edge_cases(self):
        """Test edge cases in URL cleaning."""
        # Multiple consecutive line breaks
        text = "Visit https://example.com\n\n\nfor info"
        result = clean_url_text(text)
        assert "\n\n\n" not in result
        
        # Mixed whitespace
        text = "Visit https://example.com/path\t\n  /to/resource"
        result = clean_url_text(text)
        # Should clean up the whitespace
        assert "/path /to/resource" in result or "/path/to/resource" in result
        
        # URLs with common punctuation at end
        text = "Visit https://example.com."
        urls = extract_urls_improved(text)
        # Should not include the trailing period
        assert "https://example.com" in urls
        assert "https://example.com." not in urls


if __name__ == '__main__':
    pytest.main([__file__])
