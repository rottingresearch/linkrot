from unittest.mock import patch

from linkrot import backends


def test_pymupdf_backend():
    pdf_data = b"%PDF-1.7\n1 0 obj\n<< /Title (Hello, world!) >>\nendobj\n"
    with patch("linkrot.backends.requests.get") as mock_get:
        mock_get.return_value.content = pdf_data
        result = backends.pymupdf_backend("http://example.com/test.pdf")
        assert result == "Hello, world!"
        mock_get.assert_called_once_with(
            "http://example.com/test.pdf",
            stream=True
        )
