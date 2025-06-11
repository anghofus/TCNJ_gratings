# Takes an image and calculates the phase map using the Gerchberg–Saxton (GS) algorithm.
# Then divides the phase map into an SLM-compatible 4x2 grid of exposures.
# Cody Pedersen
# June 5th, 2025

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

############################### FUNCTIONS ###############################

def get_file_path():
    """
    Opens a file dialog to let the user select exactly one image file.
    Returns the path to the selected file.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the tkinter GUI window

    while True:
        file_path = filedialog.askopenfilenames(title="Select exactly 1 image")
        if file_path == ():  # If user cancels or closes the window
            raise KeyboardInterrupt
        elif len(file_path) != 1:  # Must select exactly one file
            messagebox.showerror("Error", "Select exactly 1 image")
            continue
        else:
            break

    return file_path[0]

def gs(img, max_iter):
    """
    Applies the Gerchberg–Saxton algorithm to compute the phase map needed
    to reconstruct the input intensity image in the far field.

    Args:
        img: 2D NumPy array representing the grayscale target image
        max_iter: number of iterations to run the GS algorithm

    Returns:
        A complex-valued 2D array representing the final near-field distribution
    """
    height, width = img.shape

    # Initialize far field with image amplitude and zero phase
    far_field_phase = np.zeros((height, width))
    far_field = img * np.exp(1j * far_field_phase)

    for i in range(max_iter):
        near_field = np.fft.ifft2(far_field)               # Transform to near field
        near_field_phase = np.angle(near_field)            # Get phase of near field
        new_near_field = np.exp(1j * near_field_phase)     # Force amplitude = 1, keep phase
        far_field = np.fft.fft2(new_near_field)            # Transform back to far field
        far_field_phase = np.angle(far_field)              # Get new far-field phase
        far_field = img * np.exp(1j * far_field_phase)     # Enforce target image amplitude

        print(f"Iteration {i}")

    return new_near_field  # Final near-field result (amplitude = 1, correct phase)

############################### PROGRAM ###############################

# Load and convert image to grayscale array
image = Image.open(get_file_path()).convert("L")
image_array = np.asarray(image)

# Run GS algorithm for 1000 iterations to compute near-field phase
complex_near_field_array = gs(image_array, 1000)

# Extract phase from the complex-valued near field and scale to 0–255
phase = np.angle(complex_near_field_array)
phase_normalized_scaled = (((phase + np.pi) / (2 * np.pi)) * 255).astype(np.uint8)

# Display and save the full phase map
phase_map = Image.fromarray(phase_normalized_scaled)
phase_map.show()
phase_map.save("phase.png")

# (Optional) Visualize the reconstructed far-field intensity from the final phase
reconstructed = np.fft.fft2(phase)  # Re-apply FFT to visualize far-field pattern
reconstructed_intensity = np.abs(reconstructed)
Image.fromarray((reconstructed_intensity / np.max(reconstructed_intensity) * 255).astype(np.uint8)).show()

############################### SLM TILING ###############################

# Determine tile size for 4x2 grid
tile_height = phase_normalized_scaled.shape[0] // 4
tile_width = phase_normalized_scaled.shape[1] // 2

# Loop through 4 rows and 2 columns to create 8 tiles
for i in range(4):  # Row index
    for j in range(2):  # Column index
        # Extract tile from the full phase map
        tile_array = phase_normalized_scaled[
            i * tile_height : (i + 1) * tile_height,
            j * tile_width  : (j + 1) * tile_width
        ]
        tile_image = Image.fromarray(tile_array)
        tile_image = tile_image.resize((1920, 1152))  # Resize to match SLM resolution

        # Determine label (row and column) with zigzag raster pattern
        row = 3 - i  # Flip vertically: row 0 = bottom, row 3 = top
        if i % 2 == 0:
            col = j        # Even rows: left to right
        else:
            col = 1 - j    # Odd rows: right to left

        # Save tile image with proper label
        tile_image.save(f"tile_{row}_{col}.png")