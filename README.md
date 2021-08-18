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

Grab a copy of the code with snap or pip, and run it:

snap install linkrot  
[![linkrot](https://snapcraft.io/linkrot/badge.svg)](https://snapcraft.io/linkrot)[![linkrot](https://snapcraft.io/linkrot/trending.svg?name=0)](https://snapcraft.io/linkrot)  
pip install linkrot  

# Usage

$ linkrot [pdf-file-or-url]  
Run linkrot -h to see the help output:

$ linkrot -h  
usage: linkrot [-h] [-d OUTPUT_DIRECTORY] [-c] [-j] [-v] [-t] [-o OUTPUT_FILE]
            [--version]
            pdf

Extract metadata and references from a PDF, and optionally download all
referenced PDFs.

# Arguments

## positional arguments:
  pdf                   (Filename or URL of a PDF file)  

## optional arguments:
    -h, --help            (Show this help message and exit)  
    -d OUTPUT_DIRECTORY, --download-pdfs OUTPUT_DIRECTORY (Download all referenced PDFs into specified directory)  
    -c, --check-links     (Check for broken links)  
    -j, --json            (Output infos as JSON (instead of plain text))  
    -v, --verbose         (Print all references (instead of only PDFs))  
    -t, --text            (Only extract text (no metadata or references))  
    -o OUTPUT_FILE, --output-file OUTPUT_FILE (Output to specified file instead of console)  
    --version             (Show program's version number and exit)  

# Examples

## Extract text to console
$ linkrot https://example.com/example.pdf -t

## Extract text to file
$ linkrot https://example.com/example.pdf -t -o pdf-text.txt

## Check Links
$ linkrot https://example.com/example.pdf -c
            
# License
This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
