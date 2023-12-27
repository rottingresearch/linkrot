import argparse
from unittest.mock import patch

from linkrot import cli


def test_create_parser():
    parser = cli.create_parser()
    assert isinstance(parser, argparse.ArgumentParser)


@patch("linkrot.cli.check_pdf")
def test_cli(mock_check_pdf):
    mock_check_pdf.return_value = True
    parser = cli.create_parser()
    parsed = parser.parse_args(["-j", "./tests/pdfs/valid.pdf"])
    assert parsed.json
    assert parsed.pdf == "./tests/pdfs/valid.pdf"
    assert parsed.verbose == 0
    assert not parsed.text
    assert not parsed.debug
    cli.main(parsed)
    mock_check_pdf.assert_called_once_with("./tests/pdfs/valid.pdf")
