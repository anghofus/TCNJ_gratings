import tkinter as tk
from tkinter import ttk
import json


class Settings:
    def __init__(self):
        self.__diameter = None
        self.__focal_length = None

        self.__exposure_time = 5
        self.__grating_width = 70
        self.__grating_height = 40
        self.__com_laser = "COM1"
        self.__com_motion_controller = "COM2"

    @property
    def diameter(self):
        return self.__diameter

    @diameter.setter
    def diameter(self, value:float):
        assert value >= 0, "diameter must be grater than zero!"
        self.__diameter = value

    @property
    def focal_length(self):
        return self.__focal_length

    @focal_length.setter
    def focal_length(self, value:float):
        assert value >= 0, "focal length must be grater than zero!"
        self.__focal_length = value

    @property
    def exposure_time(self):
        return self.__exposure_time

    @exposure_time.setter
    def exposure_time(self, value:float):
        assert value >= 0, "Exposure time must be greater than zero!"
        self.__exposure_time = value

    @property
    def grating_width(self):
        return self.__grating_width

    @grating_width.setter
    def grating_width(self, value:float):
        assert value >= 0, "Grating width must be greater than zero!"
        self.__grating_width = value

    @property
    def grating_height(self):
        return self.__grating_height

    @grating_height.setter
    def grating_height(self, value:float):
        assert value >= 0, "Grating height must be greater than zero!"

    @property
    def com_laser(self):
        return self.__com_laser

    @com_laser.setter
    def com_laser(self, value:str):
        self.__com_laser = value

    @property
    def com_motion_controller(self):
        return self.__com_motion_controller

    @com_motion_controller.setter
    def com_motion_controller(self, value:str):
        self.__com_motion_controller = value

    def read_from_jason(self):
        try:
            with open('settings.json', 'r') as settings_file:
                settings = json.load(settings_file)
                self.__exposure_time = settings['exposure_time']
                self.__grating_width = settings['grating_width']
                self.__grating_height = settings['grating_height']
                self.__com_laser = settings['com_laser']
                self.__com_motion_controller = settings['com_motion_controller']
        except FileNotFoundError:
            self.write_to_jason()

    def write_to_jason(self):
        with open('settings.json', 'w') as settings_file:
            settings = {
                'exposure_time': self.__exposure_time,
                'grating_width': self.__grating_width,
                'grating_height': self.__grating_height,
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
        super().__init__(master)

        self.settings = settings

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
        self.entry_diameter.grid(row=1, column=1, sticky=tk.W, padx=10)
        self.entry_focal_length = ttk.Entry(self)
        self.entry_focal_length.grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Button(self, text="apply").grid(row=3, column=0)
        ttk.Button(self, text="settings").grid(row=3, column=1)

        self.grid(row=0, column=0, sticky="nsew")

    def button_apply(self):
        self.settings.diameter = float(self.entry_diameter.get())
        self.settings.focal_length = float(self.entry_focal_length.get())


if __name__ == "__main__":
    App()
