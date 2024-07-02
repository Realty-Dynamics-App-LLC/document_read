import os
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def truncate_and_rename_files(directory):
    for filename in os.listdir(directory):
        if len(filename) > 100:
            # Get the file extension (if any)
            file_root, file_extension = os.path.splitext(filename)
            
            # Truncate to 100 characters
            truncated_name = file_root[:100]
            
            # Generate random string of 20 characters
            random_str = get_random_string(20)
            
            # New filename
            new_filename = truncated_name + random_str + file_extension
            
            # Form full path
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)
            
            # Rename file
            os.rename(old_file, new_file)
            print(f'Renamed: {old_file} to {new_file}')

def change_extension_to_json(directory):
    for filename in os.listdir(directory):
        # Check if the file has a .txt extension
        if filename.endswith('.txt'):
            # Form the new filename by changing the extension to .json
            new_filename = filename[:-4] + '.json'
            
            # Form full paths
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)
            
            # Rename the file
            os.rename(old_file, new_file)
            print(f'Renamed: {old_file} to {new_file}')

# Usage
directory_path = '/home/jason/Downloads/sarasota/cleaned'  # Replace with your directory path
# truncate_and_rename_files(directory_path)

change_extension_to_json(directory_path)
