import tkinter as tk
from tkinter import ttk
import json
from sine_phase_plate_backend import *


class Settings:
    def __init__(self):
        self.__diameter = None
        self.__focal_length = None

        self.__exposure_time = 5
        self.__grating_width = 70
        self.__grating_height = 40
        self.__wavelength = 633
        self.__y_min = 0
        self.__y_peak_to_peak = 128
        self.__com_laser = "COM1"
        self.__com_motion_controller = "COM2"

    @property
    def diameter(self):
        return self.__diameter

    @diameter.setter
    def diameter(self, value: float):
        assert value >= 0, "diameter must be grater than zero!"
        self.__diameter = value

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

    def read_from_json(self):
        try:
            with open('settings.json', 'r') as settings_file:
                settings = json.load(settings_file)
                self.__exposure_time = settings['exposure_time']
                self.__grating_width = settings['grating_width']
                self.__grating_height = settings['grating_height']
                self.__wavelength = settings['wavelength']
                self.__com_laser = settings['com_laser']
                self.__com_motion_controller = settings['com_motion_controller']
        except FileNotFoundError:
            self.write_to_json()

    def write_to_json(self):
        with open('settings.json', 'w') as settings_file:
            settings = {
                'exposure_time': self.__exposure_time,
                'grating_width': self.__grating_width,
                'grating_height': self.__grating_height,
                'wavelength': self.__wavelength,
                'com_laser': self.__com_laser,
                'com_motion_controller': self.__com_motion_controller
            }
            json.dump(settings, settings_file, indent=4)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.settings = Settings()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title("sine phase plate app")
        self.geometry("640x480")
        self.minsize(640, 480)

        self.start_screen = StartScreen(self, self.settings)

        self.mainloop()


class StartScreen(ttk.Frame):
    def __init__(self, master, settings):
        self.master = master
        self.settings = settings
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ttk.Label(self, text="lens parameters", font=("Arial", 25)).grid(row=0, column=0, columnspan=2, padx=10,pady=10)
        ttk.Label(self, text="diameter in mm", font=("Arial", 20)).grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        ttk.Label(self, text="focal length in mm" , font=("Arial", 20)).grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)

        self.entry_diameter = ttk.Entry(self)
        if self.settings.diameter is not None:
            self.entry_diameter.insert(0, self.settings.diameter)
        self.entry_diameter.grid(row=1, column=1, sticky=tk.W, padx=10)
        self.entry_focal_length = ttk.Entry(self)
        if self.settings.focal_length is not None:
            self.entry_focal_length.insert(0, self.settings.focal_length)
        self.entry_focal_length.grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Button(self, text="apply", command=self.button_apply).grid(row=3, column=0)
        ttk.Button(self, text="settings", command=self.button_settings).grid(row=3, column=1)

        self.grid(row=0, column=0, sticky="nsew")

    def button_apply(self):
        try:
            self.settings.diameter = float(self.entry_diameter.get())
            self.settings.focal_length = float(self.entry_focal_length.get())

            self.grid_forget()
            FocusingScreen(self.master, self.settings)
        except Exception as e:
            pass

    def button_settings(self):
        self.grid_forget()
        SettingsScreen(self.master, self.settings)


class SettingsScreen(ttk.Frame):
    def __init__(self, master, settings):
        self.master = master
        self.settings = settings
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
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="settings", font=("Arial", 25)).grid(row=0, column=0, columnspan=2, padx=10,pady=10)
        ttk.Label(self, text="exposure time in s", font=("Arial", 20)).grid(row=1, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="grating width in µm", font=("Arial", 20)).grid(row=2, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="wavelength in nm", font=("Arial", 20)).grid(row=3, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="y_min", font=("Arial", 20)).grid(row=4, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="y_peak_to_peak", font=("Arial", 20)).grid(row=5, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="grating height in µm", font=("Arial", 20)).grid(row=6, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="laser COM", font=("Arial", 20)).grid(row=7, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="motion controller COM", font=("Arial", 20)).grid(row=8, column=0, padx=10, sticky=tk.W)

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

        ttk.Button(self, text="apply", command=self.button_apply).grid(row=9, column=0)
        ttk.Button(self, text="cancel", command=self.button_cancel).grid(row=9, column=1)

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

        self.settings.write_to_json()

        self.grid_forget()
        StartScreen(self.master, self.settings)

    def button_cancel(self):
        self.grid_forget()
        StartScreen(self.master, self.settings)


class FocusingScreen(ttk.Frame):
    def __init__(self, master, settings):
        self.master = master
        self.settings = settings
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

        ttk.Button(self, text="up").grid(row=1, column=1, sticky=tk.S)
        ttk.Button(self, text="center").grid(row=2, column=1)
        ttk.Button(self, text="down").grid(row=3, column=1, sticky=tk.N)
        ttk.Button(self, text="left").grid(row=2, column=0, sticky=tk.E)
        ttk.Button(self, text="right").grid(row=2, column=2, sticky=tk.W)

        ttk.Button(self, text="finish", command=self.button_finish).grid(row=4, column=0, columnspan=3)

        self.grid(row=0, column=0, sticky="nsew")

    def button_finish(self):
        self.grid_forget()
        ProcessScreen(self.master, self.settings)


class ProcessScreen(ttk.Frame):
    def __init__(self, master, settings):
        self.master = master
        self.settings = settings
        super().__init__(master)

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

        ttk.Button(self, text="Continue").grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=50)
        ttk.Button(self, text="Pause").grid(row=6, column=0, columnspan=3, padx=10)
        ttk.Button(self, text="Cancel").grid(row=6, column=0, columnspan=3, sticky=tk.E, padx=50)

        self.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    App()
