from __future__ import absolute_import, division, print_function

import os
import linkrot
import pytest

curdir = os.path.dirname(os.path.realpath(__file__))


def test_all():
    with pytest.raises(linkrot.exceptions.FileNotFoundError):
        linkrot.linkrot("asd")

    with pytest.raises(linkrot.exceptions.DownloadError):
        linkrot.linkrot("http://invalid.com/404.pdf")

    with pytest.raises(linkrot.exceptions.PDFInvalidError):
        linkrot.linkrot(os.path.join(curdir, "pdfs/invalid.pdf"))

    pdf = linkrot.linkrot(os.path.join(curdir, "pdfs/valid.pdf"))
    urls = pdf.get_references(reftype="pdf")
    assert len(urls) == 18
    # pdf.download_pdfs("/tmp/")


def test_two_pdfs():
    linkrot.linkrot(os.path.join(curdir, "pdfs/i14doc1.pdf"))
    pdf_2 = linkrot.linkrot(os.path.join(curdir, "pdfs/i14doc2.pdf"))
    assert len(pdf_2.get_references()) == 2
