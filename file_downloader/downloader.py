import requests
from urllib.parse import urlsplit
import os

def download(url: str) -> None:
    """
    Download a file from a URL and save it with the same name as in the URL.

    :param url: The URL of the file to download.
    """
    try:
        print(f"[*] Starting download from URL: {url}")

        response = requests.get(url, stream=True)
        print(f"[+] Received response from server: {response.status_code}")

        # Check for HTTP errors
        response.raise_for_status()
        print(f"[+] No HTTP errors encountered. Proceeding with download...")

        # Extract filename from URL
        filename = os.path.basename(urlsplit(url).path)
        print(f"[*] Extracted filename from URL: {filename}")

        if not filename:
            filename = 'downloaded_file'  # Default filename if extraction fails
            print(f"[*] Filename extraction failed. Using default filename: {filename}")

        # Open file in write-binary mode and start downloading
        with open(filename, 'wb') as file:
            print(f"[*] Saving file to: {filename}")
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)

        print(f"[+] File downloaded successfully and saved as {filename}")

    except requests.RequestException as e:
        print(f"[-] An error occurred during the download: {e}")
