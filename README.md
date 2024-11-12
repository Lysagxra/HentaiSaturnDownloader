# HentaiSaturn Downloader

> A Python-based tool for downloading hanime series from HentaiSaturn, featuring progress tracking for each episode. It efficiently extracts video URLs and manages downloads.

![Screenshot](https://github.com/Lysagxra/HentaiSaturnDownloader/blob/68d64c2b3b2bf2328f1e8ce1bb7a297f87c20692/misc/Screenshot.png)

## Features

- Downloads multiple episodes concurrently.
- Supports batch downloading via a list of URLs.
- Tracks download progress with a progress bar.
- Supports downloading from alternative hosts if necessary.
- Automatically creates a directory structure for organized storage.

## Directory Structure
```
project-root/
├── helpers/
│ ├── download_utils.py   # Script containing utilities for managing the download process
│ ├── format_utils.py     # Script containing formatting utilities
│ ├── progress_utils.py   # Script containing utilities for tracking download progress
│ └── streamtape2curl.py  # Module for extracting download links from alternative hosts
├── hanime_downloader.py  # Module for downloading hanime episodes
├── main.py               # Main script to run the downloader
└── URLs.txt              # Text file containing anime URLs
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

2. Navigate to the project directory:
   ```bash
   cd HentaiSaturnDownloader

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Single Hanime Download

To download a single hanime, you can use the `hanime_downloader.py` script.

### Usage

Run the script followed by the hanime URL you want to download:

```bash
python3 hanime_downloader.py <hanime_url>
```

### Example

```
python3 hanime_downloader.py https://www.hentaisaturn.tv/hentai/Boku-ni-Harem-Sefure-ga-Dekita-Riyuu
```

## Batch Download

### Usage

1. Create a `URLs.txt` file in the project root and list the hanime URLs you want to download.

2. Run the main script via the command line:

```
python3 main.py
```

The downloaded files will be saved in the `Downloads` directory.
