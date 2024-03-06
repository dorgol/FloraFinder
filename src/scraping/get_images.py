import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from concurrent.futures import ThreadPoolExecutor


def download_image(image_info):
    url, image_directory = image_info
    image_response = requests.get(url, stream=True)
    if image_response.status_code == 200:
        image_filename = url.split('/')[-1]
        with open(f'{image_directory}/{image_filename}', 'wb') as file:
            for chunk in image_response.iter_content(chunk_size=128):
                file.write(chunk)
        print(f"Downloaded {image_filename} to {image_directory}")
    else:
        print(f"Failed to download image from {url}")


def scrape_images(plant_page_url):
    response = requests.get(plant_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    folder_name = urlparse(plant_page_url).path.rstrip('/').split('/')[-1]
    image_directory = f'data/plant_images/{folder_name}'
    os.makedirs(image_directory, exist_ok=True)
    slide_divs = soup.find_all('div', class_='slide')
    image_urls = [(urljoin(plant_page_url, div.find('img')['data-src']), image_directory)
                  for div in slide_divs if div.find('img') and div.find('img').has_attr('data-src')]

    # Set up ThreadPoolExecutor to download images in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_image, image_urls)


# Example plant page URLs
plant_page_urls = [
    'https://flora.org.il/en/plants/pteaqu/',
    'https://flora.org.il/en/plants/arband/'

]

# Download images for each URL in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(scrape_images, plant_page_urls)
