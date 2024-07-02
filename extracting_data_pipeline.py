import time
import re
import os
import json
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

# Path to your ChromeDriver (replace with your actual path)
chromedriver_path = "/usr/bin/chromedriver"  # Example path for Linux
county = "Charlotte"
# Set JSON filename

directory = county
if not os.path.exists(directory):
    os.makedirs(directory)

unique_cases = os.path.join(directory, f"Charlotte_county_Chapter 3-2 - BUILDINGS AND BUILDING REGULATIONS_page_urls.json")
normal = os.path.join(directory, f"{county}_County_urls.json")
city = os.path.join(directory, f"{county}_city_urls.json")
json_filename = os.path.join(directory, f"{county} County")

# Set Chrome options to allow download
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": f"/home/jason/Downloads/{county}",  # Replace with your desired download directory
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1  # Allow multiple downloads
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

# Function to read url data 
def read_from_json_file(filename):
    existing_data = []
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                print(f"Error: The file {filename} contains invalid JSON.")
    else:
        print(f"Error: The file {filename} does not exist.")
    return existing_data


def get_random_string(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def format_filename(original_value, chapter, max_length=100):
    pattern = r"(.*?ARTICLE [IVXLCDM]+\.)"

    # Search for the pattern in the original file name
    match = re.search(pattern, original_value)
    new_value = f"{chapter}_{original_value}"

    if match:
        article_value = match.group(1).strip()
        rest_of_file_name = original_value[len(article_value):].strip()
        new_value = f"{chapter}_{article_value}_{rest_of_file_name}"

    # Append a random string of 20 characters
    new_value = f"{new_value}_{get_random_string(20)}"

    # Truncate the new value if necessary
    if len(new_value) > max_length:
        new_value = new_value[:max_length - 20] + get_random_string(20)

    return new_value

# Create a ChromeDriver service object
service = Service(chromedriver_path)

# Open a Chrome browser instance
driver = webdriver.Chrome(service=service, options=chrome_options)

##############################################
# Load data from JSON
data = read_from_json_file(unique_cases)
##############################################

chapter_link = {}
for item in data:
    chapter = item.get('text')
    link = item.get('href')
    chapter_link[chapter] = link

# Function to find elements safely
def find_elements_safe(by, value, wait):
    while True:
        try:
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            return elements
        except StaleElementReferenceException:
            print("Encountered StaleElementReferenceException, retrying...")
            time.sleep(1)

# Iterate over each chapter and link
for i, (chapter, link) in enumerate(chapter_link.items()):
    print(f"Chapter: {chapter}, Link: {link}")
    first_file = True
    error_logs = []
    try:
        # Open the target URL
        print("Opening URL...")
        driver.get(link)
        print("URL opened.")

        # Wait for the page to load and the buttons to be clickable
        wait = WebDriverWait(driver, 30)  # Wait for up to 30 seconds

        # Find all initial download buttons and link buttons
        print("Finding all download buttons and link buttons...")
        download_buttons = find_elements_safe(By.XPATH, '//span[text()="Download (Docx) of sections"]/parent::button', wait)
        link_buttons = find_elements_safe(By.XPATH, '//span[text()="Share Link to section"]/parent::button', wait)
        print(f"Found {len(download_buttons)} download buttons and {len(link_buttons)} link buttons.")

        files_with_links = {}

        for index, (initial_download_button, link_button) in enumerate(zip(download_buttons, link_buttons)):
            print(f"Processing button pair {index + 1}/{len(download_buttons)}... {i+1}/{len(chapter_link.values())}")

            # Click the initial download button
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", initial_download_button)
                driver.execute_script("arguments[0].click();", initial_download_button)

                # Wait for the popup to be visible
                popup = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="download-footer"]')))
                input_field = wait.until(EC.visibility_of_element_located((By.ID, "auxInput")))
                original_value = input_field.get_attribute('value')
                
                new_value = format_filename(original_value, chapter)
                
                                
                input_field.clear()  # Clear the existing value
                input_field.send_keys(new_value)  # Set the new value
                time.sleep(1)
                input_value = input_field.get_attribute('value')

                # Wait for the final download button within the popup to be clickable
                final_download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//i[@class="fa fa-cloud-download"]/parent::button')))
                final_download_button.click()

                # Wait some time for the download to start (adjust as needed)
                if first_file:
                    time.sleep(10)
                    first_file = False
                else:
                    time.sleep(2)
                      # Wait for 2 seconds (adjust as needed)
                print(f"Download {index + 1} initiated.")
            
            except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                error_message = f"Error for download button {index + 1}: {e}"
                print(error_message)
                error_logs.append({
                    "chapter": chapter,
                    "link": link,
                    "error": error_message
                })

            # Click the link button
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", link_button)
                time.sleep(1)  # Allow time for any animation to complete
                driver.execute_script("arguments[0].click();", link_button)

                # Wait for the popup to be visible
                textarea = wait.until(EC.visibility_of_element_located((By.XPATH, '//textarea[@id="linkUrl"]')))

                # Get the link text from the textarea
                link_text = textarea.get_attribute('value')
                file_name = f"{input_value}.docx"  # Construct file name using the new input field value
                files_with_links[file_name] = link_text

                # Close the popup
                close_button_xpath = '//i[@class="fa fa-close"]/parent::button'
                close_buttons = driver.find_elements(By.XPATH, close_button_xpath)

                if close_buttons:
                    close_button = close_buttons[5]  # Use the first close button found
                    driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                    time.sleep(1)  # Allow time for any animation to complete
                    driver.execute_script("arguments[0].click();", close_button)
                    print(f"Link button {index + 1} processed successfully.")
                else:
                    print("No close buttons found.")

                print(f"Copied link {index + 1} initiated.")
            
            except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                error_message = f"Error for link button {index + 1}: {e}"
                print(error_message)
                error_logs.append({
                    "chapter": chapter,
                    "link": link,
                    "error": error_message
                })
        # Append the new file names and links to the existing JSON file
        if files_with_links:
            append_to_json_file(f'{json_filename}.json', [files_with_links])
            #append_to_json_file(f'{json_filename}.json', [{"chapter": chapter, "files_with_links": files_with_links}])
            print("File names and links have been appended to JSON.")

    except Exception as e:
        error_message = f"General error for chapter {chapter}: {e}"
        print(error_message)
        error_logs.append({
            "chapter": chapter,
            "link": link,
            "error": error_message
        })

    # Append errors to the error JSON file
    if error_logs:
        append_to_json_file(f'{json_filename}_error.json', error_logs)


# Close the browser window
print("Closing browser...")
driver.quit()
print("Browser closed.")


county_links = {
    "Martin": "https://library.municode.com/fl/martin_county/codes/code_of_ordinances?nodeId=112034",
    "Leon": "https://library.municode.com/fl/leon_county/codes/code_of_ordinances?nodeId=10008",
    "Alachua": "https://library.municode.com/fl/alachua_county/codes/code_of_ordinances?nodeId=10343",
    "Bay": "https://library.municode.com/fl/bay_county/codes/code_of_ordinances?nodeId=14281",
    "Charlotte": "https://library.municode.com/fl/charlotte_county/codes/code_of_ordinances?nodeId=10526",
    "Indian River": "https://library.municode.com/fl/indian_river_county/codes/code_of_ordinances?nodeId=COOR_TITITHCOCOORINPR",
    "Jacksonville": "https://library.municode.com/fl/jacksonville/codes/code_of_ordinances?nodeId=12174",
    "Collier": "https://library.municode.com/fl/collier_county/codes/code_of_ordinances?nodeId=10578",
    "Lee": "https://library.municode.com/fl/lee_county/codes/code_of_ordinances?nodeId=10131",
    "Escambia": "https://library.municode.com/fl/escambia_county/codes/code_of_ordinances?nodeId=10700",
    "Flagler": "https://library.municode.com/fl/flagler_county/codes/code_of_ordinances?nodeId=12218",
    "Indian River": "https://library.municode.com/fl/indian_river_county/codes/code_of_ordinances?nodeId=12232",
    "Seminole": "https://library.municode.com/fl/seminole_county/codes/code_of_ordinances?nodeId=13774",
    "Orange": "https://library.municode.com/fl/orange_county/codes/code_of_ordinances?nodeId=10182",
    "Nassau": "https://library.municode.com/fl/nassau_county/codes/code_of_ordinances?nodeId=11325",
    "Pinellas" : "https://library.municode.com/fl/pinellas_county/codes/code_of_ordinances?nodeId=10274",
    "Hillsborough" : "https://library.municode.com/fl/hillsborough_county/codes/code_of_ordinances,_part_a?nodeId=14861",
    "Polk" : "https://library.municode.com/fl/polk_county/codes/code_of_ordinances?nodeId=11435",
    "Pasco" : "https://library.municode.com/fl/pasco_county/codes/code_of_ordinances?nodeId=10281",
    "Manatee" :"https://library.municode.com/fl/manatee_county/codes/code_of_ordinances?nodeId=10428",
    "Sarasota":"https://library.municode.com/fl/sarasota_county/codes/code_of_ordinances?nodeId=11511"
}