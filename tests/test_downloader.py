import os
import pytest

from linkrot.downloader import sanitize_url

def test_should_not_add_http_to_upper_case_url():
    result = sanitize_url("HTTP://WWW.TRACFONE.COM/TERMSANDCONDITIONS#RETURNPOLICY")
    expected = "HTTP://WWW.TRACFONE.COM/TERMSANDCONDITIONS#RETURNPOLICY"
    assert result == expected, "wrong"

def test_should_add_http_to_upper_case_url():
    result = sanitize_url("WWW.TRACFONE.COM/TERMSANDCONDITIONS#RETURNPOLICY")
    expected = "http://WWW.TRACFONE.COM/TERMSANDCONDITIONS#RETURNPOLICY"
    assert result == expected, "wrong"

def test_should_not_add_http_to_lower_case_url():
    result = sanitize_url("http://google.com")
    expected = "http://google.com"
    assert result == expected, "wrong"

def test_should_add_http_to_lower_case_url():
    result = sanitize_url("google.com")
    expected = "http://google.com"
    assert result == expected, "wrong"
