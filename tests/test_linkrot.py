import linkrot
from linkrot.exceptions import FileNotFoundError, DownloadError, PDFInvalidError
import pytest


@pytest.mark.parametrize(
    "test_case, expected",
    [
        ("asd", FileNotFoundError),
        ("http://invalid.com/404.pdf", DownloadError),
        ("./tests/pdfs/invalid.pdf", PDFInvalidError),
    ],
)
def test_linkrot_exceptions(download_pdfs, test_case, expected):
    with pytest.raises(expected):
        linkrot(test_case)


def test_valid_pdf():
    pdf = linkrot("./tests/pdfs/valid.pdf")
    urls = pdf.get_references(reftype="pdf")
    assert len(urls) == 18


def test_two_pdfs():
    linkrot("./tests/pdfs/i14doc1.pdf")
    pdf_2 = linkrot("./tests/pdfs/i14doc2.pdf")
    assert len(pdf_2.get_references()) == 2


def test_pdf_with_email_address():
    pdf_with_email_addresses = linkrot("./tests/pdfs/email_test_single_page.pdf")
    references = pdf_with_email_addresses.get_references()
    # there are only 2 email references in the pdf that should be excluded
    assert len(references) == 0


def test_pdf_with_embedded_links():
    pdf_with_embedded_links = linkrot("./tests/pdfs/embedded_link_testcase.pdf")
    references = pdf_with_embedded_links.get_references()

    assert len(references) == 7


def test_pdf_with_embedded_link_in_image():
    pdf_with_embedded_link_in_image = linkrot("./tests/pdfs/embedded_link_image.pdf")
    references = pdf_with_embedded_link_in_image.get_references()
    # assert that the reference was found
    assert len(references) == 1
    # get the reference from the set
    image_ref = references.pop()

    EMBEDDED_LINK_IN_IMAGE = "https://github.com/marshalmiller/linkrot/blob/6e6fb45239f8d06e89671e2ec68a11629747355d/branding/Asset%207@4x.png"
    assert image_ref.ref == EMBEDDED_LINK_IN_IMAGE
