# ![Logo](https://github.com/Lysagxra/SimpleHentaiSaturnDownloader/blob/80c86fcad2eb2afcda5c603a244d0a7475eb8dc3/misc/HSPlanet-logo.png) Simple HentaiSaturn Downloader

A Python-based tool for downloading hanime from HentaiSaturn.

![Screenshot](https://raw.githubusercontent.com/Lysagxra/SimpleHentaiSaturnDownloader/refs/heads/main/misc/ScreenshotHSD.png)

## Features

- Downloads hanime episodes from an HentaiSaturn URL.
- Supports batch downloading via a list of URLs.

## Directory Structure
```
project-root/
├── helpers/
│ └── streamtape2curl.py  # Python script to extract the download link from the alternative host
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
   git clone https://github.com/Lysagxra/SimpleHentaiSaturnDownloader.git

2. Navigate to the project directory:
   ```bash
   cd SimpleHentaiSaturnDownloader

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
