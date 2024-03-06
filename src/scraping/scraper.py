import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor


class PlantPageScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.last_part_url = self._get_last_part_url(url)

    def _get_last_part_url(self, url):
        """ Extracts the last part of the URL to use as the folder name. """
        parsed_url = urlparse(url)
        return parsed_url.path.rstrip('/').split('/')[-1]

    def fetch_page(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'html.parser')
        else:
            response.raise_for_status()

    def extract_images(self):
        if not self.soup:
            raise ValueError("Soup not initialized. Call fetch_page() first.")

        slide_divs = self.soup.find_all('div', class_='slide')
        for div in slide_divs:
            img = div.find('img')
            if img and img.get('data-src'):
                yield urljoin(self.url, img.get('data-src'))

    def download_images(self, image_urls):
        """ Downloads images to a folder named after the last part of the URL. """
        folder_name = f'data/plant_images/{self.last_part_url}'
        os.makedirs(folder_name, exist_ok=True)

        with ThreadPoolExecutor(max_workers=4) as executor:
            for image_url in image_urls:
                executor.submit(self._download_image, image_url, folder_name)

    def _download_image(self, image_url, folder_name):
        """ Helper function to download a single image. """
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_filename = os.path.join(folder_name, image_url.split('/')[-1])
            with open(image_filename, 'wb') as file:
                for chunk in response.iter_content(128):
                    file.write(chunk)
            print(f"Downloaded {image_filename}")
        else:
            print(f"Failed to download {image_url}")

    def extract_info_table(self):
        if not self.soup:
            raise ValueError("Soup not initialized. Call fetch_page() first.")
        tabs_list = ['tab1', 'tab2', 'tab3', 'tab4', 'tab5']
        tabs_info = []
        for tab_id in tabs_list:
            tab_content = self.soup.find('div', id=tab_id)
            if not tab_content:
                raise ValueError(f"No tab content found for id: {tab_id}")

            info_list = tab_content.find('dl', class_='info')
            info_data = {}
            if info_list:
                for dt, dd in zip(info_list.find_all('dt'), info_list.find_all('dd')):
                    category = dt.get_text(strip=True).rstrip(':')
                    result = dd.get_text(strip=True)
                    info_data[category] = result
                tabs_info.append(info_data)
            else:
                raise ValueError(f"No info list found in tab id: {tab_id}")

        return tabs_info


# Example usage
scraper = PlantPageScraper('https://flora.org.il/en/plants/iriedo/')
scraper.fetch_page()

# Extract and download images
image_urls = list(scraper.extract_images())
scraper.download_images(image_urls)

# Extract information table from multiple tabs
info_table = scraper.extract_info_table()
