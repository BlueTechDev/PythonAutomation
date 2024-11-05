from flask import Flask, render_template, request, redirect, url_for, jsonify
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

# Folders and file types from config
FOLDERS = config['folders']
DAYS_OLD_FOR_ARCHIVE = config['days_old_for_archive']

# Helper functions
def get_file_category(file_extension):
    for category, extensions in FOLDERS.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"

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

    return files_moved

def archive_old_files(directory, archive_dir, days_old=30):
    now = datetime.now()
    files_archived = 0

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

    return files_archived

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/organize', methods=['POST'])
def organize():
    desktop_files_moved = organize_files(DESKTOP_DIR)
    downloads_files_moved = organize_files(DOWNLOADS_DIR)
    total_files_moved = desktop_files_moved + downloads_files_moved
    return jsonify({'files_moved': total_files_moved})

@app.route('/archive', methods=['POST'])
def archive():
    files_archived = archive_old_files(DOWNLOADS_DIR, ARCHIVE_DIR, days_old=DAYS_OLD_FOR_ARCHIVE)
    return jsonify({'files_archived': files_archived})

@app.route('/log')
def view_log():
    if os.path.exists("weekly_log.txt"):
        with open("weekly_log.txt", "r") as log_file:
            log_content = log_file.readlines()
    else:
        log_content = ["No log file found."]
    return render_template('log.html', log_content=log_content)

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

if __name__ == "__main__":
    app.run(debug=True)
