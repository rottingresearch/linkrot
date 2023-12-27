from linkrot import extractor


def test_arxiv_regex():
    text = "This is a test arxiv:1234.56789 and arxiv.org/abs/9876.54321."
    result = extractor.extract_arxiv(text)
    assert result == ["1234.56789", "9876.54321"]


def test_doi_regex():
    text = "This is a test DOI:10.1234/56789 and doi:10.9876/54321."
    result = extractor.extract_doi(text)
    assert result == ["10.1234/56789", "10.9876/54321"]


def test_url_regex():
    text = "This is a test https://example.com and http://www.example.org."
    result = extractor.extract_urls(text)
    assert result == ["https://example.com", "http://www.example.org"]
