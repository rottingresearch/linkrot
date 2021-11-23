#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Regexes for reference matching

Web url matching:
* http://daringfireball.net/2010/07/improved_regex_for_matching_urls
* https://gist.github.com/gruber/8891611
"""
from __future__ import absolute_import, division, print_function,\
 unicode_literals

import re

# arXiv.org
ARXIV_REGEX = r"""arxiv:\s?([^\s,]+)"""
ARXIV_REGEX2 = r"""arxiv.org/abs/([^\s,]+)"""

# DOI
DOI_REGEX = r"""DOI:\s?([^\s,]+)"""


# URL Regex
URL_REGEX = r"""
    (?i)\b
    (?:
        [a-z][\w-]+://
        (?:\S+(?::\S*)?@)?
        (?:
            (?:
                [1-9]\d?|1\d\d|2[01]\d|22[0-3]
                |25[0-5]|[1-9]\d|\d
            )\.(?:
                [1-9]\d?|1\d\d|2[0-4]\d|25[0-5]
                |[1-9]\d|\d
            )\.(?:
                [1-9]\d?|1\d\d|2[0-4]\d|25[0-5]
                |[1-9]\d|\d
            )\.(?:
                [1-9]\d?|1\d\d|2[0-4]\d|25[0-5]
                |[1-9]\d|\d
            )
            |(?:
                [a-z0-9\u00a1-\uffff]
                [a-z0-9\u00a1-\uffff_-]{0,62}
                [a-z0-9\u00a1-\uffff]
            )
        )
        (?::\d{2,5})?
        (?:[/?#]\S*)?
    )
    |(?:
        www
        \.(?:
            [a-z\u00a1-\uffff]
            [a-z0-9\u00a1-\uffff_-]{0,62}
            [a-z0-9\u00a1-\uffff]
        )
        (?::\d{2,5})?
        (?:[/?#]\S*)?
    )
"""

def extract_urls(text):
    """
    This function will return all the unique URLs found in the `text` argument.

    - First we use the regex to find all matches for URLs
    - Finally we turn the list into a set, so we only end up with unique URLs\
     (no duplicates)
    """

    return set(re.findall(URL_REGEX, text, re.IGNORECASE))


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

    res = re.findall(ARXIV_REGEX, text, re.IGNORECASE) + re.findall(
        ARXIV_REGEX2, text, re.IGNORECASE
    )
    return set([r.strip(".") for r in res])


def extract_doi(text):
    """
    This function will return all the unique DOIs found in `text` argument.

    - First we find all matches of the form `DOI:`
    - Then we strip out any `.` from the start and end of any item in the list
    - Finally we turn the list into a set, so we only end up with unique DOIs\
     (no duplicates)
    """

    res = set(re.findall(DOI_REGEX, text, re.IGNORECASE))
    return set([r.strip(".") for r in res])


if __name__ == "__main__":
    print(extract_arxiv("arxiv:123 . arxiv: 345 455 http://arxiv.org/abs/876"))
