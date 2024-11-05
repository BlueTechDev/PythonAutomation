import time
import pyperclip # type: ignore
import subprocess
import os

# Set a path to the notes file where saved texts will go
NOTES_FILE_PATH = os.path.expanduser("~/Desktop/quick_notes.txt")

# Initialize clipboard content to monitor changes
previous_clipboard_content = pyperclip.paste()

# Function to display options using AppleScript and get user input
def display_options():
    try:
        script = '''
        display dialog "Choose an action for the copied text:" buttons {"Google", "Wikipedia", "YouTube", "Save to Notes"} default button "Google"
        set userChoice to button returned of result
        return userChoice
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        choice = result.stdout.strip()
        print(f"User choice received: {choice}")  # Debugging information
        
        # Set default choice if no response received
        if not choice:
            choice = "Google"
            print("No choice received; defaulting to Google.")

        return choice
    except Exception as e:
        print(f"Error displaying options: {e}")
        return "Google"  # Default fallback choice

# Function to open a search in the browser based on user's choice
def perform_action(choice, text):
    if choice == "Google":
        url = f"https://www.google.com/search?q={text}"
    elif choice == "Wikipedia":
        url = f"https://en.wikipedia.org/wiki/Special:Search?search={text}"
    elif choice == "YouTube":
        url = f"https://www.youtube.com/results?search_query={text}"
    elif choice == "Save to Notes":
        with open(NOTES_FILE_PATH, "a") as f:
            f.write(f"{text}\n")
        print(f"Text saved to notes: {text}")
        return
    else:
        print("Invalid choice received:", choice)
        return

    # Open the URL in the default web browser
    subprocess.run(["open", url])
    print(f"Opened {choice} for: {text}")

# Main loop to monitor clipboard
print("Monitoring clipboard for new text...")

try:
    while True:
        # Get current clipboard content
        current_clipboard_content = pyperclip.paste()

        # If the clipboard content has changed and isn't empty
        if current_clipboard_content != previous_clipboard_content and current_clipboard_content.strip():
            # Update previous content
            previous_clipboard_content = current_clipboard_content

            # Display options and get user's choice
            print(f"New text copied: {current_clipboard_content}")
            user_choice = display_options()

            # Perform the selected action
            perform_action(user_choice, current_clipboard_content)

        # Wait a bit before checking the clipboard again
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Clipboard monitoring stopped.")
