from unittest.mock import patch, mock_open

from linkrot.downloader import download_urls


@patch("linkrot.downloader.urlopen")
def test_download_urls(mock_urlopen):
    mock_file = mock_open()
    mock_urlopen.return_value = mock_file.return_value
    url = "http://example.com/test.pdf"
    path = "/tmp/test.pdf"
    result = download_urls(url, path)
    assert result == path
    mock_urlopen.assert_called_once_with(url)
    mock_file.assert_called_once_with(path, "wb")
