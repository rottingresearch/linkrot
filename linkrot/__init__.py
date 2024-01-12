"""
Extract metadata and links from a local or remote PDF, and
optionally download all referenced PDFs.

Features

* Extract metadata and PDF URLs from a given PDF
* Download all PDFs referenced in the original PDF
* Archive valid links via Internet Archive's Wayback Machine
* Works with local and online pdfs
* Use as command-line tool or Python package

Usage

linkrot can be used to extract info from PDF in two ways:

* Command line tool `linkrot`
* Python library `import linkrot`

>>> import linkrot
>>> pdf = linkrot.linkrot("filename-or-url.pdf")
>>> metadata = pdf.get_metadata()
>>> references_list = pdf.get_references()
>>> references_dict = pdf.get_references_as_dict()
>>> pdf.download_pdfs("target-directory")

https://github.com/rottingresearch/linkrot

Copyright (c) 2024, Marshal Miller <marshal@rottingresearch.org>
License: GPLv3 (see LICENSE for details)
"""

__title__ = "linkrot"
__version__ = "5.2.2"
__author__ = "Marshal Miller"
__license__ = "GPL-3.0-or-later"
__copyright__ = "Copyright 2024, Marshal Miller"

import os
import json
import shutil
import logging


from .extractor import extract_urls
from .backends import PyMuPDFBackend
from .downloader import download_urls
from .exceptions import FileNotFoundError, DownloadError, PDFInvalidError
from io import BytesIO
from urllib.request import Request, urlopen
from typing import Dict, Any

logger = logging.getLogger(__name__)


class linkrot:
    """
    Main class which extracts infos from PDF

    General flow:
    * init -> get_metadata()

    In detail:
    >>> import linkrot
    >>> pdf = linkrot.linkrot("filename-or-url.pdf")
    >>> print(pdf.get_metadata())
    >>> print(pdf.get_tet())
    >>> print(pdf.get_references())
    >>> pdf.download_pdfs("target-directory")
    """

    # Available after init
    uri = None  # Original URI
    fn = None  # Filename part of URI
    is_url = False  # False if file
    is_pdf = True

    stream = None  # ByteIO Stream
    reader = None  # ReaderBackend
    summary: Dict[str, Any] = {}

    def __init__(self, uri):
        """
        Open PDF handle and parse PDF metadata
        - `uri` can bei either a filename or an url
        """
        logger.debug("Init with uri: %s" % uri)

        self.uri = uri

        # Find out whether pdf is an URL or local file
        url = extract_urls(uri)
        self.is_url = len(url)

        # Grab content of reference
        if self.is_url:
            logger.debug("Reading url '%s'..." % uri)
            self.fn = uri.split("/")[-1]
            try:
                content = urlopen(Request(uri)).read()
                self.stream = BytesIO(content)
            except Exception as e:
                raise DownloadError("Error downloading\
                '{}' ({})".format(uri, str(e)))

        else:
            if not os.path.isfile(uri):
                raise FileNotFoundError("Invalid filename\
                and not an url: '%s'" % uri)
            self.fn = os.path.basename(uri)
            self.stream = open(uri, "rb")

        # Create ReaderBackend instance
        try:
            self.reader = PyMuPDFBackend(self.stream)
            # Could try to create a TextReader
        except Exception as e:
            raise PDFInvalidError("Invalid PDF ({})".format(str(e)))

        # Save metadata to user-supplied directory
        self.summary = {
            "source": {
                "type": "url" if self.is_url else "file",
                "location": self.uri,
                "filename": self.fn,
            },
            "metadata": self.reader.get_metadata(),
        }

        # Search for URLs
        self.summary["references"] = self.reader.get_references_as_dict()
        # print(self.summary)

    def get_text(self):
        return self.reader.get_text()

    def get_metadata(self):
        return self.reader.get_metadata()

    def get_references(self, reftype=None, sort=False):
        """ reftype can be `None` for all, `pdf`, etc. """
        return self.reader.get_references(reftype=reftype, sort=sort)

    def get_references_as_dict(self, reftype=None, sort=False):
        """ reftype can be `None` for all, `pdf`, etc. """
        return self.reader.get_references_as_dict(reftype=reftype, sort=sort)

    def get_references_count(self, reftype=None):
        """ reftype can be `None` for all, `pdf`, etc. """
        r = self.reader.get_references(reftype=reftype)
        return len(r)

    def download_pdfs(self, target_dir):
        logger.debug("Download pdfs to %s" % target_dir)
        assert target_dir, "Need a download directory"
        assert not os.path.isfile(target_dir), "Download directory is a file"

        # Create output directory
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            logger.debug("Created output directory '%s'" % target_dir)

        # Save original PDF to user-supplied directory
        fn = os.path.join(target_dir, self.fn)
        with open(fn, "wb") as f:
            self.stream.seek(0)
            shutil.copyfileobj(self.stream, f)
        logger.debug("- Saved original pdf as '%s'" % fn)

        fn_json = "%s.infos.json" % fn
        with open(fn_json, "w") as f:
            f.write(json.dumps(self.summary, indent=2))
        logger.debug("- Saved metadata to '%s'" % fn_json)

        # Download references
        urls = [ref.ref for ref in self.get_references("pdf")]
        if not urls:
            return

        dir_referenced_pdfs = os.path.join(target_dir,
                                           "%s-referenced-pdfs" % self.fn)
        logger.debug("Downloading %s referenced pdfs..." % len(urls))

        # Download urls as a set to avoid duplicates
        download_urls(urls, dir_referenced_pdfs)
