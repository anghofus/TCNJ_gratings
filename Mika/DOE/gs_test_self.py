import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np


def get_file_path():
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilenames(title="Select exactly 1 images")

        if file_path == ():
            raise KeyboardInterrupt
        elif len(file_path) != 1:
            messagebox.showerror("Error", "Select exactly 1 images")
            continue
        else:
            break
    return file_path[0]

def gs(img, max_iter):
    height, width = img.shape
    far_field_phase = np.zeros((height, width))
    far_field = img * np.exp(1j * far_field_phase)

    for i in range(max_iter):
        near_field = np.fft.ifft2(far_field)
        near_field_phase = np.angle(near_field)
        new_near_field = np.ones((height, width)) * np.exp(1j * near_field_phase)
        far_field = np.fft.fft2(new_near_field)
        far_field_phase = np.angle(far_field)
        far_field = img * np.exp(1j * far_field_phase)

        print(f"Iteration {i}")

    return new_near_field

image = Image.open(get_file_path()).convert("L")
image_array = np.asarray(image)

complex_near_field_array = gs(image_array, 1000)
phase = np.angle(complex_near_field_array)
phase_normalized_scaled = (((phase + np.pi) / (2 * np.pi))*255).astype(np.uint8)

phase_map = Image.fromarray(phase_normalized_scaled)
phase_map.show()
phase_map.save("phase.png")

reconstructed = np.fft.fft2(phase)
reconstructed_intensity = np.abs(reconstructed)
Image.fromarray((reconstructed_intensity / np.max(reconstructed_intensity) * 255).astype(np.uint8)).show()
