import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

# Load the data
date_counts = defaultdict(int)

with open('water_intake_log.txt', 'r') as file:
    for line in file.readlines():
        timestamp_str = line.split('- Drank water')[0].strip()
        date_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        date_only_str = date_obj.strftime('%Y-%m-%d')
        date_counts[date_only_str] += 1

dates = list(date_counts.keys())
intakes = list(date_counts.values())

# Plotting the data
plt.bar(dates, intakes, color='blue')

# Adding title and labels
plt.title("Water Intake per Day")
plt.xlabel("Date")
plt.ylabel("Times Drank Water")
plt.xticks(rotation=45)  # Rotate date labels for better visibility

# Display the graph
plt.tight_layout()
plt.show()
