#!/usr/bin/env python
"""
Example usage of the linkrot retraction checking functionality.

This script demonstrates how to use the retraction checking feature
to identify potentially retracted papers in a PDF document.
"""

from linkrot.retraction import check_dois_for_retractions
from linkrot.extractor import extract_doi


def demo_retraction_checking():
    """Demonstrate retraction checking with example DOIs."""
    
    print("Linkrot Retraction Checking Demo")
    print("=" * 40)
    
    # Example text that might be extracted from a PDF
    sample_text = """
    This research builds on previous work (DOI: 10.1126/science.1078616)
    and also references a more recent study (doi:10.1038/nature12373).
    Additional work can be found at https://doi.org/10.1000/182.
    """
    
    print("Sample text from PDF:")
    print(sample_text)
    print()
    
    # Extract DOIs from the text
    print("Extracting DOIs...")
    dois = extract_doi(sample_text)
    print(f"Found DOIs: {list(dois)}")
    print()
    
    # Check for retractions
    print("Checking for retractions...")
    result = check_dois_for_retractions(dois, verbose=True)
    
    print("\nFinal summary:")
    print(f"- Total DOIs checked: {result['summary']['total_checked']}")
    print(f"- Clean papers: {result['summary']['clean_count']}")
    print(f"- Retracted papers: {result['summary']['retracted_count']}")
    print(f"- Errors: {result['summary']['error_count']}")
    
    if result['summary']['retracted_count'] > 0:
        print("\n⚠️  WARNING: Some papers may be retracted!")
        print("Please verify the retraction status before citing.")
    else:
        print("\n✅ No retractions detected in the checked papers.")


def demo_cli_usage():
    """Show examples of CLI usage."""
    
    print("\n" + "=" * 50)
    print("CLI Usage Examples")
    print("=" * 50)
    
    examples = [
        "# Basic retraction check on a PDF:",
        "python -m linkrot.cli document.pdf -r",
        "",
        "# Check retractions and output as JSON:",
        "python -m linkrot.cli document.pdf -r -j",
        "",
        "# Check retractions with verbose output:",
        "python -m linkrot.cli document.pdf -r -v",
        "",
        "# Check retractions and also check for broken links:",
        "python -m linkrot.cli document.pdf -r -c",
        "",
        "# Save retraction check results to a file:",
        "python -m linkrot.cli document.pdf -r -o results.txt",
    ]
    
    for example in examples:
        print(example)


if __name__ == "__main__":
    demo_retraction_checking()
    demo_cli_usage()
