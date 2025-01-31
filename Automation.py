import json
import os
import shutil
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Load configuration settings from config.json
def load_config():
    try:
        logging.info("Loading configuration from config.json...")
        with open("config.json", "r") as file:
            config = json.load(file)
        logging.info("Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        logging.error("config.json file not found.")
        raise
    except json.JSONDecodeError:
        logging.error("Error decoding config.json.")
        raise

config = load_config()

# Directory paths from config
DESKTOP_DIR = os.path.expanduser(config['directories']['desktop'])
DOWNLOADS_DIR = os.path.expanduser(config['directories']['downloads'])
SCREENSHOTS_DIR = os.path.expanduser(config['directories']['screenshots'])
ARCHIVE_DIR = os.path.expanduser(config['directories']['archive'])

# Folders and file types from config
FOLDERS = config['folders']
DAYS_OLD_FOR_ARCHIVE = config['days_old_for_archive']

today = datetime.today().weekday()  # Monday is 0, Sunday is 6

def move_file(file_path, destination_dir):
    try:
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        shutil.move(file_path, destination_dir)
        logging.info(f"Moved file {file_path} to {destination_dir}")
    except Exception as e:
        logging.error(f"Error moving file {file_path} to {destination_dir}: {e}")

def organize_files(directory):
    logging.info(f"Organizing files in {directory}...")
    files_moved = 0
    try:
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                # Example logic: Move text files to a specific folder
                if file_name.endswith('.txt'):
                    move_file(file_path, os.path.join(directory, 'TextFiles'))
                files_moved += 1
        logging.info(f"Moved {files_moved} files in {directory}.")
    except Exception as e:
        logging.error(f"Error organizing files in {directory}: {e}")

# Example usage
organize_files(DESKTOP_DIR)