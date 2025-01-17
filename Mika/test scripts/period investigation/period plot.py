import matplotlib.pyplot as plt
import csv
import numpy as np
import scipy.optimize as opt

# Initialize empty lists
radius, period_x, depth_x, period_y, depth_y = [], [], [], [], []

def fit_func(x, a, b):
    return a/x+b

def theoretical_period(r):
    return (0.635*1000)/(r*1000)

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

constants = opt.curve_fit(fit_func, radius, period_y)
a, b = constants[0]

# Calculate the fitted values
fit = fit_func(radius, a, b)
theoretical = theoretical_period(radius)



# Create a figure and axis
fig, ax1 = plt.subplots(figsize=(10, 6))  # Set figure size here

# Plot the first dataset (period vs. radius) on the left y-axis
ax1.plot(radius, fit, 'b-', label=f'fit of data')
ax1.set_xlabel("Radius (mm)")
ax1.set_ylabel("Period (µm)", color="b")
ax1.tick_params(axis='y', labelcolor="b")

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()
ax2.plot(radius, theoretical, 'r.', label='theory')
ax2.set_ylabel("Period (µm)", color="r")
ax2.tick_params(axis='y', labelcolor="r")

# Add a title, legend, and grid
plt.title("Measured Period vs. theoretical period")
fig.tight_layout()  # Adjust layout to prevent overlap
ax1.grid(True)
fig.legend()
# Save the figure
plt.savefig("period_test.png")

# Show the plot
plt.show()
