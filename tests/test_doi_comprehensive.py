#!/usr/bin/env python3
"""
Comprehensive test for the improved DOI extraction functionality.
This demonstrates the enhanced DOI pattern matching capabilities.
"""

import sys
import os

# Add the linkrot directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'linkrot'))

from extractor import extract_doi

def test_doi_formats():
    """Test various DOI formats found in academic writing."""
    
    test_cases = [
        # Traditional formats
        {
            'name': 'Traditional DOI with colon',
            'text': 'DOI: 10.1000/182',
            'expected': {'10.1000/182'}
        },
        {
            'name': 'Traditional DOI lowercase',
            'text': 'doi:10.1038/nature12373',
            'expected': {'10.1038/nature12373'}
        },
        
        # URL-based formats
        {
            'name': 'HTTPS DOI URL',
            'text': 'Available at https://doi.org/10.1126/science.abc1234',
            'expected': {'10.1126/science.abc1234'}
        },
        {
            'name': 'HTTP DOI URL',
            'text': 'See http://doi.org/10.1371/journal.pone.0123456',
            'expected': {'10.1371/journal.pone.0123456'}
        },
        {
            'name': 'dx.doi.org format',
            'text': 'Reference: dx.doi.org/10.1000/456',
            'expected': {'10.1000/456'}
        },
        {
            'name': 'HTTPS dx.doi.org format',
            'text': 'See https://dx.doi.org/10.1109/ACCESS.2021.1234567',
            'expected': {'10.1109/ACCESS.2021.1234567'}
        },
        
        # DOI without colon
        {
            'name': 'DOI without colon',
            'text': 'DOI 10.1038/s41586-021-03828-1',
            'expected': {'10.1038/s41586-021-03828-1'}
        },
        
        # DOI in parentheses/brackets
        {
            'name': 'DOI in parentheses',
            'text': 'Multiple references (DOI: 10.1000/182)',
            'expected': {'10.1000/182'}
        },
        {
            'name': 'DOI in brackets',
            'text': 'See reference [doi:10.1038/nature12373]',
            'expected': {'10.1038/nature12373'}
        },
        
        # Complex DOIs
        {
            'name': 'Complex DOI with underscores',
            'text': 'doi:10.1371/journal.pone.0123456',
            'expected': {'10.1371/journal.pone.0123456'}
        },
        {
            'name': 'DOI with mixed case',
            'text': 'DOi: 10.1109/ACCESS.2021.1234567',
            'expected': {'10.1109/ACCESS.2021.1234567'}
        },
        
        # Multiple DOIs
        {
            'name': 'Multiple DOIs in text',
            'text': 'References: DOI: 10.1000/182, https://doi.org/10.1038/nature12373, and (DOI: 10.1126/science.abc1234)',
            'expected': {'10.1000/182', '10.1038/nature12373', '10.1126/science.abc1234'}
        },
        
        # PDF-like splits
        {
            'name': 'DOI split across lines',
            'text': '''
            References include DOI:
            10.1000/182 and https://doi.org/
            10.1038/nature12373
            ''',
            'expected': {'10.1000/182', '10.1038/nature12373'}
        },
        
        # Edge cases
        {
            'name': 'DOI with extra spacing',
            'text': 'doi:   10.1371/journal.pone.0123456',
            'expected': {'10.1371/journal.pone.0123456'}
        },
        {
            'name': 'DOI with trailing punctuation',
            'text': 'See DOI: 10.1000/182.',
            'expected': {'10.1000/182'}
        },
        
        # Should NOT match
        {
            'name': 'Invalid DOI format (too short)',
            'text': 'DOI: 10.1/x',
            'expected': set()  # Should not match - registrant code too short
        },
        {
            'name': 'Not a DOI',
            'text': 'Version 10.1000 of the software',
            'expected': set()  # Should not match - not a DOI
        }
    ]
    
    print("Testing Enhanced DOI Extraction")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 40)
        
        # Show the input text (truncated for readability)
        text_preview = repr(test_case['text'][:80])
        if len(test_case['text']) > 80:
            text_preview += "..."
        print(f"Input: {text_preview}")
        
        # Extract DOIs
        result = extract_doi(test_case['text'])
        expected = test_case['expected']
        
        print(f"Expected: {expected}")
        print(f"Got:      {result}")
        
        # Check if the test passed
        if result == expected:
            print("✓ PASS")
            passed += 1
        else:
            print("✗ FAIL")
            failed += 1
            
            # Show what was different
            missing = expected - result
            extra = result - expected
            if missing:
                print(f"  Missing: {missing}")
            if extra:
                print(f"  Extra:   {extra}")
    
    print("\n" + "=" * 50)
    print(f"Summary: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("\n🎉 All DOI extraction tests passed!")
        print("The improved DOI regex successfully handles:")
        print("  • Traditional DOI: formats (with and without colons)")
        print("  • URL-based DOI formats (doi.org, dx.doi.org)")
        print("  • DOIs in parentheses and brackets")
        print("  • Mixed case and extra whitespace")
        print("  • DOIs split across lines (PDF extraction)")
        print("  • Complex DOI identifiers with various characters")
        print("  • Proper validation to avoid false positives")
    else:
        print(f"\n⚠️  {failed} test(s) failed - improvements needed")
    
    return failed == 0

if __name__ == "__main__":
    success = test_doi_formats()
    sys.exit(0 if success else 1)
