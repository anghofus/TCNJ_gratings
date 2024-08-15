import tkinter as tk
from tkinter import ttk
import json
from sine_phase_plate_backend import *
import screeninfo
from PIL import Image, ImageTk
from time import sleep


class Settings:
    def __init__(self):
        self.__radius = None
        self.__focal_length = None

        self.__exposure_time = 5
        self.__grating_width = 70
        self.__grating_height = 40
        self.__wavelength = 633
        self.__y_min = 0
        self.__y_peak_to_peak = 128
        self.__com_laser = "/dev/ttyUSB0"
        self.__com_motion_controller = "/dev/ttyUSB1"
        self.__com_shutter = "/dev/ttyUSB2"

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value: float):
        assert value >= 0, "radius must be grater than zero!"
        self.__radius = value

    @property
    def focal_length(self):
        return self.__focal_length

    @focal_length.setter
    def focal_length(self, value: float):
        assert value >= 0, "focal length must be grater than zero!"
        self.__focal_length = value

    @property
    def exposure_time(self):
        return self.__exposure_time

    @exposure_time.setter
    def exposure_time(self, value: float):
        assert value >= 0, "Exposure time must be greater than zero!"
        self.__exposure_time = value

    @property
    def grating_width(self):
        return self.__grating_width

    @grating_width.setter
    def grating_width(self, value: float):
        assert value >= 0, "Grating width must be greater than zero!"
        self.__grating_width = value

    @property
    def grating_height(self):
        return self.__grating_height

    @grating_height.setter
    def grating_height(self, value: float):
        assert value >= 0, "Grating height must be greater than zero!"

    @property
    def wavelength(self):
        return self.__wavelength

    @wavelength.setter
    def wavelength(self, value: float):
        assert value >= 0, "wavelength must be greater than zero!"
        self.__wavelength = value

    @property
    def y_min(self):
        return self.__y_min

    @y_min.setter
    def y_min(self, value):
        assert 0 <= value <= 255, "y_min must be between 0 and 255"
        self.__y_min = value

    @property
    def y_peak_to_peak(self):
        return self.__y_peak_to_peak

    @y_peak_to_peak.setter
    def y_peak_to_peak(self, value):
        assert 0 <= value <= 255, "y_peak_to_peak must be between 0 and 255"
        self.__y_peak_to_peak = value

    @property
    def com_laser(self):
        return self.__com_laser

    @com_laser.setter
    def com_laser(self, value: str):
        self.__com_laser = value

    @property
    def com_motion_controller(self):
        return self.__com_motion_controller

    @com_motion_controller.setter
    def com_motion_controller(self, value: str):
        self.__com_motion_controller = value

    @property
    def com_shutter(self):
        return self.__com_shutter

    @com_shutter.setter
    def com_shutter(self, value: str):
        self.__com_shutter = value

    def read_from_json(self):
        try:
            with open('settings.json', 'r') as settings_file:
                settings = json.load(settings_file)
                self.__exposure_time = settings['exposure_time']
                self.__grating_width = settings['grating_width']
                self.__grating_height = settings['grating_height']
                self.__wavelength = settings['wavelength']
                self.__y_min = settings['y_min']
                self.__y_peak_to_peak = settings['y_peak_to_peak']
                self.__com_laser = settings['com_laser']
                self.__com_motion_controller = settings['com_motion_controller']
                self.__com_shutter = settings['com_shutter']

        except FileNotFoundError:
            self.write_to_json()

    def write_to_json(self):
        with open('settings.json', 'w') as settings_file:
            settings = {
                'exposure_time': self.__exposure_time,
                'grating_width': self.__grating_width,
                'grating_height': self.__grating_height,
                'wavelength': self.__wavelength,
                'y_min': self.__y_min,
                'y_peak_to_peak': self.__y_peak_to_peak,
                'com_laser': self.__com_laser,
                'com_motion_controller': self.__com_motion_controller,
                'com_shutter': self.__com_shutter
            }
            json.dump(settings, settings_file, indent=4)


class ImageDisplay(tk.Toplevel):
    def __init__(self, monitor):
        assert monitor > 0, "Monitor must be greater than zero!"

        super().__init__()

        # Get information about all monitors
        monitors = screeninfo.get_monitors()

        if len(monitors) < 2:
            raise NoSecondMonitorError("No second monitor found")

        # Assume the second monitor is at index 1
        second_monitor = monitors[monitor]

        self.geometry(f"{second_monitor.width}x{second_monitor.height}+{second_monitor.x}+{second_monitor.y}")
        self.attributes("-fullscreen", True)
        self.configure(background='black')

    def show_image(self, image_object):
        assert isinstance(image_object, Image.Image), "Image must be a PIL Image object"

        photo = ImageTk.PhotoImage(image_object)

        # Create a label to hold the image
        label = tk.Label(self, image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection
        label.pack()


class NoSecondMonitorError(Exception):
    pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.settings = Settings()
        self.instruments = InstrumentController(self.settings.com_laser, self.settings.com_motion_controller, self.settings.com_shutter)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title("sine phase plate app")
        self.geometry("640x480")
        self.minsize(640, 480)

        self.protocol("WM_DELETE_WINDOW", self.close_application)

        self.start_screen = StartScreen(self, self.settings, self.instruments)

        self.mainloop()

    def close_application(self):
        self.instruments.close_connection()
        self.destroy()


class StartScreen(ttk.Frame):
    def __init__(self, master, settings, instruments):
        self.master = master
        self.settings = settings
        self.instruments = instruments
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ttk.Label(self, text="lens parameters", font=("Arial", 25)).grid(row=0, column=0, columnspan=2, padx=10,pady=10)
        ttk.Label(self, text="radius in mm", font=("Arial", 20)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        ttk.Label(self, text="focal length in mm", font=("Arial", 20)).grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)

        self.entry_radius = ttk.Entry(self)
        if self.settings.radius is not None:
            self.entry_radius.insert(0, self.settings.radius)
        self.entry_radius.grid(row=1, column=1, sticky=tk.W, padx=10)
        self.entry_focal_length = ttk.Entry(self)
        if self.settings.focal_length is not None:
            self.entry_focal_length.insert(0, self.settings.focal_length)
        self.entry_focal_length.grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Button(self, text="apply", command=self.button_apply).grid(row=3, column=0)
        ttk.Button(self, text="settings", command=self.button_settings).grid(row=3, column=1)

        self.grid(row=0, column=0, sticky="nsew")

    def button_apply(self):
        try:
            self.settings.radius = float(self.entry_radius.get())
            self.settings.focal_length = float(self.entry_focal_length.get())

            self.grid_forget()
            FocusingScreen(self.master, self.settings, self.instruments)
        except Exception as e:
            pass

    def button_settings(self):
        self.grid_forget()
        SettingsScreen(self.master, self.settings, self.instruments)


class SettingsScreen(ttk.Frame):
    def __init__(self, master, settings, instruments):
        self.master = master
        self.settings = settings
        self.instruments = instruments
        super().__init__(master)

        self.settings.read_from_json()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.grid_rowconfigure(10, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="settings", font=("Arial", 25)).grid(row=0, column=0, columnspan=2, padx=10,pady=10)
        ttk.Label(self, text="exposure time in s", font=("Arial", 20)).grid(row=1, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="grating width in µm", font=("Arial", 20)).grid(row=2, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="grating height in µm", font=("Arial", 20)).grid(row=3, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="wavelength in nm", font=("Arial", 20)).grid(row=4, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="y_min", font=("Arial", 20)).grid(row=5, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="y_peak_to_peak", font=("Arial", 20)).grid(row=6, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="laser COM", font=("Arial", 20)).grid(row=7, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="motion controller COM", font=("Arial", 20)).grid(row=8, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="shutter COM", font=("Arial", 20)).grid(row=9, column=0, padx=10, sticky=tk.W)

        self.entry_exposure_time = ttk.Entry(self)
        self.entry_exposure_time.insert(0, self.settings.exposure_time)
        self.entry_exposure_time.grid(row=1, column=1, padx=10)
        self.entry_grating_width = ttk.Entry(self)
        self.entry_grating_width.insert(0, self.settings.grating_width)
        self.entry_grating_width.grid(row=2, column=1, padx=10)
        self.entry_grating_height = ttk.Entry(self)
        self.entry_grating_height.insert(0, self.settings.grating_height)
        self.entry_grating_height.grid(row=3, column=1, padx=10)
        self.entry_wavelength = ttk.Entry(self)
        self.entry_wavelength.insert(0, self.settings.wavelength)
        self.entry_wavelength.grid(row=4, column=1, padx=10)
        self.entry_y_min = ttk.Entry(self)
        self.entry_y_min.insert(0, self.settings.y_min)
        self.entry_y_min.grid(row=5, column=1, padx=10)
        self.entry_y_peak_to_peak = ttk.Entry(self)
        self.entry_y_peak_to_peak.insert(0, self.settings.y_peak_to_peak)
        self.entry_y_peak_to_peak.grid(row=6, column=1, padx=10)
        self.entry_laser_COM = ttk.Entry(self)
        self.entry_laser_COM.insert(0, self.settings.com_laser)
        self.entry_laser_COM.grid(row=7, column=1, padx=10)
        self.entry_motion_controller_COM = ttk.Entry(self)
        self.entry_motion_controller_COM.insert(0, self.settings.com_motion_controller)
        self.entry_motion_controller_COM.grid(row=8, column=1, padx=10)
        self.entry_shutter_COM = ttk.Entry(self)
        self.entry_shutter_COM.insert(0, self.settings.com_shutter)
        self.entry_shutter_COM.grid(row=9, column=1, padx=10)

        ttk.Button(self, text="apply", command=self.button_apply).grid(row=10, column=0)
        ttk.Button(self, text="cancel", command=self.button_cancel).grid(row=10, column=1)

        self.grid(row=0, column=0, sticky="nsew")

    def button_apply(self):
        self.settings.exposure_time = float(self.entry_exposure_time.get())
        self.settings.grating_width = float(self.entry_grating_width.get())
        self.settings.grating_height = float(self.entry_grating_height.get())
        self.settings.wavelength = float(self.entry_wavelength.get())
        self.settings.y_min = int(self.entry_y_min.get())
        self.settings.y_peak_to_peak = int(self.entry_y_peak_to_peak.get())
        self.settings.com_laser = self.entry_laser_COM.get()
        self.settings.com_motion_controller = self.entry_motion_controller_COM.get()
        self.settings.com_shutter = self.entry_shutter_COM.get()

        self.settings.write_to_json()

        self.grid_forget()
        StartScreen(self.master, self.settings, self.instruments)

    def button_cancel(self):
        self.grid_forget()
        StartScreen(self.master, self.settings, self.instruments)


class FocusingScreen(ttk.Frame):
    def __init__(self, master, settings, instruments):
        self.master = master
        self.settings = settings
        self.instruments = instruments
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        ttk.Label(self, text="focusing", font=("Arial", 25)).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Button(self, text="top", command=lambda: self.instruments.go_to_focus_location("top")).grid(row=1, column=1, sticky=tk.S)
        ttk.Button(self, text="center", command=lambda: self.instruments.go_to_focus_location("center")).grid(row=2, column=1)
        ttk.Button(self, text="bottom", command=lambda: self.instruments.go_to_focus_location("bottom")).grid(row=3, column=1, sticky=tk.N)
        ttk.Button(self, text="left", command=lambda: self.instruments.go_to_focus_location("left")).grid(row=2, column=0, sticky=tk.E)
        ttk.Button(self, text="right", command=lambda: self.instruments.go_to_focus_location("right")).grid(row=2, column=2, sticky=tk.W)

        ttk.Button(self, text="finish", command=self.button_finish).grid(row=4, column=0, columnspan=3)

        self.grid(row=0, column=0, sticky="nsew")

    def button_finish(self):
        self.instruments.shutter.close_shutter()
        self.grid_forget()
        ProcessScreen(self.master, self.settings, self.instruments)


class ProcessScreen(ttk.Frame):
    def __init__(self, master, settings, instruments):
        self.master = master
        self.settings = settings
        self.instruments = instruments
        super().__init__(master)

        self.generator = SinePhasePlateGeneration(self.settings.radius,
                                                  self.settings.focal_length,
                                                  self.settings.wavelength,
                                                  self.settings.grating_width,
                                                  self.settings.y_min,
                                                  self.settings.y_peak_to_peak)

        self.images = self.generator.generate_images()
        self.current_image = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        ttk.Label(self, text="process monitoring", font=("Arial", 25)).grid(row=0, column=0, columnspan=3, pady=10)
        ttk.Label(self, text="Status:", font=("Arial", 20, 'bold')).grid(row=1, column=0, sticky=tk.E, padx=10)
        ttk.Label(self, text="Progress:", font=("Arial", 20, 'bold')).grid(row=2, column=0, sticky=tk.E, padx=10)
        ttk.Label(self, text="Time left:", font=("Arial", 20, 'bold')).grid(row=3, column=0, sticky=tk.E, padx=10)
        ttk.Label(self, text="Angular velocity:", font=("Arial", 20, 'bold')).grid(row=4, column=0, sticky=tk.E, padx=10)
        ttk.Label(self, text="Position:", font=("Arial", 20, 'bold')).grid(row=5, column=0, sticky=tk.E, padx=10)

        ttk.Button(self, text="Start", command=self.button_start).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=50)
        ttk.Button(self, text="Pause", command=self.button_pause).grid(row=6, column=0, columnspan=3, padx=10)
        ttk.Button(self, text="Cancel").grid(row=6, column=0, columnspan=3, sticky=tk.E, padx=50)

        self.grid(row=0, column=0, sticky="nsew")

    def button_start(self):
        image = self.images[-1]
        self.current_image = ImageDisplay(1)
        self.current_image.show_image(image)

    def button_pause(self):
        if self.current_image:
            self.current_image.destroy()


if __name__ == "__main__":
    App()
