#!/usr/bin/python
import re

# arXiv.org
ARXIV_REGEX = r"""arxiv:\s?([^\s,]+)"""
ARXIV_REGEX2 = r"""arxiv.org/abs/([^\s,]+)"""

# DOI - Updated to handle modern DOI formats and citation styles
# Matches various formats like:
# DOI: 10.1000/182
# doi:10.1038/nature12373
# https://doi.org/10.1126/science.123456
# dx.doi.org/10.1000/182
# DOI 10.1000/182 (without colon)
# (DOI: 10.1000/182)
DOI_REGEX = r"""(?i)(?:(?:https?://)?(?:dx\.)?doi\.org/|doi:?\s*)([0-9]{2}\.[0-9]{4,}/[^\s,;)\]}>]+)"""

# Additional DOI pattern for cases with "DOI" followed by space/colon
DOI_REGEX2 = r"""(?i)doi:?\s+([0-9]{2}\.[0-9]{4,}/[^\s,;)\]}>]+)"""

# Pattern for DOIs in parentheses or brackets
DOI_REGEX3 = r"""(?i)[\(\[]doi:?\s*([0-9]{2}\.[0-9]{4,}/[^\s,;)\]}>]+)[\)\]]"""

# Common top-level domains (focused on most used TLDs for better performance)
COMMON_TLDS = r"""(?:com|net|org|edu|gov|mil|int|aero|asia|biz|cat|coop|info|jobs|mobi|museum|name|post|pro|tel|travel|xxx|io|ai|co|uk|de|jp|fr|au|ca|br|ru|cn|in|mx|it|es|nl|be|ch|se|no|dk|fi|pl|cz|at|hu|gr|pt|ie|ro|bg|hr|si|sk|lt|lv|ee|lu|mt|cy|is|li|ad|mc|sm|va|md|me|rs|mk|ba|al|by|ua|kz|kg|tj|tm|uz|am|az|ge|tr|il|lb|sy|jo|sa|ae|kw|qa|bh|om|ye|iq|ir|af|pk|bd|lk|mv|np|bt|mm|th|la|kh|vn|my|sg|bn|id|ph|tw|kr|kp|mn|hk|mo|fm|pw|mh|mp|gu|as|vi|pr|tc|vg|ag|dm|gd|kn|lc|vc|bb|tt|jm|ht|do|cu|bs|bz|gt|sv|hn|ni|cr|pa|ve|gy|sr|ec|pe|bo|py|uy|ar|cl|fk|gs)"""

# Improved URL regex that's more readable and handles PDF extraction better
URL_REGEX = rf"""(?ix)
    \b(?:
        # Full URLs with protocol (http/https)
        (?:https?://
            (?:[-\w.])+                           # domain
            (?::\d+)?                             # optional port
            (?:/(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?)? # optional path
        )|
        
        # Domain-only URLs (common in academic papers)
        (?:(?<![\w@])                             # not preceded by word char or @
            (?:[-\w]+\.)+                         # subdomains
            {COMMON_TLDS}                         # TLD
            (?:/(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?)? # optional path
        )
    )\b
"""

def clean_url_text(text):
    """
    Clean text to handle URLs that may be split across lines in PDFs.
    This is especially important for PDFs where URLs can be broken with
    line breaks, page breaks, or extra whitespace.
    """
    if not text:
        return text
    
    # Remove form feed characters (page breaks)
    text = text.replace('\x0c', ' ')
    
    # Handle URLs split with hyphens at line breaks (common in PDFs)
    # Pattern: "http://example.com/some-\npath" -> "http://example.com/somepath"
    text = re.sub(r'(https?://[^\s]+)-\s*\n\s*([a-zA-Z0-9])', r'\1\2', text, flags=re.IGNORECASE)
    
    # Handle general URL parts split across lines
    # Pattern: "https://arxiv.org/abs/\n2021.12345" -> "https://arxiv.org/abs/2021.12345"
    # Only match if the next line doesn't start with a word (to avoid capturing unrelated text)
    text = re.sub(r'(https?://[^\s]*)\s*\n\s*([^\s\w][^\s]*|[0-9][^\s]*)', r'\1\2', text, flags=re.IGNORECASE)
    
    # Handle domain splits like "example.\ncom" or "www.example.\n com"
    text = re.sub(r'([a-zA-Z0-9-]+)\.\s*\n\s*(' + COMMON_TLDS.strip('(?:)') + r')\b', 
                  r'\1.\2', text, flags=re.IGNORECASE)
    
    # Handle www splits like "www.\nexample.com"
    text = re.sub(r'www\.\s*\n\s*([a-zA-Z0-9-]+)', r'www.\1', text, flags=re.IGNORECASE)
    
    # Handle path splits without hyphens like "example.com/\npath"
    text = re.sub(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/\s*\n\s*([^\s]+)', r'\1/\2', text, flags=re.IGNORECASE)
    
    # Clean up multiple spaces but preserve structure
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    
    return text.strip()

def extract_urls(text):
    """
    This function will return all the unique URLs found in the `text` argument.
    
    Improvements for PDF extraction:
    - Handles URLs split across lines
    - Cleans up whitespace and page breaks
    - Uses more efficient regex patterns
    - Better handling of domain-only URLs common in academic papers
    """
    # First clean the text to handle PDF-specific issues
    cleaned_text = clean_url_text(text)
    
    # Find URLs using the improved regex
    urls = set(re.findall(URL_REGEX, cleaned_text))
    
    # Additional cleanup of found URLs
    cleaned_urls = set()
    for url in urls:
        # Remove trailing punctuation that shouldn't be part of URL
        url = re.sub(r'[.,;:!?\'")\]}]+$', '', url)
        
        # Ensure we have a valid URL structure
        if url and (url.startswith(('http://', 'https://')) or '.' in url):
            cleaned_urls.add(url)
    
    return cleaned_urls

def extract_arxiv(text):
    """
    This function will return all the unique occurences of `arxiv.org/abs/` or `arxiv:`.
    
    - First we find all matches of the form `arxiv:`
    - Then we find all matches of the form `arxiv.org/abs/`
    - Then we concat them into a single list
    - Then we strip out any `.` from the start and end of any item in the list
    - Finally we turn the list into a set, so we only end up with unique URLs (no duplicates)
    """
    # Clean text for better matching across lines
    cleaned_text = clean_url_text(text)
    
    res = re.findall(ARXIV_REGEX, cleaned_text, re.MULTILINE) + re.findall(
        ARXIV_REGEX2, cleaned_text, re.MULTILINE
    )
    return {r.strip(".") for r in res}

def extract_doi(text):
    """
    This function will return all the unique DOIs found in `text` argument.
    
    Handles modern DOI formats including:
    - DOI: 10.1000/182
    - doi:10.1038/nature12373  
    - https://doi.org/10.1126/science.123456
    - dx.doi.org/10.1000/182
    - DOI 10.1000/182 (without colon)
    - (DOI: 10.1000/182) in parentheses
    
    Returns:
        Set of unique DOI identifiers (without prefixes)
    """
    if not text:
        return set()
    
    # Clean text for better matching across lines
    cleaned_text = clean_url_text(text)
    
    # Find DOIs using all patterns
    dois = []
    dois.extend(re.findall(DOI_REGEX, cleaned_text, re.MULTILINE | re.IGNORECASE))
    dois.extend(re.findall(DOI_REGEX2, cleaned_text, re.MULTILINE | re.IGNORECASE))
    dois.extend(re.findall(DOI_REGEX3, cleaned_text, re.MULTILINE | re.IGNORECASE))
    
    # Clean and validate DOIs
    cleaned_dois = set()
    for doi in dois:
        # Remove trailing punctuation
        doi = doi.strip('.,;:!?')
        
        # Validate DOI format (should be like 10.xxxx/something)
        if doi and re.match(r'^10\.\d{4,}/\S+', doi):
            cleaned_dois.add(doi)
    
    return cleaned_dois

if __name__ == "__main__":
    # Test cases for improved extraction
    print("Testing arXiv extraction:")
    print(extract_arxiv("arxiv:123 . arxiv: 345 455 http://arxiv.org/abs/876"))
    
    print("\nTesting URL extraction with simple text:")
    test_text = """
    Visit https://example.com for more info.
    Also check www.test.org and http://github.com/user/repo
    """
    print(extract_urls(test_text))
    
    # Test PDF-like text with various splits
    print("\nTesting PDF-like text with line breaks:")
    pdf_text1 = """
    See the paper at https://arxiv.org/abs/
    2021.12345 and the website www.university.
    edu for details.
    """
    print("Test 1 (URL split at path):", extract_urls(pdf_text1))
    
    pdf_text2 = """
    Visit the repository at https://github.com/user/very-
    long-repository-name for the source code.
    """
    print("Test 2 (URL split with hyphen):", extract_urls(pdf_text2))
    
    pdf_text3 = """
    The documentation is available at www.
    example.com/docs and also at
    https://secondary-site.
    org/information
    """
    print("Test 3 (Domain splits):", extract_urls(pdf_text3))
    
    pdf_text4 = """
    Multiple sites: www.site1.com, https://site2.
    net/path, and http://site3.org/very-
    long-path/to/resource
    """
    print("Test 4 (Multiple split URLs):", extract_urls(pdf_text4))
    
    # Test DOI extraction with various modern formats
    print("\nTesting DOI extraction with modern formats:")
    
    # Traditional DOI formats
    doi_text1 = "DOI: 10.1000/182 and also DOI:10.1038/nature12373"
    print("Traditional format:", extract_doi(doi_text1))
    
    # URL-based DOI formats
    doi_text2 = "Available at https://doi.org/10.1126/science.abc1234 and dx.doi.org/10.1000/456"
    print("URL format:", extract_doi(doi_text2))
    
    # DOI without colon
    doi_text3 = "See DOI 10.1038/s41586-021-03828-1 for details"
    print("No colon format:", extract_doi(doi_text3))
    
    # DOI in parentheses/brackets
    doi_text4 = "Multiple references (DOI: 10.1000/182) and [doi:10.1038/nature12373]"
    print("Parentheses format:", extract_doi(doi_text4))
    
    # Mixed case and spacing
    doi_text5 = "doi:   10.1371/journal.pone.0123456 and DOi: 10.1109/ACCESS.2021.1234567"
    print("Mixed case/spacing:", extract_doi(doi_text5))
    
    # DOI split across lines (PDF-like)
    doi_text6 = """
    References include DOI:
    10.1000/182 and https://doi.org/
    10.1038/nature12373
    """
    print("Split across lines:", extract_doi(doi_text6))
    
    # Demonstrate clean_url_text function
    print("\nTesting text cleaning function:")
    dirty_text = """Visit https://www.example.com/very-
    long-path for more info. Also see www.
    university.edu/research."""
    print("Original text:")
    print(repr(dirty_text))
    print("\nCleaned text:")
    print(repr(clean_url_text(dirty_text)))
    print("\nExtracted URLs:")
    print(extract_urls(dirty_text))
