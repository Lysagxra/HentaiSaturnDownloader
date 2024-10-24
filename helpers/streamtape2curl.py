"""
This module provides functionality to extract specific information from the HTML
content of a given Streamtape URL and constructs a cURL command to download a
file from the Streamtape website.

Functions:
    get_curl_command(url: str) -> tuple: Extracts the original title and final
                                         URL from the given URL's HTML content.
    main(): Processes URLs provided as command-line arguments and prints cURL
            commands.
"""

#!/usr/bin/env python
import re
import sys
import requests

PREFIX = "https:/"
NOROBOT_TOKEN_PATTERN = (
    r".*document.getElementById.*\('norobotlink'\).innerHTML =.*?token=(.*?)'.*?;"
)
LINK_TOKEN_PATTERN = (
    r'.*<div id="ideoooolink" style="display:none;">(.*?token=).*?<[/]div>'
)
TITLE_PATTERN = r'.*<meta name="og:title" content="(.*?)">'

def get_curl_command(url: str) -> str:
    """
    Extracts specific information from the HTML content of a given URL and
    constructs a final URL and the original title.

    Args:
        url (str): The URL to send the GET request to.

    Returns:
        tuple: A tuple containing the original title (str) and the
               final URL (str).
    """
    html = requests.get(url).content.decode()

    token = re.match(
        NOROBOT_TOKEN_PATTERN, html, re.M|re.S
    ).group(1)

    infix = re.match(
        LINK_TOKEN_PATTERN, html, re.M|re.S
    ).group(1)

    final_url = f'{PREFIX}{infix}{token}'

    title = re.match(
        TITLE_PATTERN, html, re.M|re.S
    ).group(1)

    return title, final_url

def main():
    """
    Main function to process URLs provided as command-line arguments and print
    cURL commands to download files from the Streamtape website.
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} STREAMTAPE_URL...", file=sys.stderr)
        sys.exit(1)

    for url in sys.argv[1:]:
        try:
            (filename, final_url) = get_curl_command(url)
            command = f"curl -L -o '{filename}' '{final_url}'"
            print(command)

        except ValueError as val_err:
            print(f"ValueError: {val_err}", file=sys.stderr)

if __name__ == '__main__':
    main()
