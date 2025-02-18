import matplotlib.pyplot as plt
import csv
import numpy as np
import scipy.optimize as opt

# Initialize empty lists
radius, period_x, depth_x, period_y, depth_y = [], [], [], [], []

def fit_func(x, a, b):
    return a/x+b

# Read the data from the CSV file
with open('data.csv') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        radius.append(float(row[0])/1000)
        period_x.append(float(row[1]))
        depth_x.append(float(row[2]))
        period_y.append(float(row[3]))
        depth_y.append(float(row[4]))

# Convert lists to numpy arrays
radius = np.array(radius)
period_x = np.array(period_x)
depth_x = np.array(depth_x)
period_y = np.array(period_y)
depth_y = np.array(depth_y)

constants = opt.curve_fit(fit_func, radius, period_x)
a, b = constants[0]

# Calculate the fitted values
fit = fit_func(radius, a, b)


# Create a figure and axis
fig, ax1 = plt.subplots(figsize=(10, 6))  # Set figure size here

# Plot the first dataset (period vs. radius) on the left y-axis
ax1.plot(radius, period_x, 'b.', label='Period')
ax1.plot(radius, fit, 'g-', label=f'fit: a/x+b,\n a= {a:.2f}, b= {b:.2f}')
ax1.set_xlabel("Radius (mm)")
ax1.set_ylabel("Period (µm)", color="b")
ax1.tick_params(axis='y', labelcolor="b")

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()
ax2.plot(radius, depth_x, 'r.', label='Depth')  # Changed to plot against radius
ax2.set_ylabel("Depth (nm)", color="r")
ax2.tick_params(axis='y', labelcolor="r")

# Add a title, legend, and grid
plt.title("AFM measurement - X axis")
fig.tight_layout()  # Adjust layout to prevent overlap
ax1.grid(True)

# Save the figure
plt.savefig("afm_ssp_x-axis.png")

# Show the plot
plt.show()
