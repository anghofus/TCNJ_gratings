# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 19:01:36 2024

@author: Julian Honecker
"""
import serial
import time
import csv
import glob
import os
import threading
import numpy as np
from scipy import signal
from natsort import natsorted
from PIL import Image, ImageTk
from screeninfo import get_monitors
from tkinter import Toplevel, Label, Tk, filedialog, Button, Frame, Scale, Entry, messagebox, END
from SerialMotorControl_Active import MotorController


class Shutter:
    def __init__(self, port, baudrate=9600, timeout=.1, stopbits=1, bytesize=8):
        self.serial_shutter = serial.Serial()
        self.serial_shutter.port = port
        self.serial_shutter.baudrate = baudrate
        self.serial_shutter.timeout = timeout
        self.serial_shutter.stopbits = stopbits
        self.serial_shutter.bytesize = bytesize

    def write_command(self, command, close_after=False):
        """
        Send any command to a serial port.
        (arg1) self
        (arg2) command: the command to send to the motor (string)
        (arg3) close_after: close port after command, if true (boolean)
        """
        cmd = command + '\r' if not command.endswith('\r') else command
        # cmd = command
        # if cmd.find('\r') == -1:
        # cmd = cmd + '\r'
        try:
            if not self.serial_shutter.is_open:
                self.serial_shutter.open()
            self.serial_shutter.write(cmd.encode())
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
        finally:
            if close_after:
                self.serial_shutter.close()

    def read_response_until_prompt(self, prompt='>', timeout=2):
        end_time = time.time() + timeout
        received_data = ''
        while time.time() < end_time:
            if self.serial_shutter.in_waiting:
                char = self.serial_shutter.read(1).decode(errors='replace')  # Use 'replace' to handle unexpected characters gracefully
                received_data += char
                if prompt in received_data:
                    break
        return received_data
    
    def read_response(self):
        if not self.serial_shutter.is_open:
            self.serial_shutter.open()
        # Wait for device to be ready
        time.sleep(0.1)

        # Flush any previously buffered data
        self.serial_shutter.reset_input_buffer()

        # Send command
        self.serial_shutter.write(b'ens?\r')
        time.sleep(0.1)  # Adjust based on device response time

        # Read and process the response
        response = self.read_response_until_prompt()
        # Sanitize the response for safe printing
        safe_response = response.replace('\r', '\\r').replace('\n', '\\n')
        print(f"Received: {safe_response}")  # Print sanitized response exactly as desired

        # Optionally, interpret and print shutter status in human-readable form
        if '\\r1\\r' in safe_response:
            print("Shutter status: Enabled")
            return 1
        elif '\\r0\\r' in safe_response:
            print("Shutter status: Disabled")
            return 0
        else:
            print("Unexpected response format.")
            return None

    def toggle_pause(self, pause):
        """
        Opens the shutter. Pauses for a certain amount of time. Closes the shutter.
        (arg1) pause : number of seconds to pause (float)
        """
        self.write_command('ens')
        time.sleep(pause)
        self.write_command('ens')

    def toggle(self):
        self.write_command('ens')

    # Open when closed
    def startup(self):
        self.write_command('ens?', close_after=False)
        response = self.read_response()
        if response == 0:  # Indicates the shutter is closed/disabled
            print("Shutter is closed. Opening shutter...")
            self.write_command('ens')  # Send command to open/enable the shutter
        elif response == 1:
            print("Shutter is already open.")
        else:
            print("Failed to read shutter state. Check connection.")
            
    # Close when open
    def shutdown(self):
        self.write_command('ens?', close_after=False)
        response = self.read_response()
        if response == 1:  # Indicates the shutter is closed/disabled
            print("Shutter is opened. Closing shutter...")
            self.write_command('ens')  # Send command to open/enable the shutter
        elif response == 0:
            print("Shutter is already closed.")
        else:
            print("Failed to read shutter state. Check connection.")

    def close_connection(self):
        try:
            if self.serial_shutter.is_open:
                self.serial_shutter.close()
        except serial.SerialException as e:
            print(f"Error closing serial port: {e}")


class SLMWindow:
    def __init__(self, master, grating=None):
        # Monitor controlling
        active_monitors = get_monitors()

        # Assuming the second monitor is the SLM monitor
        # slm_monitor = active_monitors[1]
        begin_slm_horizontal = active_monitors[1].x
        begin_slm_vertical = active_monitors[1].y
        width = 1920
        height = 1152

        # Create a window on the SLM monitor
        self.image_window = master
        self.window_slm = Toplevel(self.image_window)
        self.window_slm.geometry(f'{width}x{height}+{begin_slm_horizontal}+{begin_slm_vertical}')
        # self.window_slm.geometry(f'{slm_monitor.width}x{slm_monitor.height}+{slm_monitor.x}+{slm_monitor.y}')
        self.window_slm.overrideredirect(True)

        # Default grating if none provided
        if grating is None:
            array = np.zeros((height, width), dtype=np.uint16)
            default_image = Image.fromarray(array)
            default_image = default_image.convert('L')
            grating = ImageTk.PhotoImage(default_image)
        elif not isinstance(grating, ImageTk.PhotoImage):
            grating = ImageTk.PhotoImage(Image.open(grating))

        # Load the image into the SLM monitor window
        self.window_slm_label = Label(self.window_slm, image=grating)
        self.window_slm_label.pack(fill="both", expand=True)
        self.window_slm_label.image = grating  # Keep a reference!

        # Bind escape key to close window
        self.window_slm.bind("<Escape>", lambda e: self.close_window())

    def display(self, grating_path):
        # Ensure updates happen in the main thread
        self.image_window.after(0, self._update_image, grating_path)

    def _update_image(self, grating_path):
        # Load and display the new image, maintaining a reference to avoid garbage collection
        try:
            grating = ImageTk.PhotoImage(Image.open(grating_path))
            self.window_slm_label.configure(image=grating)
            self.window_slm_label.image = grating  # Keep a reference!
        except Exception as e:
            print(f"Error loading image {grating_path}: {e}")
            # Optionally, display an error message on the SLM window

    def display_text(self, msg):
        # Schedule the text update to be safe with threads
        self.image_window.after(0, lambda: self.window_slm_label.config(text=msg))

    def close_window(self):
        # Ensure the window is closed in the main thread
        self.image_window.after(0, lambda: self.window_slm.destroy())


class PrintingPicture:
    def __init__(self, filepath=None, slm=None):
        self.color = None
        self.x_max = 1  # Default Xmax value
        self.filepath = filepath
        self.slm = slm
        self.rgb = [0, 0, 0]

    def save_color_and_x_max(self, new_color, x_max):
        self.color = new_color
        self.x_max = x_max

        print(f"ColorStorage saved Xmax: {self.x_max}")
        print(f"ColorStorage saved color: {self.color}")
        self.rgb = self.hex_to_rgb(self.color)
        print(f"ColorStorage saved color: {self.rgb}")
        image = self.make_SLM_pattern(*self.rgb, self.x_max)
        # image.save("C:/Users/mcgeelab/Desktop/PrintingImages/Image1.png")
        if self.filepath:  # Check if filepath is set
            image_path = os.path.join(self.filepath, "Image1.png")
            image.save(image_path)
            print(f"Image saved at {image_path}")
            # Display the image using slm, if available
            if self.slm:
                self.slm.display(image_path)
            else:
                print("SLM instance not available for displaying the image.")
        else:
            print("Filepath not set. Image not saved.")

    def hex_to_rgb(self, hex_color):
        # Assuming hex_color is a string like "#FFFFFF"
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def make_SLM_pattern(self, red, green, blue, x_max):
        t = np.linspace(0, 1920, 1920)

        # Variable X_max
        # f1 = 1 / 30  # blue
        f1 = 1 / (x_max * 1)
        # f2 = 1 / 32.7  # green
        f2 = 1 / (x_max * 1.09)
        # f3 = 1 / 38.91  # red
        f3 = 1 / (x_max * 1.297)
        # Ymax = 128, Ymin = 0
        # st = np.clip((1 + signal.sawtooth(2 * np.pi * f1 * t)) * 128, 0, 255)
        st = (1 + signal.sawtooth(2 * np.pi * f1 * t)) * 64
        st1 = (1 + signal.sawtooth(2 * np.pi * f2 * t)) * 64
        st2 = (1 + signal.sawtooth(2 * np.pi * f3 * t)) * 64

        array = np.zeros((1152, 1920))
        i = 0
        j = 0
        
        total = red + green + blue
        
        if x_max == 1 or total == 0:
            # Create a black array and return as an image
            array = np.zeros((1152, 1920), dtype=np.uint8)  # A black image
            return Image.fromarray(array).convert("RGB")
        
        # Normalize RGB values to be proportional to the lengths for each color region
        regionblue = 1920 * (blue / total)
        regiongreen = 1920 * (green / total)
        regionred = 1920 * (red / total)

        while i < regionblue:
            array[0][i] = (st[i])
            i = i + 1

        while i < regionblue + regiongreen - 1:
            array[0][i] = (st1[i])
            i = i + 1

        while i < 1920:
            array[0][i] = (st2[i])
            i = i + 1

        while j < 1152:
            array[j] = array[0]
            j = j + 1

        # array = np.clip(array, 0, 255)  # Ensure values are within [0, 255]
        # array = array.astype(np.uint8)  # Convert to uint8 type for image generation
        # data = Image.fromarray(array)
        # image = data.convert("RGB")
        data = Image.fromarray(array)
        image = data.convert("RGB")
        return image


class ColorPicker:
    def __init__(self, on_color_save=None):
        self.on_color_save = on_color_save
        self.selected_color = "#FFFFFF"  # Default color
        self.x_max = 1  # Default value for Xmax
        self.customFont = ("Helvetica", 16)

    def open_color_picker(self):
        self.popup = Toplevel()
        self.popup.grab_set()
        self.popup.title("RGB Color Picker")

        # Initialize all GUI components here, similar to your original function but using instance attributes
        self.red_scale = self.create_scale(self.popup, 0, 'Red')
        self.green_scale = self.create_scale(self.popup, 1, 'Green')
        self.blue_scale = self.create_scale(self.popup, 2, 'Blue')
        self.brightness_scale = self.create_scale(self.popup, 3, 'Brightness', from_=1, to_=100, resolution_=1)
        self.brightness_scale.set(100)  # Set default brightness to 100%
        # Make sure to pass a specific command for the Xmax scale during its creation
        self.xmax_scale = self.create_scale(self.popup, 4, 'Xmax', from_=1, to_=255, resolution_=1,
                                            command=self.update_xmax_from_slider)
        self.xmax_scale.set(1)  # Default value for Xmax

        # Entry fields
        self.red_entry = self.create_entry(self.popup, 0)
        self.green_entry = self.create_entry(self.popup, 1)
        self.blue_entry = self.create_entry(self.popup, 2)
        self.brightness_entry = self.create_entry(self.popup, 3, default_value="100")
        self.hex_entry = self.create_entry(self.popup, 4, span=2)
        # Xmax entry setup with direct validation binding
        self.xmax_entry = self.create_entry(self.popup, 4, default_value="1")
        self.xmax_entry.bind("<KeyRelease>", self.validate_xmax_entry)

        # Color preview label
        self.color_preview = Label(self.popup, bg='black', width=20, height=14)
        self.color_preview.grid(row=0, column=2, rowspan=5, padx=20, pady=20)

        # Save color button
        Button(self.popup, text="Save Color", font=self.customFont, command=self.save_selected_color).grid(row=5, column=2)

        self.popup.wait_window()  # This halts execution of the calling function until the popup is closed.

    def create_scale(self, popup, row, label, from_=0, to_=255, resolution_=1, command=None):
        if command is None:
            command = self.update_preview_from_sliders
        scale = Scale(popup, from_=from_, to_=to_, orient='horizontal', label=label, resolution=resolution_,
                      command=command, length=300, width=20, sliderlength=30, font=self.customFont)
        scale.grid(row=row, column=0)
        return scale

    def create_entry(self, popup, row, span=1, default_value=""):
        entry = Entry(popup, width=7, font=self.customFont)
        entry.grid(row=row, column=1, columnspan=span)
        if default_value:
            entry.insert(0, default_value)
        entry.bind("<KeyRelease>", self.update_preview_from_entries)

        return entry

    def update_xmax_from_slider(self, value):
        # This method is bound to the Xmax scale (slider)
        self.xmax_entry.delete(0, END)
        self.xmax_entry.insert(0, value)  # Slider directly updates the entry

    def validate_xmax_entry(self, event=None):
        # Validate and correct the entry, then update the slider
        content = self.xmax_entry.get()
        if not content.isdigit() or not content:
            corrected_value = "1"
        else:
            corrected_value = min(255, max(1, int(content)))

        # If correction is needed, update the entry
        if str(corrected_value) != content:
            self.xmax_entry.delete(0, END)
            self.xmax_entry.insert(0, str(corrected_value))

        self.x_max = corrected_value
        self.xmax_scale.set(corrected_value)  # Ensure slider is in sync

    # Function to update color preview from slider values
    def update_preview_from_sliders(self, event=None):
        r, g, b = self.red_scale.get(), self.green_scale.get(), self.blue_scale.get()
        brightness = self.brightness_scale.get() / 100.0
        self.update_entries_and_preview(r, g, b, brightness)

    # Function to update entries and color preview based on current values
    def update_entries_and_preview(self, r, g, b, brightness):
        # Adjust for brightness and update the HEX color
        rb, gb, bb = [int(color * brightness) for color in (r, g, b)]
        hex_color = f'#{rb:02x}{gb:02x}{bb:02x}'

        # Update entries
        for entry, value in zip((self.red_entry, self.green_entry, self.blue_entry, self.brightness_entry),
                                (r, g, b, self.brightness_scale.get())):
            entry.delete(0, END)
            entry.insert(0, str(value))

        # Update HEX entry and color preview
        self.hex_entry.delete(0, END)
        self.hex_entry.insert(0, hex_color)
        self.color_preview.config(bg=hex_color)

    def update_preview_from_entries(self, event):
        # This function is triggered when the RGB or brightness entry fields are manually updated
        try:
            r = min(255, int(self.red_entry.get()) if self.red_entry.get() else 0)
            g = min(255, int(self.green_entry.get()) if self.green_entry.get() else 0)
            b = min(255, int(self.blue_entry.get()) if self.blue_entry.get() else 0)
            brightness = min(100, int(self.brightness_entry.get()) if self.brightness_entry.get() else 100)

            # Directly set the values back into the entries to correct over-the-limit inputs
            self.red_entry.delete(0, END)
            self.red_entry.insert(0, str(r))
            self.green_entry.delete(0, END)
            self.green_entry.insert(0, str(g))
            self.blue_entry.delete(0, END)
            self.blue_entry.insert(0, str(b))
            self.brightness_entry.delete(0, END)
            self.brightness_entry.insert(0, str(brightness))

            # Update the sliders according to the corrected values
            self.red_scale.set(r)
            self.green_scale.set(g)
            self.blue_scale.set(b)
            self.brightness_scale.set(brightness)

            # Calculate the adjusted RGB values based on brightness
            rb, gb, bb = [int(color * (brightness / 100.0)) for color in (r, g, b)]

            # Update HEX entry and color preview
            hex_color = f'#{rb:02x}{gb:02x}{bb:02x}'
            self.hex_entry.delete(0, END)
            self.hex_entry.insert(0, hex_color)
            self.color_preview.config(bg=hex_color)

        except ValueError:
            # If conversion to integer fails, it means the entry is not a valid number
            pass

    def save_selected_color(self):
        self.selected_color = self.hex_entry.get()
        # self.x_max = self.xmax_scale.get()  # Get the Xmax value
        self.x_max = int(self.xmax_entry.get())  # Ensure we use the entry's value
        messagebox.showinfo("Color Saved", f"Color {self.selected_color} has been saved.")
        if self.on_color_save:
            self.on_color_save(self.selected_color, self.x_max)
        self.popup.destroy()


# Image Processing and SLM Display Handling
class SLMManager:
    def __init__(self, motor_controller):
        # Initialize with path to images and settings
        self.configure_paths(initial_filepath='C:/Users/mcgeelab/Desktop/SLMImages/')
        self.printing_filepath = None
        self.status_label = None  # Placeholder for the status label
        self.motor_controller = motor_controller  # Initialize with a motor controller
        self.slm = None  # Initialized later when root is available
        # Maximum Exposure-Time can be set here
        self.max_exp_time = 4
        self.printing_speed = 40

        self.imagesSLM = []  # List of image paths
        self.added_RGB_values = []  # List of added RGB values for each image
        self.exp_times = []  # List of exposure times for each image

        self.positions_X = []
        self.positions_Z = []
        self.absolute_offset_X = 0
        self.absolute_offset_Z = 0
        self.rows = 0
        self.columns = 0
        self.start_pos_X = 0
        self.start_pos_Z = 0

        self.current_mode = None
        self.currentImage = 0  # Index of the currently displayed image

        self.printing_lines = 0  # Index for all lines that get printed
        self.printing_rows = 0
        self.currentLine = 0  # Index for the current line

        # Needed if Paused while Printing, for Stitching we usually close directly after open and then go into Pause
        self.shutter_opened = False  # Tracks the current state of the shutter
        self.PauseActive = False  # Tracks whether the system is currently paused
        self.ExitActive = False  # Tracks whether the system should be exited or not
        self.re_enable = False  # Indicates if the shutter needs to be reopened after a pause

        self.final_callback = None
        self.pause_function = None
        self.exit_function = None
        self.boundary_exit_function = None

    def reset_parameter(self):
        # Reset important lists
        self.imagesSLM = []
        self.added_RGB_values = []
        self.exp_times = []

        # Reset Position-Variables
        self.positions_X = []
        self.positions_Z = []
        self.absolute_offset_X = 0
        self.absolute_offset_Z = 0
        self.rows = 0
        self.columns = 0
        self.start_pos_X = 0
        self.start_pos_Z = 0

        # Reset Stitching Parameter
        self.current_mode = None
        self.currentImage = 0

        # Reset Printing Parameter
        self.printing_lines = 0
        self.printing_rows = 0
        self.currentLine = 0

        # Ensure Exit and Pause Parameter aare reset:
        self.shutter_opened = False
        self.PauseActive = False
        self.ExitActive = False
        self.re_enable = False

        # No old Callback-Functions
        self.final_callback = None
        self.pause_function = None
        self.exit_function = None
        self.boundary_exit_function = None

    def configure_paths(self, initial_filepath):
        self.added_RGB_values_filepath = os.path.join(initial_filepath, "added_RGB_values.csv")
        self.dataset_filepath = os.path.join(initial_filepath, "dataset.csv")

    def initialize_slm_window(self, root):
        # Ensures SLMWindow is initialized when root is ready
        if self.slm is None:
            self.slm = SLMWindow(root)

    def update_status(self, status):
        """Update the status label text."""
        if self.status_label:
            self.status_label.config(text=status)

    def reset_final_callback(self):
        """Resets the final callback to None safely."""
        self.final_callback = None

    def next_image(self):
        self.currentImage += 1
        image_path = self.imagesSLM[self.currentImage]  # Get the next image path
        self.slm.display(image_path)  # Display the next image using the SLMWindow instance
        print(f"Displaying image {self.currentImage+1} of {len(self.imagesSLM)}: {os.path.basename(image_path)}")

    def open_images(self, callback=None):
        # Logic to load and display images
        # Choose directory and get all PNG

        self.reset_parameter()

        self.filepath = filedialog.askdirectory()
        if not self.filepath:
            print("No directory selected.")
            self.update_status("No directory selected. Please try again.")
            return

        self.imagesSLM = natsorted(glob.glob(f"{self.filepath}/*.png"), key=lambda x: int(x.split("_")[1].split(".")[0]))
        self.configure_paths(initial_filepath=self.filepath)

        if not self.imagesSLM:
            print("No PNG files found in the specified directory.")
            self.update_status("No PNG files found. Please try again.")
            return
        print("PNG files in the specified directory found")

        if os.path.exists(self.dataset_filepath) & os.path.exists(self.added_RGB_values_filepath):

            # I want the Pop-Up Window right here and stop the code from continuing
            self.open_settings_stitch_popup()

            self.load_csv_data(path_to_csv=self.dataset_filepath)
            print("Exposure Times and Absolute Values loaded!")
        else:
            print("CSV file not found")
            self.slm_manager.update_status("CSV-file not found. Please try again.")
            return
        
        num_images = len(self.imagesSLM)
        # Display information about the loaded images and exposure times
        print(f"{num_images} images and exposure times loaded.")

        # Display the first image
        self.current_mode = None
        self.currentImage = 0
        self.update_status("Ready")
        self.slm.display(self.imagesSLM[self.currentImage])
        print(f"Displaying the first image: {os.path.basename(self.imagesSLM[self.currentImage])}")
        if callback:
            callback()

    # Revise stitching_logic
    def stitching_logic(self, mode=None, callback=None, pause_function=None, exit_function=None, boundary_exit_function=None):
        # Make sure callbacks are saved and stay even after schedule with after()
        if callback is not None:
            self.final_callback = callback
        if pause_function is not None:
            self.pause_function = pause_function
        if exit_function is not None:
            self.exit_function = exit_function
        if boundary_exit_function is not None:
            self.boundary_exit_function = boundary_exit_function

        # Check for Exit before
        if self.ExitActive:
            if self.exit_function is None:
                raise ValueError('exit_function is None and cannot be called.')
            else:
                try:
                    self.exit_function()
                except Exception as e:
                    raise ValueError(f'Error executing exit_function: {e}') from e
                finally:
                    return

        # Then check for Pause
        if self.PauseActive:
            if self.pause_function is None:
                raise ValueError('pause_function is None and cannot be called.')
            else:
                try:
                    self.pause_function()
                except Exception as e:  # Catching a general exception to avoid bare except
                    raise ValueError(f'Error executing pause_function: {e}') from e
                finally:
                    return

        # if none of the before, continue
        if self.currentImage <= len(self.imagesSLM):
            if self.currentImage == 0:
                self.current_mode = mode
            
            if self.currentImage < len(self.imagesSLM):
                self.update_status(f"Current Status: Busy with {self.current_mode} Stitching. Pixel {self.currentImage + 1} of {len(self.imagesSLM)}")
            elif self.currentImage == len(self.imagesSLM):
                self.update_status("Current Status: Resetting to Center after Stitching!")

            # Movement after pulling up the picture (First picture already there)
            if self.current_mode == 'absolute':
                threading.Thread(target=self.motor_controller.stitching_absolute, args=(
                    self.columns, self.rows, self.max_exp_time, self.positions_X, self.positions_Z,
                    self.absolute_offset_X, self.absolute_offset_Z, self.after_movement_stitching,
                    self.boundary_exit_function)).start()
            elif self.current_mode == 'relative':
                threading.Thread(target=self.motor_controller.stitching_relative, args=(
                    self.columns, self.rows, self.max_exp_time, self.start_pos_X, self.start_pos_Z,
                    self.after_movement_stitching, self.boundary_exit_function)).start()
            else:
                raise ValueError("Incorrect Stitching-Mode chosen")
        else:
            # If it is the last image, just update the status to indicate completion
            self.update_status(f'Done with {self.current_mode} Stitching')
            print("No more Images! Stitching has been completed")
            if self.final_callback:
                self.final_callback()

    def after_movement_stitching(self):
        # Exposure after movement and pulling up a picture
        if self.currentImage < len(self.imagesSLM):
            time.sleep(1.25)
            shutter = Shutter("COM6")
            self.shutter_opened = True
            shutter.toggle_pause(self.exp_times[self.currentImage])
            shutter.close_connection()
            self.shutter_opened = False
            
        if self.currentImage + 1 < len(self.imagesSLM):
            self.slm.image_window.after(30, self.next_image)
        elif self.currentImage + 1 >= len(self.imagesSLM):
            # Allows to exit at next .after in the Logic
            self.currentImage += 1
            print("Movement and Exposure finished")
        # Scheduling the next function!
        self.slm.image_window.after(50, self.stitching_logic)

    def prepare_printing(self, callback=None):
        print("Preparing Printing")

        self.reset_parameter()

        # Ensure the SLMWindow is initialized; this requires access to the Tk root,
        # which should be available in the context where prepare_printing is called.

        # Ask for a filepath to save
        self.printing_filepath = filedialog.askdirectory()
        if not self.printing_filepath:
            print("No directory selected.")
            self.update_status("No directory selected. Please try again.")
            return

        # User input for Offset and Speed and wait till saved also amount of columns and rows
        self.open_settings_print_popup()

        # Choose Color ?XMAX? and directly create an image (Save lets us continue)?
        # Open created image!
        print_picture = PrintingPicture(filepath=self.printing_filepath, slm=self.slm)
        color_picker = ColorPicker(on_color_save=print_picture.save_color_and_x_max)
        color_picker.open_color_picker()

        if callback:
            callback()

    def printing_logic(self, callback=None, pause_function=None, exit_function=None, boundary_exit_function=None):
        if callback is not None:
            # Usually the Beginning
            self.final_callback = callback
        if pause_function is not None:
            self.pause_function = pause_function
        if exit_function is not None:
            self.exit_function = exit_function
        if boundary_exit_function is not None:
            self.boundary_exit_function = boundary_exit_function

        # Check for Exit before
        if self.ExitActive:
            if self.exit_function is None:
                raise ValueError('exit_function is None and cannot be called.')
            else:
                try:
                    self.exit_function()
                except Exception as e:
                    raise ValueError(f'Error executing exit_function: {e}') from e
                finally:
                    return

        # Then check for Pause
        if self.PauseActive:
            if self.pause_function is None:
                raise ValueError('pause_function is None and cannot be called.')
            else:
                try:
                    self.pause_function()
                except Exception as e:  # Catching a general exception to avoid bare except
                    raise ValueError(f'Error executing pause_function: {e}') from e
                finally:
                    return

        # will take care of printing
        if self.currentLine <= (self.printing_lines + 1):
            if self.currentLine == 0:
                self.update_status("Current Status: Moving to Start-Location for Printing!")
            elif self.currentLine <= self.printing_lines:
                self.update_status(f"Current Status: Busy with Printing. Line {self.currentLine} of {self.printing_lines}")
            else:
                self.update_status("Current Status: Resetting to Center after Printing!")
            # Startup
            if self.currentLine == 1:
                # Open Shutter
                shutter = Shutter("COM6")
                shutter.toggle()
                shutter.close_connection()
                self.shutter_opened = True

            # Logic for printing, basically start threading with a callback
            threading.Thread(target=self.motor_controller.printing, args=(
                self.printing_lines, self.printing_rows, self.printing_speed, self.start_pos_X, self.start_pos_Z,
                self.after_movement_printing, self.boundary_exit_function)).start()

            # Always count up after a line
            self.currentLine += 1
        else:
            self.update_status("Done with Printing")
            print("No more Lines! Printing has been completed")
            if self.final_callback:
                self.final_callback()

    def after_movement_printing(self):
        # End
        if self.currentLine == (self.printing_lines + 1):
            # Close Shutter
            shutter = Shutter("COM6")
            shutter.toggle()
            shutter.close_connection()
            self.shutter_opened = False
        self.slm.image_window.after(50, self.printing_logic)

    def load_csv_data(self, path_to_csv):
        """Load positions and RGB values from a CSV file into memory."""
        try:
            with open(path_to_csv, newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header
                # Reset lists to ensure they're empty before loading new data
                self.added_RGB_values = []
                self.positions_X = []
                self.positions_Z = []

                # Read values from each row and append to the respective lists
                for row in reader:
                    self.added_RGB_values.append(float(row[0]))
                    self.positions_X.append(int(row[1]))
                    self.positions_Z.append(int(row[2]))
            # Calculate Exposure times and store in the List exp_times
            self.exp_times = [(value / 765) * self.max_exp_time if value != 0 else 0 for value in self.added_RGB_values]
            self.read_columns_and_rows(data_x=self.positions_X)
        except FileNotFoundError:
            print(f"CSV file not found: {path_to_csv}")
        except ValueError as e:
            print(f"Error processing CSV file: {e}")

    def read_columns_and_rows(self, data_x):
        """Calculate the length of numbers in a list until the second occurrence of the same number, so the columns."""
        width_columns = 0
        # height_rows = 0
        prev_num = None

        for num in data_x:
            if prev_num is not None and num == prev_num:
                break
            width_columns += 1
            prev_num = num
        else:
            width_columns = len(data_x)  # If no second occurrence, set width to the length of data

        height_rows = len(data_x) / width_columns
        self.rows = height_rows
        self.columns = width_columns
        return width_columns, height_rows

    # New stuff for the Popup-Window (Stitching) and parts for printing

    def open_settings_print_popup(self):
        popup = Toplevel()
        popup.grab_set()
        popup.title("Settings for Printing")
        customFont = ("Helvetica", 16)

        # Speed setting (reuse the pattern from Maximum Exposure Time but adjust limits)
        Label(popup, text="Maximum speed (Counts/s while 1 Count = 0.5 µm):", font=customFont).grid(row=0, column=0,
                                                                                                    sticky="w")
        speed_scale = Scale(popup, from_=1, to=80, orient='horizontal', length=400)
        speed_scale.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        speed_entry = Entry(popup, width=10, font=customFont)
        speed_entry.grid(row=0, column=1)
        speed_entry.insert(0, "1")

        # Offset_X setting (reuse existing logic)
        Label(popup, text="Offset X (None for centered):", font=customFont).grid(row=2, column=0, sticky="w")
        offset_x_scale = Scale(popup, from_=-20000, to=20000, orient='horizontal', length=400)
        offset_x_scale.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        offset_x_entry = Entry(popup, width=10, font=customFont)
        offset_x_entry.grid(row=2, column=1)
        offset_x_entry.insert(0, "None")

        # Offset_Z setting (reuse existing logic)
        Label(popup, text="Offset Z (None for centered):", font=customFont).grid(row=4, column=0, sticky="w")
        offset_z_scale = Scale(popup, from_=-20000, to=20000, orient='horizontal', length=400)
        offset_z_scale.grid(row=5, column=0, sticky='ew', pady=(0, 20))
        offset_z_entry = Entry(popup, width=10, font=customFont)
        offset_z_entry.grid(row=4, column=1)
        offset_z_entry.insert(0, "None")

        # Columns setting
        Label(popup, text="Columns (amount of printed lines):", font=customFont).grid(row=6, column=0, sticky="w")
        columns_scale = Scale(popup, from_=1, to=90, orient='horizontal', length=400)
        columns_scale.grid(row=7, column=0, sticky='ew', pady=(0, 20))
        columns_entry = Entry(popup, width=10, font=customFont)
        columns_entry.grid(row=6, column=1)
        columns_entry.insert(0, "1")

        # Rows setting
        Label(popup, text="Rows (equals the height of the lines):", font=customFont).grid(row=8, column=0, sticky="w")
        rows_scale = Scale(popup, from_=1, to=90, orient='horizontal', length=400)
        rows_scale.grid(row=9, column=0, sticky='ew', pady=(0, 20))
        rows_entry = Entry(popup, width=10, font=customFont)
        rows_entry.grid(row=8, column=1)
        rows_entry.insert(0, "1")

        # Add the new settings to the configure_entry_bindings method and the save settings button
        # Similar logic to what is done in open_settings_stitch_popup
        self.configure_entry_bindings(speed_entry=speed_entry, speed_scale=speed_scale, offset_x_entry=offset_x_entry,
                                      offset_x_scale=offset_x_scale, offset_z_entry=offset_z_entry,
                                      offset_z_scale=offset_z_scale, columns_entry=columns_entry,
                                      columns_scale=columns_scale, rows_entry=rows_entry, rows_scale=rows_scale)

        # Save Settings Button
        Button(popup, text="Save Settings",
               command=lambda: self.save_settings(popup, speed=speed_entry.get(), offset_x=offset_x_entry.get(),
                                                  offset_z=offset_z_entry.get(), columns=columns_entry.get(),
                                                  rows=rows_entry.get()), font=customFont).grid(row=10, column=0, columnspan=2)

        popup.wait_window()

    def open_settings_stitch_popup(self):
        popup = Toplevel()
        popup.grab_set()  # Make the popup modal
        popup.title("Settings for Stitching")

        # Setup UI elements including labels, scales, and entry fields.
        # Setup bindings for each entry to its corresponding scale.
        # The command for each scale now directly updates its corresponding entry.

        # Define a font
        customFont = ("Helvetica", 16)

        # Maximum Exposure Time
        Label(popup, text="Maximum Exposure Time (in s per Pixel):", font=customFont).grid(row=0, column=0, sticky="w")
        max_exp_scale = Scale(popup, from_=1, to=20, orient='horizontal', length=400)
        max_exp_scale.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        max_exp_entry = Entry(popup, width=10, font=customFont)
        max_exp_entry.grid(row=0, column=1)
        max_exp_entry.insert(0, "1")

        # Offset X
        Label(popup, text="Offset X (None is centered(only relative, will be 0 for absolute)):", font=customFont).grid(row=2, column=0, sticky="w")
        offset_x_scale = Scale(popup, from_=-20000, to=20000, orient='horizontal', length=400)
        offset_x_scale.grid(row=3, column=0, sticky='ew', pady=(0, 20))
        offset_x_entry = Entry(popup, width=10, font=customFont)
        offset_x_entry.grid(row=2, column=1)
        offset_x_entry.insert(0, "None")

        # Offset Z
        Label(popup, text="Offset Z (None is centered(only relative, will be 0 for absolute)):", font=customFont).grid(row=4, column=0, sticky="w")
        offset_z_scale = Scale(popup, from_=-20000, to=20000, orient='horizontal', length=400)
        offset_z_scale.grid(row=5, column=0, sticky='ew', pady=(0, 20))
        offset_z_entry = Entry(popup, width=10, font=customFont)
        offset_z_entry.grid(row=4, column=1)
        offset_z_entry.insert(0, "None")

        self.configure_entry_bindings(max_exp_entry=max_exp_entry, max_exp_scale=max_exp_scale, offset_x_entry=offset_x_entry,
                                      offset_x_scale=offset_x_scale, offset_z_entry=offset_z_entry, offset_z_scale=offset_z_scale)

        # Save Settings Button
        Button(popup, text="Save Settings",
               command=lambda: self.save_settings(popup, max_exp=max_exp_entry.get(), offset_x=offset_x_entry.get(),
                                                  offset_z=offset_z_entry.get()), font=customFont).grid(row=6, column=0, columnspan=2)

        popup.wait_window()  # This halts execution of the calling function until the popup is closed.

    def sync_entry_with_scale(self, entry, scale, min_val, max_val, allow_none, event=None):
        """
            Synchronize the scale widget's value based on changes in the entry widget, reacting to key events.
            This function is tailored to adjust the scale based on valid entry input and reset the entry for invalid input,
            with behavior adjustments based on the allow_none flag.

            Parameters:
            - entry: The Tkinter Entry widget to read the value from.
            - scale: The Tkinter Scale widget to update.
            - min_val: The minimum allowed value for the scale.
            - max_val: The maximum allowed value for the scale.
            - allow_none: Indicates whether "None" is an acceptable value, affecting error handling.
            - event: The event that triggered this function, providing context for the input (optional).
        """
        # Retrieve and trim the current text from the entry widget
        val = entry.get().strip()

        # Only proceed with the logic specific to Slider 1 if allow_none is False
        if not allow_none:
            try:
                # Attempt to convert the entry value to an integer
                num_val = int(val)

                # Clamp the number to the allowed range
                num_val = max(min_val, min(num_val, max_val))

                # Update the scale's value to reflect the clamped or valid input
                scale.set(num_val)

                # Ensure the entry reflects the potentially clamped value
                entry.delete(0, 'end')
                entry.insert(0, str(num_val))

            except ValueError:
                # For any non-numeric input, reset the entry and scale to the minimum value
                entry.delete(0, 'end')
                entry.insert(0, str(min_val))
                scale.set(min_val)

        # The following logic applies only to Slider 2 and 3, where allow_none is True
        elif allow_none:
            # Check if there's an event and it's a backspace or delete event
            if event and event.keysym in ["BackSpace", "Delete"]:
                if val:
                    # If there's some input, reduce it towards "None"
                    entry.delete(0, 'end')
                    entry.insert(0, "None")
                    scale.set(0)
                return  # Exit after handling backspace/delete to ensure only one action is taken

            # For numeric input or a single '-' sign
            if val.isdigit() or val == "-" or (val.startswith("-") and val[1:].isdigit()):
                try:
                    num_val = int(val)
                    # Clamp the value within the allowed range
                    num_val = max(-20000, min(num_val, 20000))
                    scale.set(num_val)

                    if str(num_val) != val:
                        entry.delete(0, 'end')
                        entry.insert(0, str(num_val))

                except ValueError:
                    if val == "-":
                        return  # Keep "-" as it is for negative number initiation
                    else:
                        self.reset_to_zero(entry, scale)
            elif val == "" or val.lower() == "none":
                # Handle the case where the field is cleared or set to "None"
                self.reset_to_zero(entry, scale)
            else:
                # For all other cases of invalid input
                self.reset_to_zero(entry, scale)

    def reset_to_zero(self, entry, scale):
        """
        Helper function to reset the entry to "0" and the scale to 0,
        used for handling invalid input for sliders where allow_none is True.
        """
        entry.delete(0, 'end')
        entry.insert(0, "0")
        scale.set(0)

    def configure_entry_bindings(self, max_exp_entry=None, max_exp_scale=None, speed_entry=None, speed_scale=None,
                                 offset_x_entry=None, offset_x_scale=None, offset_z_entry=None, offset_z_scale=None,
                                 columns_entry=None, columns_scale=None, rows_entry=None, rows_scale=None):
        """Configure the bindings for the entries and scales."""
        if max_exp_entry is not None:
            max_exp_entry.bind("<KeyRelease>", lambda e: self.sync_entry_with_scale(max_exp_entry, max_exp_scale, 1, 20, False, e))
        if speed_entry is not None:
            speed_entry.bind("<KeyRelease>", lambda e: self.sync_entry_with_scale(speed_entry, speed_scale, 1, 80, False, e))
        if offset_x_entry is not None:
            offset_x_entry.bind("<KeyRelease>", lambda e: self.sync_entry_with_scale(offset_x_entry, offset_x_scale, -20000, 20000, True, e))
        if offset_z_entry is not None:
            offset_z_entry.bind("<KeyRelease>", lambda e: self.sync_entry_with_scale(offset_z_entry, offset_z_scale, -20000, 20000, True, e))
        if columns_entry is not None:
            columns_entry.bind("<KeyRelease>", lambda e: self.sync_entry_with_scale(columns_entry, columns_scale, 1, 90, False, e))
        if rows_entry is not None:
            rows_entry.bind("<KeyRelease>", lambda e: self.sync_entry_with_scale(rows_entry, rows_scale, 1, 90, False, e))

        # Update scale directly to reflect the corresponding entry
        if max_exp_scale is not None:
            max_exp_scale.config(command=lambda val: self.sync_scale_with_entry(max_exp_scale, max_exp_entry))
        if speed_scale is not None:
            speed_scale.config(command=lambda val: self.sync_scale_with_entry(speed_scale, speed_entry))
        if offset_x_scale is not None:
            offset_x_scale.config(command=lambda val: self.sync_scale_with_entry(offset_x_scale, offset_x_entry, True))
        if offset_z_scale is not None:
            offset_z_scale.config(command=lambda val: self.sync_scale_with_entry(offset_z_scale, offset_z_entry, True))
        if columns_scale is not None:
            columns_scale.config(command=lambda val: self.sync_scale_with_entry(columns_scale, columns_entry))
        if rows_scale is not None:
            rows_scale.config(command=lambda val: self.sync_scale_with_entry(rows_scale, rows_entry))

    def sync_scale_with_entry(self, scale, entry, allow_none=False):
        """Function to update entry based on scale movement."""
        val = scale.get()
        if allow_none and val == 0:
            entry.delete(0, END)
            entry.insert(0, "None")
        else:
            entry.delete(0, END)
            entry.insert(0, str(val))

    def save_settings(self, popup, max_exp=None, speed=None, offset_x=None, offset_z=None, columns=None, rows=None):
        """
            Adjusts and saves the settings, converting "None" or empty entries for Offset X and Offset Z
            into Python's None type before saving.

            Parameters:
            - popup: The popup window instance to be destroyed after saving.
            - max_exp: The value from the maximum exposure time entry.
            - offset_x: The value from the offset X entry, converted to None if applicable.
            - offset_z: The value from the offset Z entry, converted to None if applicable.
        """
        if max_exp is not None:
            # Convert max_exp to an integer, defaulting to a specific value (e.g., 4) if conversion fails
            try:
                self.max_exp_time = int(max_exp)
            except ValueError:
                self.max_exp_time = 4  # Default value if conversion fails
            print(f"Saved Maximum Exposure Time: {self.max_exp_time} s")

        if speed is not None:
            # Convert speed to an integer, defaulting to a specific value (e.g., 40) if conversion fails
            try:
                self.printing_speed = int(speed)
            except ValueError:
                self.printing_speed = 40  # Default value if conversion fails
            print(f"Saved speed: {self.printing_speed} Counts/s")

        if columns is not None:
            # Convert columns to an integer, defaulting to a specific value (e.g., 10) if conversion fails
            try:
                self.printing_lines = int(columns)
            except ValueError:
                self.printing_lines = 10  # Default value if conversion fails
            print(f"Saved lines for Printing: {self.printing_lines}")

        if rows is not None:
            # Convert rows to an integer, defaulting to a specific value (e.g., 10) if conversion fails
            try:
                self.printing_rows = int(rows)
            except ValueError:
                self.printing_rows = 10  # Default value if conversion fails
            print(f"Saved rows for Printing: {self.printing_rows}")

        # Process offset_x and offset_z
        # Convert "None" or empty string to Python None for offset_x and offset_z
        # For relative movement
        try:
            self.start_pos_X = None if offset_x.strip().lower() == "none" or not offset_x.strip() else int(offset_x)
        except ValueError:
            self.start_pos_X = None  # Set to None if conversion fails

        try:
            self.start_pos_Z = None if offset_z.strip().lower() == "none" or not offset_z.strip() else int(offset_z)
        except ValueError:
            self.start_pos_Z = None  # Set to None if conversion fails

        # Setting absolute offsets, default to 0 if None
        self.absolute_offset_X = 0 if self.start_pos_X is None else self.start_pos_X
        self.absolute_offset_Z = 0 if self.start_pos_Z is None else self.start_pos_Z

        print(
            f"Settings Saved:\n"
            f"Relative: Offset X: {self.start_pos_X}\n"
            f"Offset Z: {self.start_pos_Z}\n"
            f"Absolute: Offset X: {self.absolute_offset_X}\n"
            f"Offset Z: {self.absolute_offset_Z}"
        )
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
        popup.destroy()


class ApplicationController:
    def __init__(self, slm_manager, motor_controller):
        self.slm_manager = slm_manager
        self.motor_controller = motor_controller
        self.root = None  # Initialize root as None

        self.buttons = []  # List to store button references
        self.button_names = {}  # Dictionary to map button names to references

        # 0 nothing only during init or after reset, 1 Top, 2 Bottom, 3 Left, 4 Right, 5 Finish Focus
        self.current_focus = 0

        # 0 at beginning, 1 after motor initialized, 2 after Focus complete
        # 3 at preparing for stitching, 4 absolute stitching started, 5 absolute stitching complete
        # 6 relative stitching started, 7 relative stitching complete
        # 8 at preparing for printing, 9 printing started, 10 printing complete
        self.current_stage = 0  # Tracks the current stage of the operation

        self.movement_aborted = False

    def set_root_window(self, root):
        self.root = root

    def add_button(self, button, name):
        """Add a button reference to the list and map a name to it."""
        self.buttons.append(button)
        self.button_names[name] = button

    def disable_button(self, name):
        """Disable a button by its name."""
        if name in self.button_names:
            self.button_names[name].config(state='disabled')

    def enable_button(self, name):
        """Enable a button by its name."""
        if name in self.button_names:
            self.button_names[name].config(state='normal')

    def disable_all_buttons(self):
        """Disable all buttons."""
        for button in self.buttons:
            button.config(state='disabled')

    def enable_all_buttons(self):
        """Enable all buttons."""
        for button in self.buttons:
            button.config(state='normal')

    # Functions for button commands

    def recenter_sequence_logic(self):
        print("Recentering sequence...")
        self.disable_all_buttons()
        self.enable_button("ExitAll")
        self.slm_manager.update_status('Current Status: Recentering sequence in progress!')
        # Start the recentering sequence in a separate thread and pass the callback
        threading.Thread(target=self.motor_controller.recenter_sequence,
                         args=(self.recenter_sequence_complete,)).start()

    def recenter_sequence_complete(self):
        """Callback method to run after recentering is complete."""
        self.current_stage = 0
        self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
            'Recentering sequence complete! Please Initialize Motor!'))
        # Use lambda to pass arguments to self.enable_button
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("InitializeMotor"))

    def initialize_motors_logic(self):
        print("Initializing motors...")
        self.disable_all_buttons()
        self.slm_manager.update_status('Current Status: Motors get initialized!')
        threading.Thread(target=self.motor_controller.initialize_everything,
                         args=(self.initialize_motors_complete,)).start()

    def initialize_motors_complete(self):
        self.current_stage = 1
        self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
            'Initialization complete! Move the stage close to the Film to Focus!'))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("TopFocus"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("BottomFocus"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("LeftFocus"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("RightFocus"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("FinishFocus"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ExitAll"))

    def focus_logic(self, direction):
        if direction == "Finish":
            print("Moving to Center of the Film...")
            self.disable_all_buttons()
            self.enable_button("ExitAll")
            self.slm_manager.update_status('Current Status: Moving to the Center (0:0)!')
            self.current_focus = 5
            # Start in a separate thread and pass the callback
            threading.Thread(target=self.motor_controller.finish_focus,
                             args=(self.focus_logic_complete,)).start()

        elif direction == "Top" or direction == "Bottom" or direction == "Left" or direction == "Right":
            print(f"Moving to the {direction} of the Film...")
            self.disable_all_buttons()
            self.enable_button("ExitAll")
            self.slm_manager.update_status(f'Current Status: Moving to the {direction} of the Film!')
            if direction == "Top":
                self.current_focus = 1
                threading.Thread(target=self.motor_controller.focus_top,
                                 args=(self.focus_logic_complete,)).start()
            elif direction == "Bottom":
                self.current_focus = 2
                threading.Thread(target=self.motor_controller.focus_bottom,
                                 args=(self.focus_logic_complete,)).start()
            elif direction == "Left":
                self.current_focus = 3
                threading.Thread(target=self.motor_controller.focus_left,
                                 args=(self.focus_logic_complete,)).start()
            elif direction == "Right":
                self.current_focus = 4
                threading.Thread(target=self.motor_controller.focus_right,
                                 args=(self.focus_logic_complete,)).start()
            else:
                raise ValueError("Mistake by calling the correct Function in its Thread thru wrong Name-Assignment")
        else:
            raise ValueError(f'The direction {direction} does not exist!')

    def focus_logic_complete(self):
        if self.current_focus == 5:
            # We used Finish and are in the center, ready to continue
            self.current_stage = 2
            self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
                'Focus complete and in the center! Choose Stitching or Printing or Focus further!'))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("TopFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("BottomFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("LeftFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("RightFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("PreparePrint"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ReadStitch"))
        elif self.current_focus == 1:
            # Wrap up Focus Top
            self.current_stage = 1
            self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
                'Top has been reached! Now Focus the Film!'))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("BottomFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("LeftFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("RightFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("FinishFocus"))
        elif self.current_focus == 2:
            # Wrap up Focus Bottom
            self.current_stage = 1
            self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
                'Bottom has been reached! Now Focus the Film!'))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("TopFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("LeftFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("RightFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("FinishFocus"))
        elif self.current_focus == 3:
            # Wrap up Focus Left
            self.current_stage = 1
            self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
                'Left has been reached! Now Focus the Film!'))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("TopFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("BottomFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("RightFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("FinishFocus"))
        elif self.current_focus == 4:
            # Wrap up Focus Right
            self.current_stage = 1
            self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
                'Right has been reached! Now Focus the Film!'))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("TopFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("BottomFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("LeftFocus"))
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("FinishFocus"))
        else:
            raise ValueError("Could not complete the Focus at the end!")

    def read_stitch_logic(self):
        print("Read for Stitching")
        self.current_stage = 3
        self.disable_all_buttons()
        self.enable_button("ReadStitch")
        self.enable_button("ExitAll")
        self.slm_manager.update_status('Current Status: Preparing for Stitching')
        self.slm_manager.slm.image_window.after(50, lambda: self.slm_manager.open_images(self.read_stitch_complete))

    def read_stitch_complete(self):
        self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
            'Stitching has been prepared! Please choose Absolute or Relative Stitching!'))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("StitchAbsolute"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("StitchRelative"))

    def stitch_button_logic(self, mode):
        print(f"Stitching {mode}...")
        if mode == 'absolute':
            self.current_stage = 4
        elif mode == 'relative':
            self.current_stage = 6
        else:
            raise ValueError(f'Wrong mode for the Logic chosen: {mode}')
        self.disable_all_buttons()
        self.enable_button("ExitAll")
        self.enable_button("PauseAll")
        self.slm_manager.update_status(f'Current Status: Busy with {mode} Stitching')
        self.slm_manager.slm.image_window.after(50, lambda: self.slm_manager.stitching_logic(mode, self.stitch_button_complete, self.pause_operation, self.exit_operation, self.boundary_error_reset))

    def stitch_button_complete(self):
        if self.current_stage == 4:
            self.current_stage = 5
            self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
                'Current Status: Absolute Stitching has been completed'))
        elif self.current_stage == 6:
            self.current_stage = 7
            self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
                'Current Status: Relative Stitching has been completed'))
        else:
            raise ValueError("Wrong current Stage!")
        self.slm_manager.reset_final_callback()
        self.slm_manager.slm.image_window.after(0, self.disable_all_buttons)
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ExitAll"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("PreparePrint"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ReadStitch"))

    def prepare_print_logic(self):
        print("Preparing print...")
        self.current_stage = 8
        self.disable_all_buttons()
        self.enable_button("PreparePrint")
        self.enable_button("ExitAll")
        self.slm_manager.update_status('Current Status: Preparing for Printing')
        self.slm_manager.slm.image_window.after(50, lambda: self.slm_manager.prepare_printing(self.prepare_print_complete))

    def prepare_print_complete(self):
        self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
            'Printing has been prepared! Please continue now!'))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("Print"))

    def print_button_logic(self):
        print("Starting print...")
        self.current_stage = 9
        self.disable_all_buttons()
        self.enable_button("ExitAll")
        self.enable_button("PauseAll")
        self.slm_manager.update_status("Current Status: Busy with Printing")
        self.slm_manager.slm.image_window.after(50, lambda: self.slm_manager.printing_logic(self.print_button_complete, self.pause_operation, self.exit_operation, self.boundary_error_reset))

    def print_button_complete(self):
        self.current_stage = 10
        self.slm_manager.reset_final_callback()
        self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
            'Current Status: Printing has been completed'))
        self.slm_manager.slm.image_window.after(0, self.disable_all_buttons)
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ExitAll"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("PreparePrint"))
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ReadStitch"))

    # Important Logic for Pause and Exit

    def pause_init(self):
        print("Initialize Pause...Might take a while, since Pausing happens after movement is done")
        self.slm_manager.update_status('Current Status: Pause has been initiated! Might take a while, since Pausing happens after movement is done')
        # Indicate the system is paused
        self.slm_manager.PauseActive = True
        self.disable_all_buttons()

    def pause_operation(self):
        # Movement should be done so now actually Pause
        # Disable relevant UI buttons except for "Continue" and "Exit"
        self.slm_manager.slm.image_window.after(10, lambda: self.enable_button("ContinueAll"))

        # Check if the shutter is opened and needs to be closed
        if self.slm_manager.shutter_opened:
            shutter = Shutter("COM6")
            shutter.toggle()
            self.slm_manager.shutter_opened = False
            shutter.close_connection()
            self.slm_manager.re_enable = True  # Mark that the shutter needs to be reopened upon continue

        self.slm_manager.slm.image_window.after(10, lambda: self.slm_manager.update_status(
            'Current Status: System paused. Press "Continue" to resume.'))
        print("System paused. Press 'Continue' to resume.")

    def continue_operation(self):
        print("Continue...")
        # Reset the pause flag
        self.slm_manager.PauseActive = False

        # Reopen the shutter if it was closed due to pausing
        if self.slm_manager.re_enable:
            shutter = Shutter("COM6")
            self.slm_manager.shutter_opened = True
            shutter.toggle()
            shutter.close_connection()
            self.slm_manager.re_enable = False

        # Re-enable some UI buttons
        self.disable_all_buttons()
        self.enable_button("ExitAll")
        self.enable_button("PauseAll")
        self.slm_manager.update_status(
            'Current Status: Resuming system operation!')

        # Decide next action based on the current stage
        if self.current_stage == 4 or self.current_stage == 6:
            # absolute or relative stitching, because of Implementation we will not be able to change relative or absolute here
            # we will automatically continue the process with the same mode and in the main thread!
            self.slm_manager.slm.image_window.after(0, self.slm_manager.stitching_logic)
        elif self.current_stage == 9:
            # main thread!
            self.slm_manager.slm.image_window.after(0, self.slm_manager.printing_logic)

        print("Resuming system operation.")

    def exit_init(self):
        print("Initialize Exit...Movement will be stopped!")
        self.slm_manager.update_status(
            'Current Status: Exit has been initiated! All Movement will be stopped!')
        # Indicate the system is paused
        self.slm_manager.ExitActive = True
        self.disable_all_buttons()

        # Interrupt all movement here in a  different thread!
        if self.current_stage == 4 or self.current_stage == 6:
            threading.Thread(target=self.motor_controller.exit_stop_movement, args=(self.exit_movement_stopped,)).start()
        elif self.current_stage == 9:
            threading.Thread(target=self.motor_controller.exit_stop_movement, args=(self.exit_movement_stopped, 3)).start()
        elif self.current_stage == 1:
            threading.Thread(target=self.motor_controller.exit_stop_movement, args=(self.exit_movement_stopped, 1)).start()
            self.slm_manager.slm.image_window.after(50, self.exit_operation)
        elif self.current_stage == 0:
            threading.Thread(target=self.motor_controller.exit_stop_movement, args=(self.exit_movement_stopped, 3)).start()
            self.slm_manager.slm.image_window.after(50, self.exit_operation)
        else:
            # to make sure we are in the center and there are no other movements that shouldnt be there
            threading.Thread(target=self.motor_controller.exit_stop_movement, args=(self.exit_movement_stopped, 1)).start()
            self.exit_operation()

    def exit_movement_stopped(self):
        self.movement_aborted = True

    def exit_operation(self):
        # print("Exit...")
        self.slm_manager.slm.image_window.after(50, lambda: self.slm_manager.update_status(
            'Current Status: Waiting for Movement-Abortion!'))
        # Check if the shutter is opened and needs to be closed
        if self.slm_manager.shutter_opened:
            shutter = Shutter("COM6")
            self.slm_manager.shutter_opened = False
            shutter.toggle()
            shutter.close_connection()

        if self.movement_aborted:
            # Move to 0:0
            #self.motor_controller.move_to_zero()
            self.motor_controller.close_connection()
            # Fully exit here
            self.root.destroy()
        else:
            # Schedule after
            self.slm_manager.slm.image_window.after(50, self.exit_operation)
    
    def boundary_error_reset(self):
        self.slm_manager.slm.image_window.after(0, lambda: self.slm_manager.update_status(
            'Starting Points and/or Offset out of Boundaries, Danger of Hitting the Lens!! Please restart!'))
        self.slm_manager.slm.image_window.after(0, self.disable_all_buttons)
        self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ExitAll"))
        if self.current_stage == 4 or self.current_stage == 6:
            self.current_stage = 3
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("ReadStitch"))
        elif self.current_stage == 9:
            self.current_stage = 8
            self.slm_manager.slm.image_window.after(0, lambda: self.enable_button("PreparePrint"))


def setup_gui(app_controller):
    root = Tk()
    app_controller.slm_manager.initialize_slm_window(root=root)
    app_controller.set_root_window(root=root)
    root.title("Motor Control Panel")

    # Define a consistent font and size for all buttons
    button_font = ('Helvetica', 16)

    # Current Status Label
    status_label = Label(root, text="!!Important: Pull Stage Back to not hit the Lens!!", font=button_font)
    status_label.pack(fill='x', pady=5)
    # Update the app_controller's slm_manager status_label reference
    app_controller.slm_manager.status_label = status_label

    # Frame for Initialization
    frame_init = Frame(root)
    frame_init.pack(fill='x', pady=5)
    Label(frame_init, text="Initialization", font=button_font).pack(side='left', padx=10)

    # Buttons within Frame for Initialization
    recenter_sequence_button = Button(frame_init, text="Recenter-Sequence (optional)", command=app_controller.recenter_sequence_logic, font=button_font)
    recenter_sequence_button.pack(side='left', padx=5)
    initialize_motor_button = Button(frame_init, text="Initialize Motor (necessary)", command=app_controller.initialize_motors_logic, font=button_font)
    initialize_motor_button.pack(side='left', padx=5)

    # Add Button-Reference to ApplicationController
    app_controller.add_button(recenter_sequence_button, name="RecenterSequence")
    app_controller.add_button(initialize_motor_button, name="InitializeMotor")

    # Frame for Focussing
    frame_focus = Frame(root)
    frame_focus.pack(fill='x', pady=5)
    Label(frame_focus, text="Focus on Film", font=button_font).pack(side='left', padx=10)

    # Buttons within Frame for Focussing
    top_focus_button = Button(frame_focus, text="Top", command=lambda: app_controller.focus_logic("Top"), font=button_font)
    top_focus_button.pack(side='left', padx=5)
    bottom_focus_button = Button(frame_focus, text="Bottom", command=lambda: app_controller.focus_logic("Bottom"), font=button_font)
    bottom_focus_button.pack(side='left', padx=5)
    left_focus_button = Button(frame_focus, text="Left", command=lambda: app_controller.focus_logic("Left"), font=button_font)
    left_focus_button.pack(side='left', padx=5)
    right_focus_button = Button(frame_focus, text="Right", command=lambda: app_controller.focus_logic("Right"), font=button_font)
    right_focus_button.pack(side='left', padx=5)
    finish_focus_button = Button(frame_focus, text="Finish Focus or go to 0:0", command=lambda: app_controller.focus_logic("Finish"), font=button_font)
    finish_focus_button.pack(side='left', padx=5)

    # Add Button-Reference to ApplicationController
    app_controller.add_button(top_focus_button, name="TopFocus")
    app_controller.add_button(bottom_focus_button, name="BottomFocus")
    app_controller.add_button(left_focus_button, name="LeftFocus")
    app_controller.add_button(right_focus_button, name="RightFocus")
    app_controller.add_button(finish_focus_button, name="FinishFocus")

    # Frame for Stitching
    frame_stitching = Frame(root)
    frame_stitching.pack(fill='x', pady=5)
    Label(frame_stitching, text="Stitching", font=button_font).pack(side='left', padx=10)

    # Buttons within Frame for Stitching
    read_stitch_button = Button(frame_stitching, text="Read for Stitching", command=app_controller.read_stitch_logic, font=button_font)
    read_stitch_button.pack(side='left', padx=5)
    stitch_absolute_button = Button(frame_stitching, text="Stitch Absolute", command=lambda: app_controller.stitch_button_logic('absolute'), font=button_font)
    stitch_absolute_button.pack(side='left', padx=5)
    stitch_relative_button = Button(frame_stitching, text="Stitch Relative", command=lambda: app_controller.stitch_button_logic('relative'), font=button_font)
    stitch_relative_button.pack(side='left', padx=5)

    # Add Button-Reference to ApplicationController
    app_controller.add_button(read_stitch_button, name="ReadStitch")
    app_controller.add_button(stitch_absolute_button, name="StitchAbsolute")
    app_controller.add_button(stitch_relative_button, name="StitchRelative")

    # Frame for Printing
    frame_printing = Frame(root)
    frame_printing.pack(fill='x', pady=5)
    Label(frame_printing, text="Printing", font=button_font).pack(side='left', padx=10)

    # Buttons within Frame for Printing
    prepare_print_button = Button(frame_printing, text="Prepare Printing", command=app_controller.prepare_print_logic, font=button_font)
    prepare_print_button.pack(side='left', padx=5)
    print_button = Button(frame_printing, text="Print", command=app_controller.print_button_logic, font=button_font)
    print_button.pack(side='left', padx=5)

    # Add Button-Reference to ApplicationController
    app_controller.add_button(prepare_print_button, name="PreparePrint")
    app_controller.add_button(print_button, name="Print")

    # Frame for Other
    frame_other = Frame(root)
    frame_other.pack(fill='x', pady=5)
    Label(frame_other, text="Other", font=button_font).pack(side='left', padx=10)

    # Buttons within Frame for Other
    pause_all_button = Button(frame_other, text="Pause", command=app_controller.pause_init, font=button_font)
    pause_all_button.pack(side='left', padx=5)
    continue_all_button = Button(frame_other, text="Continue", command=app_controller.continue_operation, font=button_font)
    continue_all_button.pack(side='left', padx=5)
    exit_all_button = Button(frame_other, text="Exit", command=app_controller.exit_init, font=button_font)
    exit_all_button.pack(side='left', padx=5)

    # Add Button-Reference to ApplicationController
    app_controller.add_button(pause_all_button, name="PauseAll")
    app_controller.add_button(continue_all_button, name="ContinueAll")
    app_controller.add_button(exit_all_button, name="ExitAll")

    # We want to make sure only Init and Exit is usable at beginning!
    app_controller.disable_all_buttons()
    app_controller.enable_button("RecenterSequence")
    app_controller.enable_button("ExitAll")
    app_controller.enable_button("InitializeMotor")

    root.mainloop()


def main():
    motor_controller = MotorController(port="COM7", baudrate=9600)
    slm_manager = SLMManager(motor_controller=motor_controller)  # No filepath needed at initialization
    app_controller = ApplicationController(slm_manager, motor_controller)
    setup_gui(app_controller=app_controller)


if __name__ == "__main__":
    main()
