import time
import os
import datetime

LOG_FILE = "water_intake_log.txt"

def send_notification(title, message):
    return os.system(f"osascript -e 'display dialog \"{message}\" with title \"{title}\" buttons {{\"I drank water\", \"Snooze\", \"Exit\"}} default button 1'") == 0

def log_water_intake():
    with open(LOG_FILE, 'a') as file:
        file.write(f"{datetime.datetime.now()} - Drank water\n")

def main():
    try:
        while True:
            response = send_notification("Water Reminder", "Did you drink water?")
            if response:  # If "I drank water" is pressed
                log_water_intake()
            elif not response:  # If "Exit" is pressed
                break
            time.sleep(60 * 30)  # Remind every 30 minutes
    except KeyboardInterrupt:
        print("\nWater reminder stopped.")

if __name__ == "__main__":
    main()
