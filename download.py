import time
import re
import os
import json
import string
import random
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
# Set Chrome options to allow download
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": f"/home/jason/Downloads/{county}",  # Replace with your desired download directory
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Function to append new entries to a JSON file
def append_to_json_file(filename, new_entries):
    #print(new_entries)
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

# Target website URL
url = "https://library.municode.com/fl/charlotte_county/codes/code_of_ordinances?nodeId=GEORSPAC_CH1-10LIBURE_ARTXVISEMERE"
# Change this accordingly 
chapter = "ARTICLE XVI. - SECONDARY METAL RECYCLERS" 
all_links = []
is_article = True
article_value =""
files_with_links = {}

directory = county 
if not os.path.exists(directory):
    os.makedirs(directory)

json_filename = os.path.join(directory, f"{county} County")


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

    # Find all initial download buttons and link buttons
    print("Finding all download buttons and link buttons...")
    download_buttons = find_elements_safe(By.XPATH, '//span[text()="Download (Docx) of sections"]/parent::button')
    link_buttons = find_elements_safe(By.XPATH, '//span[text()="Share Link to section"]/parent::button')
    print(f"Found {len(download_buttons)} download buttons and {len(link_buttons)} link buttons.")
    error_logs = []

    for index, (initial_download_button, link_button) in enumerate(zip(download_buttons, link_buttons)):
        print(f"Processing button pair {index + 1}/{len(download_buttons)}...")
        # Click the initial download button
        try:
            # print("Waiting for initial download button to be clickable...")
            # Ensure the button is in the viewport
            driver.execute_script("arguments[0].scrollIntoView(true);", initial_download_button)

            # Click using JavaScript to avoid interception issues
            driver.execute_script("arguments[0].click();", initial_download_button)
            # print("Initial download button clicked.")
            
            # Wait for the popup to be visible
            # print("Waiting for popup to be visible...")
            popup = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="download-footer"]')))
            # print("Popup is visible.")
            
            input_field = wait.until(EC.visibility_of_element_located((By.ID, "auxInput")))
            original_value = input_field.get_attribute('value')

            new_value = format_filename(original_value, chapter)
            

            

            input_field.clear()  # Clear the existing value
            input_field.send_keys(new_value)  # Set the new value
            time.sleep(1)
            input_value = input_field.get_attribute('value')
            # print(f"Input field value set to: {input_value}")

            # Wait for the final download button within the popup to be clickable
            # print("Waiting for final download button in the popup to be clickable...")
            final_download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//i[@class="fa fa-cloud-download"]/parent::button')))
            # print("Final download button found. Clicking it...")
            final_download_button.click()

            # (Optional) Wait some time for the download to start (adjust as needed)
            time.sleep(5)  # Wait for 2 seconds (adjust as needed)
            # print(f"Download {index + 1} initiated.")
        
        except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                error_message = f"Error for download button {index + 1}: {e}"
                print(error_message)
                error_logs.append({
                    "chapter": chapter,
                    "link": url,
                    "error": error_message
                })

        # Click the link button
        try:
            # print("Waiting for link button to be clickable...")
            driver.execute_script("arguments[0].scrollIntoView(true);", link_button)
            time.sleep(1)  # Allow time for any animation to complete
            driver.execute_script("arguments[0].click();", link_button)
            # print("Link button clicked.")

            # Wait for the popup to be visible
            # print("Waiting for popup to be visible...")
            textarea = wait.until(EC.visibility_of_element_located((By.XPATH, '//textarea[@id="linkUrl"]')))
            # print("Popup is visible.")

            # Get the link text from the textarea
            link_text = textarea.get_attribute('value')
            all_links.append(link_text)
            file_name = f"{input_value}docx"  # Construct file name using the new input field value
            files_with_links[file_name] = link_text
            # print("Textarea link:", link_text)
            
            # Close the popup
            # print("Getting close button")
            close_button_xpath = '//i[@class="fa fa-close"]/parent::button'
            close_buttons = driver.find_elements(By.XPATH, close_button_xpath)
            # print(f"Found {len(close_buttons)} close buttons with XPath: {close_button_xpath}")

            if close_buttons:
                close_button = close_buttons[5]  # Use the first close button found
                driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                time.sleep(1)  # Allow time for any animation to complete
                driver.execute_script("arguments[0].click();", close_button)
                print("Popup closed.")
            else:
                print("Close button not found.")

            print(f"Copied link {index + 1} initiated.")
        
        except (TimeoutException, ElementClickInterceptedException, StaleElementReferenceException) as e:
                error_message = f"Error for link button {index + 1}: {e}"
                print(error_message)
                error_logs.append({
                    "chapter": chapter,
                    "link": link_text,
                    "error": error_message
                })

    print("All buttons processed.")

except Exception as e:
    error_message = f"General error for chapter {chapter}: {e}"
    print(error_message)
    error_logs.append({
        "chapter": chapter,
        "link": url,
        "error": error_message
    })


# Append the new file names and links to the existing JSON file
append_to_json_file(f'{json_filename}.json', [files_with_links])
print("File names and links have been appended to files_with_links.json.")

# Append the new file names and links to the existing JSON file
# if files_with_links:
#     append_to_json_file(f'{json_filename}.json', [{"chapter": chapter, "files_with_links": files_with_links}])
#     print("File names and links have been appended to JSON.")


# Append errors to the error JSON file
if error_logs:
    append_to_json_file(f'{json_filename}_error.json', error_logs)



# Close the browser window
print("Closing browser...")
driver.quit()
print("Browser closed.")