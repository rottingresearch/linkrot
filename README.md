![linkrot logo](https://github.com/marshalmiller/linkrot/blob/6e6fb45239f8d06e89671e2ec68a11629747355d/branding/Asset%207@4x.png)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frottingresearch%2Flinkrot.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Frottingresearch%2Flinkrot?ref=badge_shield)
# Introduction

Scans PDFs for links written in plaintext and checks if they are active or returns an error code. It then generates a report of its findings. Extract references (PDF, URL, DOI, arXiv) and metadata from a PDF.

**New in v5.2.2**: Retraction checking! linkrot now automatically checks DOIs against retraction databases to identify potentially retracted papers, helping ensure research integrity.

Check out our sister project, [Rotting Research](https://github.com/marshalmiller/rottingresearch), for a web app implementation of this project.

# Features

- Extract references and metadata from a given PDF.  
- Detects PDF, URL, arXiv and DOI references.
- **Check DOIs for retracted papers** (using the -r flag).
- Archives valid links using Internet Archive's Wayback Machine (using the -a flag).
- Checks for valid SSL certificate.  
- Find broken hyperlinks (using the -c flag).  
- Output as text or JSON (using the -j flag).  
- Extract the PDF text (using the --text flag).  
- Use as command-line tool or Python package.  
- Works with local and online PDFs.  

# Installation

## PyPI (Recommended)
Grab a copy of the code with pip:
 
```bash
pip install linkrot
```

## Debian/Ubuntu Package
For Debian/Ubuntu systems, you can build and install a .deb package:

```bash
# Install build dependencies
sudo apt-get install dpkg-dev debhelper dh-python python3-setuptools

# Build the package
python3 setup-deb-build.py
./build-deb.sh

# Install the packages
sudo dpkg -i ../python3-linkrot_*.deb ../linkrot_*.deb
sudo apt-get install -f  # Fix any dependency issues
```

See `debian/README.md` for detailed packaging instructions.

# Usage

linkrot can be used to extract info from a PDF in two ways:
- Command line/Terminal tool `linkrot`
- Python library `import linkrot`

## 1. Command Line/Terminal tool

```bash
linkrot [pdf-file-or-url]
```

Run linkrot -h to see the help output:
```bash
linkrot -h
```

usage: 
```bash 
linkrot [-h] [-d OUTPUT_DIRECTORY] [-c] [-r] [-j] [-v] [-t] [-o OUTPUT_FILE] [--version] pdf
```

Extract metadata and references from a PDF, and optionally download all
referenced PDFs.

### Arguments

#### positional arguments:
  pdf                   (Filename or URL of a PDF file)  

#### optional arguments:
    -h, --help            (Show this help message and exit)  
    -d OUTPUT_DIRECTORY,  --download-pdfs OUTPUT_DIRECTORY (Download all referenced PDFs into specified directory)  
    -c, --check-links     (Check for broken links)  
    -r, --check-retractions (Check DOIs for retracted papers)
    -j, --json            (Output infos as JSON (instead of plain text))  
    -v, --verbose         (Print all references (instead of only PDFs))  
    -t, --text            (Only extract text (no metadata or references))  
    -a, --archive	  (Archive actvice links)
    -o OUTPUT_FILE,        --output-file OUTPUT_FILE (Output to specified file instead of console)  
    --version             (Show program's version number and exit)  

### PDF Samples

For testing purposes, you can find PDF samples in [shared MEGA](https://mega.nz/folder/uwBxVSzS#lpBtSz49E9dqHtmrQwp0Ig) folder](https://mega.nz/folder/uwBxVSzS#lpBtSz49E9dqHtmrQwp0Ig).

### Examples

#### Extract text to console.
```bash
linkrot https://example.com/example.pdf -t
```

#### Extract text to file
```bash
linkrot https://example.com/example.pdf -t -o pdf-text.txt
```

#### Check Links
```bash
linkrot https://example.com/example.pdf -c
```

#### Check for Retracted Papers
```bash
linkrot https://example.com/example.pdf -r
```

#### Check Both Links and Retractions
```bash
linkrot https://example.com/example.pdf -c -r
```

#### Get Results as JSON with Retraction Check
```bash
linkrot https://example.com/example.pdf -r -j
```

## 2. Main Python Library

Import the library: 
```python
import linkrot
```

Create an instance of the linkrot class like so: 
```python
pdf = linkrot.linkrot("filename-or-url.pdf") #pdf is the instance of the linkrot class
```

Now the following function can be used to extract specific data from the pdf:

### get_metadata()
Arguments: None

Usage: 
```python
metadata = pdf.get_metadata() #pdf is the instance of the linkrot class
``` 

Return type: Dictionary `<class 'dict'>`

Information Provided: All metadata, secret metadata associated with the PDF including Creation date, Creator, Title, etc...

### get_text()
Arguments: None

Usage: 
```python
text = pdf.get_text() #pdf is the instance of the linkrot class
```

Return type: String `<class 'str'>`

Information Provided: The entire content of the PDF in string form.

### get_references(reftype=None, sort=False)
Arguments: 

	reftype: The type of reference that is needed 
		 values: 'pdf', 'url', 'doi', 'arxiv'. 
		 default: Provides all reference types.
	
	sort: Whether reference should be sorted or not
	      values: True or False. 
	      default: Is not sorted.
	
Usage: 
```python
references_list = pdf.get_references() #pdf is the instance of the linkrot class
```

Return type: Set `<class 'set'>` of `<linkrot.backends.Reference object>`

	linkrot.backends.Reference object has 3 member variables:
	- ref: actual URL/PDF/DOI/ARXIV
	- reftype: type of reference
	- page: page on which it was referenced

Information Provided: All references with their corresponding type and page number. 

### get_references_as_dict(reftype=None, sort=False)
Arguments: 

	reftype: The type of reference that is needed 
		 values: 'pdf', 'url', 'doi', 'arxiv'. 
		 default: Provides all reference types.
	
	sort: Whether reference should be sorted or not
	      values: True or False. 
	      default: Is not sorted.
	
Usage: 
```python
references_dict = pdf.get_references_as_dict() #pdf is the instance of the linkrot class
```

Return type: Dictionary `<class 'dict'>` with keys 'pdf', 'url', 'doi', 'arxiv' that each have a list `<class 'list'>` of refs of that type.

Information Provided: All references in their corresponding type list.


### download_pdfs(target_dir)
Arguments: 

	target_dir: The path of the directory to which the reference PDFs should be downloaded 
	
Usage: 
```python
pdf.download_pdfs("target-directory") #pdf is the instance of the linkrot class
```

Return type: None

Information Provided: Downloads all the reference PDFs to the specified directory.

## 3. Linkrot downloader functions

Import:
```python
from linkrot.downloader import sanitize_url, get_status_code, check_refs
```
### sanitize_url(url)
Arguments: 

	url: The url to be sanitized.
	
Usage: 
```python
new_url = sanitize_url(old_url) 
```

Return type: String `<class 'str'>`

Information Provided: URL is prefixed with 'http://' if it was not before and makes sure it is in utf-8 format.

### get_status_code(url)
Arguments: 

	url: The url to be checked for its status. 
	
Usage: 
```python
status_code = get_status_code(url) 
```

Return type: String `<class 'str'>`

Information Provided: Checks if the URL is active or broken.

### check_refs(refs, verbose=True, max_threads=MAX_THREADS_DEFAULT)
Arguments: 

	refs: set of linkrot.backends.Reference objects
	verbose: whether it should print every reference with its code or just the summary of the link checker
	max_threads: number of threads for multithreading
	
Usage: 
```python
check_refs(pdf.get_references()) #pdf is the instance of the linkrot class
```

Return type: None

Information Provided: Prints references with their status code and a summary of all the broken/active links on terminal.

## 4. Linkrot extractor functions

Import:
```python
from linkrot.extractor import extract_urls, extract_doi, extract_arxiv
```

Get pdf text:
```python
text = pdf.get_text() #pdf is the instance of the linkrot class
```

### extract_urls(text)
Arguments: 

	text: String of text to extract urls from
	
Usage: 
```python
urls = extract_urls(text)
```

Return type: Set `<class 'set'>` of URLs

Information Provided: All URLs in the text

### extract_arxiv(text)
Arguments: 

	text: String of text to extract arXivs from
	
Usage: 
```python
arxiv = extract_arxiv(text)
```

Return type: Set `<class 'set'>` of arxivs

Information Provided: All arXivs in the text

### extract_doi(text)
Arguments: 

	text: String of text to extract DOIs from
	
Usage: 
```python
doi = extract_doi(text)
```

Return type: Set `<class 'set'>` of DOIs

Information Provided: All DOIs in the text

## 5. Linkrot retraction functions

Import:
```python
from linkrot.retraction import check_dois_for_retractions, RetractionChecker
```

### check_dois_for_retractions(dois, verbose=False)
Arguments: 

	dois: Set of DOI strings to check for retractions
	verbose: Whether to print detailed results
	
Usage: 
```python
# Get DOIs from PDF text
text = pdf.get_text()
dois = extract_doi(text)

# Check for retractions
result = check_dois_for_retractions(dois, verbose=True)
```

Return type: Dictionary with retraction results and summary

Information Provided: Checks each DOI against retraction databases and provides detailed information about any retracted papers found.

### RetractionChecker class
For more advanced usage, you can use the RetractionChecker class directly:

```python
checker = RetractionChecker()

# Check individual DOI
result = checker.check_doi("10.1000/182")

# Check multiple DOIs
results = checker.check_multiple_dois({"10.1000/182", "10.1038/nature12373"})

# Get summary
summary = checker.get_retraction_summary(results)
```

The retraction checker uses multiple methods to detect retractions:
- CrossRef API for retraction notices in metadata
- Analysis of DOI landing pages for retraction indicators
- Extensible design for adding more retraction databases

# Code of Conduct
To view our code of conduct please visit our [Code of Conduct page](https://github.com/marshalmiller/rottingresearch/blob/main/code_of_conduct.md).
            
# License
This program is licensed with an [GPLv3 License](https://github.com/marshalmiller/linkrot/blob/main/LICENSE).


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frottingresearch%2Flinkrot.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Frottingresearch%2Flinkrot?ref=badge_large)