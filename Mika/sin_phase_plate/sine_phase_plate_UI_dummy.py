import tkinter as tk
from tkinter import ttk
from sine_phase_plate_backend import *


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.settings = Settings()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title("sine phase plate app")
        self.geometry("800x600")
        self.minsize(640, 480)

        self.protocol("WM_DELETE_WINDOW", self.close_application)

        self.start_screen = StartScreen(self)

        self.mainloop()

    def close_application(self):
        self.destroy()


class StartScreen(ttk.Frame):
    def __init__(self, master):
        assert isinstance(master, App)

        self.master: App = master

        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ttk.Label(self, text="lens parameters", font=("Arial", 25)).grid(row=0, column=0, columnspan=2, padx=10,
                                                                         pady=10)
        ttk.Label(self, text="radius in mm", font=("Arial", 20)).grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)
        ttk.Label(self, text="focal length in mm", font=("Arial", 20)).grid(row=2, column=0, sticky=tk.E, padx=10,
                                                                            pady=10)

        self.entry_radius = ttk.Entry(self)
        if self.master.settings.radius is not None:
            self.entry_radius.insert(0, self.master.settings.radius)
        self.entry_radius.grid(row=1, column=1, sticky=tk.W, padx=10)
        self.entry_focal_length = ttk.Entry(self)
        if self.master.settings.focal_length is not None:
            self.entry_focal_length.insert(0, self.master.settings.focal_length)
        self.entry_focal_length.grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Button(self, text="apply", command=self.button_apply).grid(row=3, column=0)
        ttk.Button(self, text="settings", command=self.button_settings).grid(row=3, column=1)

        self.grid(row=0, column=0, sticky="nsew")

    def button_apply(self):
        self.grid_forget()
        FocusingScreen(self.master)

    def button_settings(self):
        self.grid_forget()
        SettingsScreen(self.master)


class SettingsScreen(ttk.Frame):
    def __init__(self, master):
        assert isinstance(master, App)

        self.master: App = master

        super().__init__(master)

        self.master.settings.read_from_json()

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
        self.grid_rowconfigure(11, weight=1)
        self.grid_rowconfigure(12, weight=1)
        self.grid_rowconfigure(13, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="settings", font=("Arial", 25)).grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        ttk.Label(self, text="exposure time in s", font=("Arial", 20)).grid(row=1, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="grating width in µm", font=("Arial", 20)).grid(row=2, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="grating height in µm", font=("Arial", 20)).grid(row=3, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="wavelength in nm", font=("Arial", 20)).grid(row=4, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="laser power in mW", font=("Arial", 20)).grid(row=5, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="y_min", font=("Arial", 20)).grid(row=6, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="y_peak_to_peak", font=("Arial", 20)).grid(row=7, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="center_point_x", font=("Arial", 20)).grid(row=8, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="center_point_y", font=("Arial", 20)).grid(row=9, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="port laser", font=("Arial", 20)).grid(row=10, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="port motion controller", font=("Arial", 20)).grid(row=11, column=0, padx=10, sticky=tk.W)
        ttk.Label(self, text="port shutter", font=("Arial", 20)).grid(row=12, column=0, padx=10, sticky=tk.W)

        self.entry_exposure_time = ttk.Entry(self)
        self.entry_exposure_time.insert(0, self.master.settings.exposure_time)
        self.entry_exposure_time.grid(row=1, column=1, padx=10)
        self.entry_grating_width = ttk.Entry(self)
        self.entry_grating_width.insert(0, self.master.settings.grating_width)
        self.entry_grating_width.grid(row=2, column=1, padx=10)
        self.entry_grating_height = ttk.Entry(self)
        self.entry_grating_height.insert(0, self.master.settings.grating_height)
        self.entry_grating_height.grid(row=3, column=1, padx=10)
        self.entry_wavelength = ttk.Entry(self)
        self.entry_wavelength.insert(0, self.master.settings.wavelength)
        self.entry_wavelength.grid(row=4, column=1, padx=10)
        self.entry_laser_power = ttk.Entry(self)
        self.entry_laser_power.insert(0, self.master.settings.laser_power)
        self.entry_laser_power.grid(row=5, column=1, padx=10)
        self.entry_y_min = ttk.Entry(self)
        self.entry_y_min.insert(0, self.master.settings.y_min)
        self.entry_y_min.grid(row=6, column=1, padx=10)
        self.entry_y_peak_to_peak = ttk.Entry(self)
        self.entry_y_peak_to_peak.insert(0, self.master.settings.y_peak_to_peak)
        self.entry_y_peak_to_peak.grid(row=7, column=1, padx=10)
        self.entry_center_point_x = ttk.Entry(self)
        self.entry_center_point_x.insert(0, self.master.settings.center_point_x)
        self.entry_center_point_x.grid(row=8, column=1, padx=10)
        self.entry_center_point_y = ttk.Entry(self)
        self.entry_center_point_y.insert(0, self.master.settings.center_point_y)
        self.entry_center_point_y.grid(row=9, column=1, padx=10)
        self.entry_port_laser = ttk.Entry(self)
        self.entry_port_laser.insert(0, self.master.settings.port_laser)
        self.entry_port_laser.grid(row=10, column=1, padx=10)
        self.entry_port_motion_controller = ttk.Entry(self)
        self.entry_port_motion_controller.insert(0, self.master.settings.port_motion_controller)
        self.entry_port_motion_controller.grid(row=11, column=1, padx=10)
        self.entry_port_shutter = ttk.Entry(self)
        self.entry_port_shutter.insert(0, self.master.settings.port_shutter)
        self.entry_port_shutter.grid(row=12, column=1, padx=10)

        ttk.Button(self, text="apply", command=self.button_apply).grid(row=13, column=0)
        ttk.Button(self, text="cancel", command=self.button_cancel).grid(row=13, column=1)

        self.grid(row=0, column=0, sticky="nsew")

    def button_apply(self):
        self.master.settings.exposure_time = float(self.entry_exposure_time.get())
        self.master.settings.grating_width = float(self.entry_grating_width.get())
        self.master.settings.grating_height = float(self.entry_grating_height.get())
        self.master.settings.wavelength = float(self.entry_wavelength.get())
        self.master.settings.laser_power = float(self.entry_laser_power.get())
        self.master.settings.y_min = int(self.entry_y_min.get())
        self.master.settings.y_peak_to_peak = int(self.entry_y_peak_to_peak.get())
        self.master.settings.center_point_x = float(self.entry_center_point_x.get())
        self.master.settings.center_point_y = float(self.entry_center_point_y.get())
        self.master.settings.port_laser = self.entry_port_laser.get()
        self.master.settings.port_motion_controller = self.entry_port_motion_controller.get()
        self.master.settings.port_shutter = self.entry_port_shutter.get()

        self.master.settings.write_to_json()

        self.grid_forget()
        StartScreen(self.master)

    def button_cancel(self):
        self.grid_forget()
        StartScreen(self.master)


class FocusingScreen(ttk.Frame):
    def __init__(self, master):
        assert isinstance(master, App)

        self.master: App = master

        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        ttk.Label(self, text="focusing", font=("Arial", 25)).grid(row=0,
                                                                  column=0,
                                                                  columnspan=3,
                                                                  pady=10)

        ttk.Button(self, text="top").grid(row=1,column=1,sticky=tk.S)
        ttk.Button(self, text="center").grid(row=2,column=1)
        ttk.Button(self, text="bottom").grid(row=3,column=1,sticky=tk.N)
        ttk.Button(self, text="left").grid(row=2,column=0,sticky=tk.E)
        ttk.Button(self, text="right").grid(row=2,column=2,sticky=tk.W)

        ttk.Button(self, text="finish", command=self.button_finish).grid(row=4, column=0, columnspan=3)

        self.grid(row=0, column=0, sticky="nsew")

    def button_finish(self):
        self.grid_forget()
        ProcessScreen(self.master)


class ProcessScreen(ttk.Frame):
    def __init__(self, master):
        assert isinstance(master, App)

        self.master: App = master

        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        ttk.Label(self, text="process monitoring", font=("Arial", 25)).grid(row=0, column=0, columnspan=3, pady=10)

        self.label_status = ttk.Label(self, text="Status:", font=("Arial", 20, 'bold'))
        self.label_status.grid(row=1, column=0, sticky=tk.E, padx=10)
        self.label_progress = ttk.Label(self, text="Progress:", font=("Arial", 20, 'bold'))
        self.label_progress.grid(row=2, column=0, sticky=tk.E, padx=10)
        self.label_angular_velocity = ttk.Label(self, text="Angular velocity:", font=("Arial", 20, 'bold'))
        self.label_angular_velocity.grid(row=3, column=0, sticky=tk.E, padx=10)
        self.label_position = ttk.Label(self, text="Position:", font=("Arial", 20, 'bold'))
        self.label_position.grid(row=4, column=0, sticky=tk.E, padx=10)

        self.label_status_value = ttk.Label(self, text="not started", font=("Arial", 20))
        self.label_status_value.grid(row=1, column=1, sticky=tk.W, padx=10)
        self.label_progress_value = ttk.Label(self, text="---", font=("Arial", 20))
        self.label_progress_value.grid(row=2, column=1, sticky=tk.W, padx=10)
        self.label_angular_velocity_value = ttk.Label(self, text="0", font=("Arial", 20))
        self.label_angular_velocity_value.grid(row=3, column=1, sticky=tk.W, padx=10)
        self.label_position_value = ttk.Label(self, text="---", font=("Arial", 20))
        self.label_position_value.grid(row=4, column=1, sticky=tk.W, padx=10)

        self.button_start = ttk.Button(self, text="Start", command=self.method_button_start)
        self.button_start.grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=50)
        self.button_cancel = ttk.Button(self, text="Cancel", command=self.method_button_cancel)
        self.button_cancel.grid(row=5, column=0, columnspan=3, sticky=tk.E, padx=50)

        self.grid(row=0, column=0, sticky="nsew")

    def method_button_start(self):
        self.label_status_value.configure(text="running")
        self.label_progress_value.configure(text=f"0"
                                                 f" / 35 "
                                                 f"(0 %)")
        self.label_angular_velocity_value.configure(text=f"3.98 deg/s")
        self.label_position_value.configure(text=f"X: 3.325 mm "
                                                 f"Y: 16.688 mm "
                                                 f"φ: 0 deg")

    def method_button_cancel(self):
        self.master.close_application()


if __name__ == "__main__":
    App()
