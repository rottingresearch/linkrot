#!/usr/bin/env python
"""
Command line tool to get metadata and URLs from a local or remote PDF,
and optionally download all referenced PDFs.
"""

import sys
import argparse
import json

from urllib.parse import urlparse

import linkrot
from linkrot.downloader import check_refs
from linkrot.archive import archive_links
from linkrot.retraction import check_dois_for_retractions
from linkrot.extractor import extract_doi


# print(sys.version)
# print("stdout encoding: %s" % sys.stdout.encoding)


def exit_with_error(code, *objs):
    """Produces the error messsage

    Args:
        code: Error code
        *objs: Exception encountered

    """
    print("ERROR %s:" % code, *objs, file=sys.stderr)
    exit(code)


# Error Status Codes
ERROR_FILE_NOT_FOUND = 1
ERROR_DOWNLOAD = 2
ERROR_PDF_INVALID = 4


def create_parser():
    """Creates the Arguement Parser Object and\
    adds all the required arguments to it.

    Returns:
        ArgumentParser

    """

    # Creating the ArgumentParser object
    parser = argparse.ArgumentParser(
        description="Extract metadata and references from a PDF, and "
        "optionally download all referenced PDFs. Visit "
        "https://github.com/marshalmiller/linkrot for more information.",
        epilog="",
    )

    # Adding information about the ArgumentParser about program arguments

    parser.add_argument("pdf", help="Filename or URL of a PDF file")

    parser.add_argument(
        "-d",
        "--download-pdfs",
        metavar="OUTPUT_DIRECTORY",
        help="Download all referenced PDFs into specified directory",
    )

    parser.add_argument(
        "-c", "--check-links", action="store_true",
        help="Check for broken links"
    )

    parser.add_argument(
        "-r", "--check-retractions", action="store_true",
        help="Check DOIs for retracted papers"
    )

    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output infos as JSON (instead of plain text)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Print all references (instead of only PDFs)",
    )

    # parser.add_argument("--debug",
    #                     action='store_true',
    #                     help="Output debug infos")

    parser.add_argument(
        "-t",
        "--text",
        action="store_true",
        help="Only extract text (no metadata or references)",
    )

    parser.add_argument(
        "-a",
        "--archive",
        action="store_true",
        help="Archive active links",
    )

    parser.add_argument(
        "-o", "--output-file", help="Output to specified file\
         instead of console"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s v{version}".format(version=linkrot.__version__),
    )
    return parser


def get_text_output(pdf, args):
    """ Normal output of infos of linkrot instance """
    # Metadata
    ret = ""
    ret += "Document info:\n"
    metadata = pdf.get_metadata()
    metadata.pop(None, None)
    for k, v in sorted(pdf.get_metadata().items()):
        if v:
            ret += "- {} = {}\n".format(k, str(v).strip("/"))

    # References
    ref_cnt = pdf.get_references_count()
    ret += "\nReferences: %s\n" % ref_cnt
    refs = pdf.get_references_as_dict()
    for k in refs:
        ret += "- {}: {}\n".format(k.upper(), len(refs[k]))

        # doi references
        if k == 'url':
            doi_ref = []
            for u in refs[k]:
                host = urlparse(u).hostname
                if host and host.endswith(".doi.org"):
                    doi_ref.append(u)
            ret += "- {}: {}\n".format('DOI', len(doi_ref))

    # Retraction check summary (if available)
    if hasattr(pdf, 'summary') and 'retraction_check' in pdf.summary:
        retraction_info = pdf.summary['retraction_check']['summary']
        ret += "\nRetraction Check:\n"
        ret += "- Total DOIs checked: {}\n".format(
            retraction_info['total_checked'])
        ret += "- Clean papers: {}\n".format(retraction_info['clean_count'])
        ret += "- Retracted papers: {}\n".format(
            retraction_info['retracted_count'])
        if retraction_info['retracted_count'] > 0:
            ret += "- ⚠️  WARNING: Retracted papers found!\n"

    if args.verbose == 0:
        if "pdf" in refs:
            ret += "\nPDF References:\n"
            for ref in refs["pdf"]:
                ret += "- %s\n" % ref
        elif ref_cnt:
            ret += "\nTip: You can use the '-v' flag to see all references\n"
    else:
        if ref_cnt:
            for reftype in refs:
                ret += "\n%s References:\n" % reftype.upper()
                for ref in refs[reftype]:
                    ret += "- %s\n" % ref

    return ret.strip()


def print_to_console(text):
    # Prints a (unicode) string to the console, encoded depending on the stdout
    # encoding (eg. cp437 on Windows). Works with Python 2 and 3.
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        bytes_string = text.encode(sys.stdout.encoding, "backslashreplace")
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(bytes_string)
        else:
            text = bytes_string.decode(sys.stdout.encoding, "strict")
            sys.stdout.write(text)
    sys.stdout.write("\n")


def main():

    # Creating the parser and parsing the arguments
    parser = create_parser()
    args = parser.parse_args()

    # if args.debug:
    #     logging.basicConfig(
    #             level=logging.DEBUG,
    #             format='%(levelname)s - %(module)s - %(message)s')

    # Check if file exists
    try:
        pdf = linkrot.linkrot(args.pdf)
    except linkrot.exceptions.FileNotFoundError as e:
        exit_with_error(ERROR_FILE_NOT_FOUND, str(e))
    except linkrot.exceptions.DownloadError as e:
        exit_with_error(ERROR_DOWNLOAD, str(e))
    except linkrot.exceptions.PDFInvalidError as e:
        exit_with_error(ERROR_PDF_INVALID, str(e))

    # Perhaps only output text
    if args.text:
        text = pdf.get_text()
        if args.output_file:
            # to file (in utf-8)
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            # to console
            print_to_console(text)
        return

    # Print Metadata
    if args.json:
        # in JSON format
        text = json.dumps(pdf.summary, indent=4)
        if args.output_file:
            # to file (in utf-8)
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            # to console
            print_to_console(text)
    else:
        # in text format
        text = get_text_output(pdf, args)
        if args.output_file:
            # to file (in utf-8)
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            # to console
            print_to_console(text)

    # Checking for broken links
    if args.check_links:
        refs_all = pdf.get_references()
        refs = [ref for ref in refs_all if ref.reftype in ["url", "pdf"]]
        print("\nChecking %s URLs for broken links..." % len(refs))
        check_refs(refs)

    # Archive active links
    if args.archive:
        refs_all = pdf.get_references()
        refs = [ref for ref in refs_all if ref.reftype in ["url"]]
        print("\nArchieve %s URLs..." % len(refs))
        archive_links(refs)

    # Check for retracted papers
    if args.check_retractions:
        text = pdf.get_text()
        dois = extract_doi(text)
        if dois:
            print(f"\nFound {len(dois)} DOI(s) to check for retractions...")
            retraction_results = check_dois_for_retractions(dois, verbose=True)
            
            # Add retraction info to summary if JSON output
            if args.json:
                pdf.summary["retraction_check"] = retraction_results
        else:
            print("\nNo DOIs found in the document to check for retractions.")

    # Check for errors in downloading and then produce the output
    try:
        if args.download_pdfs:
            print(
                "\nDownloading %s pdfs to '%s'..."
                % (len(pdf.get_references("pdf")), args.download_pdfs)
            )
            pdf.download_pdfs(args.download_pdfs)
            print("All done!")
    except Exception as e:
        exit_with_error(ERROR_DOWNLOAD, str(e))


if __name__ == "__main__":
    main()
