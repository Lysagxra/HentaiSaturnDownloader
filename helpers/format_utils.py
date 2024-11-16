"""
This module provides utility functions for processing and formatting
hanime-related strings and URLs. It includes functions for checking and
removing specific patterns from strings, extracting anime IDs from URLs,
and formatting anime names by removing designated substrings.
"""

ENDSTRINGS = ["Sub ITA", "ITA"]

def extract_hanime_name(soup):
    """
    Extracts the hanime name from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed
                              HTML content.

    Returns:
        str: The extracted hanime name if found.

    Raises:
        ValueError: If the container with the specified class is not found in
                    the BeautifulSoup object.
        AttributeError: If there is an error extracting the hanime name.
    """
    try:
        title_container = soup.find(
            'div', {'class': "container hentai-title-as mb-3 w-100"}
        )
        if title_container is None:
            raise ValueError("Hanime title container not found.")

        return title_container.find('b').get_text()

    except AttributeError as attr_err:
        return AttributeError(f"Error extracting hanime name: {attr_err}")

def format_hanime_name(hanime_name):
    """
    Formats the hanime name by removing specific substrings at the end.

    Args:
        hanime_name (str): The hanime name extracted from the page.

    Returns:
        str: The formatted hanime name.

    Raises:
        ValueError: If the hanime name format is invalid.
    """
    def remove_substrings_at_end(string, substrings):
        for substring in substrings:
            if string.endswith(substring):
                return string[:-len(substring)].strip()
        return string

    try:
        return remove_substrings_at_end(hanime_name, ENDSTRINGS)

    except IndexError as indx_err:
        raise ValueError("Invalid hanime name format.") from indx_err
