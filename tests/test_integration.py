"""
Comprehensive integration tests for the entire linkrot library.
Tests end-to-end functionality and module interactions.
"""

import pytest
import tempfile
import os
import json
import shutil
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

import linkrot
from linkrot.backends import Reference, PyMuPDFBackend
from linkrot.cli import main
from linkrot.downloader import check_refs, download_urls
from linkrot.archive import archive_links


class TestFullWorkflowIntegration:
    """Test complete end-to-end workflows."""

    @patch('linkrot.PyMuPDFBackend')
    @patch('builtins.open')
    @patch('os.path.isfile')
    def test_complete_pdf_analysis_workflow(self, mock_isfile, mock_open, mock_backend):
        """Test complete PDF analysis from file to results."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = b"fake pdf"
        
        # Create comprehensive mock backend
        mock_reader = Mock()
        mock_reader.get_text.return_value = """
        Research Paper Title
        
        This paper references several sources including:
        - https://example.com/paper1.pdf
        - http://arxiv.org/abs/2023.12345
        - DOI:10.1234/example.research
        - https://website.com for additional information
        """
        
        mock_reader.get_metadata.return_value = {
            "Title": "Research Paper",
            "Author": "Dr. Researcher",
            "Pages": 10,
            "CreationDate": "2023-12-01"
        }
        
        # Create mock references
        refs = [
            Mock(ref="https://example.com/paper1.pdf", reftype="pdf", page=1),
            Mock(ref="2023.12345", reftype="arxiv", page=1),
            Mock(ref="10.1234/example.research", reftype="doi", page=1),
            Mock(ref="https://website.com", reftype="url", page=1)
        ]
        
        mock_reader.get_references.return_value = refs
        mock_reader.get_references_as_dict.return_value = {
            "pdf": ["https://example.com/paper1.pdf"],
            "arxiv": ["2023.12345"],
            "doi": ["10.1234/example.research"],
            "url": ["https://website.com"]
        }
        
        mock_backend.return_value = mock_reader
        
        # Test the workflow
        pdf = linkrot.linkrot("research.pdf")
        
        # Verify initialization
        assert pdf.uri == "research.pdf"
        assert pdf.fn == "research.pdf"
        assert not pdf.is_url
        
        # Test all getter methods
        text = pdf.get_text()
        metadata = pdf.get_metadata()
        references = pdf.get_references()
        refs_dict = pdf.get_references_as_dict()
        ref_count = pdf.get_references_count()
        
        # Verify results
        assert "Research Paper Title" in text
        assert metadata["Title"] == "Research Paper"
        assert len(references) == 4
        assert ref_count == 4
        assert "pdf" in refs_dict
        assert "arxiv" in refs_dict
        assert "doi" in refs_dict
        assert "url" in refs_dict
        
        # Verify summary structure
        assert "source" in pdf.summary
        assert "metadata" in pdf.summary
        assert "references" in pdf.summary

    @patch('linkrot.urlopen')
    @patch('linkrot.PyMuPDFBackend')
    @patch('linkrot.extract_urls')
    def test_url_based_pdf_workflow(self, mock_extract_urls, mock_backend, mock_urlopen):
        """Test workflow with URL-based PDF."""
        # Setup URL detection
        mock_extract_urls.return_value = ["http://example.com/paper.pdf"]
        
        # Setup URL response
        mock_response = Mock()
        mock_response.read.return_value = b"fake pdf content"
        mock_urlopen.return_value = mock_response
        
        # Setup backend
        mock_reader = Mock()
        mock_reader.get_metadata.return_value = {"Title": "Online Paper"}
        mock_reader.get_references_as_dict.return_value = {"url": ["http://reference.com"]}
        mock_backend.return_value = mock_reader
        
        # Test workflow
        pdf = linkrot.linkrot("http://example.com/paper.pdf")
        
        assert pdf.is_url
        assert pdf.fn == "paper.pdf"
        assert pdf.uri == "http://example.com/paper.pdf"

    @patch('sys.argv', ['linkrot', 'test.pdf', '--json'])
    @patch('linkrot.linkrot')
    def test_cli_json_output_integration(self, mock_linkrot_class):
        """Test CLI with JSON output integration."""
        # Setup mock
        mock_pdf = Mock()
        mock_pdf.get_metadata.return_value = {"Title": "Test Document"}
        mock_pdf.get_references_as_dict.return_value = {"pdf": ["ref.pdf"]}
        mock_pdf.summary = {
            "source": {"location": "test.pdf", "type": "file", "filename": "test.pdf"},
            "metadata": {"Title": "Test Document"},
            "references": {"pdf": ["ref.pdf"]}
        }
        mock_linkrot_class.return_value = mock_pdf
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
        
        # Verify JSON output
        output = mock_stdout.getvalue()
        json_data = json.loads(output)
        
        assert "source" in json_data
        assert "metadata" in json_data
        assert "references" in json_data
        assert json_data["metadata"]["Title"] == "Test Document"

    def test_reference_processing_integration(self):
        """Test reference creation and processing integration."""
        # Test various reference types
        test_cases = [
            ("https://example.com/paper.pdf", "pdf", "https://example.com/paper.pdf"),
            ("http://example.com", "url", "http://example.com"),
            ("https://arxiv.org/abs/2023.12345", "arxiv", "2023.12345"),  # arXiv ID extracted
            ("DOI:10.1234/example", "doi", "10.1234/example")  # DOI extracted
        ]
        
        for url, expected_type, expected_ref in test_cases:
            ref = Reference(url)
            assert ref.ref == expected_ref
            assert ref.reftype == expected_type

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    def test_link_checking_integration(self, mock_threadpool, mock_get_status):
        """Test link checking integration with references."""
        # Setup status codes
        status_map = {
            "http://good.com": 200,
            "http://notfound.com": 404,
            "http://error.com": 500
        }
        
        def status_side_effect(url):
            return status_map.get(url, 200)
        
        mock_get_status.side_effect = status_side_effect
        
        # Setup threadpool
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        # Create test references
        refs = [
            Mock(ref="http://good.com", page=1),
            Mock(ref="http://notfound.com", page=2),
            Mock(ref="http://error.com", page=3)
        ]
        
        result = check_refs(refs, verbose=False)
        
        # Verify results
        assert "Summary of link checker:" in result
        assert "working" in result or "broken" in result

    @patch('requests.get')
    @patch('linkrot.archive.ThreadPool')
    def test_archiving_integration(self, mock_threadpool, mock_requests):
        """Test link archiving integration."""
        # Setup successful archive response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Location': '/web/20231201000000/http://example.com'
        }
        mock_requests.return_value = mock_response
        
        mock_pool = Mock()
        mock_threadpool.return_value = mock_pool
        
        def mock_map(func, refs_list):
            for ref in refs_list:
                func(ref)
        
        mock_pool.map = mock_map
        
        # Test archiving
        refs = [Mock(ref="http://example.com")]
        archive_links(refs)
        
        # Verify archive request was made
        mock_requests.assert_called_once()

    @patch('linkrot.download_urls')
    def test_pdf_download_integration(self, mock_download):
        """Test PDF download integration."""
        # Create a mock linkrot object with proper stream
        pdf = Mock()
        pdf.fn = "test.pdf"
        
        # Create a mock stream that returns bytes
        mock_stream = Mock()
        mock_stream.read.return_value = b"fake pdf content"
        pdf.stream = mock_stream
        pdf.download_pdfs = linkrot.linkrot.download_pdfs.__get__(pdf, linkrot.linkrot)
        
        # Setup references
        pdf_refs = [Mock(ref="http://example.com/ref.pdf", reftype="pdf")]
        pdf.get_references.return_value = pdf_refs
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf.download_pdfs(tmpdir)
            
            # Verify download was called
            mock_download.assert_called_once()


class TestErrorHandlingIntegration:
    """Test error handling across modules."""

    def test_file_not_found_propagation(self):
        """Test FileNotFoundError propagation through system."""
        with pytest.raises(linkrot.FileNotFoundError):
            linkrot.linkrot("nonexistent_file.pdf")

    @patch('urllib.request.urlopen')
    @patch('linkrot.extract_urls')
    def test_download_error_propagation(self, mock_extract_urls, mock_urlopen):
        """Test DownloadError propagation."""
        mock_extract_urls.return_value = ["http://example.com/test.pdf"]
        mock_urlopen.side_effect = Exception("Network error")
        
        with pytest.raises(linkrot.DownloadError):
            linkrot.linkrot("http://example.com/test.pdf")

    @patch('linkrot.PyMuPDFBackend')
    @patch('builtins.open')
    @patch('os.path.isfile')
    def test_pdf_invalid_error_propagation(self, mock_isfile, mock_open, mock_backend):
        """Test PDFInvalidError propagation."""
        mock_isfile.return_value = True
        mock_backend.side_effect = Exception("Invalid PDF")
        
        with pytest.raises(linkrot.PDFInvalidError):
            linkrot.linkrot("invalid.pdf")

    @patch('sys.argv', ['linkrot', 'nonexistent.pdf'])
    def test_cli_error_handling(self):
        """Test CLI error handling integration."""
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Should exit with file not found error code
        assert exc_info.value.code == 1


class TestPerformanceIntegration:
    """Test performance characteristics of integrated workflows."""

    @patch('linkrot.PyMuPDFBackend')
    @patch('builtins.open')
    @patch('os.path.isfile')
    def test_large_reference_list_performance(self, mock_isfile, mock_open, mock_backend):
        """Test performance with large number of references."""
        mock_isfile.return_value = True
        
        # Create many references
        large_ref_list = []
        for i in range(100):
            ref = Mock()
            ref.ref = f"http://example{i}.com/paper.pdf"
            ref.reftype = "pdf"
            large_ref_list.append(ref)
        
        mock_reader = Mock()
        mock_reader.get_metadata.return_value = {"Title": "Large Paper"}
        mock_reader.get_references.return_value = large_ref_list
        mock_reader.get_references_as_dict.return_value = {
            "pdf": [ref.ref for ref in large_ref_list]
        }
        mock_backend.return_value = mock_reader
        
        import time
        start_time = time.time()
        
        pdf = linkrot.linkrot("large_paper.pdf")
        refs = pdf.get_references()
        ref_count = pdf.get_references_count()
        
        end_time = time.time()
        
        # Should handle large reference lists efficiently
        assert len(refs) == 100
        assert ref_count == 100
        assert end_time - start_time < 1.0  # Should complete quickly

    @patch('linkrot.downloader.get_status_code')
    @patch('linkrot.downloader.ThreadPool')
    def test_concurrent_link_checking_performance(self, mock_threadpool, mock_get_status):
        """Test concurrent link checking performance."""
        mock_get_status.return_value = 200
        
        # Create realistic threadpool behavior
        import threading
        import time
        
        actual_pool = linkrot.threadpool.ThreadPool(5)
        mock_threadpool.return_value = actual_pool
        
        # Create many references to check
        refs = []
        for i in range(20):
            ref = Mock()
            ref.ref = f"http://example{i}.com"
            ref.page = i
            refs.append(ref)
        
        start_time = time.time()
        result = check_refs(refs, verbose=False)
        end_time = time.time()
        
        # Should complete reasonably quickly with threading
        assert end_time - start_time < 2.0
        assert "Summary of link checker:" in result


class TestModuleInteractionIntegration:
    """Test interactions between different modules."""

    def test_extractor_backend_integration(self):
        """Test integration between extractor and backends modules."""
        from linkrot import extractor
        from linkrot.backends import Reference
        
        # Test text with various reference types
        test_text = """
        Visit https://example.com for more info.
        See paper at arxiv:2023.12345
        Citation: DOI:10.1234/example.research
        Download from http://files.example.com/paper.pdf
        """
        
        # Extract using extractor
        urls = extractor.extract_urls(test_text)
        arxivs = extractor.extract_arxiv(test_text)
        dois = extractor.extract_doi(test_text)
        
        # Create references using backends
        references = []
        for url in urls:
            references.append(Reference(url))
        
        # Verify integration
        assert len(urls) >= 2  # Should find URLs
        assert len(arxivs) >= 1  # Should find arXiv
        assert len(dois) >= 1  # Should find DOI
        assert len(references) >= 2  # Should create references

    @patch('linkrot.threadpool.ThreadPool')
    def test_downloader_threadpool_integration(self, mock_threadpool):
        """Test integration between downloader and threadpool modules."""
        # Use real threadpool for integration test
        real_pool = linkrot.threadpool.ThreadPool(3)
        mock_threadpool.return_value = real_pool
        
        with patch('os.makedirs'):
            with patch('os.path.exists', return_value=False):
                urls = [
                    "http://example.com/file1.pdf",
                    "http://example.com/file2.pdf",
                    "http://example.com/file3.pdf"
                ]
                
                # Should use threadpool successfully
                download_urls(urls, "/tmp/test")

    def test_cli_all_modules_integration(self):
        """Test CLI integration with all modules."""
        with patch('sys.argv', ['linkrot', 'test.pdf', '--verbose', '--check-links']):
            with patch('linkrot.linkrot') as mock_linkrot_class:
                with patch('linkrot.downloader.check_refs') as mock_check:
                    
                    # Setup comprehensive mock
                    mock_pdf = Mock()
                    mock_pdf.get_metadata.return_value = {"Title": "Integration Test"}
                    mock_pdf.get_references.return_value = [Mock(ref="http://test.com")]
                    mock_pdf.get_references_as_dict.return_value = {"url": ["http://test.com"]}
                    mock_linkrot_class.return_value = mock_pdf
                    
                    mock_check.return_value = "Link check complete"
                    
                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        main()
                    
                    # Verify all components were used
                    mock_linkrot_class.assert_called_once_with('test.pdf')
                    mock_check.assert_called_once()
                    
                    output = mock_stdout.getvalue()
                    assert "Integration Test" in output
                    assert "Link check complete" in output


class TestRealFileIntegration:
    """Test integration with real files if available."""

    def test_real_pdf_if_available(self):
        """Test with real PDF files if they exist in test directory."""
        test_pdf_path = "/Users/Marshal/Documents/GitHub/linkrot/tests/pdfs/valid.pdf"
        
        if os.path.exists(test_pdf_path):
            # Test with real file
            pdf = linkrot.linkrot(test_pdf_path)
            
            # Basic functionality should work
            text = pdf.get_text()
            metadata = pdf.get_metadata()
            references = pdf.get_references()
            
            assert isinstance(text, str)
            assert isinstance(metadata, dict)
            assert isinstance(references, list)
            
            # Should have some content
            assert len(text) > 0
            
            # Test reference counting
            total_count = pdf.get_references_count()
            pdf_count = pdf.get_references_count(reftype="pdf")
            
            assert total_count >= pdf_count
            assert total_count >= 0

    def test_real_workflow_if_files_available(self):
        """Test complete workflow with real files if available."""
        test_pdf_path = "/Users/Marshal/Documents/GitHub/linkrot/tests/pdfs/valid.pdf"
        
        if os.path.exists(test_pdf_path):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Test complete workflow
                pdf = linkrot.linkrot(test_pdf_path)
                
                # Get all information
                text = pdf.get_text()
                metadata = pdf.get_metadata()
                references = pdf.get_references()
                refs_dict = pdf.get_references_as_dict()
                
                # Test download (if there are PDF references)
                pdf_refs = pdf.get_references(reftype="pdf")
                if pdf_refs:
                    # Note: We won't actually download in tests
                    # but we can test the setup
                    output_dir = os.path.join(tmpdir, "downloads")
                    # pdf.download_pdfs(output_dir)  # Commented out to avoid actual downloads
                
                # Verify we got reasonable results
                assert len(text) > 100  # Should have substantial content
                assert "Title" in metadata or "title" in metadata or len(metadata) > 0
