# Simple HentaiSaturn Downloader

> A Python-based tool to download anime series from HentaiSaturn, tracking progress for each episode. It extracts video URLs and handles downloads efficiently.

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
│ ├── format_utils.py     # Python script containing formatting utility for anime name
│ ├── progress_utils.py   # Python script containing progress utility
│ └── streamtape2curl.py  # Module to extract the download link from the alternative host
├── hanime_downloader.py  # Python script to download the hanime episodes
├── main.py               # Main Python script to run the downloader
└── URLs.txt              # Text file containing album URLs
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

Run the script followed by the hanime URL you want download:

```bash
python3 hanime_downloader.py <hanime_page_url>
```

Example

```
python3 hanime_downloader.py https://www.hentaisaturn.tv/hentai/Bubble-de-House-de-XXX
```

## Batch Download

### Usage

1. Create a `URLs.txt` file in the project root and list the hanime URLs you want to download.

2. Run the main script via the command line:

```
python3 main.py
```

The downloaded files will be saved in the `Downloads` directory.
