"""
This script downloads hanime episodes from a given HentaiSaturn URL.

It extracts the hanime ID, formats the hanime name, retrieves episode IDs and
URLs, and downloads each episode using the richwget tool.

Dependencies:
    - requests: For making HTTP requests.
    - bs4 (BeautifulSoup): For parsing HTML content.

Custom Modules:
    - ProgressBar (richwget): For downloading with a progress bar.
    - streamtape2curl (get_curl_command): For extract the download link from the
                                          alternative host.

Usage:
    - Run the script with the URL of the hanime page as a command-line argument.
    - It will create a directory structure in the 'Downloads' folder based on
      the hanime name where each episode will be downloaded.
"""

import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)

from helpers.streamtape2curl import get_curl_command as get_alt_download_link

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_FOLDER = "Downloads"
CHUNK_SIZE = 8192

PATTERN = r"-a+$"
ENDSTRINGS = ["Sub ITA", "ITA"]

COLORS = {
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'DARKCYAN': '\033[36m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m'
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
        "Gecko/20100101 Firefox/117.0"
    )
}

def ends_with_pattern(main_string):
    """
    Check if a string ends with the pattern "-a...a", where 'a...' means one or
    more 'a' characters.

    Args:
        main_string (str): The string to check.

    Returns:
        bool: True if the string ends with the pattern, False otherwise.
    """
    match = re.search(PATTERN, main_string)
    return match is not None

def remove_pattern(main_string):
    """
    Remove the substring of the type "-a...a" from the end of a main string.

    Args:
        main_string (str): The string from which to remove the substring.

    Returns:
        str: The string with the specified substring removed from the end.
    """
    return re.sub(PATTERN, '', main_string)

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

        hanime_name = title_container.find('b').get_text()
        return hanime_name

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
                return string.replace(substring, '').strip()
        return string

    try:
        formatted_hanime_name = remove_substrings_at_end(
            hanime_name, ENDSTRINGS
        )
        return formatted_hanime_name

    except IndexError:
        raise ValueError("Invalid hanime name format.")

def get_episode_urls(soup):
    """
    Extracts URLs based on a given tag, attribute from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML.

    Returns:
        list: A list of matching URLs.
    """
    links = soup.find_all(
        'a',
        {
            'href': True,
            'target': "_blank",
            'class': "btn btn-dark mb-1 bottone-ep"
        }
    )
    return [link.get('href') for link in links]

def get_video_urls(episode_urls):
    """
    Retrieves video URLs from a list of episode URLs.

    Args:
        episode_urls (list): A list of episode URLs.

    Returns:
        list: A list of video URLs.

    Raises:
        requests.RequestException: If an error occurs while making an
                                   HTTP request.
    """
    def extract_video_url(episode_url):
        try:
            response = requests.get(episode_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            video_url_container = soup.find(
                'a',
                {
                    'class':"btn btn-light w-100 mt-3 mb-3 font-weight-bold",
                    'href': True
                }
            )
            return video_url_container['href']

        except requests.RequestException as req_err:
            print(f"Error fetching episode URL {episode_url}: {req_err}")
            return None

    return [
        url for url in map(extract_video_url, episode_urls)
        if url is not None
    ]

def progress_bar():
    """
    Creates and returns a progress bar for tracking download progress.

    Returns:
        Progress: A Progress object configured with relevant columns.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        "-",
        TransferSpeedColumn(),
        "-",
        TimeRemainingColumn(),
        transient=True
    )

def get_episode_file_name(episode_download_link):
    """
    Extract the file name from the provided episode download link.

    Args:
        episode_download_link (str): The download link for the episode.

    Returns:
        str: The extracted file name, or None if the link is None or empty.
    """
    try:
        return episode_download_link.split('/')[-1] \
            if episode_download_link else None

    except IndexError as indx_err:
        print(f"Error while extracting the file name: {indx_err}")

def download_episode(
        index, num_episodes, download_link, download_path, is_default_host=True
):
    """
    Downloads an episode from the specified link and provides progress updates.

    Args:
        index (int): The index of the episode (0-based).
        num_episodes (int): The total number of episodes available.
        download_link (str): The URL from which to download the episode.
        download_path (str): The directory path where the episode file will be
                             saved.
        is_default_host (bool): Indicates whether the default host is being
                                used. Defaults to True.

    Prints:
        Progress messages during the download process.

    Raises:
        requests.RequestException: If there is an error with the HTTP request.
        OSError: If there is an error with file operations, such as writing to
                 disk.
        ValueError: If the content-length is invalid or not provided in the
                    response headers.
    """
    print(f"\t[+] Downloading Episode {index + 1}/{num_episodes}...")

    try:
        response = requests.get(download_link, stream=True, headers=HEADERS)
        response.raise_for_status()

        file_name = get_episode_file_name(download_link)
        final_path = os.path.join(download_path, file_name) \
            if is_default_host else download_path
        file_size = int(response.headers.get('content-length', -1))

        with open(final_path, 'wb') as file:
            with progress_bar() as pbar:
                task = pbar.add_task("[cyan]Progress", total=file_size)

                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)
                        pbar.update(task, advance=len(chunk))

    except requests.RequestException as req_error:
        print(f"HTTP request failed for episode {index + 1}: {req_error}")
    except OSError as os_error:
        print(f"File operation failed for episode {index + 1}: {os_error}")

def get_alt_video_url(url):
    """
    Retrieves an alternative video URL by appending a server parameter to the
    original URL.

    Args:
        url (str): The original video URL to be processed.

    Returns:
        str: The alternative video URL found in the anchor tag.

    Raises:
        requests.RequestException: If there is an issue with the GET request.
        IndexError: If no valid anchor tags are found in the response.
    """
    alt_url = url + "&server=1"

    try:
        response = requests.get(alt_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        url_container = soup.find('a', {'href': True, 'target': "_blank"})

        if not url_container:
            raise IndexError("No tags found with the target '_blank'.")

        return url_container['href']

    except requests.RequestException as req_err:
        print(f"Error processing video URL {url}: {req_err}")

    except IndexError as indx_err:
        print(f"Error finding alternative video URL: {indx_err}")

def download_from_alt_host(url, index, num_episodes, download_path):
    """
    Downloads a video from an alternative host by retrieving the alternative
    video URL, generating a cURL command, and downloading the episode to the
    specified path.

    Args:
        url (str): The original video URL to be processed.
        index (int): The index of the episode to be downloaded.
        num_episodes (int): The total number of episodes to be downloaded.
        download_path (str): The directory path where the episode should be
                             downloaded.

    Raises:
        ValueError: If the alternative video URL cannot be retrieved.
    """
    alt_video_url = get_alt_video_url(url)

    if not alt_video_url:
        raise ValueError(f"Failed to retrieve alternative video URL for {url}.")

    (alt_filename, alt_download_link) = get_alt_download_link(alt_video_url)
    alt_download_path = os.path.join(download_path, alt_filename)
    download_episode(
        index, num_episodes, alt_download_link, alt_download_path,
        is_default_host=False
    )

def extract_download_link(soup):
    """
    Extract the download link for a video from the provided BeautifulSoup
    object.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the HTML
                              content of a webpage.

    Returns:
        str: The extracted download link for the video, or None if no link is
             found.
    """
    script_tags = soup.find_all('script')

    for script_tag in script_tags:
        if script_tag.string:
            match = re.search(r'file:\s*"([^"]+)"', script_tag.string)

            if match:
                return match.group(1)

    print("\t[-] No download link found.")
    return None

def process_video_url(url, index, num_episodes, download_path):
    """
    Processes a video URL to extract and download its associated files.
    If no source links are found, it attempts to download from an alternative
    host.

    Args:
        url (str): The video URL.
        index (int): The index of the episode.
        num_episodes (int): The total number of episodes.
        download_path (str): The path to save the downloaded episode.

    Raises:
        requests.RequestException: If there is an error with the HTTP request
                                   while processing the video URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        download_link = extract_download_link(soup)

        if download_link:
            download_episode(index, num_episodes, download_link, download_path)
        else:
            download_from_alt_host(url, index, num_episodes, download_path)

    except requests.RequestException as req_err:
        print(f"Error processing video URL {url}: {req_err}")

def download_hanime(hanime_name, video_urls, num_episodes, download_path):
    """
    Downloads hanime episodes from provided video URLs and saves them to
    the specified path.

    Args:
        hanime_name (str): The name of the hanime.
        video_urls (list): A list of video URLs.
        num_episodes (int): The total number of episodes.
        download_path (str): The path to save the downloaded episodes.

    Prints:
        Progress messages for downloading each episode and completion message
        when all episodes are downloaded.
    """
    print(f"\nDownloading Hanime: {COLORS['BOLD']}{hanime_name}{COLORS['END']}")

    for (index, video_url) in enumerate(video_urls):
        process_video_url(video_url, index, num_episodes, download_path)

    print("\t[\u2713] Download complete.")

def create_download_directory(download_path):
    """
    Creates a directory for downloads if it doesn't exist.

    Args:
        download_path (str): The path to create the download directory.

    Raises:
        OSError: If there is an error creating the directory.
    """
    try:
        os.makedirs(download_path, exist_ok=True)
    except OSError as os_err:
        print(f"Error creating directory: {os_err}")
        sys.exit(1)

def fetch_hanime_page(url):
    """
    Fetches the hanime page and returns its BeautifulSoup object.

    Args:
        url (str): The URL of the hanime page.

    Returns:
        BeautifulSoup: The BeautifulSoup object containing the HTML.

    Raises:
        requests.RequestException: If there is an error with the HTTP request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    except requests.RequestException as req_err:
        print(f"Error fetching the hanime page: {req_err}")
        sys.exit(1)

def process_hanime_download(url):
    """
    Download a series of Hanime episodes from the specified URL.

    Args:
        url (str): The URL of the Hanime series to download.

    Raises:
        ValueError: If there is an issue extracting the Hanime ID or name
                    from the URL or the page content.

    Creates:
        A directory for the Hanime series in the current working directory,
        where all episodes will be downloaded.
    """
    soup = fetch_hanime_page(url)

    try:
        hanime_name = format_hanime_name(extract_hanime_name(soup))

        download_path = os.path.join(os.getcwd(), DOWNLOAD_FOLDER, hanime_name)
        create_download_directory(download_path)

        episode_urls = get_episode_urls(soup)

        video_urls = get_video_urls(episode_urls)
        num_episodes = len(video_urls)

        download_hanime(hanime_name, video_urls, num_episodes, download_path)

    except ValueError as val_err:
        print(f"Value error: {val_err}")

def main():
    """
    Main function to download hanime episodes from a given HentaiSaturn URL.

    Command-line Arguments:
        <hanime_url> (str): The URL of the hanime page to download
                            episodes from.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python3 {SCRIPT_NAME} <hanime_url>")
        sys.exit(1)

    url = sys.argv[1]
    process_hanime_download(url)

if __name__ == '__main__':
    main()
