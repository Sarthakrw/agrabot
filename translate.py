import os
import json
import time
from shutil import copytree, ignore_patterns, rmtree
from deep_translator import GoogleTranslator

# Define the source and target folders
source_folder = 'data/data_en'
target_folder = 'data/data_sw3'
progress_log = 'translation_progress.log'

translator = GoogleTranslator(source='en', target='sw')

# Function to translate text from English to Swahili
def translate_text(text):
    return translator.translate(text)

# Function to translate a single JSON file
def translate_file(filepath, start_index=0):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)

    translated_data = []
    for i, item in enumerate(data[start_index:], start=start_index):
        start = time.time()
        item['question'] = translate_text(item['question'])
        print(f"Translated question {i + 1} in {time.time() - start:.4f} seconds")
        
        start = time.time()
        item['answer'] = translate_text(item['answer'])
        print(f"Translated answer {i + 1} in {time.time() - start:.4f} seconds")
        
        translated_data.append(item)
        
        # Write to file every 20 pairs
        if (i + 1) % 20 == 0:
            write_translated_data(filepath, translated_data)
            translated_data.clear()
            update_progress_log(filepath, i + 1)

    # Write any remaining translated data
    if translated_data:
        write_translated_data(filepath, translated_data)
        update_progress_log(filepath, len(data))

    return translated_data

# Function to write translated data to a JSON file
def write_translated_data(filepath, data):
    target_filepath = os.path.join(target_folder, os.path.relpath(filepath, source_folder))
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
    # Append to the file
    if os.path.exists(target_filepath):
        with open(target_filepath, 'r+', encoding='utf-8') as file:
            existing_data = json.load(file)
            existing_data.extend(data)
            file.seek(0)
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
    else:
        with open(target_filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

# Function to update the progress log
def update_progress_log(filename, index):
    with open(progress_log, 'w') as log_file:
        log_file.write(f"{filename},{index}\n")

# Function to read the progress log
def read_progress_log():
    if os.path.exists(progress_log):
        with open(progress_log, 'r') as log_file:
            content = log_file.readline().strip()
            if content:
                filename, index = content.split(',')
                return filename, int(index)
    return None, 0

# Read the progress log to resume from the last stop
last_filename, last_index = read_progress_log()

# If no progress log, remove the target folder and start fresh
if not last_filename and os.path.exists(target_folder):
    rmtree(target_folder)

# Copy the entire folder structure to the target folder without JSON files (only if starting fresh)
if not last_filename:
    start = time.time()
    copytree(source_folder, target_folder, ignore=ignore_patterns('*.json'))
    print(f"Copied folder structure in {time.time() - start:.4f} seconds")

# Walk through all files and directories within the source folder
for root, _, files in os.walk(source_folder):
    for filename in files:
        if filename.endswith('.json'):  # Ensure it's a JSON file
            source_filepath = os.path.join(root, filename)
            
            # If resuming, skip files that have been completed
            if last_filename and filename < last_filename:
                continue
            
            start = time.time()
            translated_data = translate_file(source_filepath, start_index=last_index if filename == last_filename else 0)
            print(f"Translated file {filename} in {time.time() - start:.4f} seconds")
            
            # Reset progress for the next file
            last_index = 0

print("Translation complete. Translated files are saved in the 'data_sw3' folder.")
