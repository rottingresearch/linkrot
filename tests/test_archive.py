from unittest.mock import patch

from linkrot import archive


@patch("linkrot.archive.requests.get")
def test_web_archive(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.headers = {
        'Content-Location': '/web/20210101010101/http://example.com'
    }
    result = archive.web_archive('http://example.com')
    expected_result = (
        'https://web.archive.org/web/20210101010101/'
        'http://example.com'
    )
    assert result == expected_result
    mock_get.assert_called_once_with(
        'https://web.archive.org/save/http://example.com',
        headers=archive.headers
    )
