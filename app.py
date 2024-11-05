from flask import Flask, render_template, request, jsonify
import json
import os
import shutil
from datetime import datetime, timedelta

app = Flask(__name__)

# Load configuration settings from config.json
def load_config():
    with open("config.json", "r") as file:
        config = json.load(file)
    return config

config = load_config()

# Directory paths from config
DESKTOP_DIR = os.path.expanduser(config['directories']['desktop'])
DOWNLOADS_DIR = os.path.expanduser(config['directories']['downloads'])
SCREENSHOTS_DIR = os.path.expanduser(config['directories']['screenshots'])
ARCHIVE_DIR = os.path.expanduser(config['directories']['archive'])

# Global counters for tracking file movements
stats = {
    "total_files_moved": 0,
    "total_files_archived": 0,
    "total_screenshots_organized": 0
}

# Helper function to categorize file types
def get_file_category(file_extension):
    for category, extensions in config['folders'].items():
        if file_extension.lower() in extensions:
            return category
    return "Others"

# Function to organize files
def organize_files(directory):
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

    stats["total_files_moved"] += files_moved
    return files_moved

# Function to archive old files
def archive_old_files(directory, archive_dir, days_old=30):
    files_archived = 0
    now = datetime.now()

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        if os.path.isdir(file_path) or file_name.startswith('.'):
            continue

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

    stats["total_files_archived"] += files_archived
    return files_archived

# Function to organize screenshots
def organize_screenshots():
    project_keywords = {
        "Meeting": ["meeting", "call", "discussion"],
        "Presentation": ["presentation", "slide", "ppt"],
        "Design": ["design", "mockup", "sketch"]
    }

    month_folder = datetime.now().strftime("%B_%Y")
    target_month_dir = os.path.join(SCREENSHOTS_DIR, month_folder)
    os.makedirs(target_month_dir, exist_ok=True)

    screenshots_moved = 0

    for file_name in os.listdir(DESKTOP_DIR):
        file_path = os.path.join(DESKTOP_DIR, file_name)

        if os.path.isdir(file_path) or not file_name.lower().startswith("screenshot"):
            continue

        for project, keywords in project_keywords.items():
            if any(keyword.lower() in file_name.lower() for keyword in keywords):
                target_folder = os.path.join(SCREENSHOTS_DIR, project)
                os.makedirs(target_folder, exist_ok=True)
                target_path = target_folder
                break
        else:
            target_path = target_month_dir

        target_file_path = os.path.join(target_path, file_name)

        if os.path.exists(target_file_path):
            base, ext = os.path.splitext(file_name)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            target_file_path = os.path.join(target_path, f"{base}_{timestamp}{ext}")

        shutil.move(file_path, target_file_path)
        screenshots_moved += 1
        print(f"Moved Screenshot: {file_name} -> {target_path}")

    stats["total_screenshots_organized"] += screenshots_moved
    return screenshots_moved

# Flask routes
@app.route('/')
def index():
    return render_template('index.html', summary_stats=stats)

@app.route('/organize', methods=['POST'])
def organize_route():
    desktop_files_moved = organize_files(DESKTOP_DIR)
    downloads_files_moved = organize_files(DOWNLOADS_DIR)
    total_files_moved = desktop_files_moved + downloads_files_moved
    return jsonify({'files_moved': total_files_moved})

@app.route('/archive', methods=['POST'])
def archive_route():
    files_archived = archive_old_files(DOWNLOADS_DIR, ARCHIVE_DIR, days_old=config['days_old_for_archive'])
    return jsonify({'files_archived': files_archived})

@app.route('/screenshots', methods=['POST'])
def organize_screenshots_route():
    screenshots_moved = organize_screenshots()
    return jsonify({'screenshots_moved': screenshots_moved})

if __name__ == "__main__":
    app.run(debug=True)
