# importing modules
from .colorprint import colorprint, OKGREEN, FAIL
from .threadpool import ThreadPool
from collections import defaultdict
import ssl
import os
import re


from urllib.request import Request, urlopen, HTTPError
from urllib.error import URLError

unicode = str

# global variable
MAX_THREADS_DEFAULT = 7

# Used to allow downloading files even if https certificate doesn't match
if hasattr(ssl, "_create_unverified_context"):
    ssl_unverified_context = ssl._create_unverified_context()
else:
    # Not existing in Python 2.6
    ssl_unverified_context = ssl.SSLContext()


def sanitize_url(url):
    """ Make sure this url works with urllib2 (ascii, http, etc) """
    if not url:
        return ""
    if not re.match('^http', url, re.IGNORECASE):
        # if url and not url.startswith("http"):
        url = "http://%s" % url
    url = url.encode("ascii", "ignore").decode("utf-8")
    return url


def get_status_code(url):
    """ Perform HEAD request and return status code """
    try:
        request = Request(sanitize_url(url))
        request.add_header(
            "User-Agent",
            "Mozilla/5.0 (compatible; MSIE 9.0; " "Windows NT 6.1;\
             Trident/5.0)",
        )
        request.get_method = lambda: "HEAD"
        response = urlopen(request, context=ssl_unverified_context)
        # print response.info()
        return response.getcode()
    except HTTPError as e:
        return e.code
    except URLError as e:
        return e.reason
    except Exception as e:
        print(e, url)
        return None


def check_refs(refs, verbose=True, max_threads=MAX_THREADS_DEFAULT):
    """ Check if urls exist """
    codes = defaultdict(list)

    def check_url(ref):
        url = ref.ref
        status_code = str(get_status_code(url))
        codes[status_code].append(ref)
        if verbose:
            if status_code == "200":
                colorprint(OKGREEN, "{} - {}".format(status_code, url))
            else:
                colorprint(FAIL, "{} - {}".format(status_code, url))

    # Start a threadpool and add the check-url tasks
    try:
        pool = ThreadPool(5)
        pool.map(check_url, refs)
        pool.wait_completion()

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass

    # Print summary
    output = "\nSummary of link checker:"
    print(output)
    if "200" in codes:
        output += "\n" + colorprint(OKGREEN, "%s working" % len(codes["200"]))
    for c in sorted(codes):
        if c != "200":
            output += "\n" + colorprint(FAIL, "{} broken (reason: {})".format(len(codes[c]), c))  # noqa: E501
            for ref in codes[c]:
                o = "  - %s" % ref.ref
                if ref.page > 0:
                    o += " (page %s)" % ref.page
                print(o)
                output += "\n" + o

    return output


def download_urls(
    urls, output_directory, verbose=True, max_threads=MAX_THREADS_DEFAULT
):
    """ Download urls to a target directory """
    assert type(urls) in [list, tuple, set], "Urls must be some kind of list"
    assert len(urls), "Need urls"
    assert output_directory, "Need an output_directory"

    # Remove duplicates
    urls = list(set(urls))

    def vprint(s):
        if verbose:
            print(s)
# Download URL content in Directory

    def download_url(url):
        try:
            fn = url.split("/")[-1].split("?")[0]
            fn_download = os.path.join(output_directory, fn)
            with open(fn_download, "wb") as f:
                request = Request(sanitize_url(url))
                request.add_header(
                    "User-Agent",
                    "Mozilla/5.0 (compatible; "
                    "MSIE 9.0; Windows NT 6.1; Trident/5.0)",
                )
                response = urlopen(request, context=ssl_unverified_context)
                status_code = response.getcode()
                if status_code == 200:
                    f.write(urlopen(request).read())
                    colorprint(OKGREEN, "Downloaded '%s' to '%s'" %
                                        (url, fn_download))
                else:
                    colorprint(FAIL, "Error downloading '%s' (%s)" %
                                     (url, status_code))
        except HTTPError as e:
            colorprint(FAIL, "Error downloading '{}' ({})".format(url, e.code))
        except URLError as e:
            error_message = "Error downloading '{}' ({})".format(url, e.reason)
            colorprint(FAIL, error_message)
        except Exception as e:
            colorprint(FAIL, "Error downloading '{}' ({})".format(url, str(e)))

    # Create directory
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        vprint("Created directory '%s'" % output_directory)
# Start a threadpool and add the download url tasks.
    try:
        pool = ThreadPool(5)
        pool.map(download_url, urls)
        pool.wait_completion()

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass
