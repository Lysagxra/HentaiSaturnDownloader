# HentaiSaturn Downloader

> A Python-based tool for downloading hanime series from HentaiSaturn, featuring progress tracking for each episode. It efficiently extracts video URLs and manages downloads.

![Screenshot](https://github.com/Lysagxra/HentaiSaturnDownloader/blob/68d64c2b3b2bf2328f1e8ce1bb7a297f87c20692/misc/Screenshot.png)

## Features

- Downloads multiple episodes concurrently.
- Supports batch downloading via a list of URLs.
- Supports downloading a specified range of episodes.
- Tracks download progress with a progress bar.
- Supports downloading from alternative hosts if necessary.
- Automatically creates a directory structure for organized storage.

## Directory Structure
```
project-root/
├── helpers/
│ ├── download_utils.py    # Utilities for managing the download process
│ ├── file_utils.py        # Utilities for managing file operations
│ ├── format_utils.py      # Utilities for processing and formatting strings or URLs
│ ├── general_utils.py     # Miscellaneous utility functions
│ ├── progress_utils.py    # Tools for progress tracking and reporting
│ └── streamtape_utils.py  # Module for extracting download links from alternative host
├── hanime_downloader.py   # Module for downloading hanime episodes
├── main.py                # Main script to run the downloader
└── URLs.txt               # Text file containing anime URLs
```

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `rich` - for progress display in terminal

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Lysagxra/HentaiSaturnDownloader.git
```

3. Navigate to the project directory:

```bash
cd HentaiSaturnDownloader
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Single Hanime Download

To download a single hanime, you can use the `hanime_downloader.py` script.

### Usage

Run the script followed by the hanime URL you want to download:

```bash
python3 anime_downloader.py <anime_url> [--start <start_episode>] [--end <end_episode>]
```

- `<anime_url>`: The URL of the anime series.
- `--start <start_episode>`: The starting episode number (optional).
- `--end <end_episode>`: The ending episode number (optional).

### Examples

To download all episodes:
```
python3 hanime_downloader.py https://www.hentaisaturn.tv/hentai/Boku-ni-Harem-Sefure-ga-Dekita-Riyuu
```

To download a specific range of episodes (e.g., episodes 2 to 3):
```bash
python3 hanime_downloader.py https://www.hentaisaturn.tv/hentai/Boku-ni-Harem-Sefure-ga-Dekita-Riyuu --start 2 --end 3
```

To download episodes starting from a specific episode:
```bash
python3 hanime_downloader.py https://www.hentaisaturn.tv/hentai/Boku-ni-Harem-Sefure-ga-Dekita-Riyuu --start 2
```
In this case, the script will download all episodes starting from the `--start` episode to the last episode.

## Batch Download

### Usage

1. Create a `URLs.txt` file in the project root and list the hanime URLs you want to download.

- Example of `URLs.txt`:

```
https://www.hentaisaturn.tv/hentai/Boku-ni-Harem-Sefure-ga-Dekita-Riyuu
https://www.hentaisaturn.tv/hentai/Isekai-Kita-no-de-Special-Skill
https://www.hentaisaturn.tv/hentai/Enjo-Kouhai-HS
```

- Ensure that each URL is on its own line without any extra spaces.
- You can add as many URLs as you need, following the same format.

2. Run the main script via the command line:

```
python3 main.py
```

The downloaded files will be saved in the `Downloads` directory.
