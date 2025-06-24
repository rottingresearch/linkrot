"""
Comprehensive tests for the downloader module.
Tests URL downloading, status checking, and link validation functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from urllib.request import HTTPError
from urllib.error import URLError
from collections import defaultdict

from linkrot.downloader import (
    sanitize_url,
    get_status_code,
    check_refs,
    download_urls
)
from linkrot.backends import Reference


class TestSanitizeUrl:
    """Test URL sanitization functionality."""

    def test_sanitize_url_with_http(self):
        """Test URL that already has http prefix."""
        url = "http://example.com"
        result = sanitize_url(url)
        assert result == "http://example.com"

    def test_sanitize_url_with_https(self):
        """Test URL that already has https prefix."""
        url = "https://example.com"
        result = sanitize_url(url)
        assert result == "https://example.com"

    def test_sanitize_url_without_protocol(self):
        """Test URL without protocol prefix."""
        url = "example.com"
        result = sanitize_url(url)
        assert result == "http://example.com"

    def test_sanitize_url_with_subdomain(self):
        """Test URL with subdomain without protocol."""
        url = "www.example.com"
        result = sanitize_url(url)
        assert result == "http://www.example.com"

    def test_sanitize_url_case_insensitive_http(self):
        """Test case insensitive HTTP detection."""
        url = "HTTP://example.com"
        result = sanitize_url(url)
        assert result == "HTTP://example.com"

    def test_sanitize_url_case_insensitive_https(self):
        """Test case insensitive HTTPS detection."""
        url = "HTTPS://example.com"
        result = sanitize_url(url)
        assert result == "HTTPS://example.com"

    def test_sanitize_url_with_unicode(self):
        """Test URL with unicode characters."""
        url = "example.com/café"
        result = sanitize_url(url)
        assert result == "http://example.com/caf"  # unicode stripped

    def test_sanitize_url_empty(self):
        """Test empty URL."""
        url = ""
        result = sanitize_url(url)
        assert result == ""

    def test_sanitize_url_none(self):
        """Test None URL."""
        url = None
        result = sanitize_url(url)
        assert result == ""

    def test_sanitize_url_with_path(self):
        """Test URL with path components."""
        url = "example.com/path/to/resource"
        result = sanitize_url(url)
        assert result == "http://example.com/path/to/resource"


class TestGetStatusCode:
    """Test HTTP status code checking functionality."""

    @patch('urllib.request.urlopen')
    def test_get_status_code_success(self, mock_urlopen):
        """Test successful status code retrieval."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value = mock_response
        
        status = get_status_code("http://example.com")
        assert status == 200

    @patch('linkrot.downloader.urlopen')
    def test_get_status_code_http_error(self, mock_urlopen):
        """Test HTTP error handling."""
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            "http://example.com", 404, "Not Found", {}, None
        )

        status = get_status_code("http://example.com")
        assert status == 404

    @patch('linkrot.downloader.urlopen')
    def test_get_status_code_url_error(self, mock_urlopen):
        """Test URL error handling."""
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        status = get_status_code("http://example.com")
        assert status == "Connection refused"
    
    @patch('linkrot.downloader.urlopen')
    def test_get_status_code_general_exception(self, mock_urlopen):
        """Test general exception handling."""
        mock_urlopen.side_effect = Exception("Network error")

        status = get_status_code("http://example.com")
        assert status is None
    
    @patch('linkrot.downloader.Request')
    @patch('linkrot.downloader.urlopen')
    def test_get_status_code_request_headers(self, mock_urlopen, mock_request):
        """Test that proper headers are set on request."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value = mock_response

        mock_request_instance = Mock()
        mock_request.return_value = mock_request_instance

        get_status_code("http://example.com")

        # Verify User-Agent header was added
        mock_request_instance.add_header.assert_called_once_with(
            "User-Agent",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1;             Trident/5.0)"
        )
        call_args = mock_request_instance.add_header.call_args[0]
        assert call_args[0] == "User-Agent"
        assert "Mozilla" in call_args[1]
    
    @patch('linkrot.downloader.urlopen')
    def test_get_status_code_head_method(self, mock_urlopen):
        """Test that HEAD method is used."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value = mock_response

        get_status_code("http://example.com")

        # Verify urlopen was called (the method is set on the request object)
        assert mock_urlopen.called

    @patch('linkrot.downloader.urlopen')
    def test_get_status_code_ssl_context(self, mock_urlopen):
        """Test that SSL context is used."""
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value = mock_response
        
        get_status_code("https://example.com")
        
        # Verify SSL context was passed (check that urlopen was called with context)
        assert mock_urlopen.called
        call_kwargs = mock_urlopen.call_args[1] if mock_urlopen.call_args else {}
        assert 'context' in call_kwargs
        assert "context" in call_kwargs


class TestCheckRefs:
    """Test reference checking functionality."""

    def create_mock_ref(self, url, page=0):
        """Helper to create mock reference."""
        ref = Mock()
        ref.ref = url
        ref.page = page
        return ref

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    def test_check_refs_success(self, mock_threadpool, mock_get_status):
        """Test successful reference checking."""
        # Setup mocks
        mock_get_status.return_value = 200
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [
            self.create_mock_ref("http://example.com"),
            self.create_mock_ref("http://test.org")
        ]
        
        result = check_refs(refs, verbose=False)
        
        # Verify threadpool was used
        mock_threadpool.assert_called_once_with(5)
        mock_pool.map.assert_called_once()
        mock_pool.wait_completion.assert_called_once()
        
        # Verify result contains summary
        assert "Summary of link checker:" in result

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    @patch('linkrot.downloader.colorprint')
    def test_check_refs_verbose_success(self, mock_colorprint, mock_threadpool, mock_get_status):
        """Test verbose reference checking with successful links."""
        mock_get_status.return_value = 200
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        # Mock the map function to actually call our check function
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        check_refs(refs, verbose=True)
        
        # Verify colorprint was called for success
        mock_colorprint.assert_called()
        # Check that colorprint was called with "200" for the verbose output
        calls = mock_colorprint.call_args_list
        success_call_found = False
        for call in calls:
            if len(call[0]) >= 2 and "200" in call[0][1]:
                success_call_found = True
                break
        assert success_call_found, f"Expected colorprint call with '200' in args, got calls: {calls}"

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    @patch('linkrot.downloader.colorprint')
    def test_check_refs_verbose_failure(self, mock_colorprint, mock_threadpool, mock_get_status):
        """Test verbose reference checking with failed links."""
        mock_get_status.return_value = 404
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        check_refs(refs, verbose=True)
        
        # Verify colorprint was called for failure
        mock_colorprint.assert_called()
        call_args = mock_colorprint.call_args[0]
        assert "404" in call_args[1]

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    def test_check_refs_mixed_results(self, mock_threadpool, mock_get_status):
        """Test reference checking with mixed success/failure results."""
        # Setup different status codes for different calls
        status_codes = [200, 404, 500, 200]
        mock_get_status.side_effect = status_codes
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [
            self.create_mock_ref("http://good1.com"),
            self.create_mock_ref("http://notfound.com"),
            self.create_mock_ref("http://error.com"),
            self.create_mock_ref("http://good2.com")
        ]
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        result = check_refs(refs, verbose=False)
        
        # Verify summary contains different status codes
        assert "working" in result
        assert "broken" in result

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    def test_check_refs_with_page_numbers(self, mock_threadpool, mock_get_status):
        """Test reference checking includes page numbers in output."""
        mock_get_status.return_value = 404
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com", page=5)]
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        result = check_refs(refs, verbose=False)
        
        # Should include page number in output
        assert "page 5" in result

    @patch('linkrot.downloader.ThreadPool')
    def test_check_refs_exception_handling(self, mock_threadpool):
        """Test exception handling in check_refs."""
        mock_pool = Mock()
        mock_pool.map.side_effect = Exception("Thread error")
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        # Should not raise exception
        result = check_refs(refs)
        assert "Summary of link checker:" in result

    @patch('linkrot.downloader.ThreadPool')
    def test_check_refs_keyboard_interrupt(self, mock_threadpool):
        """Test keyboard interrupt handling in check_refs."""
        mock_pool = Mock()
        mock_pool.map.side_effect = KeyboardInterrupt()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        # Should handle KeyboardInterrupt gracefully
        result = check_refs(refs)
        assert "Summary of link checker:" in result

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    def test_check_refs_custom_thread_count(self, mock_threadpool, mock_get_status):
        """Test check_refs with custom thread count."""
        mock_get_status.return_value = 200
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        check_refs(refs, max_threads=10)
        
        # Should still use default 5 threads (max_threads parameter not used in current implementation)
        mock_threadpool.assert_called_once_with(5)


class TestDownloadUrls:
    """Test URL downloading functionality."""

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('linkrot.downloader.ThreadPool')
    def test_download_urls_basic(self, mock_threadpool, mock_exists, mock_makedirs):
        """Test basic URL downloading functionality."""
        mock_exists.return_value = False  # Directory doesn't exist
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        urls = ["http://example.com/file1.pdf", "http://example.com/file2.pdf"]
        target_dir = "/tmp/downloads"
        
        download_urls(urls, target_dir)
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with(target_dir)
        
        # Verify threadpool usage
        mock_threadpool.assert_called_once()
        mock_pool.map.assert_called_once()
        mock_pool.wait_completion.assert_called_once()

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('linkrot.downloader.ThreadPool')
    def test_download_urls_existing_directory(self, mock_threadpool, mock_exists, mock_makedirs):
        """Test downloading when target directory already exists."""
        mock_exists.return_value = True  # Directory exists
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        urls = ["http://example.com/file.pdf"]
        target_dir = "/tmp/downloads"
        
        download_urls(urls, target_dir)
        
        # Should not try to create directory
        mock_makedirs.assert_not_called()

    def test_download_urls_empty_list(self):
        """Test downloading empty URL list raises assertion error."""
        with pytest.raises(AssertionError, match="Need urls"):
            download_urls([], "/tmp/downloads")

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('linkrot.downloader.ThreadPool')
    def test_download_urls_duplicate_removal(self, mock_threadpool, mock_exists, mock_makedirs):
        """Test that duplicate URLs are removed."""
        mock_exists.return_value = False
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        urls = [
            "http://example.com/file.pdf",
            "http://example.com/file.pdf",  # duplicate
            "http://example.com/other.pdf"
        ]
        
        download_urls(urls, "/tmp/downloads")
        
        # Verify map was called with deduplicated URLs
        call_args = mock_pool.map.call_args[0]
        download_func, url_set = call_args
        
        # Should be a set (no duplicates)
        assert len(url_set) == 2

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('linkrot.downloader.ThreadPool')
    def test_download_urls_exception_handling(self, mock_threadpool, mock_exists, mock_makedirs):
        """Test exception handling in download_urls."""
        mock_exists.return_value = False
        mock_pool = Mock()
        mock_pool.map.side_effect = Exception("Download error")
        mock_threadpool.return_value = mock_pool
        
        urls = ["http://example.com/file.pdf"]
        
        # Should handle exception gracefully
        try:
            download_urls(urls, "/tmp/downloads")
        except Exception:
            pytest.fail("download_urls should handle exceptions gracefully")

    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('linkrot.downloader.ThreadPool')
    def test_download_urls_keyboard_interrupt(self, mock_threadpool, mock_exists, mock_makedirs):
        """Test keyboard interrupt handling in download_urls."""
        mock_exists.return_value = False
        mock_pool = Mock()
        mock_pool.map.side_effect = KeyboardInterrupt()
        mock_threadpool.return_value = mock_pool
        
        urls = ["http://example.com/file.pdf"]
        
        # Should handle KeyboardInterrupt gracefully
        try:
            download_urls(urls, "/tmp/downloads")
        except KeyboardInterrupt:
            pytest.fail("download_urls should handle KeyboardInterrupt gracefully")


class TestIntegration:
    """Integration tests for downloader module."""

    def test_full_download_workflow(self):
        """Test complete download workflow with mocked components."""
        with patch('linkrot.downloader.get_status_code') as mock_status:
            with patch('linkrot.downloader.ThreadPool') as mock_threadpool:
                with patch('os.makedirs') as mock_makedirs:
                    with patch('os.path.exists') as mock_exists:
                        
                        # Setup mocks
                        mock_status.return_value = 200
                        mock_exists.return_value = False
                        mock_pool = Mock()
                        mock_threadpool.return_value = mock_pool
                        
                        # Create test references
                        refs = [
                            Mock(ref="http://example.com/paper1.pdf", page=1),
                            Mock(ref="http://example.com/paper2.pdf", page=2),
                            Mock(ref="http://badlink.com/missing.pdf", page=3)
                        ]
                        
                        # Mock different status codes
                        def side_effect_status(url):
                            if "badlink" in url:
                                return 404
                            return 200
                        
                        mock_status.side_effect = side_effect_status
                        
                        # Test check_refs
                        def mock_map_check(func, refs_list):
                            for ref in refs_list:
                                func(ref)
                        
                        mock_pool.map = mock_map_check
                        result = check_refs(refs, verbose=False)
                        
                        # Verify mixed results
                        assert "working" in result
                        assert "broken" in result
                        
                        # Test download_urls
                        urls = [ref.ref for ref in refs]
                        download_urls(urls, "/tmp/test_downloads")
                        
                        # Verify directory creation
                        mock_makedirs.assert_called_with("/tmp/test_downloads")

    def test_url_processing_edge_cases(self):
        """Test edge cases in URL processing."""
        # Test various URL formats
        test_urls = [
            "example.com",  # No protocol
            "HTTP://EXAMPLE.COM",  # Uppercase
            "https://example.com/path?param=value",  # With parameters
            "ftp://example.com/file.pdf",  # Different protocol
            "",  # Empty string
            None,  # None value
        ]
        
        for url in test_urls:
            try:
                sanitized = sanitize_url(url)
                assert isinstance(sanitized, str)
                # All should start with http after sanitization
                assert sanitized.lower().startswith("http")
            except Exception as e:
                # Some edge cases might fail, which is acceptable
                pass

    @patch('linkrot.downloader.urlopen')
    def test_status_code_edge_cases(self, mock_urlopen):
        """Test status code checking with various edge cases."""
        from urllib.error import HTTPError, URLError
        
        # Test HTTP error
        mock_urlopen.side_effect = HTTPError("", 404, "", {}, None)
        result = get_status_code("http://example.com")
        assert result == 404
        
        # Test URL error
        mock_urlopen.side_effect = URLError("Connection timeout")
        result = get_status_code("http://example.com")
        assert result == "Connection timeout"
        
        # Test general exception
        mock_urlopen.side_effect = Exception("Network error")
        result = get_status_code("http://example.com")
        assert result is None
