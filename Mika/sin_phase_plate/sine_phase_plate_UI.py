import tkinter as tk
from tkinter import ttk
from sine_phase_plate_backend import *
import screeninfo
from PIL import Image, ImageTk
import queue
import logging
import coloredlogs


log_level = logging.INFO
logging.basicConfig(level=log_level)

logger = logging.getLogger(__name__)

field_styles = {
    'asctime': {'color': 'white'},  # Timestamp in white
    'levelname': {'color': 'blue', 'bold': True},  # Level name in bold blue
}
coloredlogs.install(
    level=log_level,
    logger=logger,
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    field_styles=field_styles)


class ImageDisplay(tk.Toplevel):
    def __init__(self, monitor: int):
        assert isinstance(monitor, int) and monitor >= 0, "Monitor must be a non-negative integer!"

        super().__init__()

        # Get information about all monitors
        monitors = screeninfo.get_monitors()

        if len(monitors) <= monitor:
            raise NoSecondMonitorError(f"Monitor index {monitor} is out of range. Found {len(monitors)} monitors.")

        # Select the specified monitor
        selected_monitor = monitors[monitor]

        self.geometry(f"{selected_monitor.width}x{selected_monitor.height}+{selected_monitor.x}+{selected_monitor.y}")
        self.configure(background='black')
        
        self.overrideredirect(True)

        # Initialize the label to None
        self.label = None

    def show_image(self, image_object):
        assert isinstance(image_object, Image.Image), "Image must be a PIL Image object"

        photo = ImageTk.PhotoImage(image_object)

        if self.label is None:
            # Create a label to hold the image
            self.label = tk.Label(self, image=photo)
            self.label.image = photo  # Keep a reference to avoid garbage collection
            self.label.pack()
        else:
            self.__update_image(photo)

    def thread_safe_show_image(self, image_object):
        assert isinstance(image_object, Image.Image), "Image must be a PIL Image object"
        self.after(0, self.show_image, image_object)

    def __update_image(self, photo):
        assert isinstance(photo, ImageTk.PhotoImage), "Image must be a PhotoImage object"

        # Update the image in the existing label
        self.label.configure(image=photo)
        self.label.image = photo  # Update the reference to avoid garbage collection


class NoSecondMonitorError(Exception):
    pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.settings = Settings()

        self.command_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.motion_control_monitor = MotionControlThreadMonitor()
        self.image_display = ImageDisplay(0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title("sine phase plate app")
        self.geometry("800x600")
        self.minsize(640, 480)

        self.protocol("WM_DELETE_WINDOW", self.close_application)

        self.start_screen = StartScreen(self)

        self.mainloop()

    def close_application(self):
        self.motion_control_monitor.kill_flag = True
        self.destroy()

    def error_check(self):
        if self.error_queue.empty():
            return True
        else:
            error = self.error_queue.get()
            self.error_queue.task_done()
            raise Exception(error)


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
        try:
            self.master.settings.radius = float(self.entry_radius.get())
            self.master.settings.focal_length = float(self.entry_focal_length.get())
        except Exception:
            return

        motion_control_thread = MotionControlThread(self.master.settings,
                                                    self.master.command_queue,
                                                    self.master.error_queue,
                                                    self.master.motion_control_monitor,
                                                    self.master.image_display)
        motion_control_thread.start()

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
        self.master.settings.center_point_y = int(self.entry_center_point_y.get())
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

        ttk.Button(self, text="top", command=lambda: self.go_to_focus_location("top")).grid(row=1,
                                                                                            column=1,
                                                                                            sticky=tk.S)
        ttk.Button(self, text="center", command=lambda: self.go_to_focus_location("center")).grid(row=2,
                                                                                                  column=1)
        ttk.Button(self, text="bottom", command=lambda: self.go_to_focus_location("bottom")).grid(row=3,
                                                                                                  column=1,
                                                                                                  sticky=tk.N)
        ttk.Button(self, text="left", command=lambda: self.go_to_focus_location("left")).grid(row=2,
                                                                                              column=0,
                                                                                              sticky=tk.E)
        ttk.Button(self, text="right", command=lambda: self.go_to_focus_location("right")).grid(row=2,
                                                                                                column=2,
                                                                                                sticky=tk.W)

        ttk.Button(self, text="finish", command=self.button_finish).grid(row=4, column=0, columnspan=3)

        self.grid(row=0, column=0, sticky="nsew")

    def button_finish(self):
        self.master.command_queue.put(['close_shutter'])
        self.master.command_queue.put(['go_to_focus_location', 'center'])
        self.error_check()
        self.grid_forget()
        ProcessScreen(self.master)

    def go_to_focus_location(self, focused_location: str):
        self.master.command_queue.put(['go_to_focus_location', focused_location])
        self.error_check()

    def error_check(self):
        self.master.error_check()
        if self.master.motion_control_monitor.busy_flag:
            self.after(500, self.error_check)


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
        self.master.command_queue.put(['print'])
        self.update_label()
        self.error_check()

    def method_button_cancel(self):
        self.master.close_application()

    def update_label(self):
        if self.master.motion_control_monitor.busy_flag:
            self.label_status_value.configure(text="running")
        else:
            self.label_status_value.configure(text="not running")
        self.label_progress_value.configure(text=f"{self.master.motion_control_monitor.ring_counter}"
                                                 f" / {self.master.motion_control_monitor.rings_total} "
                                                 f"({self.master.motion_control_monitor.percentage_done:.2f} %)")
        self.label_angular_velocity_value.configure(text=f"{self.master.motion_control_monitor.speed_axis3} deg/s")
        self.label_position_value.configure(text=f"X: {self.master.motion_control_monitor.position_axis1} mm "
                                                 f"Y: {self.master.motion_control_monitor.position_axis2} mm "
                                                 f"φ: {self.master.motion_control_monitor.position_axis3} deg")
        self.after(500, self.update_label)

    def error_check(self):
        self.master.error_check()
        if self.master.motion_control_monitor.busy_flag:
            self.after(500, self.error_check)


if __name__ == "__main__":
    App()
