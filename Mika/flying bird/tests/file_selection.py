import tkinter as tk
from tkinter import filedialog, messagebox


def select_images():
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilenames(title="Select exactly 6 images")

        if file_path == ():
            raise KeyboardInterrupt
        elif len(file_path) != 6:
            messagebox.showerror("Error", "Select exactly 6 images")
            continue
        else:
            break
    return file_path


path_image1, path_image2, path_image3, path_image4, path_image5, path_image6 = select_images()

print(path_image1)
print(path_image2)
print(path_image3)
print(path_image4)
print(path_image5)
print(path_image6)