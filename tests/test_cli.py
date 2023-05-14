from linkrot import cli


def test_cli():
    parser = cli.create_parser()
    parsed = parser.parse_args(["-j", "./tests/pdfs/valid.pdf"])
    assert parsed.json
    assert parsed.pdf == "./tests/pdfs/valid.pdf"
