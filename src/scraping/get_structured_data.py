import requests
from bs4 import BeautifulSoup
import pandas as pd

# This is an example URL, replace with the actual URL you're scraping
plant_page_url = 'https://flora.org.il/en/plants/pteaqu/'

response = requests.get(plant_page_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the dl element containing the data
tab_content = soup.find('div', id='tab5')
dl = tab_content.find('dl', class_='info')

# Extract terms (dt) and definitions (dd) into a dictionary
data_dict = {}
for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
    category = dt.get_text(strip=True).rstrip(':')
    result = dd.get_text(strip=True)
    data_dict[category] = result

# Create a DataFrame from the dictionary
df = pd.DataFrame([data_dict])

# Display the DataFrame
print(df)