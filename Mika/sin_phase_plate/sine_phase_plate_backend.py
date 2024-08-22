import time

import numpy as np
import math
import scipy
from PIL import Image
from shutter_controller import *
from esp_controller import *
from laser_controller import *
import json
import threading
from threading import Thread
import queue


# TODO: write log statements


class Settings:
    def __init__(self):
        self.__radius = None
        self.__focal_length = None

        self.__exposure_time = 5
        self.__grating_width = 70
        self.__grating_height = 40
        self.__wavelength = 633
        self.__laser_power = 150
        self.__y_min = 0
        self.__y_peak_to_peak = 128
        self.__port_laser = "/dev/ttyUSB0"
        self.__port_motion_controller = "/dev/ttyUSB1"
        self.__port_shutter = "/dev/ttyUSB2"

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
    def laser_power(self):
        return self.__laser_power

    @laser_power.setter
    def laser_power(self, value: float):
        assert 30 <= value <= 300, "laser_power must be between 30 and 300 mW"
        self.__laser_power = value

    @property
    def y_min(self):
        return self.__y_min

    @y_min.setter
    def y_min(self, value: int):
        assert 0 <= value <= 255, "y_min must be between 0 and 255"
        self.__y_min = value

    @property
    def y_peak_to_peak(self):
        return self.__y_peak_to_peak

    @y_peak_to_peak.setter
    def y_peak_to_peak(self, value: int):
        assert 0 <= value <= 255, "y_peak_to_peak must be between 0 and 255"
        self.__y_peak_to_peak = value

    @property
    def port_laser(self):
        return self.__port_laser

    @port_laser.setter
    def port_laser(self, value: str):
        self.__port_laser = value

    @property
    def port_motion_controller(self):
        return self.__port_motion_controller

    @port_motion_controller.setter
    def port_motion_controller(self, value: str):
        self.__port_motion_controller = value

    @property
    def port_shutter(self):
        return self.__port_shutter

    @port_shutter.setter
    def port_shutter(self, value: str):
        self.__port_shutter = value

    def read_from_json(self):
        try:
            with open('settings.json', 'r') as settings_file:
                settings = json.load(settings_file)
                self.__exposure_time = settings['exposure_time']
                self.__grating_width = settings['grating_width']
                self.__grating_height = settings['grating_height']
                self.__wavelength = settings['wavelength']
                self.__laser_power = settings['laser_power']
                self.__y_min = settings['y_min']
                self.__y_peak_to_peak = settings['y_peak_to_peak']
                self.__port_laser = settings['port_laser']
                self.__port_motion_controller = settings['port_motion_controller']
                self.__port_shutter = settings['port_shutter']

        except FileNotFoundError:
            self.write_to_json()

    def write_to_json(self):
        with open('settings.json', 'w') as settings_file:
            settings = {
                'exposure_time': self.__exposure_time,
                'grating_width': self.__grating_width,
                'grating_height': self.__grating_height,
                'wavelength': self.__wavelength,
                'laser_power': self.__laser_power,
                'y_min': self.__y_min,
                'y_peak_to_peak': self.__y_peak_to_peak,
                'port_laser': self.__port_laser,
                'port_motion_controller': self.__port_motion_controller,
                'port_shutter': self.__port_shutter
            }
            json.dump(settings, settings_file, indent=4)


class SinePhasePlateGeneration:
    def __init__(self,
                 radius: float,
                 focal_length: float,
                 wavelength: float,
                 grating_width: int,
                 y_min: int,
                 y_peak_to_peak: int):

        self.__radius = radius / 1000
        self.__focal_length = focal_length / 1000
        self.__wavelength = wavelength / 10 ** 9
        self.__grating_width = grating_width / 10 ** 6

        self.__slm_px_width = 1920
        self.__slm_px_height = 1200
        self.__y_min = y_min
        self.__y_peak_to_peak = y_peak_to_peak

        self.__slm_count = int(self.__radius / self.__grating_width)
        self.__slm_count_diameter = self.__slm_count * 2
        self.__linespace_width = int(self.__slm_count * 1920)
        self.__pixel_width = self.__radius / self.__linespace_width

        self.__r_linespace = np.linspace(0, self.__linespace_width, self.__linespace_width)
        self.__waveform = []

    @property
    def wavelength(self):
        return self.__wavelength

    @property
    def y_min(self):
        return self.__y_min

    @y_min.setter
    def y_min(self, value):
        assert value > 0, "y_min must be grater than zero!"
        self.__y_min = value

    @property
    def y_peak_to_peak(self):
        return self.__y_peak_to_peak

    @y_peak_to_peak.setter
    def y_peak_to_peak(self, value):
        assert value > 0, "y_peak_to_peak must be grater than zero!"
        self.__y_peak_to_peak = value

    def generate_images(self):
        self.__generate_waveform()
        images = self.__generate_slm_images()
        return images

    def __generate_waveform(self):
        print("System: Generating waveform")
        for i in range(self.__linespace_width):
            r = i * self.__pixel_width
            self.__waveform.append(self.__chirp_function(r))
        print("System: Waveform generated")

    def __generate_slm_images(self):
        print("System: Generating SLM images")
        images = []
        image_array = np.zeros((self.__slm_px_height, self.__slm_px_width), dtype=np.uint8)
        for i in range(self.__slm_count):
            start = self.__slm_px_width * i
            stop = start + self.__slm_px_width
            for j in range(self.__slm_px_height):
                image_array[j] = self.__waveform[start:stop]
            image = Image.fromarray(image_array)
            images.append(image)
            print(f"System: {i+1} of {self.__slm_count} SLM images generated")
        return images

    def __chirp_function(self, r):
        f = self.__y_min + ((1 + scipy.signal.sawtooth(math.radians((2 * np.pi) / (self.__focal_length * self.__wavelength) * r ** 2))) / 2) * self.__y_peak_to_peak
        return f


class InstrumentController:
    def __init__(self, port_laser: str, port_esp: str, port_shutter: str):
        self.laser = LaserController(port_laser)
        self.esp = ESPController(port_esp)
        self.shutter = ShutterController(port_shutter)

        if not self.laser.connection_check():
            raise Exception('Laser not connected')
        if not self.esp.connection_check():
            raise Exception('ESP not connected')
        if not self.shutter.connection_check():
            raise Exception('Shutter not connected')

        self.esp.start_up()
        self.shutter.close_shutter()
        self.laser.send_command("L=1")

    def close_connection(self):
        self.laser.close_connection()
        self.esp.close_connection()
        self.shutter.close_connection()

    def go_to_focus_location(self, focus_location):
        if focus_location == "top":
            coordinates = (4.91, 22)
        elif focus_location == "bottom":
            coordinates = (4.91, 8)
        elif focus_location == "left":
            coordinates = (12, 16.51)
        elif focus_location == "right":
            coordinates = (0, 16.51)
        elif focus_location == "center":
            coordinates = (4.91, 16.51)
        else:
            raise Exception('invalid focus location')

        self.laser.send_command("P=30")
        self.shutter.close_shutter()

        self.esp.move_to_coordinates(coordinates[0], coordinates[1])
        self.esp.wait_for_movement()

    def sine_phase_plate_printing(self, image_index: int, grating_width: float, grating_height: float, exposure_time: float, laser_power: float):
        assert image_index >= 0, "image index must be grater than zero"
        assert grating_width > 0, "grating width must be grater than zero"
        assert exposure_time > 0, "exposure time must be grater than zero"
        assert 30 <= laser_power <= 300, "laser power must be between 30 and 300 mW"

        radius = grating_width * (image_index + 1)
        angular_speed = grating_height / (exposure_time * radius)

        self.esp.move_axis_relative(1, grating_width)
        self.esp.wait_for_movement()
        self.laser.send_command("L=1")
        self.laser.send_command(f"P={laser_power}")
        self.esp.move_axis_relative(3, 360, angular_speed)


class MotionControlThread(Thread):
    def __init__(self, settings, command_queue, error_queue, monitor, image_display):
        assert isinstance(settings, Settings), "settings must be a Settings object"
        assert isinstance(command_queue, queue.Queue), "command_queue must be a queue object"
        assert isinstance(error_queue, queue.Queue), "error_queue must be a queue object"
        assert isinstance(monitor, MotionControlThreadMonitor), "monitor must be a MotionControlThreadMonitor object"

        super().__init__()
        self.settings = settings
        self.command_queue = command_queue
        self.error_queue = error_queue
        self.monitor = monitor
        self.image_display = image_display
        self.instruments = InstrumentController(self.settings.port_laser, self.settings.port_motion_controller, self.settings.port_shutter)

        self.function_map = {
            'go_to_focus_location': self.instruments.go_to_focus_location,
            'print': self.instruments.sine_phase_plate_printing,
            'start_up': self.instruments.esp.start_up()
        }

    def run(self):
        while not self.monitor.kill_flag:
            if self.command_queue.empty():
                pass
            else:
                command = self.command_queue.get()
                self.__handle_command(command)
                self.command_queue.task_done()

    def __handle_command(self, command: list):
        function_str = command[0]
        parameters = command[1:]

        try:
            func = self.function_map.get(function_str, lambda: self.__default_function(function_str))
            func(parameters)
        except Exception as e:
            print(f"System: Error in {repr(function_str)}: {e}")
            self.error_queue.put(e)

    def __default_function(self, function_str):
        print(f"System: Command {function_str} unknown")
        self.error_queue.put(f"Command {repr(function_str)} unknown")

    def print(self, images):
        grating_width = self.settings.grating_width / 1000
        grating_height = self.settings.grating_height / 1000
        for image_index, image in enumerate(images):
            self.image_display.thread_safe_show_image(image)
            self.instruments.sine_phase_plate_printing(image_index, grating_width, grating_height, self.settings.exposure_time, self.settings.laser_power)
            self.wait()
            if self.monitor.kill_flag:
                break

    def wait(self):
        while any(self.instruments.esp.get_motion_status()):
            start_time = time.time()
            if self.monitor.kill_flag:
                self.instruments.esp.abort_movement()
            else:
                position = self.instruments.esp.get_axis_position()
                self.monitor.position_axis1 = position[0]
                self.monitor.position_axis2 = position[1]
                self.monitor.position_axis3 = position[2]
                speed = self.instruments.esp.get_axis_speed()
                self.monitor.speed_axis1 = speed[0]
                self.monitor.speed_axis2 = speed[1]
                self.monitor.speed_axis3 = speed[2]

                while time.time() < start_time + 0.5:
                    pass
# TODO: Implement pausing

class MotionControlThreadMonitor:
    def __init__(self):
        # Attributes:
        self.__busy_flag = None
        self.__kill_flag = False
        self.__abort_movement_flag = False
        self.__speed_axis1 = None
        self.__speed_axis2 = None
        self.__speed_axis3 = None
        self.__position_axis1 = None
        self.__position_axis2 = None
        self.__position_axis3 = None

        # Locks:
        self.__busy_flag_lock = threading.Lock()
        self.__kill_flag_lock = threading.Lock()
        self.__abort_movement_flag_lock = threading.Lock()
        self.__speed_axis1_lock = threading.Lock()
        self.__speed_axis2_lock = threading.Lock()
        self.__speed_axis3_lock = threading.Lock()
        self.__position_axis1_lock = threading.Lock()
        self.__position_axis2_lock = threading.Lock()
        self.__position_axis3_lock = threading.Lock()

    @property
    def busy_flag(self):
        with self.__busy_flag_lock:
            return self.__busy_flag

    @busy_flag.setter
    def busy_flag(self, value: bool):
        with self.__busy_flag_lock:
            self.__busy_flag = value

    @property
    def kill_flag(self):
        with self.__kill_flag_lock:
            return self.__kill_flag

    @kill_flag.setter
    def kill_flag(self, value: bool):
        with self.__kill_flag_lock:
            self.__kill_flag = value

    @property
    def abort_movement_flag(self):
        with self.__abort_movement_flag_lock:
            return self.__abort_movement_flag

    @abort_movement_flag.setter
    def abort_movement_flag(self, value: bool):
        with self.__abort_movement_flag_lock:
            self.__abort_movement_flag = value

    @property
    def speed_axis1(self):
        with self.__speed_axis1_lock:
            return self.__speed_axis1

    @speed_axis1.setter
    def speed_axis1(self, value):
        with self.__speed_axis1_lock:
            self.__speed_axis1 = value

    @property
    def speed_axis2(self):
        with self.__speed_axis2_lock:
            return self.__speed_axis2

    @speed_axis2.setter
    def speed_axis2(self, value):
        with self.__speed_axis2_lock:
            self.__speed_axis2 = value

    @property
    def speed_axis3(self):
        with self.__speed_axis3_lock:
            return self.__speed_axis3

    @speed_axis3.setter
    def speed_axis3(self, value):
        with self.__speed_axis3_lock:
            self.__speed_axis3 = value

    @property
    def position_axis2(self):
        with self.__position_axis2_lock:
            return self.__position_axis2

    @property
    def position_axis1(self):
        with self.__position_axis1_lock:
            return self.__position_axis1

    @position_axis1.setter
    def position_axis1(self, value):
        with self.__position_axis1_lock:
            self.__position_axis1 = value

    @position_axis2.setter
    def position_axis2(self, value):
        with self.__position_axis2_lock:
            self.__position_axis2 = value

    @property
    def position_axis3(self):
        with self.__position_axis3_lock:
            return self.__position_axis3

    @position_axis3.setter
    def position_axis3(self, value):
        with self.__position_axis3_lock:
            self.__position_axis3 = value
