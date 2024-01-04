#!/usr/bin/python
import re

# arXiv.org
ARXIV_REGEX = r"""arxiv:\s?([^\s,]+)"""
ARXIV_REGEX2 = r"""arxiv.org/abs/([^\s,]+)"""

# DOI
DOI_REGEX = r"""DOI:\s?([^\s,]+)"""

# URL
URL_REGEX = re.compile(
    r'\b(https?|ftp|file)://[-A-Z0-9+&@#/%?=~_|!:,.;]*[-A-Z0-9+&@#/%=~_|]|'
    r'\bwww\.[-A-Z0-9+&@#/%?=~_|!:,.;]*[-A-Z0-9+&@#/%=~_|]',
    re.IGNORECASE | re.MULTILINE
)


def extract_urls(text):
    """
    This function will return all the unique URLs found in the `text` argument.

    - First we use the regex to find all matches for URLs
    - Finally we turn the list into a set, so we only end up with unique URLs\
     (no duplicates)
    """
    return set(re.findall(URL_REGEX, text, re.MULTILINE))


def extract_arxiv(text):
    """
    This function will return all the unique occurences of `arvix.org/abs/` or\
     `arvix:`.

    - First we find all matches of the form `arvix:`
    - Then we find all matches of the form `arvic.org/abs/`
    - Then we concat them into a single list
    - Then we strip out any `.` from the start and end of any item in the list
    - Finally we turn the list into a set, so we only end up with unique URLs\
     (no duplicates)
    """

    res = re.findall(ARXIV_REGEX, text, re.MULTILINE) + re.findall(
        ARXIV_REGEX2, text, re.MULTILINE
    )
    return {r.strip(".") for r in res}


def extract_doi(text):
    """
    This function will return all the unique DOIs found in `text` argument.

    - First we find all matches of the form `DOI:`
    - Then we strip out any `.` from the start and end of any item in the list
    - Finally we turn the list into a set, so we only end up with unique DOIs\
     (no duplicates)
    """

    res = set(re.findall(DOI_REGEX, text, re.MULTILINE))
    return {r.strip(".") for r in res}


if __name__ == "__main__":
    print(extract_arxiv("arxiv:123 . arxiv: 345 455 http://arxiv.org/abs/876"))
