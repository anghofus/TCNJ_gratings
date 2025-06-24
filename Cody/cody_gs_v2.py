import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

def get_file_path():
    """
    Opens a file dialog to select a single image file.
    Returns the file path as a string.
    """
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilenames(title="Select exactly 1 image")
        if file_path == ():
            raise KeyboardInterrupt  # User canceled
        elif len(file_path) != 1:
            messagebox.showerror("Error", "Select exactly 1 image")
        else:
            return file_path[0]


def gs(img, max_iter):
    """
    Performs the Gerchberg-Saxton algorithm.
    Args:
        img: 2D numpy array (grayscale image as amplitude constraint)
        max_iter: number of iterations
    Returns:
        2D complex numpy array representing the final near-field result
    """
    amp = img / 255
    height, width = img.shape
    far_field_phase = np.zeros((height, width)) #np.random.rand(height, width) * 2 * np.pi #starts with random phase
    far_field = amp * np.exp(1j * far_field_phase)

    for i in range(max_iter):
        near_field = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(far_field)))
        near_field_phase = np.angle(near_field)
        new_near_field = 1 * np.exp(1j * near_field_phase)
        far_field = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(new_near_field)))
        far_field_phase = np.angle(far_field)
        far_field = amp * np.exp(1j * far_field_phase)

        print(f"Iteration {i}")

    return new_near_field


# --- Main Execution ---

# Load grayscale image
image = Image.open(get_file_path()).convert("L")
image_array = np.asarray(image)

# Run Gerchberg-Saxton algorithm
complex_near_field_array = gs(image_array, 100)

# Extract and normalize the phase to 0–255 for visualization
#direct mapping
phase = np.angle(complex_near_field_array)
phase_normalized_scaled = (((phase + np.pi) / (2 * np.pi)) * 128).astype(np.uint8) #trying mapping directly to 128

# Save and display the phase map
phase_map = Image.fromarray(phase_normalized_scaled)
phase_map.show()
phase_map.save("phase.png")

# Reconstruct far-field intensity for verification
reconstructed_field = np.exp(1j * phase)  # reconstruct complex field from phase
far_field = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(reconstructed_field)))  # proper FFT with shifts
intensity = np.abs(far_field) ** 2
normalized_intensity = (intensity / np.max(intensity) * 255).astype(np.uint8)
Image.fromarray(normalized_intensity).show()

