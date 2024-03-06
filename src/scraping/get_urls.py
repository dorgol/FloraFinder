from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

# Setup Chrome and WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Go to the webpage
driver.get('https://flora.org.il/en/plants/')

# Wait for the dynamic content to load
sleep(5)

# Scroll down the page to load all elements
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for new content to load
    sleep(10)

    # Calculate new scroll height and compare with the last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Now that all content is loaded, find all the elements
plant_elements = driver.find_elements(By.CSS_SELECTOR, 'div.item > a')

# Extract the URLs
plant_urls = [element.get_attribute('href') for element in plant_elements]

# Close the driver
driver.quit()

with open('plant_urls.txt', 'w') as file:
    for url in plant_urls:
        file.write(url + '\n')

print("URLs have been saved to plant_urls.txt")