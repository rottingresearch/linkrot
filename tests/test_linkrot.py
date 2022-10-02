
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

def test_pdf_with_email_address():
    pdf_with_email_addresses = linkrot.linkrot(os.path.join(curdir, "pdfs/email_test_single_page.pdf"))
    references = pdf_with_email_addresses.get_references()
    # there are only 2 email references in the pdf that should be excluded
    assert len(references) == 0


def test_pdf_with_embedded_links():
    pdf_with_embedded_links = linkrot.linkrot(os.path.join(curdir, "pdfs/embedded_link_testcase.pdf"))
    references = pdf_with_embedded_links.get_references()

    assert len(references) == 7


def test_pdf_with_embedded_link_in_image():
    pdf_with_embedded_link_in_image = linkrot.linkrot(os.path.join(curdir, "pdfs/embedded_link_image.pdf"))
    references = pdf_with_embedded_link_in_image.get_references()
    # assert that the reference was found
    assert len(references) == 1
    # get the reference from the set
    image_ref = references.pop()

    EMBEDDED_LINK_IN_IMAGE = "https://github.com/marshalmiller/linkrot/blob/6e6fb45239f8d06e89671e2ec68a11629747355d/branding/Asset%207@4x.png"
    assert image_ref.ref == EMBEDDED_LINK_IN_IMAGE