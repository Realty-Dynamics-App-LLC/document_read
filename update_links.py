import os
import json
import re

def transform_key(key):
    key = key.replace('_', '')     # Remove underscores
    key = key.replace('-', '')     # Remove hyphens
    key = key.replace(';', '')     # Remove semicolons
    key = key.replace(' ', '')     # Remove spaces
    key = key.replace('docx', '')  # Remove 'docx' if it's part of the key (not clear if needed)
    key = re.sub(r'[\(\)]', '', key)        # Remove parentheses (if any)
    key = re.sub(r'[^\w]', '', key)        # Replace non-word characters (including \u) with underscores
    return key

def update_txt_files(txt_files_directory, transformed_data):
    for filename in os.listdir(txt_files_directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(txt_files_directory, filename)

            with open(filepath, 'r', encoding='utf-8') as file:
                content = json.load(file)

            base_filename = os.path.splitext(filename)[0]
            base_filename = base_filename.replace('_', '').replace('.', '')

            # Find corresponding transformed key in transformed_data
            updated_link = None
            for item in transformed_data:
                if base_filename in item:
                    updated_link = item[base_filename]
                    break

            # Update the link field if a matching transformed key is found
            if updated_link is not None:
                content['link'] = updated_link
            
            # Write the updated content back to the text file
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(content, file, ensure_ascii=False, indent=4)

# Example usage
txt_files_directory = '/home/jason/Downloads/sarasota/cleaned'

# Load JSON data
json_file_path = '/home/jason/Desktop/internship/Florida_municode/code/Sarasota County.json'
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# Transform keys in JSON data
transformed_data = []
for item in json_data:
    transformed_item = {}
    for original_key, value in item.items():
        transformed_key = transform_key(original_key)
        transformed_item[transformed_key] = value
    transformed_data.append(transformed_item)

# Update .txt files based on transformed keys
update_txt_files(txt_files_directory, transformed_data)
