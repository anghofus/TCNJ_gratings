#divides an image into a 4x2 grid of tiles
#Cody Pedersen
#June 5th, 2025

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np


def get_file_path(): #function that opens a file dialog and lets you select an image
    root = tk.Tk()
    root.withdraw()

    while True:    #file path comes from tkinter library (library to do user interface stuff)
        file_path = filedialog.askopenfilenames(title="Select exactly 1 images")

        if file_path == ():  #this if just checks if its the correct length, if an empty string is returned, this means the user hasn't selected
            raise KeyboardInterrupt
        elif len(file_path) != 1:   #makes sure the user only selected one image
            messagebox.showerror("Error", "Select exactly 1 images")  #if you selected too many images, he will give error message
            continue
        else:         #passes all the checks
            break      #terminates loop
    return file_path[0]  #returns a string with the file path to the image you selected

image = Image.open(get_file_path()).convert("L")  #makes user choose image
image_array = np.asarray(image)                   #converts image object into an array

tile_height = image_array.shape[0]//4
tile_width = image_array.shape[1]//2

for i in range(4):                     #i keeps track of row
    for j in range(2):                 #j iterates through columns
        tile_array = image_array[i*tile_height:(i+1)*tile_height, j*tile_width:(j+1)*tile_width]
        tile_image = Image.fromarray(tile_array) #turns the numpy array into an image
        tile_image = tile_image.resize((1920, 1152))

        row = 3 - i #makes us start labelling at the bottom row
        if i % 2 == 0: #if we are in a even row, we want to label left to right
            col = j
        else:          #if in odd index row, label right to left
            col = 1 - j
        tile_image.save(f"tile_{row}_{col}.png")     #saves the image

