import os
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

path = get_file_path()

image = Image.open(path).convert('L')

image_array = np.asarray(image)

ifft = np.fft.irfft2(image_array)
ifft_shifted_normalized = ifft/ np.max(ifft) * 255

final_image = Image.fromarray(ifft_shifted_normalized).convert('L')
final_image.save("Test.jpg")
