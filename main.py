import os
import time
import datetime

# Determine the absolute path to the directory containing this script
script_dir = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = os.path.join(script_dir, "water_intake_log.txt")

def send_notification(title, message):
    return os.system(f"osascript -e 'display dialog \"{message}\" with title \"{title}\" buttons {{\"I drank water\", \"Snooze\", \"Exit\"}} default button 1'")

def log_water_intake():
    with open(LOG_FILE, 'a') as file:
        file.write(f"{datetime.datetime.now()} - Drank water\n")

def main():
    try:
        while True:
            response = send_notification("Water Reminder", "Did you drink water?")
            if response == 0:  # If "I drank water" is pressed
                log_water_intake()
            elif response == 256:  # If "Snooze" is pressed
                pass
            elif response == 512:  # If "Exit" is pressed
                break
            time.sleep(60 * 30)  # Remind every 30 minutes
    except KeyboardInterrupt:
        print("\nWater reminder stopped.")

if __name__ == "__main__":
    main()
