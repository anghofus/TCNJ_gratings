import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os


class DoeGeneration:
    def __init__(self):
        self.file_path = get_file_path()
        self.output_path = os.path.join(os.getcwd(), "output")

        self.image_size = (1152, 1920)

        self.image = Image.open(self.file_path)

    def

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
    return str(file_path)
