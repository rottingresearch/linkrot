"""
Comprehensive tests for the exceptions module.
Tests custom exception classes and their functionality.
"""

import pytest
from linkrot.exceptions import (
    FileNotFoundError,
    DownloadError,
    PDFInvalidError,
    PDFExtractionError
)


class TestFileNotFoundError:
    """Test FileNotFoundError exception."""

    def test_file_not_found_error_creation(self):
        """Test basic exception creation."""
        error = FileNotFoundError("File not found")
        assert str(error) == "File not found"

    def test_file_not_found_error_inheritance(self):
        """Test that it inherits from Exception."""
        error = FileNotFoundError("Test message")
        assert isinstance(error, Exception)

    def test_file_not_found_error_raise(self):
        """Test raising the exception."""
        with pytest.raises(FileNotFoundError) as exc_info:
            raise FileNotFoundError("Test file not found")
        
        assert str(exc_info.value) == "Test file not found"

    def test_file_not_found_error_empty_message(self):
        """Test exception with empty message."""
        error = FileNotFoundError("")
        assert str(error) == ""

    def test_file_not_found_error_no_message(self):
        """Test exception with no message."""
        error = FileNotFoundError()
        assert str(error) == ""

    def test_file_not_found_error_multiple_args(self):
        """Test exception with multiple arguments."""
        error = FileNotFoundError("File", "not", "found")
        # Should contain all arguments in string representation
        error_str = str(error)
        assert "File" in error_str
        assert "not" in error_str
        assert "found" in error_str


class TestDownloadError:
    """Test DownloadError exception."""

    def test_download_error_creation(self):
        """Test basic exception creation."""
        error = DownloadError("Download failed")
        assert str(error) == "Download failed"

    def test_download_error_inheritance(self):
        """Test that it inherits from Exception."""
        error = DownloadError("Test message")
        assert isinstance(error, Exception)

    def test_download_error_raise(self):
        """Test raising the exception."""
        with pytest.raises(DownloadError) as exc_info:
            raise DownloadError("Network error occurred")
        
        assert str(exc_info.value) == "Network error occurred"

    def test_download_error_with_url(self):
        """Test exception with URL information."""
        url = "http://example.com/file.pdf"
        error = DownloadError(f"Failed to download {url}")
        assert url in str(error)

    def test_download_error_empty_message(self):
        """Test exception with empty message."""
        error = DownloadError("")
        assert str(error) == ""

    def test_download_error_no_message(self):
        """Test exception with no message."""
        error = DownloadError()
        assert str(error) == ""

    def test_download_error_with_nested_exception(self):
        """Test exception with nested exception information."""
        nested_error = "Connection timeout"
        error = DownloadError(f"Download failed: {nested_error}")
        assert nested_error in str(error)


class TestPDFInvalidError:
    """Test PDFInvalidError exception."""

    def test_pdf_invalid_error_creation(self):
        """Test basic exception creation."""
        error = PDFInvalidError("Invalid PDF format")
        assert str(error) == "Invalid PDF format"

    def test_pdf_invalid_error_inheritance(self):
        """Test that it inherits from Exception."""
        error = PDFInvalidError("Test message")
        assert isinstance(error, Exception)

    def test_pdf_invalid_error_raise(self):
        """Test raising the exception."""
        with pytest.raises(PDFInvalidError) as exc_info:
            raise PDFInvalidError("PDF is corrupted")
        
        assert str(exc_info.value) == "PDF is corrupted"

    def test_pdf_invalid_error_with_details(self):
        """Test exception with detailed error information."""
        details = "Unable to parse PDF structure"
        error = PDFInvalidError(f"Invalid PDF: {details}")
        assert details in str(error)

    def test_pdf_invalid_error_empty_message(self):
        """Test exception with empty message."""
        error = PDFInvalidError("")
        assert str(error) == ""

    def test_pdf_invalid_error_no_message(self):
        """Test exception with no message."""
        error = PDFInvalidError()
        assert str(error) == ""


class TestPDFExtractionError:
    """Test PDFExtractionError exception."""

    def test_pdf_extraction_error_creation(self):
        """Test basic exception creation."""
        error = PDFExtractionError("Failed to extract content")
        assert str(error) == "Failed to extract content"

    def test_pdf_extraction_error_inheritance(self):
        """Test that it inherits from Exception."""
        error = PDFExtractionError("Test message")
        assert isinstance(error, Exception)

    def test_pdf_extraction_error_raise(self):
        """Test raising the exception."""
        with pytest.raises(PDFExtractionError) as exc_info:
            raise PDFExtractionError("Content extraction failed")
        
        assert str(exc_info.value) == "Content extraction failed"

    def test_pdf_extraction_error_with_page_info(self):
        """Test exception with page information."""
        page_num = 5
        error = PDFExtractionError(f"Failed to extract content from page {page_num}")
        assert str(page_num) in str(error)

    def test_pdf_extraction_error_empty_message(self):
        """Test exception with empty message."""
        error = PDFExtractionError("")
        assert str(error) == ""

    def test_pdf_extraction_error_no_message(self):
        """Test exception with no message."""
        error = PDFExtractionError()
        assert str(error) == ""


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_exception(self):
        """Test that all custom exceptions inherit from Exception."""
        exceptions = [
            FileNotFoundError,
            DownloadError,
            PDFInvalidError,
            PDFExtractionError
        ]
        
        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)

    def test_exceptions_are_distinct(self):
        """Test that all exceptions are distinct classes."""
        exceptions = [
            FileNotFoundError,
            DownloadError,
            PDFInvalidError,
            PDFExtractionError
        ]
        
        # Each exception should be a different class
        for i, exc1 in enumerate(exceptions):
            for j, exc2 in enumerate(exceptions):
                if i != j:
                    assert exc1 != exc2

    def test_exception_catching_specificity(self):
        """Test that specific exceptions can be caught specifically."""
        # Test FileNotFoundError
        try:
            raise FileNotFoundError("Test")
        except FileNotFoundError:
            pass  # Should catch specifically
        except Exception:
            pytest.fail("Should have caught FileNotFoundError specifically")
        
        # Test DownloadError
        try:
            raise DownloadError("Test")
        except DownloadError:
            pass  # Should catch specifically
        except Exception:
            pytest.fail("Should have caught DownloadError specifically")
        
        # Test PDFInvalidError
        try:
            raise PDFInvalidError("Test")
        except PDFInvalidError:
            pass  # Should catch specifically
        except Exception:
            pytest.fail("Should have caught PDFInvalidError specifically")
        
        # Test PDFExtractionError
        try:
            raise PDFExtractionError("Test")
        except PDFExtractionError:
            pass  # Should catch specifically
        except Exception:
            pytest.fail("Should have caught PDFExtractionError specifically")

    def test_generic_exception_catching(self):
        """Test that custom exceptions can be caught as generic Exceptions."""
        exceptions_to_test = [
            FileNotFoundError("Test file error"),
            DownloadError("Test download error"),
            PDFInvalidError("Test PDF error"),
            PDFExtractionError("Test extraction error")
        ]
        
        for exc in exceptions_to_test:
            try:
                raise exc
            except Exception as caught:
                assert isinstance(caught, type(exc))
                assert str(caught) == str(exc)


class TestExceptionUsageScenarios:
    """Test realistic usage scenarios for exceptions."""

    def test_file_handling_scenario(self):
        """Test file handling scenario with FileNotFoundError."""
        def open_pdf(filepath):
            if not filepath or filepath == "nonexistent.pdf":
                raise FileNotFoundError(f"PDF file '{filepath}' not found")
            return "file_content"
        
        # Test successful case
        result = open_pdf("valid.pdf")
        assert result == "file_content"
        
        # Test error case
        with pytest.raises(FileNotFoundError) as exc_info:
            open_pdf("nonexistent.pdf")
        
        assert "nonexistent.pdf" in str(exc_info.value)

    def test_download_scenario(self):
        """Test download scenario with DownloadError."""
        def download_file(url):
            if "invalid" in url or "404" in url:
                raise DownloadError(f"Failed to download from {url}")
            return "downloaded_content"
        
        # Test successful case
        result = download_file("http://valid.com/file.pdf")
        assert result == "downloaded_content"
        
        # Test error cases
        with pytest.raises(DownloadError) as exc_info:
            download_file("http://invalid.com/file.pdf")
        
        assert "invalid.com" in str(exc_info.value)

    def test_pdf_processing_scenario(self):
        """Test PDF processing scenario with PDF exceptions."""
        def process_pdf(pdf_content):
            if pdf_content == "invalid_format":
                raise PDFInvalidError("PDF format is not recognized")
            elif pdf_content == "extraction_fails":
                raise PDFExtractionError("Unable to extract text from PDF")
            return "processed_content"
        
        # Test successful case
        result = process_pdf("valid_pdf_content")
        assert result == "processed_content"
        
        # Test invalid format
        with pytest.raises(PDFInvalidError):
            process_pdf("invalid_format")
        
        # Test extraction failure
        with pytest.raises(PDFExtractionError):
            process_pdf("extraction_fails")

    def test_nested_exception_handling(self):
        """Test handling multiple exception types in sequence."""
        def complex_pdf_operation(filename, url=None):
            if not filename:
                raise FileNotFoundError("No filename provided")
            
            if url and "download_fail" in url:
                raise DownloadError(f"Cannot download from {url}")
            
            if "invalid" in filename:
                raise PDFInvalidError(f"PDF {filename} is invalid")
            
            if "extract_fail" in filename:
                raise PDFExtractionError(f"Cannot extract from {filename}")
            
            return "success"
        
        # Test all error types
        with pytest.raises(FileNotFoundError):
            complex_pdf_operation("")
        
        with pytest.raises(DownloadError):
            complex_pdf_operation("test.pdf", "http://download_fail.com")
        
        with pytest.raises(PDFInvalidError):
            complex_pdf_operation("invalid.pdf")
        
        with pytest.raises(PDFExtractionError):
            complex_pdf_operation("extract_fail.pdf")
        
        # Test success case
        result = complex_pdf_operation("valid.pdf")
        assert result == "success"
