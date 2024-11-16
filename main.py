"""
This module provides functionality to read URLs from a file, process
them for downloading Hanime content, and write results back to the file.

Usage:
    To use this module, ensure that 'URLs.txt' is present in the same
    directory as this script. Execute the script to read URLs, download
    content, and clear the URL list upon completion.
"""

from helpers.file_utils import read_file, write_file
from helpers.general_utils import clear_terminal
from hanime_downloader import process_hanime_download

FILE = 'URLs.txt'

def process_urls(urls):
    """
    Validates and downloads items for a list of URLs.

    Args:
        urls (list): A list of URLs to process.
    """
    for url in urls:
        process_hanime_download(url)

def main():
    """
    Main function to execute the script.

    Reads URLs from a file, processes them, and clears the file at the end.
    """
    clear_terminal()
    urls = read_file(FILE)
    process_urls(urls)
    write_file(FILE)

if __name__ == '__main__':
    main()
