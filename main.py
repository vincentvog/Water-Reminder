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
            "IMAGE_PATH": os.path.join(self.script_dir, "images", "water_glass.png"),}
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
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab4 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text="Home")
        self.tab_control.add(self.tab2, text="Graph")
        self.tab_control.add(self.tab3, text="Logs")
        self.tab_control.add(self.tab4, text="About")
        self.tab_control.pack()

        content_frame = tk.Frame(self.tab1, borderwidth=2, relief=tk.SOLID, highlightthickness=0)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        tk.Label(content_frame, text="Did you drink water?", pady=0).pack(pady=(50, 0))
        tk.Button(content_frame, text="I drank water", command=self.log_water_intake).pack(pady=(0, 0))

        self.countdown_label = tk.Label(content_frame, text="")
        self.countdown_label.pack(pady=(20, 0))

        reminder_entry_frame = tk.Frame(content_frame)
        reminder_entry_frame.pack(pady=(20, 0))

        tk.Label(reminder_entry_frame, text="Type below to adjust reminder period (minutes):").pack()
        self.reminder_entry = tk.Entry(reminder_entry_frame)
        self.reminder_entry.pack(side=tk.LEFT)

        self.reminder_button = tk.Button(reminder_entry_frame, text="Set Reminder", command=self.set_reminder_period)
        self.reminder_button.pack(side=tk.LEFT)

        graph_frame = tk.Frame(self.tab2)
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.figure = plt.Figure(figsize=(7, 4), dpi=100)
        self.graph = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.graph_widget = self.graph.get_tk_widget()
        self.graph_widget.pack(fill=tk.BOTH, expand=True)

        self.log_tree = ttk.Treeview(self.tab3, columns=("Date", "Time", "Action"), show="headings")
        self.log_tree.heading("Date", text="Date")
        self.log_tree.heading("Time", text="Time")
        self.log_tree.heading("Action", text="Action")

        self.log_tree.column("Date", anchor="center")
        self.log_tree.column("Time", anchor="center")
        self.log_tree.column("Action", anchor="center")

        self.log_tree.pack(fill=tk.BOTH, expand=True)

        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

        about_text_widget = tk.Text(self.tab4, wrap=tk.WORD, width=40, height=10)
        about_text_widget.insert(tk.END, "Stay hydrated throughout the day with this simple water reminder script. "
                                          "This script sends notifications to remind you to drink water at regular intervals.\n\n")
        about_text_widget.tag_configure("bold", font=("Helvetica", 12, "bold"))

        about_text_widget.insert(tk.END, "Features\n", "bold")
        about_text_widget.insert(tk.END, "- Regular Notifications: Sends a reminder every 30 minutes.\n"
                                          "- Intuitive Responses: Log your water intake with a simple button click.\n"
                                          "- History Tracking: Keeps a log of your water intake timestamps.\n\n")

        about_text_widget.insert(tk.END, "Developed by:\n", "bold")
        about_text_widget.insert(tk.END, "- Mihnea Andrei Radulescu\n- Vincent Francis Vogelesang\n\n")

        about_text_widget.insert(tk.END, "Year:\n", "bold")
        about_text_widget.insert(tk.END, "- 2023\n")

        about_text_widget.config(state=tk.DISABLED)
        about_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_tab_change(self, event):
        selected_tab = event.widget.tab(event.widget.select(), "text")

        if selected_tab == "Graph" or selected_tab == "Logs":
            tab_content_width = self.tab_control.winfo_reqwidth()
            tab_content_height = self.tab_control.winfo_reqheight()

            # Calculate centered position for the larger window
            x_centered = (screenwidth - tab_content_width) // 2
            y_centered = (screenheight - tab_content_height) // 2

            if selected_tab == "Logs":
                self.load_logs()
                self.root.geometry(f"{window_width + 300}x{window_height + 100}+{x_centered}+{y_centered}")
            else:
                self.root.geometry(f"{window_width + 300}x{window_height + 100}+{x_centered}+{y_centered}")
        else:
            self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

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

    def load_logs(self):
        self.log_tree.delete(*self.log_tree.get_children())
        
        try:
            with open(self.config.paths["LOG_FILE"], "r") as log_file:
                log_entries = []
                for line in log_file:
                    parts = line.strip().split(" - ")
                    if len(parts) == 2 and parts[1] == "Drank water":
                        try:
                            datetime_obj = datetime.datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S.%f')
                            date = datetime_obj.strftime('%Y-%m-%d')
                            time = datetime_obj.strftime('%H:%M:%S')
                            action = "Drank water"
                            log_entries.append((date, time, action))
                        except ValueError:
                            pass

                for entry in log_entries:
                    self.log_tree.insert("", "end", values=entry)

                column_widths = {"Date": 100, "Time": 80, "Action": 150}
                for column, width in column_widths.items():
                    self.log_tree.column(column, width=width)
                    self.log_tree.heading(column, text=column, command=lambda c=column: self.sort_logs(c))
        except FileNotFoundError:
            pass

    def update_countdown(self):
        current_time = datetime.datetime.now()

        if self.last_log_time:
            time_since_last_log = current_time - self.last_log_time
            if time_since_last_log.total_seconds() >= self.config.REMINDER_INTERVAL * 60 and not self.notification_running:
                countdown_text = "Time to drink water!"
                response = self.send_notification("Water Reminder", "Did you drink water?")
                if response == 0:
                    self.notification_running = False
                    self.log_water_intake()
                elif response == 1:
                    self.notification_running = True
                elif response == 2:
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
    
    def set_reminder_period(self):
        try:
            new_period = int(self.reminder_entry.get())
            if new_period <= 0:
                raise ValueError("Reminder period must be a positive integer")
            self.config.REMINDER_INTERVAL = new_period
            self.update_countdown()
            self.reminder_entry.delete(0, tk.END)
            self.reminder_entry.insert(0, str(new_period))
        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Water Intake Tracker")
    
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    window_width, window_height = 450, 350
    x_coordinate = (screenwidth - window_width) // 2
    y_coordinate = (screenheight - window_height) // 2
    
    root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
    
    app = WaterIntakeApp(root)
    root.after(0, app.update_countdown)
    root.mainloop()
