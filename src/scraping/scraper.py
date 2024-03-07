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

    def extract_description(self):
        if not self.soup:
            raise ValueError("Soup not initialized. Call fetch_page() first.")

        description_div = self.soup.find('div', class_='info-block description')
        if not description_div:
            return ''
        else:

            # Extract and concatenate all text within the description div
            description_texts = description_div.find_all(string=True)
            description = ' '.join(description_texts).strip()

            # Replace multiple whitespace characters with a single space
            description = ' '.join(description.split())

            return description

    def extract_family(self):
        if not self.soup:
            raise ValueError("Soup not initialized. Call fetch_page() first.")

        # Find the 'dt' with the text 'Family:'
        dt_family = self.soup.find(lambda tag: tag.name == 'dt' and 'Family:' in tag.text)
        if not dt_family:
            raise ValueError("No family information found.")

        # Find the 'dd' following the 'dt'
        dd_family = dt_family.find_next_sibling('dd')
        if not dd_family:
            raise ValueError("No family description found.")

        # Extract family name text and link
        family_name = dd_family.get_text(strip=True)
        family_link = dd_family.find('a')['href'] if dd_family.find('a') else None

        return {'family_name': family_name, 'family_link': family_link}

    def get_full_data(self):
        scraper = PlantPageScraper(self.url)
        scraper.fetch_page()

        images = list(scraper.extract_images())
        self.download_images(images)
        # Here you would call the method to download the images if needed

        info_table = scraper.extract_info_table()
        description = scraper.extract_description()
        family_info = scraper.extract_family()
        return info_table, description, family_info

# Example usage
scraper = PlantPageScraper('https://flora.org.il/en/plants/ptevit/')


scraper.fetch_page()

# Extract and download images
image_urls = list(scraper.extract_images())
scraper.download_images(image_urls)

# Extract information table from multiple tabs
info_table = scraper.extract_info_table()

description = scraper.extract_description()
print(description)

family_info = scraper.extract_family()
print(family_info)
