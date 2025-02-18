import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_name = filedialog.askopenfilenames()

print(type(file_name))