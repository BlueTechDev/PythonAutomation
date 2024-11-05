import json
import os
import shutil
from datetime import datetime, timedelta
from dotenv import load_dotenv  # type: ignore # Ensure dotenv is imported

# Load environment variables from .env file
load_dotenv()

# Load configuration settings from config.json
def load_config():
    print("Loading configuration from config.json...")
    with open("config.json", "r") as file:
        config = json.load(file)
    print("Configuration loaded successfully.")
    return config

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

# Organize daily
def organize_files(directory):
    print(f"Organizing files in {directory}...")
    files_moved = 0
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        
        if os.path.isdir(file_path) or file_name.startswith('.'):
            continue

        file_extension = os.path.splitext(file_name)[1]
        category = get_file_category(file_extension)
        
        target_folder = os.path.join(directory, category)
        os.makedirs(target_folder, exist_ok=True)
        
        target_path = os.path.join(target_folder, file_name)
        
        if os.path.exists(target_path):
            base, ext = os.path.splitext(file_name)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            target_path = os.path.join(target_folder, f"{base}_{timestamp}{ext}")
        
        shutil.move(file_path, target_path)
        files_moved += 1
        print(f"Moved: {file_name} -> {target_folder}")

    print(f"Total files moved in {directory}: {files_moved}")
    return files_moved

# Helper function to categorize file types
def get_file_category(file_extension):
    for category, extensions in FOLDERS.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"

# Archive old files only on Sundays
def archive_old_files(directory, archive_dir, days_old=30):
    print(f"Archiving old files in {directory} (older than {days_old} days)...")
    now = datetime.now()
    files_archived = 0

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        
        if os.path.isdir(file_path) or file_name.startswith('.'):
            continue
        
        # Use last accessed time instead of modified time
        file_access_time = datetime.fromtimestamp(os.path.getatime(file_path))
        if now - file_access_time > timedelta(days=days_old):
            os.makedirs(archive_dir, exist_ok=True)
            target_path = os.path.join(archive_dir, file_name)
            
            if os.path.exists(target_path):
                base, ext = os.path.splitext(file_name)
                timestamp = file_access_time.strftime("%Y%m%d")
                target_path = os.path.join(archive_dir, f"{base}_{timestamp}{ext}")
            
            shutil.move(file_path, target_path)
            files_archived += 1
            print(f"Archived: {file_name} -> {archive_dir}")

    print(f"Total files archived in {directory}: {files_archived}")
    return files_archived

def log_summary(total_files_moved, total_files_archived):
    print("Logging weekly summary...")
    with open("weekly_log.txt", "a") as log_file:
        log_file.write(f"Weekly Summary - {datetime.now().strftime('%Y-%m-%d')}\n")
        log_file.write(f"Files Moved: {total_files_moved}\n")
        log_file.write(f"Files Archived: {total_files_archived}\n")
        log_file.write("=" * 40 + "\n")
    print("Weekly summary logged.")

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class DownloadEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            organize_files(DOWNLOADS_DIR)

def organize_screenshots():
    print("Organizing screenshots by month...")
    month_folder = datetime.now().strftime("%B_%Y")
    target_month_dir = os.path.join(SCREENSHOTS_DIR, month_folder)
    os.makedirs(target_month_dir, exist_ok=True)

    screenshots_moved = 0
    for file_name in os.listdir(DESKTOP_DIR):
        file_path = os.path.join(DESKTOP_DIR, file_name)
        
        if os.path.isdir(file_path) or not file_name.startswith("Screenshot"):
            continue

        target_path = os.path.join(target_month_dir, file_name)
        
        if os.path.exists(target_path):
            base, ext = os.path.splitext(file_name)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            target_path = os.path.join(target_month_dir, f"{base}_{timestamp}{ext}")
        
        shutil.move(file_path, target_path)
        screenshots_moved += 1
        print(f"Moved Screenshot: {file_name} -> {target_month_dir}")

    print(f"Total screenshots moved: {screenshots_moved}")
    return screenshots_moved

# Start monitoring Downloads for real-time file organization
if __name__ == "__main__":
    print("Starting file organizer...")

    # Organize files daily if it’s a weekday
    if today in range(0, 5):  # Monday to Friday
        files_moved_desktop = organize_files(DESKTOP_DIR)
        files_moved_downloads = organize_files(DOWNLOADS_DIR)
        total_files_moved = files_moved_desktop + files_moved_downloads
    else:
        total_files_moved = 0

    # Archive old files and log if today is Sunday
    if today == 6:  # Sunday
        total_files_archived = archive_old_files(DOWNLOADS_DIR, ARCHIVE_DIR, days_old=DAYS_OLD_FOR_ARCHIVE)
        log_summary(total_files_moved, total_files_archived)
    else:
        total_files_archived = 0

    # Monitor Downloads folder for real-time organization
    event_handler = DownloadEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DOWNLOADS_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping file organizer...")
        observer.stop()
    observer.join()

    print("File organization complete.")
