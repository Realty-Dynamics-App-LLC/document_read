import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Path to your ChromeDriver (replace with your actual path)
chromedriver_path = "/usr/bin/chromedriver"  # Example path for Linux

# Set Chrome options to allow download
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")  # Maximize on launch

chrome_options.add_experimental_option("prefs", {
    "download.default_directory": "/home/jason/Downloads",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Function to append new entries to a JSON file
def append_to_json_file(filename, new_entries):
    if os.path.exists(filename):
        # Read existing data
        with open(filename, 'r') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # Append new entries to existing data
    existing_data.extend(new_entries)

    # Write updated data back to the file
    with open(filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)


# Create a ChromeDriver service object
service = Service(chromedriver_path)

# Open a Chrome browser instance
driver = webdriver.Chrome(service=service, options=chrome_options)

directory = "Lee" 
if not os.path.exists(directory):
    os.makedirs(directory)

json_filename = os.path.join(directory, f"{directory}_County_urls.json")
# Target website URL
url = "https://library.municode.com/fl/lee_county/codes/land_development_code?nodeId=LECOFLLADECO"


try:
    # Open the target URL
    print("Opening URL...")
    driver.get(url)
    print("URL opened.")

    # Wait for the page to load and the buttons to be clickable
    wait = WebDriverWait(driver, 30)  # Wait for up to 30 seconds

    def find_elements_safe(by, value):
        while True:
            try:
                elements = wait.until(EC.presence_of_all_elements_located((by, value)))
                return elements
            except StaleElementReferenceException:
                print("Encountered StaleElementReferenceException, retrying...")
                time.sleep(1)

    # Find all links and extract the href and nested span text
    print("Getting all links from chapters...")
    url_list_buttons = find_elements_safe(By.XPATH, '//a[@class="toc-item-heading"]')
    
    print(f"{len(url_list_buttons)} links")

    all_links = []

    for button in url_list_buttons:
        link_text = button.find_element(By.XPATH, './/span').text
        link_href = button.get_attribute("href")
        all_links.append({"text": link_text, "href": link_href})

    #print(all_links)
    print(f"Collected {len(all_links)} links.")

    # Append to JSON file
    append_to_json_file(json_filename, all_links)
    print(f"Data appended to {json_filename}")

except TimeoutException as e:
    print("Timed out waiting for elements to be clickable or visible.")
    print(e)

finally:
    # Close the browser window
    print("Closing browser...")
    driver.quit()
    print("Browser closed.")
