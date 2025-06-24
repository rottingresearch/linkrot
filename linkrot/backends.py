"""
PDF Backend: PyMuPDF
"""

import logging
from re import compile

# Character Detection Helper
import chardet

# Find URLs in text via regex
from . import extractor

# import PyMuPDF
import fitz

logger = logging.getLogger(__name__)


def make_compat_str(in_str):
    """
    Tries to guess encoding of [str/bytes] and
    return a string
    """
    assert isinstance(in_str, (bytes, str))
    if not in_str:
        return ""

    # Chardet in Py3 works on bytes objects
    if not isinstance(in_str, bytes):
        return in_str

    # Detect the encoding now
    enc = chardet.detect(in_str)

    # Decode the object into a string object
    try:
        out_str = in_str.decode(enc["encoding"])
    except UnicodeDecodeError as err:  # noqa: F841
        out_str = ""

    # Cleanup
    if enc["encoding"] == "UTF-16BE":
        # Remove byte order marks (BOM)
        if out_str.startswith("\\ufeff"):
            out_str = out_str[1:]
    return out_str


class Reference:
    """ Generic Reference """

    ref = ""
    reftype = "url"
    page = 0

    def __init__(self, uri, page=0):
        self.ref = uri
        self.reftype = "url"
        self.page = page

        self.pdf_regex = compile(r"\.pdf(:?\?.*)?$")

        # Detect reftype by filetype
        if self.pdf_regex.search(uri.lower()):
            self.reftype = "pdf"
            return

        # Detect reftype by extractor
        arxiv = extractor.extract_arxiv(uri)
        if arxiv:
            self.ref = arxiv.pop()
            self.reftype = "arxiv"
            return

        doi = extractor.extract_doi(uri)
        if doi:
            self.ref = doi.pop()
            self.reftype = "doi"
            return

    def __hash__(self):
        return hash(self.ref)

    def __eq__(self, other):
        assert isinstance(other, Reference)
        return self.ref == other.ref

    def __str__(self):
        return "<{}: {}>".format(self.reftype, self.ref)


class ReaderBackend:
    """
    Base class of all Readers (eg. for PDF files, text, etc.)

    The job of a Reader is to extract Text and Links.
    """

    text = ""
    metadata = {}
    references = set()

    def __init__(self):
        self.text = ""
        self.metadata = {}
        self.references = set()

    def get_metadata(self):
        return self.metadata

    def metadata_key_cleanup(self, d, k):
        """ Recursively clean metadata dictionaries """
        if isinstance(d[k], str):
            d[k] = d[k].strip()
            if not d[k]:
                del d[k]
        elif isinstance(d[k], (list, tuple)):
            new_list = []
            for item in d[k]:
                if isinstance(item, str):
                    if item.strip():
                        new_list.append(item.strip())
                elif item:
                    new_list.append(item)
            d[k] = new_list
            if len(d[k]) == 0:
                del d[k]
        elif isinstance(d[k], dict):
            for k2 in list(d[k].keys()):
                self.metadata_key_cleanup(d[k], k2)

    def metadata_cleanup(self):
        """ Clean metadata (delete all metadata fields without values) """
        for k in list(self.metadata.keys()):
            self.metadata_key_cleanup(self.metadata, k)

    def get_text(self):
        return self.text

    def get_references(self, reftype=None, sort=False):
        refs = self.references
        if reftype:
            refs = {ref for ref in refs if ref.reftype == reftype}
        return sorted(refs, key=lambda x: x.ref) if sort else refs

    def get_references_as_dict(self, reftype=None, sort=False):
        ret = {}
        refs = self.references
        if reftype:
            refs = {ref for ref in refs if ref.reftype == reftype}
        for r in sorted(refs, key=lambda x: x.ref) if sort else refs:
            if r.reftype in ret:
                ret[r.reftype].append(r.ref)
            else:
                ret[r.reftype] = [r.ref]
        return ret


class PyMuPDFBackend(ReaderBackend):
    def __init__(self, pdf_stream, password="", pagenos=None, maxpages=0):
        # noqa: C901
        if pagenos is None:
            pagenos = []

        ReaderBackend.__init__(self)
        self.pdf_stream = pdf_stream

        # Extract Metadata
        doc = fitz.open(pdf_stream)
        if doc.metadata:
            for k in doc.metadata:
                v = doc.metadata[k]
                # print(repr(v), type(v))
                if isinstance(v, (bytes, str)):
                    self.metadata[k] = make_compat_str(v)

        # Extract Content
        content = ""
        self.metadata["Pages"] = 0
        self.curpage = 0
        foundLinks = []
        for page in doc:
            # Read page contents
            content += page.get_text() + '\x0c'
            self.metadata["Pages"] += 1
            self.curpage += 1
            link = page.first_link

            # Collect URL annotations
            # try:
            while link:
                if link.is_external:
                    refs = self.resolve_PDFObjRef(link.uri)
                    foundLinks.append(link.uri)
                    if refs:
                        if isinstance(refs, list):
                            for ref in refs:
                                if ref:
                                    self.references.add(ref)
                        elif isinstance(refs, Reference):
                            self.references.add(refs)
                link = link.next

            # except Exception as e:
            # logger.warning(str(e))

        # Remove empty metadata entries
        self.metadata_cleanup()

        # Get text from stream
        self.text = content
        # print(self.text)

        # Extract URL references from text
        for pageno, page in enumerate(self.text.split('\x0c'), 1):
            for url in extractor.extract_urls(page):
                if any(url in ref for ref in foundLinks):
                    continue
                self.references.add(Reference(url, pageno))
                foundLinks.append(url)

            for ref in extractor.extract_arxiv(page):
                self.references.add(Reference(ref, pageno))

            for ref in extractor.extract_doi(page):
                self.references.add(Reference(ref, pageno))

    def resolve_PDFObjRef(self, obj_ref):
        """
        Resolves PDFObjRef objects. Returns either None, a Reference object or
        a list of Reference objects.
        """
        if isinstance(obj_ref, list):
            return [self.resolve_PDFObjRef(item) for item in obj_ref]

        if isinstance(obj_ref, bytes):
            obj_ref = obj_ref.decode("utf-8")

        if not obj_ref.startswith("mailto:"):
            if isinstance(obj_ref, str):
                ref = obj_ref
                return Reference(ref, self.curpage)
