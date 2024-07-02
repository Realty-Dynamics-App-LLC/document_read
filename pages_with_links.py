import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

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
county = "Charlotte"
# Target website URL
chapter = "PART IV - MUNICIPAL SERVICE BENEFIT AND TAXING UNITS"
url = "https://library.municode.com/fl/charlotte_county/codes/code_of_ordinances?nodeId=PTIVMUSEBETAUN"
directory = county 
if not os.path.exists(directory):
    os.makedirs(directory)

json_county_name = f"{county}_county_{chapter}_page_urls.json"
json_city_name = f"{county}_city_urls.json"
json_filename = os.path.join(directory, json_county_name)

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

    # Dynamically click "Load more" button if present
    while True:
        try:
            # Use a shorter wait time for checking the button
            short_wait = WebDriverWait(driver, 5)
            load_more = short_wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Load more")]')))
            load_more.click()
            time.sleep(1)  # Allow some time for new content to load
        except TimeoutException:
            print("No more 'Load more' button found.")
            break
        except NoSuchElementException:
            print("No 'Load more' button found.")
            break
 
    # time.sleep(3)
    # Find all links with 'ARTICLE' in the href attribute
    print("Getting all links from chapters...")

    #### This value has to change according to the page
    url_list_buttons = find_elements_safe(By.XPATH, '//a[contains(text(), "Chapter")]')
    
    print(f"{len(url_list_buttons)} links found")
    all_links = []

    for link in url_list_buttons:
        link_text = link.text.strip()  # Get the text of the link
        link_text_with_chapter = f"{chapter}_{link_text}"
        link_href = link.get_attribute("href")  # Get the href attribute
        all_links.append({"text": link_text_with_chapter, "href": link_href})

    print(f"Collected {len(all_links)} links.")

    print(all_links)
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
