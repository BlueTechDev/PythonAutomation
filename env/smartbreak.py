import time
import random
import subprocess  # Import subprocess for running osascript commands on macOS

# Set the interval for break reminders (in seconds)
WORK_INTERVAL = 60 * 60  # 1 minute for testing

# List of reminder messages
REMINDERS = [
    "Time to stretch!",
    "Grab a glass of water!",
    "Look away from the screen for 20 seconds.",
    "Take a deep breath and relax.",
    "Stand up and move around a bit!",
    "Rest your eyes to reduce strain."
]

def send_break_notification():
    message = random.choice(REMINDERS)
    # Use osascript to show macOS notification
    script = f'display notification "{message}" with title "Break Reminder"'
    subprocess.run(["osascript", "-e", script])
    print(f"Notification sent: {message}")

if __name__ == "__main__":
    print("Smart Break Reminder started...")

    try:
        while True:
            # Wait for the work interval to pass
            time.sleep(WORK_INTERVAL)
            
            # Send a random break reminder notification
            send_break_notification()
            
    except KeyboardInterrupt:
        print("Break Reminder stopped.")
