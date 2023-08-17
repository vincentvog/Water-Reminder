import tkinter as tk
from tkinter import ttk
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import os

class Config:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.paths = {
            "LOG_FILE": os.path.join(self.script_dir, "water_intake_log.txt"),
            "IMAGE_PATH": os.path.join(self.script_dir, "images", "water_glass.png"),

        }
        self.REMINDER_INTERVAL = 30  # in minutes

class WaterIntakeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Intake Tracker")
        self.config = Config()

        self.water_intake = []
        self.last_log_time = None
        self.notification_running = False

        self.setup_ui()

        self.load_water_intake()
        self.update_graph()
        self.read_last_log_time()
        self.update_countdown()

    def setup_ui(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text="Water Intake")
        self.tab_control.add(self.tab2, text="Graph")
        self.tab_control.pack()

        tk.Label(self.tab1, text="Did you drink water?").pack()
        tk.Button(self.tab1, text="I drank water", command=self.log_water_intake).pack()

        self.countdown_label = tk.Label(self.tab1, text="")
        self.countdown_label.pack()

        self.figure = plt.Figure(figsize=(7, 5), dpi=100)
        self.graph = FigureCanvasTkAgg(self.figure, master=self.tab2)
        self.graph.get_tk_widget().pack()

    def log_water_intake(self):
        now = datetime.datetime.now()
        self.water_intake.append(now)
        with open(self.config.paths["LOG_FILE"], "a") as log_file:
            log_file.write(f"{now.strftime('%Y-%m-%d %H:%M:%S.%f')} - Drank water\n")
        self.last_log_time = now
        self.update_graph()
        self.update_countdown()
        self.notification_running = False

    def read_last_log_time(self):
        try:
            with open(self.config.paths["LOG_FILE"], "r") as log_file:
                lines = log_file.readlines()
                if lines:
                    last_log_entry = lines[-1].strip().split(" - ")[0]
                    self.last_log_time = datetime.datetime.strptime(last_log_entry, "%Y-%m-%d %H:%M:%S.%f")
        except FileNotFoundError:
            pass

    def load_water_intake(self):
        try:
            with open(self.config.paths["LOG_FILE"], "r") as log_file:
                for line in log_file:
                    parts = line.strip().split(" - ")
                    if len(parts) == 2 and parts[1] == "Drank water":
                        try:
                            datetime_obj = datetime.datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S.%f')
                            self.water_intake.append(datetime_obj)
                        except ValueError:
                            pass
        except FileNotFoundError:
            pass

    def update_graph(self):
        self.figure.clear()
        drink_count = Counter([entry.date() for entry in self.water_intake])
        unique_dates = list(drink_count.keys())
        counts = list(drink_count.values())

        ax = self.figure.add_subplot(111)
        bars = ax.bar(range(len(unique_dates)), counts)
        ax.set_xticks(range(len(unique_dates)))
        ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in unique_dates], rotation=0, ha='center')

        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count),
                    ha='center', va='bottom', fontsize=9)
        
        ax.set_ylabel('Number of Drinks')
        ax.set_xlabel('Date')

        plt.tight_layout()
        self.graph.draw()

    def update_countdown(self):
        current_time = datetime.datetime.now()

        if self.last_log_time:
            time_since_last_log = current_time - self.last_log_time
            if time_since_last_log.total_seconds() >= self.config.REMINDER_INTERVAL * 60 and not self.notification_running:
                countdown_text = "Time to drink water!"
                response = self.send_notification("Water Reminder", "Did you drink water?")
                if response == 0:  # "I drank water" button clicked
                    self.notification_running = False  # Reset the flag
                    self.log_water_intake()  # Log the water intake
                elif response == 1:  # "Snooze" button clicked
                    self.notification_running = True
                elif response == 2:  # "Exit" button clicked
                    self.root.quit()
            else:
                if time_since_last_log.total_seconds() >= self.config.REMINDER_INTERVAL * 60:
                    self.notification_running = False
                time_until_next_reminder = datetime.timedelta(minutes=self.config.REMINDER_INTERVAL) - time_since_last_log
                minutes, seconds = divmod(int(time_until_next_reminder.total_seconds()), 60)
                countdown_text = f"Next reminder in: {minutes:02d}:{seconds:02d}"
        else:
            countdown_text = "Time to drink water!"
            self.send_notification("Water Reminder", "Did you drink water?")

        self.countdown_label.config(text=countdown_text)
        self.root.after(1000, self.update_countdown)

    def send_notification(self, title, message):
        osascript_cmd = (
            f"osascript -e 'do shell script \"afplay /System/Library/Sounds/Blow.aiff\"' & "
            f"osascript -e 'display dialog \"{message}\" with title \"{title}\" buttons {{\"I drank water\", \"Snooze\", \"Exit\"}} default button 1 "
            f"with icon POSIX file \"{self.config.paths['IMAGE_PATH']}\"'")
        

        response = os.system(osascript_cmd)
        return response

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterIntakeApp(root)
    root.after(0, app.update_countdown)
    root.mainloop()