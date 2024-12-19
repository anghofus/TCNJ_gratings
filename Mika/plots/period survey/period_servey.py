import matplotlib.pyplot as plt
import csv
import numpy as np

# Initialize empty lists
radius, period, depth = [], [], []

# Read the data from the CSV file
with open('data.csv') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        radius.append(float(row[0]))
        period.append(float(row[1]))
        depth.append(float(row[2]))

# Convert lists to numpy arrays
radius = np.array(radius)
period = np.array(period)
depth = np.array(depth)

# Create a figure and axis
fig, ax1 = plt.subplots(figsize=(10, 6))  # Set figure size here

# Plot the first dataset (period vs. radius) on the left y-axis
ax1.plot(radius, period, 'b.', label='Period')
ax1.set_xlabel("Radius (mm)")
ax1.set_ylabel("Period (µm)", color="b")
ax1.tick_params(axis='y', labelcolor="b")

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()
ax2.plot(radius, depth, 'r.', label='Depth')  # Changed to plot against radius
ax2.set_ylabel("Depth (nm)", color="r")
ax2.tick_params(axis='y', labelcolor="r")

# Add a title, legend, and grid
plt.title("Period Survey")
fig.tight_layout()  # Adjust layout to prevent overlap
ax1.grid(True)

# Save the figure
plt.savefig("period_survey.png")

# Show the plot
plt.show()
