from linkrot import exceptions


def test_file_not_found_error():
    try:
        raise exceptions.FileNotFoundError("Could not open PDF URI")
    except exceptions.FileNotFoundError as e:
        assert str(e) == "Could not open PDF URI"


def test_download_error():
    try:
        raise exceptions.DownloadError("Could not open PDF URI")
    except exceptions.DownloadError as e:
        assert str(e) == "Could not open PDF URI"


def test_pdf_invalid_error():
    try:
        raise exceptions.PDFInvalidError("Could not decode PDF content")
    except exceptions.PDFInvalidError as e:
        assert str(e) == "Could not decode PDF content"
