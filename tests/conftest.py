import pytest
from mega import Mega
import shutil
import os
from constants import PDFS


@pytest.fixture(scope="module")
def download_pdfs():
    # setup
    os.mkdir("./tests/pdfs")
    # mega client
    mega = Mega()
    m = mega.login()
    for url in PDFS.values():
        m.download_url(url, "./tests/pdfs")
    yield
    # teardown
    shutil.rmtree("./tests/pdfs")
