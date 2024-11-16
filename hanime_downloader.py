"""
This script downloads hanime episodes from a given HentaiSaturn URL.

It extracts the hanime ID, formats the hanime name, retrieves episode IDs and
URLs, and downloads each episode using the richwget tool.

Usage:
    - Run the script with the URL of the hanime page as a command-line argument.
    - It will create a directory structure in the 'Downloads' folder based on
      the hanime name where each episode will be downloaded.
"""

import os
import re
import sys
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from rich.live import Live

from helpers.streamtape_utils import get_curl_command as get_alt_download_link
from helpers.download_utils import save_file_with_progress, run_in_parallel
from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.format_utils import extract_hanime_name, format_hanime_name
from helpers.general_utils import (
    fetch_page, create_download_directory, clear_terminal
)

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_FOLDER = "Downloads"

TIMEOUT = 10
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
        "Gecko/20100101 Firefox/117.0"
    ),
    "Connection": "keep-alive"
}

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
            soup = fetch_page(episode_url)
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

    video_urls = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(extract_video_url, episode_url): episode_url
            for episode_url in episode_urls
        }

        for future in as_completed(futures):
            video_url = future.result()
            if video_url:
                video_urls.append(video_url)

    return video_urls

def get_episode_filename(download_link):
    """
    Extract the file name from the provided episode download link.

    Args:
        download_link (str): The download link for the episode. This should be
                             a valid URL pointing to the file location.

    Returns:
        str: The extracted file name from the URL. Returns `None` if the link
             is `None` or an empty string.

    Raises:
        IndexError: If the link is improperly formatted and does not contain a 
                    file name in the expected position (e.g., the URL is empty
                    or malformed).
    """
    if download_link:
        parsed_url = urlparse(download_link)
        return os.path.basename(parsed_url.path)

    return None

def download_episode(
        download_link, download_path, task_info, is_default_host=True
):
    """
    Downloads an episode from the specified link and provides real-time
    progress updates.

    Args:
        download_link (str): The URL from which to download the episode.
        download_path (str): The directory path where the episode file will
                             be saved.
        task_info (tuple): A tuple containing progress tracking information:
            - job_progress: The progress bar object.
            - task: The specific task being tracked.
            - overall_task: The overall progress task being updated.
        is_default_host (bool): Indicates whether the default host is being
                                used. Defaults to True.

    Raises:
        requests.RequestException: If there is an error with the HTTP request,
                                   such as connectivity issues or invalid URLs.
    """
    try:
        response = requests.get(
            download_link, stream=True, headers=HEADERS, timeout=TIMEOUT
        )
        response.raise_for_status()

        file_name = get_episode_filename(download_link)
        final_path = (
            os.path.join(download_path, file_name) if is_default_host
            else download_path
        )
        save_file_with_progress(response, final_path, task_info)

    except requests.RequestException as req_error:
        print(f"HTTP request failed: {req_error}")

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
        soup = fetch_page(alt_url)

        url_container = soup.find('a', {'href': True, 'target': "_blank"})
        if not url_container:
            raise IndexError("No tags found with the target '_blank'.")

        return url_container['href']

    except requests.RequestException as req_err:
        print(f"Error processing video URL {url}: {req_err}")

    except IndexError as indx_err:
        print(f"Error finding alternative video URL: {indx_err}")

    return None

def download_from_alt_host(url, download_path, task_info):
    """
    Downloads a video from an alternative host by retrieving the alternative
    video URL, generating a cURL command, and downloading the episode to the
    specified path.

    Args:
        url (str): The original video URL to be processed.
        download_path (str): The directory path where the episode should be
                             downloaded.
        task_info (tuple): A tuple containing progress tracking information.

    Raises:
        ValueError: If the alternative video URL cannot be retrieved.
    """
    alt_video_url = get_alt_video_url(url)
    if not alt_video_url:
        raise ValueError(
            f"Failed to retrieve alternative video URL for {url}."
        )

    (alt_filename, alt_download_link) = get_alt_download_link(alt_video_url)
    alt_download_path = os.path.join(download_path, alt_filename)
    download_episode(
        alt_download_link, alt_download_path, task_info, is_default_host=False
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
    pattern = r'file:\s*"([^"]+)"'
    script_tags = soup.find_all('script')

    for script_tag in script_tags:
        if script_tag.string:
            match = re.search(pattern, script_tag.string)
            if match:
                return match.group(1)

    print("No download link found.")
    return None

def process_video_url(url, download_path, task_info):
    """
    Processes a video URL to extract and download its associated files.
    If no source links are found, it attempts to download from an alternative
    host.

    Args:
        url (str): The video URL.
        download_path (str): The path to save the downloaded episode.
        task_info (tuple): A tuple containing progress tracking information.

    Raises:
        requests.RequestException: If there is an error with the HTTP request
                                   while processing the video URL.
    """
    try:
        soup = fetch_page(url)

        download_link = extract_download_link(soup)
        if download_link:
            download_episode(download_link, download_path, task_info)
        else:
            download_from_alt_host(url, download_path, task_info)

    except requests.RequestException as req_err:
        print(f"Error processing video URL {url}: {req_err}")

def download_hanime(hanime_name, video_urls, download_path):
    """
    Concurrently downloads episodes of a specified anime from provided video
    URLs and tracks the download progress in real-time.

    Parameters:
        hanime_name (str): The name of the hanime being downloaded.
        video_urls (list): A list of URLs corresponding to each episode to be
                           downloaded.
        download_path (str): The local directory path where the downloaded
                             episodes will be saved.
    """
    job_progress = create_progress_bar()
    progress_table = create_progress_table(hanime_name, job_progress)

    with Live(progress_table, refresh_per_second=10):
        run_in_parallel(
            process_video_url, video_urls, job_progress, download_path
        )

def process_hanime_download(url):
    """
    Download a series of Hanime episodes from the specified URL.

    Args:
        url (str): The URL of the Hanime series to download.

    Raises:
        ValueError: If there is an issue extracting the Hanime ID or name
                    from the URL or the page content.
    """
    soup = fetch_page(url)

    try:
        hanime_name = format_hanime_name(extract_hanime_name(soup))
        download_path = create_download_directory(hanime_name)

        episode_urls = get_episode_urls(soup)
        video_urls = get_video_urls(episode_urls)
        download_hanime(hanime_name, video_urls, download_path)

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

    clear_terminal()
    url = sys.argv[1]
    process_hanime_download(url)

if __name__ == '__main__':
    main()
