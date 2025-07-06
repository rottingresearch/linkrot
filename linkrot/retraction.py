#!/usr/bin/env python
"""
Retraction Watch Database integration for checking retracted papers.

This module provides functionality to check DOIs against the Retraction
Watch Database to identify retracted papers and provide warnings about
their use in citations.
"""

import requests
import time
from typing import Set, Dict, Optional
from urllib.parse import quote

from linkrot.colorprint import colorprint, OKBLUE, FAIL, WARNING


class RetractionChecker:
    """
    A class to check DOIs against the Retraction Watch Database.

    The Retraction Watch Database is a comprehensive database of retracted
    scholarly articles. This checker helps identify when cited papers
    have been retracted.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the retraction checker.

        Args:
            api_key: Optional API key for Retraction Watch Database.
                    If not provided, will attempt to use public endpoints.
        """
        self.api_key = api_key
        self.base_url = "http://retractiondatabase.org/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'linkrot-retraction-checker/1.0'
        })

        # Cache to avoid repeated API calls for same DOIs
        self.cache = {}

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds between requests
    
    def _rate_limit(self):
        """Implement basic rate limiting to be respectful to the API."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def check_doi(self, doi: str) -> Dict:
        """
        Check a single DOI against the Retraction Watch Database.

        Args:
            doi: The DOI to check (e.g., "10.1000/182")

        Returns:
            Dict containing retraction information:
            {
                'doi': str,
                'is_retracted': bool,
                'retraction_date': Optional[str],
                'reason': Optional[str],
                'notice_url': Optional[str],
                'title': Optional[str],
                'journal': Optional[str]
            }
        """
        if not doi:
            return {'doi': doi, 'is_retracted': False, 'error': 'Empty DOI'}

        # Check cache first
        if doi in self.cache:
            return self.cache[doi]

        # Implement rate limiting
        self._rate_limit()
        
        result = {
            'doi': doi,
            'is_retracted': False,
            'retraction_date': None,
            'reason': None,
            'notice_url': None,
            'title': None,
            'journal': None,
            'error': None
        }
        
        try:
            # Try multiple approaches to check for retractions

            # Method 1: Direct API call (if available)
            retraction_info = self._check_via_api(doi)
            if retraction_info:
                result.update(retraction_info)

            # Method 2: Check via CrossRef API for retraction notices
            if not result['is_retracted']:
                crossref_info = self._check_via_crossref(doi)
                if crossref_info:
                    result.update(crossref_info)

            # Method 3: Check common retraction indicators in metadata
            if not result['is_retracted']:
                metadata_info = self._check_metadata_indicators(doi)
                if metadata_info:
                    result.update(metadata_info)

        except Exception as e:
            result['error'] = f"Error checking DOI: {str(e)}"

        # Cache the result
        self.cache[doi] = result
        return result
    
    def _check_via_api(self, doi: str) -> Optional[Dict]:
        """
        Check retraction status via Retraction Watch API.

        Note: This is a placeholder implementation as the Retraction Watch
        Database API access may require special permissions.
        """
        try:
            # This would be the actual API call if we had access
            # url = f"{self.base_url}/search"
            # params = {'doi': doi}
            # response = self.session.get(url, params=params, timeout=10)
            
            # For now, return None as we don't have direct API access
            return None

        except Exception:
            return None
    
    def _check_via_crossref(self, doi: str) -> Optional[Dict]:
        """
        Check for retraction information via CrossRef API.

        CrossRef sometimes contains retraction notices and corrections.
        """
        try:
            url = f"https://api.crossref.org/works/{quote(doi)}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                work = data.get('message', {})

                # Check for retraction indicators
                title = work.get('title', [''])[0].lower()
                subject = ' '.join(work.get('subject', [])).lower()

                # Common retraction indicators
                retraction_keywords = [
                    'retraction', 'retracted', 'withdrawn', 'withdrawal',
                    'correction', 'erratum', 'corrigendum'
                ]

                is_retracted = any(keyword in title or keyword in subject
                                   for keyword in retraction_keywords[:4])

                if is_retracted:
                    return {
                        'is_retracted': True,
                        'title': work.get('title', [''])[0],
                        'journal': (work.get('container-title', [''])[0]
                                    if work.get('container-title') else None),
                        'reason': 'Detected via CrossRef metadata',
                        'notice_url': f"https://doi.org/{doi}"
                    }

        except Exception:
            pass

        return None
    
    def _check_metadata_indicators(self, doi: str) -> Optional[Dict]:
        """
        Check for retraction indicators in paper metadata.

        This method looks for common patterns that might indicate
        a retraction or withdrawal.
        """
        try:
            # Check DOI.org for metadata
            url = f"https://doi.org/{doi}"
            response = self.session.get(url, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                text = response.text.lower()

                # Strong retraction indicators
                strong_indicators = [
                    'this article has been retracted',
                    'this paper has been retracted',
                    'retraction notice',
                    'withdrawn by the author',
                    'article withdrawn'
                ]

                for indicator in strong_indicators:
                    if indicator in text:
                        return {
                            'is_retracted': True,
                            'reason': f'Retraction notice found: '
                                      f'"{indicator}"',
                            'notice_url': url
                        }

        except Exception:
            pass

        return None
    
    def check_multiple_dois(self, dois: Set[str]) -> Dict[str, Dict]:
        """
        Check multiple DOIs for retractions.

        Args:
            dois: Set of DOI strings to check

        Returns:
            Dict mapping DOI to retraction information
        """
        results = {}

        for i, doi in enumerate(dois):
            if i > 0:  # Add delay between requests
                time.sleep(0.5)

            results[doi] = self.check_doi(doi)

        return results
    
    def get_retraction_summary(self, results: Dict[str, Dict]) -> Dict:
        """
        Generate a summary of retraction check results.

        Args:
            results: Results from check_multiple_dois

        Returns:
            Summary dictionary with counts and lists
        """
        total_dois = len(results)
        retracted_dois = [doi for doi, info in results.items()
                          if info.get('is_retracted', False)]
        error_dois = [doi for doi, info in results.items()
                      if info.get('error')]

        return {
            'total_checked': total_dois,
            'retracted_count': len(retracted_dois),
            'error_count': len(error_dois),
            'retracted_dois': retracted_dois,
            'error_dois': error_dois,
            'clean_count': total_dois - len(retracted_dois) - len(error_dois)
        }


def check_dois_for_retractions(dois: Set[str], verbose: bool = False) -> Dict:
    """
    Convenience function to check a set of DOIs for retractions.

    Args:
        dois: Set of DOI strings to check
        verbose: Whether to print detailed information

    Returns:
        Dictionary containing check results and summary
    """
    if not dois:
        return {
            'results': {},
            'summary': {'total_checked': 0, 'retracted_count': 0}
        }

    checker = RetractionChecker()

    if verbose:
        colorprint(OKBLUE, f"Checking {len(dois)} DOIs for retractions...")

    results = checker.check_multiple_dois(dois)
    summary = checker.get_retraction_summary(results)

    # Print results if verbose
    if verbose:
        _print_retraction_results(results, summary)

    return {
        'results': results,
        'summary': summary
    }


def _print_retraction_results(results: Dict[str, Dict], summary: Dict):
    """Print formatted retraction check results."""

    print("\nRetraction Check Results:")
    print("========================")
    print(f"Total DOIs checked: {summary['total_checked']}")
    print(f"Clean papers: {summary['clean_count']}")
    print(f"Retracted papers: {summary['retracted_count']}")
    print(f"Errors: {summary['error_count']}")

    # Print retracted papers with details
    if summary['retracted_count'] > 0:
        colorprint(FAIL, "\n⚠️  RETRACTED PAPERS FOUND:")
        for doi in summary['retracted_dois']:
            info = results[doi]
            colorprint(FAIL, f"  DOI: {doi}")
            if info.get('title'):
                print(f"    Title: {info['title']}")
            if info.get('journal'):
                print(f"    Journal: {info['journal']}")
            if info.get('reason'):
                print(f"    Reason: {info['reason']}")
            if info.get('retraction_date'):
                print(f"    Retraction Date: {info['retraction_date']}")
            if info.get('notice_url'):
                print(f"    Notice: {info['notice_url']}")
            print()

    # Print errors if any
    if summary['error_count'] > 0:
        colorprint(WARNING, "\n⚠️  Errors encountered:")
        for doi in summary['error_dois']:
            error = results[doi].get('error', 'Unknown error')
            print(f"  {doi}: {error}")


if __name__ == "__main__":
    # Test the retraction checker
    test_dois = {
        "10.1126/science.1078616",  # This might be retracted (test case)
        "10.1038/nature12373",     # Regular paper
        "10.1000/182"              # Test DOI
    }
    
    print("Testing Retraction Checker:")
    print("=" * 30)
    
    result = check_dois_for_retractions(test_dois, verbose=True)
    print(f"\nSummary: {result['summary']}")
