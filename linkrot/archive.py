# Adds links to Wayback Machine from the Internet Archive
from __future__ import absolute_import, division, print_function,\
 unicode_literals
from .colorprint import colorprint, OKGREEN, FAIL
from .threadpool import ThreadPool
from collections import defaultdict
import ssl
import os
import sys
import re


def archive_link(url):

  if 'web.archive' in url:
    return url,url
  try:
    r = requests.get('https://web.archive.org/save/' + url)
  except:
    return url,url
  if r.status_code == 403:
    return url,url
  else:
    try:
      return url,'https://web.archive.org' + r.headers['content-location']
    except:
      return url,url

    try:
        pool = ThreadPool(5)
        pool.map(check_url, refs)
        pool.wait_completion()

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass
