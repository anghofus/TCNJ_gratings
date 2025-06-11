# Performs the inverse FFT on an image and displays the resulting phase and amplitude in the near field
# Cody Pedersen
# June 5th, 2025

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

############################### FUNCTIONS ###############################

def get_file_path():
    """
    Opens a file dialog for the user to select exactly one image file.
    Returns the file path to the selected image.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root tkinter window

    while True:
        # Open file dialog and wait for user to select a file
        file_path = filedialog.askopenfilenames(title="Select exactly 1 image")

        if file_path == ():  # User clicked cancel or closed the window
            raise KeyboardInterrupt
        elif len(file_path) != 1:  # Ensure only one file is selected
            messagebox.showerror("Error", "Select exactly 1 image")
            continue
        else:
            break  # Valid selection made

    return file_path[0]  # Return the path to the selected image


############################### PROGRAM ###############################

# Load and preprocess the image
image = Image.open(get_file_path()).convert("L")  # Convert image to grayscale ("L" = luminance)
image_array = np.asarray(image)                   # Convert image to a NumPy array for numerical operations

# Get image dimensions
height, width = image_array.shape

# Generate random far-field phase values between 0 and 2π
far_field_phase = np.random.rand(height, width) * 2 * np.pi

# Construct the far field as a complex-valued image:
# Real part: pixel intensity
# Imaginary part: encodes phase
far_field = image_array * np.exp(1j * far_field_phase)

# Display original image
Image.fromarray(image_array).show()

# Display the random far-field phase map (rescaled to 0–255)
Image.fromarray((((far_field_phase) / (2 * np.pi)) * 255).astype(np.uint8)).show()

# Compute the near field via inverse 2D FFT
near_field = np.fft.ifft2(far_field)

# Extract the phase and amplitude of the near field
near_field_phase = np.angle(near_field)        # Phase values in range [-π, π]
near_field_amplitude = np.abs(near_field)      # Amplitude values (real-valued)

# Normalize and scale the phase to [0, 255] for display
near_field_phase_normalized_scaled = (((near_field_phase + np.pi) / (2 * np.pi)) * 255).astype(np.uint8)
near_field_phase_map = Image.fromarray(near_field_phase_normalized_scaled)
near_field_phase_map.show()

# Normalize and scale the amplitude to [0, 255] for display
near_field_amplitude_normalized_scaled = ((near_field_amplitude / np.max(near_field_amplitude)) * 255).astype(np.uint8)
near_field_amplitude_map = Image.fromarray(near_field_amplitude_normalized_scaled)
near_field_amplitude_map.show()