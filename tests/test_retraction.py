#!/usr/bin/env python
"""
Unit tests for the retraction module.

Tests the functionality for checking DOIs against retraction databases
and identifying retracted papers.
"""

import pytest
from unittest.mock import patch, Mock
from linkrot.retraction import (
    RetractionChecker,
    check_dois_for_retractions,
    _print_retraction_results
)


class TestRetractionChecker:
    """Test cases for the RetractionChecker class."""

    def test_init(self):
        """Test RetractionChecker initialization."""
        checker = RetractionChecker()
        assert checker.api_key is None
        assert checker.base_url == "http://retractiondatabase.org/api"
        assert isinstance(checker.cache, dict)
        assert checker.min_request_interval == 1.0

    def test_init_with_api_key(self):
        """Test RetractionChecker initialization with API key."""
        api_key = "test_key_123"
        checker = RetractionChecker(api_key=api_key)
        assert checker.api_key == api_key

    def test_check_doi_empty(self):
        """Test checking an empty DOI."""
        checker = RetractionChecker()
        result = checker.check_doi("")
        assert result['doi'] == ""
        assert result['is_retracted'] is False
        assert result['error'] == 'Empty DOI'

    def test_check_doi_none(self):
        """Test checking a None DOI."""
        checker = RetractionChecker()
        result = checker.check_doi(None)
        assert result['doi'] is None
        assert result['is_retracted'] is False
        assert result['error'] == 'Empty DOI'

    def test_check_doi_caching(self):
        """Test that DOI checks are cached."""
        checker = RetractionChecker()
        doi = "10.1000/test"
        
        # First call should make actual check
        with patch.object(checker, '_check_via_crossref', return_value=None):
            with patch.object(checker, '_check_metadata_indicators',
                              return_value=None):
                result1 = checker.check_doi(doi)
        
        # Second call should use cache
        result2 = checker.check_doi(doi)
        
        assert result1 == result2
        assert doi in checker.cache

    @patch('requests.Session.get')
    def test_check_via_crossref_success(self, mock_get):
        """Test successful CrossRef API check."""
        checker = RetractionChecker()
        
        # Mock successful CrossRef response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {
                'title': ['Retraction: Some paper title'],
                'container-title': ['Nature'],
                'subject': []
            }
        }
        mock_get.return_value = mock_response
        
        result = checker._check_via_crossref("10.1000/test")
        
        assert result is not None
        assert result['is_retracted'] is True
        assert result['title'] == 'Retraction: Some paper title'
        assert result['journal'] == 'Nature'
        assert result['reason'] == 'Detected via CrossRef metadata'

    @patch('requests.Session.get')
    def test_check_via_crossref_not_retracted(self, mock_get):
        """Test CrossRef API check for non-retracted paper."""
        checker = RetractionChecker()
        
        # Mock successful CrossRef response without retraction indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {
                'title': ['Some normal paper title'],
                'container-title': ['Nature'],
                'subject': []
            }
        }
        mock_get.return_value = mock_response
        
        result = checker._check_via_crossref("10.1000/test")
        
        assert result is None

    @patch('requests.Session.get')
    def test_check_via_crossref_error(self, mock_get):
        """Test CrossRef API check with network error."""
        checker = RetractionChecker()
        
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        result = checker._check_via_crossref("10.1000/test")
        
        assert result is None

    @patch('requests.Session.get')
    def test_check_metadata_indicators_retracted(self, mock_get):
        """Test metadata check finding retraction notice."""
        checker = RetractionChecker()
        
        # Mock DOI.org response with retraction notice
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "This article has been retracted due to errors"
        mock_get.return_value = mock_response
        
        result = checker._check_metadata_indicators("10.1000/test")
        
        assert result is not None
        assert result['is_retracted'] is True
        assert 'this article has been retracted' in result['reason']

    @patch('requests.Session.get')
    def test_check_metadata_indicators_clean(self, mock_get):
        """Test metadata check for clean paper."""
        checker = RetractionChecker()
        
        # Mock DOI.org response without retraction indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "This is a normal research article abstract"
        mock_get.return_value = mock_response
        
        result = checker._check_metadata_indicators("10.1000/test")
        
        assert result is None

    def test_check_multiple_dois(self):
        """Test checking multiple DOIs."""
        checker = RetractionChecker()
        dois = {"10.1000/test1", "10.1000/test2"}
        
        with patch.object(checker, 'check_doi') as mock_check:
            mock_check.side_effect = [
                {'doi': '10.1000/test1', 'is_retracted': False},
                {'doi': '10.1000/test2', 'is_retracted': True}
            ]
            
            results = checker.check_multiple_dois(dois)
            
            assert len(results) == 2
            assert mock_check.call_count == 2

    def test_get_retraction_summary(self):
        """Test summary generation."""
        checker = RetractionChecker()
        
        results = {
            '10.1000/test1': {'is_retracted': False},
            '10.1000/test2': {'is_retracted': True},
            '10.1000/test3': {'is_retracted': False, 'error': 'Network error'},
            '10.1000/test4': {'is_retracted': False}
        }
        
        summary = checker.get_retraction_summary(results)
        
        assert summary['total_checked'] == 4
        assert summary['retracted_count'] == 1
        assert summary['error_count'] == 1
        assert summary['clean_count'] == 2
        assert '10.1000/test2' in summary['retracted_dois']
        assert '10.1000/test3' in summary['error_dois']


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_check_dois_for_retractions_empty(self):
        """Test checking empty DOI set."""
        result = check_dois_for_retractions(set())
        
        assert result['results'] == {}
        assert result['summary']['total_checked'] == 0
        assert result['summary']['retracted_count'] == 0

    @patch('linkrot.retraction.RetractionChecker')
    def test_check_dois_for_retractions_with_dois(self, mock_checker_class):
        """Test checking DOIs with mocked checker."""
        mock_checker = Mock()
        mock_checker_class.return_value = mock_checker
        
        # Mock checker methods
        mock_results = {
            '10.1000/test': {'is_retracted': False}
        }
        mock_summary = {
            'total_checked': 1,
            'retracted_count': 0,
            'error_count': 0,
            'clean_count': 1
        }
        
        mock_checker.check_multiple_dois.return_value = mock_results
        mock_checker.get_retraction_summary.return_value = mock_summary
        
        dois = {'10.1000/test'}
        result = check_dois_for_retractions(dois, verbose=False)
        
        assert result['results'] == mock_results
        assert result['summary'] == mock_summary
        mock_checker.check_multiple_dois.assert_called_once_with(dois)

    def test_print_retraction_results_clean(self, capsys):
        """Test printing results with no retractions."""
        results = {
            '10.1000/test': {'is_retracted': False}
        }
        summary = {
            'total_checked': 1,
            'retracted_count': 0,
            'error_count': 0,
            'clean_count': 1,
            'retracted_dois': [],
            'error_dois': []
        }
        
        _print_retraction_results(results, summary)
        
        captured = capsys.readouterr()
        assert "Total DOIs checked: 1" in captured.out
        assert "Clean papers: 1" in captured.out
        assert "Retracted papers: 0" in captured.out

    def test_print_retraction_results_with_retractions(self, capsys):
        """Test printing results with retractions."""
        results = {
            '10.1000/retracted': {
                'is_retracted': True,
                'title': 'A Retracted Paper',
                'journal': 'Test Journal',
                'reason': 'Data fabrication',
                'notice_url': 'https://doi.org/10.1000/retracted'
            }
        }
        summary = {
            'total_checked': 1,
            'retracted_count': 1,
            'error_count': 0,
            'clean_count': 0,
            'retracted_dois': ['10.1000/retracted'],
            'error_dois': []
        }
        
        _print_retraction_results(results, summary)
        
        captured = capsys.readouterr()
        assert "RETRACTED PAPERS FOUND" in captured.out
        assert "10.1000/retracted" in captured.out
        assert "A Retracted Paper" in captured.out


if __name__ == "__main__":
    pytest.main([__file__])
