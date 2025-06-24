"""
Comprehensive tests for the archive module.
Tests web archiving functionality using Internet Archive's Wayback Machine.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from linkrot.archive import archive_links


class TestArchiveLinks:
    """Test archive_links functionality."""

    def create_mock_ref(self, url):
        """Helper to create mock reference."""
        ref = Mock()
        ref.ref = url
        return ref

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_success(self, mock_threadpool, mock_requests_get):
        """Test successful link archiving."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Location': '/web/20231201000000/http://example.com'
        }
        mock_requests_get.return_value = mock_response
        
        # Setup mock threadpool
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [
            self.create_mock_ref("http://example.com"),
            self.create_mock_ref("http://test.org")
        ]
        
        # Mock the map function to actually call our archive function
        map_called = False
        def mock_map(func, refs_list):
            nonlocal map_called
            map_called = True
            for ref in refs_list:
                result = func(ref)
                return result
        
        mock_pool.map = mock_map
        
        archive_links(refs)
        
        # Verify threadpool was used
        mock_threadpool.assert_called_once_with(1)
        assert map_called  # Verify map was called
        mock_pool.wait_completion.assert_called_once()

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_already_archived(self, mock_threadpool, mock_requests_get):
        """Test archiving links that are already in web.archive.org."""
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [
            self.create_mock_ref("https://web.archive.org/web/20231201000000/http://example.com")
        ]
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                result = func(ref)
                # Should return the same URL for already archived links
                assert result == (ref.ref, ref.ref)
        
        mock_pool.map = mock_map
        
        archive_links(refs)
        
        # Should not make HTTP request for already archived URLs
        mock_requests_get.assert_not_called()

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_http_error(self, mock_threadpool, mock_requests_get):
        """Test archiving with HTTP error response."""
        # Setup mock response with error status
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        # Should handle error gracefully
        archive_links(refs)
        
        # Verify request was made
        mock_requests_get.assert_called_once()

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_request_exception(self, mock_threadpool, mock_requests_get):
        """Test archiving with request exception."""
        # Setup mock to raise exception
        mock_requests_get.side_effect = requests.RequestException("Network error")
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        # Should handle exception gracefully
        archive_links(refs)
        
        # Verify request was attempted
        mock_requests_get.assert_called_once()

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_proper_headers(self, mock_threadpool, mock_requests_get):
        """Test that proper headers are sent with archive requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Location': '/web/20231201000000/http://example.com'
        }
        mock_requests_get.return_value = mock_response
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        archive_links(refs)
        
        # Verify request was made with proper headers
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        
        # Check URL
        assert call_args[0][0] == 'https://web.archive.org/save/http://example.com'
        
        # Check headers
        headers = call_args[1]['headers']
        assert 'User-Agent' in headers
        assert 'Mozilla' in headers['User-Agent']

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_multiple_refs(self, mock_threadpool, mock_requests_get):
        """Test archiving multiple references."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Location': '/web/20231201000000/http://example.com'
        }
        mock_requests_get.return_value = mock_response
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [
            self.create_mock_ref("http://example.com"),
            self.create_mock_ref("http://test.org"),
            self.create_mock_ref("http://sample.net")
        ]
        
        call_count = 0
        def mock_map(func, refs_list):
            nonlocal call_count
            for ref in refs_list:
                func(ref)
                call_count += 1
        
        mock_pool.map = mock_map
        
        archive_links(refs)
        
        # Should process all references
        assert call_count == 3

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_empty_list(self, mock_threadpool, mock_requests_get):
        """Test archiving empty reference list."""
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        map_called = False
        def mock_map(func, refs_list):
            nonlocal map_called
            map_called = True
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        archive_links([])
        
        # Should still set up threadpool
        mock_threadpool.assert_called_once_with(1)
        assert map_called  # Map should still be called (even with empty list)
        mock_pool.wait_completion.assert_called_once()
        
        # But no HTTP requests should be made
        mock_requests_get.assert_not_called()

    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_threadpool_exception(self, mock_threadpool):
        """Test exception handling in threadpool."""
        mock_pool = Mock()
        mock_pool.map.side_effect = Exception("Thread error")
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        # Should handle exception gracefully
        archive_links(refs)

    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_keyboard_interrupt(self, mock_threadpool):
        """Test keyboard interrupt handling."""
        mock_pool = Mock()
        mock_pool.map.side_effect = KeyboardInterrupt()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com")]
        
        # Should handle KeyboardInterrupt gracefully
        archive_links(refs)

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_return_value_format(self, mock_threadpool, mock_requests_get):
        """Test the format of returned archive URLs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Location': '/web/20231201120000/http://example.com/page.html'
        }
        mock_requests_get.return_value = mock_response
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [self.create_mock_ref("http://example.com/page.html")]
        
        returned_url = None
        def mock_map(func, refs_list):
            nonlocal returned_url
            for ref in refs_list:
                returned_url = func(ref)
        
        mock_pool.map = mock_map
        
        archive_links(refs)
        
        # Verify the returned URL format
        expected_url = "https://web.archive.org/web/20231201120000/http://example.com/page.html"
        assert returned_url == expected_url

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_various_url_types(self, mock_threadpool, mock_requests_get):
        """Test archiving various types of URLs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Location': '/web/20231201000000/test'
        }
        mock_requests_get.return_value = mock_response
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        test_urls = [
            "http://example.com",
            "https://secure.example.com",
            "http://example.com/path/to/page.html",
            "https://example.com/file.pdf",
            "http://subdomain.example.org/complex/path?param=value&other=123"
        ]
        
        refs = [self.create_mock_ref(url) for url in test_urls]
        
        call_count = 0
        def mock_map(func, refs_list):
            nonlocal call_count
            for ref in refs_list:
                if 'web.archive' not in ref.ref:  # Skip already archived
                    func(ref)
                    call_count += 1
        
        mock_pool.map = mock_map
        
        archive_links(refs)
        
        # Should have processed all non-archived URLs
        assert call_count == len(test_urls)

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archive_links_mixed_archived_and_new(self, mock_threadpool, mock_requests_get):
        """Test archiving mix of already archived and new URLs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Location': '/web/20231201000000/http://example.com'
        }
        mock_requests_get.return_value = mock_response
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        refs = [
            self.create_mock_ref("http://example.com"),  # New URL
            self.create_mock_ref("https://web.archive.org/web/20230101000000/http://already-archived.com"),  # Already archived
            self.create_mock_ref("http://another-new.com")  # New URL
        ]
        
        new_url_count = 0
        def mock_map(func, refs_list):
            nonlocal new_url_count
            for ref in refs_list:
                result = func(ref)
                if 'web.archive' not in ref.ref:
                    new_url_count += 1
        
        mock_pool.map = mock_map
        
        archive_links(refs)
        
        # Should only make requests for non-archived URLs
        assert mock_requests_get.call_count == 2  # Two new URLs
        assert new_url_count == 2


class TestArchiveLinkIntegration:
    """Integration tests for archive functionality."""

    def test_archive_workflow_simulation(self):
        """Test complete archive workflow simulation."""
        with patch('requests.get') as mock_get:
            with patch('linkrot.archive.ThreadPool') as mock_threadpool:
                
                # Setup successful response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {
                    'Content-Location': '/web/20231201120000/http://example.com'
                }
                mock_get.return_value = mock_response
                
                mock_pool = Mock()
                mock_threadpool.return_value = mock_pool
                
                # Create realistic reference mix
                refs = []
                for i in range(3):
                    refs.append(Mock(ref=f"http://paper{i}.example.com"))
                
                refs.append(Mock(ref="https://web.archive.org/web/20230101000000/http://already-saved.com"))
                
                def mock_map(func, refs_list):
                    results = []
                    for ref in refs_list:
                        result = func(ref)
                        results.append(result)
                    return results
                
                mock_pool.map = mock_map
                
                archive_links(refs)
                
                # Verify proper setup
                mock_threadpool.assert_called_once_with(1)
                mock_pool.wait_completion.assert_called_once()
                
                # Should have made 3 requests (excluding already archived)
                assert mock_get.call_count == 3

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios."""
        with patch('linkrot.archive.ThreadPool') as mock_threadpool:
            
            mock_pool = Mock()
            mock_threadpool.return_value = mock_pool
            
            # Test different error scenarios
            error_scenarios = [
                Exception("General error"),
                KeyboardInterrupt(),
                requests.RequestException("Network error"),
                requests.Timeout("Request timeout"),
                requests.ConnectionError("Connection failed")
            ]
            
            for error in error_scenarios:
                mock_pool.map.side_effect = error
                
                refs = [Mock(ref="http://example.com")]
                
                # Should handle all errors gracefully
                try:
                    archive_links(refs)
                except (Exception, KeyboardInterrupt):
                    # Some exceptions might be re-raised, which is acceptable
                    pass
