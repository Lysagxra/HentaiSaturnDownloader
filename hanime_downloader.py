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
import sys
import re
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from rich.live import Live

from helpers.streamtape2curl import get_curl_command as get_alt_download_link
from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.format_utils import extract_hanime_name, format_hanime_name

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_FOLDER = "Downloads"

MAX_WORKERS = 3
TIMEOUT = 10
CHUNK_SIZE = 8192

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
        "Gecko/20100101 Firefox/117.0"
    )
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
            response = requests.get(episode_url, timeout=TIMEOUT)
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
        is_default_host (bool): Indicates whether the default host is being used.
                                Defaults to True. Affects the file-saving path.

    Prints:
        Progress messages during the download process, updating the user on the
        completion percentage of the episode download.

    Raises:
        requests.RequestException: If there is an error with the HTTP request,
                                   such as connectivity issues or invalid URLs.
        OSError: If there is an error with file operations, such as writing to
                 disk or permission issues.
    """
    def save_file_with_progress(response, final_path, file_size, task_info):
        (job_progress, task, overall_task) = task_info
        total_downloaded = 0

        with open(final_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    total_downloaded += len(chunk)
                    progress_percentage = (total_downloaded / file_size) * 100
                    job_progress.update(task, completed=progress_percentage)

        job_progress.update(task, completed=100, visible=False)
        job_progress.advance(overall_task)

    try:
        response = requests.get(
            download_link, stream=True, headers=HEADERS, timeout=TIMEOUT
        )
        response.raise_for_status()

        file_name = get_episode_file_name(download_link)
        final_path = os.path.join(download_path, file_name) \
            if is_default_host else download_path
        file_size = int(response.headers.get('content-length', -1))
        save_file_with_progress(response, final_path, file_size, task_info)

    except requests.RequestException as req_error:
        print(f"HTTP request failed: {req_error}")

    except OSError as os_error:
        print(f"File operation failed: {os_error}")

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
        response = requests.get(alt_url, timeout=TIMEOUT)
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
        raise ValueError(f"Failed to retrieve alternative video URL for {url}.")

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
    script_tags = soup.find_all('script')

    for script_tag in script_tags:
        if script_tag.string:
            match = re.search(r'file:\s*"([^"]+)"', script_tag.string)

            if match:
                return match.group(1)

    print("\t[-] No download link found.")
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
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

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

    Usage:
        This function initializes a progress bar to display the download
        status of each episode and updates the overall progress as episodes
        are downloaded.
    """
    def manage_running_tasks(futures):
        while futures:
            for future in list(futures.keys()):
                if future.running():
                    task = futures.pop(future)
                    job_progress.update(task, visible=True)

    job_progress = create_progress_bar()
    progress_table = create_progress_table(hanime_name, job_progress)
    num_episodes = len(video_urls)

    with Live(progress_table, refresh_per_second=10):
        futures = {}

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            overall_task = job_progress.add_task(
                "[cyan]Progress", total=num_episodes, visible=True
            )

            for indx, video_url in enumerate(video_urls):
                task = job_progress.add_task(
                    f"[cyan]Episode {indx + 1}/{num_episodes}",
                    total=100, visible=False
                )
                future = executor.submit(
                    process_video_url, video_url, download_path,
                    (job_progress, task, overall_task)
                )
                futures[future] = task
                manage_running_tasks(futures)

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
        response = requests.get(url, timeout=TIMEOUT)
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

        download_path = os.path.join(DOWNLOAD_FOLDER, hanime_name)
        create_download_directory(download_path)

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

    url = sys.argv[1]
    process_hanime_download(url)

if __name__ == '__main__':
    main()
