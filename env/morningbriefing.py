import requests # type: ignore
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import os

# API keys and endpoints
WEATHER_API_KEY = "fc439d5ce8fed328ebf397a8351b72a2"
NEWS_API_KEY = "c33648e334504f7a8d3d9562a78d70f6"
LOCATION = "New York"  # Replace with your city
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={WEATHER_API_KEY}&units=metric"
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

# Function to get today's weather
def get_weather():
    try:
        response = requests.get(WEATHER_URL)
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        weather = f"{temp}°C, {description}"
        return f"Weather in {LOCATION}: {weather}"
    except Exception as e:
        return f"Weather info unavailable: {e}"

# Function to get today's top news headlines
def get_news():
    try:
        response = requests.get(NEWS_URL)
        data = response.json()
        articles = data["articles"][:3]  # Get top 3 headlines
        headlines = [f"- {article['title']}" for article in articles]
        return "Today's Top News:\n" + "\n".join(headlines)
    except Exception as e:
        return f"News info unavailable: {e}"

# Function to get calendar events for today using AppleScript
def get_calendar_events():
    script = '''
    set today to current date
    tell application "Calendar"
        set theEvents to ""
        repeat with e in (every event of calendar "Calendar" whose start date > today and start date < today + 1 * days)
            set theEvents to theEvents & summary of e & " at " & start date of e & linefeed
        end repeat
    end tell
    return theEvents
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    events = result.stdout.strip()
    return "Today's Events:\n" + events if events else "No events scheduled today."

# Function to get reminders for today using AppleScript
def get_reminders():
    script = '''
    tell application "Reminders"
        set todayReminders to ""
        repeat with r in (every reminder whose due date is not missing value and due date ≤ (current date))
            set todayReminders to todayReminders & name of r & " - Due " & due date of r & linefeed
        end repeat
    end tell
    return todayReminders
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    reminders = result.stdout.strip()
    return "Today's Reminders:\n" + reminders if reminders else "No reminders due today."

# Function to get a motivational quote
def get_quote():
    try:
        response = requests.get("https://api.quotable.io/random")
        data = response.json()
        quote = f"Quote of the Day: \"{data['content']}\" - {data['author']}"
        return quote
    except Exception as e:
        return f"Quote unavailable: {e}"

# Compile the briefing
def morning_briefing():
    briefing = [
        f"Good morning! Here’s your briefing for {datetime.now().strftime('%A, %B %d, %Y')}:",
        "-" * 40,
        get_weather(),
        get_news(),
        get_calendar_events(),
        get_reminders(),
        get_quote(),
    ]
    return "\n\n".join(briefing)

# Display the briefing in a GUI
def display_briefing_gui():
    briefing = morning_briefing()
    
    # Initialize tkinter window
    root = tk.Tk()
    root.title("Morning Briefing")
    root.geometry("400x500")  # Set window size

    # Create a scrollable text area
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=25, font=("Arial", 10))
    text_area.insert(tk.INSERT, briefing)
    text_area.config(state=tk.DISABLED)  # Make text area read-only
    text_area.pack(pady=10, padx=10)

    # Add a close button
    close_button = tk.Button(root, text="Close", command=root.destroy)
    close_button.pack(pady=10)

    # Start the tkinter event loop
    root.mainloop()

# Run the briefing GUI
if __name__ == "__main__":
    display_briefing_gui()
