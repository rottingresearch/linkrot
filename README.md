![linkrot logo](https://github.com/marshalmiller/linkrot/blob/6e6fb45239f8d06e89671e2ec68a11629747355d/branding/Asset%207@4x.png)
# Introduction

Scans pdfs for links written in plaintext and checks if they are active or returns an error code. It then generates a report of its findings. Extract references (pdf, url, doi, arxiv) and metadata from a PDF.

# Features

- Extract references and metadata from a given PDF.  
- Detects pdf, url, arxiv and doi references.  
- Checks for valid SSL certificate.  
- Find broken hyperlinks (using the -c flag).  
- Output as text or JSON (using the -j flag).  
- Extract the PDF text (using the --text flag).  
- Use as command-line tool or Python package.  
- Works with local and online pdfs.  

# Installation

Grab a copy of the code with pip:
 
```bash
pip install linkrot
```

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
linkrot [-h] [-d OUTPUT_DIRECTORY] [-c] [-j] [-v] [-t] [-o OUTPUT_FILE] [--version] pdf
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
    -j, --json            (Output infos as JSON (instead of plain text))  
    -v, --verbose         (Print all references (instead of only PDFs))  
    -t, --text            (Only extract text (no metadata or references))  
    -o OUTPUT_FILE,        --output-file OUTPUT_FILE (Output to specified file instead of console)  
    --version             (Show program's version number and exit)  

### Examples

#### Extract text to console
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

	target_dir: The path of the directory to which the reference pdfs should be downloaded 
	
Usage: 
```python
pdf.download_pdfs("target-directory") #pdf is the instance of the linkrot class
```

Return type: None

Information Provided: Downloads all the reference pdfs to specified directory.

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

Information Provided: Checks if the url is active or broken.

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

	text: String of text to extract arxivs from
	
Usage: 
```python
arxiv = extract_arxiv(text)
```

Return type: Set `<class 'set'>` of arxivs

Information Provided: All arxivs in the text

### extract_doi(text)
Arguments: 

	text: String of text to extract dois from
	
Usage: 
```python
doi = extract_doi(text)
```

Return type: Set `<class 'set'>` of dois

Information Provided: All dois in the text

# Code of Conduct
To view our code of conduct please visit our [Code of Conduct page](https://github.com/marshalmiller/rottingresearch/blob/main/code_of_conduct.md).
            
# License
This program is licensed with an [MIT License](https://github.com/marshalmiller/linkrot/blob/main/LICENSE).
