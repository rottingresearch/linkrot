# Adds links to Wayback Machine from the Internet Archive
import requests
from .threadpool import ThreadPool


def archive_links(refs):
    """archive  urls """

    def web_archive(ref):
        url = ref.ref
        if 'web.archive' in url:
            return url, url
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}  # noqa: E501
            r = requests.get('https://web.archive.org/save/' +
                             url,  headers=headers)
            if r.status_code == 200:
                result = r.headers['Content-Location']
                internet_archive_url = "https://web.archive.org%s" % result
                return internet_archive_url
            else:
                print(f"archive status code:{r.status_code} for {url}")
        except Exception as e:
            print(f"Archive failed for {url}. Error: {str(e)}")

    try:
        pool = ThreadPool(1)
        pool.map(web_archive, refs)
        pool.wait_completion()

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass
