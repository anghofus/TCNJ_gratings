# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 21:23:44 2024

@author: Julian Honecker

Already implemented:
initiate abort_deceleration  Done
add homing method to initialize - Done
Function to go to corners of the film to get in focus - Done
relative stitching (include manual) - Done
printing (include manual) - Done
absolute stitching (include manual) - Done
check if values are in range - Done
integrate into functions - Done
integrate check_homing to validate everything has been set - Done

To-Do, important:
if we hit limit switches????? Tell, reset, end everything?
Use and check Home_switch with position function
Recheck where we reset stuff and make sure it works and aligns with the rest

Maybe Implementation:
Integrate more Homing-Methods
if smt set wrong, repeat? or get out of process

Ideas, not important:
check if value already set?
?Function called reset-check
change baudrate to set second after that
integrate get_command after stuff to see result actually?


"""
import serial
import time


class MotorController:

    def __init__(self, port='COM7', baudrate=9600, timeout=1):
        # Create a serial connection to the motor
        # self.motor_port = 'COM7'
        # self.motor_baudrate =  9600
        # self.timeout = 1
        self.motor_port = port
        self.motor_baudrate = baudrate
        self.motor_timeout = timeout
        self.serial_motor = serial.Serial(self.motor_port, self.motor_baudrate, timeout=self.motor_timeout)
        self.motor_connection_is_open = True

        # Some baudrates we want to save
        self.initial_baudrate = 9600
        self.target_baudrate = 115200

        # Every Register we need
        self.test_register = 'r0x70 2 0'
        self.baudrate_register = 'r0x90'
        self.axis_register = 'r0xab'
        self.mode_register = 'r0x24'
        self.position_register = 'r0xca'
        self.velocity_register = 'r0xcb'
        self.acceleration_register = 'r0xcc'
        self.deceleration_register = 'r0xcd'
        self.jerk_register = 'r0xce'
        self.motion_profile_register = 'r0xc8'
        self.abort_deceleration_register = 'r0xcf'
        # Homing-Register
        self.homing_method_register = 'r0xc2'
        self.homing_fast_velocity_register = 'r0xc3'
        self.homing_slow_velocity_register = 'r0xc4'
        self.homing_accel_decel_register = 'r0xc5'
        self.homing_offset_register = 'r0xc6'

        # Register we need to read
        self.trajectory_register = 'r0xc9'
        self.event_register = 'r0xa0'
        self.current_position_register = 'r0x32'

        # Trajectory Register Bits
        self.trajectory_register_homing_error_bit = 11  # Bit 11 indicates there was an Error with Homing
        self.trajectory_register_referenced_bit = 12  # Bit 12 indicates if the axis is referenced
        self.trajectory_register_homing_bit = 13  # Bit 13 indicates if the drive is running a home command
        self.trajectory_register_move_aborted_bit = 14  # Bit 14 indicated, the last move was aborted
        self.trajectory_register_in_motion_bit = 15  # Bit 15 indicates motion completion

        self.axis_translations = {
            'X': '0',
            'Z': '1',
            '0': 'X',
            '1': 'Z'
        }

        self.available_axes = [axis_name for axis_name in self.axis_translations.keys() if axis_name.isalpha()]

        # To make sure we don't move without setting all parameters beforehand
        # No other problem will be looking for problems in Event Status Register  or Trajectory Register
        self.check_axis = {
            'X': {'motor_enabled': False, 'motion_profile_set': False, 'mode_set': False, 'velocity_set': False,
                  'acceleration_set': False, 'deceleration_set': False, 'position_set': False,
                  'no_other_problem': True},
            'Z': {'motor_enabled': False, 'motion_profile_set': False, 'mode_set': False, 'velocity_set': False,
                  'acceleration_set': False, 'deceleration_set': False, 'position_set': False, 'no_other_problem': True}
        }
        self.check_homing = {
            'X': {'motor_enabled': False, 'fast_velocity_set': False, 'slow_velocity_set': False,
                  'accel_decel_set': False, 'homing_method_chosen': False, 'home_offset_set': False},
            'Z': {'motor_enabled': False, 'fast_velocity_set': False, 'slow_velocity_set': False,
                  'accel_decel_set': False, 'homing_method_chosen': False, 'home_offset_set': False}
        }

        # Name of the event | ActualStatus | ImportantForErrorDetection | NormalStatus
        self.event_statuses = {
            'X': [
                {"Name": "Short circuit detected", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Drive over temperature", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Over voltage", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Under voltage", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Motor temperature sensor active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Feedback error", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Motor phasing error", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Current output limited", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Voltage output limited", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Positive limit switch active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Negative limit switch active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Enable input not active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Drive is disabled by software", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Trying to stop motor", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Motor brake activated", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "PWM outputs disabled", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Positive software limit condition", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Negative software limit condition", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Tracking error", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Tracking warning", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Drive has been reset", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Position has wrapped", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Drive fault", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Velocity limit has been reached", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Acceleration limit has been reached", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Position outside of tracking window", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Home switch is active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Set if trajectory is running or motor has not yet settled into position", "ActualStatus": 0,
                 "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Velocity window", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Phase not yet initialized", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Command fault. PWM or other command signal not present", "ActualStatus": 0,
                 "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Not defined", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0}
            ],
            'Z': [
                {"Name": "Short circuit detected", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Drive over temperature", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Over voltage", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Under voltage", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Motor temperature sensor active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Feedback error", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Motor phasing error", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Current output limited", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Voltage output limited", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Positive limit switch active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Negative limit switch active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Enable input not active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},  # If 1, motor wont move
                {"Name": "Drive is disabled by software", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Trying to stop motor", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},  # If 1, motor wont move
                {"Name": "Motor brake activated", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},  # If 1, motor wont move
                {"Name": "PWM outputs disabled", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},  # If 1, motor wont move
                {"Name": "Positive software limit condition", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Negative software limit condition", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Tracking error", "ActualStatus": 0, "ImportantForErrorDetection": False, "NormalStatus": 0},
                {"Name": "Tracking warning", "ActualStatus": 0, "ImportantForErrorDetection": False, "NormalStatus": 0},
                {"Name": "Drive has been reset", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Position has wrapped", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Drive fault", "ActualStatus": 0, "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Velocity limit has been reached", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Acceleration limit has been reached", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Position outside of tracking window", "ActualStatus": 0, "ImportantForErrorDetection": False,
                 "NormalStatus": 0},
                {"Name": "Home switch is active", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Set if trajectory is running or motor has not yet settled into position", "ActualStatus": 0,
                 "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Velocity window", "ActualStatus": 0, "ImportantForErrorDetection": False, "NormalStatus": 0},
                {"Name": "Phase not yet initialized", "ActualStatus": 0, "ImportantForErrorDetection": True,
                 "NormalStatus": 0},
                {"Name": "Command fault. PWM or other command signal not present", "ActualStatus": 0,
                 "ImportantForErrorDetection": True, "NormalStatus": 0},
                {"Name": "Not defined", "ActualStatus": 0, "ImportantForErrorDetection": False, "NormalStatus": 0}
            ]
        }
        self.current_index = 0
        self.initialized = 0
        self.start = 0
        self.focus_init = 0
        
        self.rows = 0
        self.columns = 0
        self.max_exp_time = 0
        self.time_movement = 2
        self.current_line = 0
        self.speed_printing = 0
        self.length_movement = 0

        # Stuff for Stitching:
        self.SLM_stitching_pixel_X = 484
        self.SLM_stitching_pixel_Z = 290
        self.SLM_stitching_half_pixel = (self.SLM_stitching_pixel_X / 2)

        # Stuff needed explicitly for Printing:
        self.SLM_printing_pixel = 480
        self.SLM_printing_height = 290
        self.SLM_printing_width = 480
        # WHatever we override from the other Pixel for example 4
        self.SLM_printing_offset = 4
        self.SLM_printing_half_pixel = (self.SLM_printing_pixel / 2)
        self.SLM_printing_height_difference = (self.SLM_printing_pixel - self.SLM_printing_height)
        self.SLM_printing_half_height = (self.SLM_printing_height / 2)


        self.height_grading = 0
        self.width_grading = 0

        self.absolute_position_X = []
        self.absolute_position_Z = []
        
        self.start_pos_X = 0
        self.start_pos_Z = 0

        # in counts
        self.max_size = 43840
        self.max_limit = (self.max_size / 2)
        self.min_limit = (-1 * self.max_limit)
        
        # Whether we are inside our set Parameters or not
        self.OutOfBoundaries = False  # Initialize boundary flag

    def close_connection(self):
        if self.motor_connection_is_open:
            self.serial_motor.close()
            self.motor_connection_is_open = False

    def open_connection(self):
        if not self.motor_connection_is_open:
            self.serial_motor = serial.Serial(self.motor_port, self.motor_baudrate, timeout=self.motor_timeout)
            self.motor_connection_is_open = True

    def translate_axis(self, axis):
        """
        Only for Low-Level, not meant for the User!
        Translates axis between 'X', 'Z' and '0', '1'.
        If input is 'X', 'x', 'Z', or 'z', returns '0' or '1'.
        If input is '0' or '1', returns 'X' or 'Z'.
        Converts lowercase 'x' and 'z' to uppercase before translation.
        """
        # Convert input to uppercase if it's 'x' or 'z'
        axis_upper = axis.upper() if axis in ['x', 'z'] else axis
        return self.axis_translations.get(axis_upper, None)

    def normalize_axis(self, axis):
        """Normalize the axis input to uppercase to ensure case-insensitive comparison."""
        if axis is not None:
            return axis.upper()
        return axis

    def all_axes_check(self, axis):
        """
        Determines the axes to initialize based on input.
        If 'all' is specified, returns both 'X' and 'Z'.
        Otherwise, returns a list containing the specified axis.
        """
        if axis is not None:
            if axis.lower() == 'all':
                return self.available_axes
            else:
                return [axis.upper()]
        else:
            return [axis]

    # Set any parameter and check for Response
    def set_command(self, set_register, axis=None):
        """Send a set command to the motor controller and return the response."""
        if axis is None or axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            # Construct the full command with optional axis prefix
            if axis is not None:
                axis_name = self.translate_axis(axis)
                full_set_command = f'{axis_name} s {set_register}'
            else:
                full_set_command = f's {set_register}'

            # ser.write(bytes('{0}\r'.format(full_set_command), 'utf-8'))  # Send the command
            self.serial_motor.write(bytes(f'{full_set_command}\r', 'utf-8'))
            time.sleep(0.03)

            response = b''
            if self.serial_motor.in_waiting:
                response += self.serial_motor.read(self.serial_motor.in_waiting)
                decoded = response.decode('utf-8', errors='ignore').strip()
                # print('{}: {}'.format(full_set_command, decoded))
                if decoded.lower().endswith("ok"):
                    print(f'Set command "{full_set_command.strip()}" successful: {decoded}')
                    return True
                else:
                    print(f'Set command "{full_set_command.strip()}" received no ok, instead received: {decoded}')
                    return False
            else:
                print(f"No response received to '{full_set_command.strip()}' command.")
                return None
        else:
            print("Axis was not correctly set. Please set to 'X', 'Z' or None")

    # Read any Parameter
    def get_command(self, get_register, axis=None):
        """Read a parameter from the drive."""
        if axis is None or axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            # Construct the full command with optional axis prefix
            if axis is not None:
                axis_name = self.translate_axis(axis)
                full_get_command = f'{axis_name} g {get_register}'
            else:
                full_get_command = f'g {get_register}'

            # ser.write(bytes('{0}\r'.format(full_get_command), 'utf-8'))  # Send the command
            self.serial_motor.write(bytes(f'{full_get_command}\r', 'utf-8'))
            time.sleep(0.03)

            response = b''
            if self.serial_motor.in_waiting:
                response += self.serial_motor.read(self.serial_motor.in_waiting)
                decoded = response.decode('utf-8', errors='ignore').strip()
                if decoded.startswith('v'):
                    # Assuming the value is always after 'v '
                    # This will split the response into ['v', 'value'] and assign 'value' accordingly
                    _, value = decoded.split(' ', 1)
                    print(f'Get command "{full_get_command.strip()}" received: {value}')
                    return value
                else:
                    print(
                        f'Get Command "{full_get_command.strip()}" failed to read parameter or parameter not found. Answer: "{decoded}"')
                    return None
            else:
                print(f"No response received to '{full_get_command.strip()}' command.")
                return None
        else:
            print("Axis was not correctly set. Please set to 'X', 'Z' or None")

    # Copy any parameter, we are currently not using it
    def copy_command(self, copy_register, axis=None):
        """Copy a parameter from the RAM or FLash to FLash or RAM"""
        if axis is None or axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            # Construct the full command with optional axis prefix
            if axis is not None:
                axis_name = self.translate_axis(axis)
                full_copy_command = f'{axis_name} c {copy_register}'
            else:
                full_copy_command = f'c {copy_register}'

            self.serial_motor.write(bytes(f'{full_copy_command}\r', 'utf-8'))  # Corrected format string usage
            # ser.write(bytes('{0}\r'.format(full_copy_command), 'utf-8'))
            time.sleep(0.03)  # Short delay to allow the device to process the command

            response = b''
            if self.serial_motor.in_waiting:
                response += self.serial_motor.read(self.serial_motor.in_waiting)
                decoded = response.decode('utf-8', errors='ignore').strip()
                if decoded.lower().endswith("ok"):
                    print(f'Copy command "{full_copy_command.strip()}" successful: {decoded}')
                    return True
                else:
                    print(f'Copy command "{full_copy_command.strip()}" received no ok, instead received: {decoded}')
                    return False
            else:
                print(f'No response received to "{full_copy_command.strip()}" command.')
                return None
        else:
            print("Axis was not correctly set. Please set to 'X', 'Z' or None")

    # Reset all or specific drives
    def reset_command(self, axis=None):
        """Allows to reset the drives"""
        if axis is None or axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            # Construct the full command with optional axis prefix
            if axis is not None:
                # Ensure this translates 'X'/'Z' to numeric correctly
                axis_name = self.translate_axis(axis)
                full_reset_command = f'{axis_name} r'
            else:
                full_reset_command = 'r'
            # self.serial_motor.write(bytes('{0}\r'.format(full_reset_command), 'utf-8'))
            self.serial_motor.write(bytes(f'{full_reset_command}\r', 'utf-8'))
            # self.serial_motor.write(bytes(f'{full_reset_command}\r', 'utf-8'))
            time.sleep(1)

            print("Reset command has been sent!")
            self.serial_motor.baudrate = self.initial_baudrate

            self.reset_status(self.check_axis, axis=axis)
            self.reset_status(self.check_homing, axis=axis)
            '''
            # Reset status indicators for all or specific axis
            if axis is not None:
                # Reset only the specified axis
                for parameter in self.check_axis[axis]:  # Ensure axis is 'X' or 'Z' if those are the keys
                    self.check_axis[axis][parameter] = False
                self.update_events(axis=axis)
                print(f"Reset and status indicators updated for axis {axis}.")
            else:
                # Reset for all axes
                for each_axis in [axis for axis in self.axis_translations if axis.isalpha()]:
                    # print(each_axis)  # This will print 'X' and 'Z'
                    for parameter in self.check_axis[each_axis]:
                        self.check_axis[each_axis][parameter] = False
                    self.update_events(axis=each_axis)
                print("Reset and status indicators updated for all axes.")
            '''
        else:
            print("Axis was not correctly set. Please set to 'X', 'Z' or None")

    def trajectory_generator_command(self, axis=None, trajectory_mode=None):
        # We only want a specific axis and not a general command here
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            # Map trajectory_mode to corresponding numerical value
            mode_mapping = {'abort': 0, 'move': 1, 'home': 2}
            if trajectory_mode in mode_mapping:
                trajectory_mode = mode_mapping[trajectory_mode]
            else:
                raise ValueError("Invalid mode for the Trajectory Generator. Please choose 'abort', 'move', or 'home'.")
            # Construct the full command with optional axis prefix
            if axis is not None:
                axis_name = self.translate_axis(axis)
                full_trajectory_command = f'{axis_name} t {trajectory_mode}'
            else:
                full_trajectory_command = f't {trajectory_mode}'
            # ser.write(bytes('{0}\r'.format(full_trajectory_command), 'utf-8'))
            self.serial_motor.write(bytes(f'{full_trajectory_command}\r', 'utf-8'))
            time.sleep(0.1)

            response = b''
            if self.serial_motor.in_waiting:
                response += self.serial_motor.read(self.serial_motor.in_waiting)
                decoded = response.decode('utf-8', errors='ignore').strip()
                if decoded.lower().endswith("ok"):
                    print(f'Trajectory command "{full_trajectory_command.strip()}" successful: {decoded}')
                    return True
                else:
                    print(f'Trajectory command "{full_trajectory_command.strip()}" failed: {decoded}')
                    return False
            else:
                print(f"No response received to '{full_trajectory_command.strip()}' command.")
                return None
        else:
            print("Axis was not correctly set. Please set to 'X', 'Z'. None is not allowed for movements!")

    def reset_status(self, status_type, axis=None):
        """
        Reset status indicators for all or a specific axis for either 'check_axis' or 'check_homing'.

        Parameters:
            status_type (dict): The status indicators dictionary to reset ('check_axis' or 'check_homing').
            axis (str, optional): The specific axis to reset ('X', 'Z'). If None, resets all axes.
        """
        if axis is not None:
            # Reset only the specified axis
            for parameter in status_type[axis]:  # Ensure axis is 'X' or 'Z' if those are the keys
                status_type[axis][parameter] = False
            self.update_events(axis=axis)
            print(f"Reset and status indicators updated for axis {axis}.")
        else:
            # Reset for all axes
            for each_axis in [axis for axis in self.axis_translations if axis.isalpha()]:
                for parameter in status_type[each_axis]:
                    status_type[each_axis][parameter] = False
                self.update_events(axis=each_axis)
            print("Reset and status indicators updated for all axes.")

    # Read either a specific event or all
    def read_event_status(self, axis=None, specific_event=None):
        # Only allowed axes
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # Only available Events
            status_value_str = self.get_command(self.event_register, axis)
            if status_value_str is not None:
                # Convert the status value from dec to integer directly since "v" is already stripped
                status_value = int(status_value_str)

                # Determine the range of events to update: specific event or all
                if specific_event is None:
                    events_to_update = range(len(self.event_statuses[axis]))
                elif specific_event is not None and 0 <= specific_event < len(self.event_statuses[axis]):
                    events_to_update = [specific_event]
                else:
                    raise ValueError("Specific event index is out of range.")

                for i in events_to_update:
                    event = self.event_statuses[axis][i]
                    event["ActualStatus"] = (status_value >> i) & 1  # Update the ActualStatus
                    # print(f"Updated ActualStatus for {event['Name']} to {event['ActualStatus']}.")
            else:
                raise ValueError("Failed to read the Event Status Register.")
        else:
            raise ValueError("Invalid axis or no axis specified.")

    # Check either a specific event or all
    def check_event_status(self, axis=None, specific_event=None):
        discrepancies = []  # Collects descriptions of all discrepancies found
        # Only allowed axes
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # Determine the range of events to update: specific event or all
            if specific_event is None:
                events_to_check = range(len(self.event_statuses[axis]))
            elif specific_event is not None and 0 <= specific_event < len(self.event_statuses[axis]):
                events_to_check = [specific_event]
            else:
                raise ValueError("Specific event index is out of range.")
            for i in events_to_check:
                event = self.event_statuses[axis][i]
                if event["ActualStatus"] != event["NormalStatus"]:
                    discrepancies.append(f"Bit {i} ({event['Name']}) indicates a problem.")
                    if specific_event is not None:
                        # If checking a specific event and a discrepancy is found, set a targeted message and break
                        discrepancies.append(f"Specific event that has been chosen disrupted: {event['Name']}")
                        break  # Stop processing as we found the discrepancy in the specific event

            # Update the 'no_other_problem' flag in `check_axis` based on findings
            self.check_axis[axis]['no_other_problem'] = not discrepancies
            # Report findings
            if discrepancies:
                print(f"Discrepancies found for axis {axis}:")
                # for discrepancy in discrepancies:
                # print(discrepancy)
            else:
                status_message = "No discrepancies found." if specific_event is None else "Specific event matches its normal state."
                print(status_message)
        else:
            raise ValueError("Invalid axis or no axis specified.")

    def update_events(self, axis=None, specific_event=None):
        self.read_event_status(axis, specific_event)
        self.check_event_status(axis, specific_event)

    # Attempt to connect to the motor
    def attempt_communication(self, baud_rate, max_attempts=5):
        """
        Attempt to communicate with the motor using a list of baud rates until successful or until attempts are exhausted.
        Args:
        baud_rate: The baud rate to attempt.
        max_attempts: Maximum number of attempts.
        Returns:
        success flag, successful baud rate or None
        """
        original_baudrate = self.serial_motor.baudrate  # Store the initial baud rate to restore later if needed
        print(f"Initial baud rate: {self.initial_baudrate}. Attempting communication at {baud_rate}...")

        self.serial_motor.baudrate = baud_rate  # Adjust Baudrate for current attempt
        for attempt in range(max_attempts):
            print(f"Attempt {attempt + 1} at {baud_rate} baud...")
            try:
                if self.set_command(self.test_register):
                    print(f"Communication successful at {baud_rate}.")
                    return True, baud_rate
                else:
                    print(f"No 'ok' response at {baud_rate} baud in attempt {attempt + 1}.")
                    if attempt >= 4:  # If more than 3 attempts have been made, attempt a reset
                        print(f"More than 2 attempts made, automatic reset to {self.initial_baudrate}...")
                        self.serial_motor.baudrate = self.initial_baudrate
                    time.sleep(0.1)
            except serial.SerialException as e:
                print(f"Error attempting to open serial port at {baud_rate} baud in attempt {attempt + 1}: {e}")
                time.sleep(0.1)
        self.serial_motor.baudrate = original_baudrate
        return False, original_baudrate

    # Change Baudrate
    def set_baudrate(self, target_baud_rate):
        """Attempt to change the baud rate and verify it by sending a test command."""
        # Change baud rate to target_baud_rate
        current_baudrate = self.serial_motor.baudrate
        baudrate_command = f'{self.baudrate_register} {target_baud_rate}'
        print(f"Attempting to change baud rate to {target_baud_rate}...")
        self.set_command(baudrate_command)  # Send command to change baudrate
        self.serial_motor.baudrate = target_baud_rate  # Change baudrate to target
        time.sleep(0.03)  # Give some time for the device to adjust to the new baud rate

        print("Verifying baud rate change...")
        verification_response = self.set_command(self.test_register)  # Send verification command

        if verification_response is True:
            print(f"Baudrate successfully changed to {target_baud_rate} and verified.")
        else:
            print("Failed to verify baud rate change, reset to 9600. Check device and command.")
            self.serial_motor.baudrate = current_baudrate

    # Checks the limits of the variables
    def check_limit_for_values(self, to_check, value):
        if to_check == 'position':
            value_for_position = value
            if (value_for_position > 300000) or (value_for_position < -300000):
                raise ValueError(f"The Value {value_for_position} for Position is Invalid")
            else:
                print("Value for Position is Valid")

        elif to_check == 'velocity':
            value_for_velocity = value
            if (value_for_velocity > 40000) or (value_for_velocity < 0.1):
                raise ValueError(f"The Value {value_for_velocity} for Velocity is Invalid")
            else:
                print("Value for Velocity is Valid")

        elif to_check == 'acceleration':
            value_for_acceleration = value
            if (value_for_acceleration > 100000) or (value_for_acceleration < 10):
                raise ValueError(f"The Value {value_for_acceleration} for Acceleration is Invalid")
            else:
                print("Value for Acceleration is Valid")

        elif to_check == 'deceleration':
            value_for_deceleration = value
            if (value_for_deceleration > 100000) or (value_for_deceleration < 10):
                raise ValueError(f"The Value {value_for_deceleration} for Deceleration is Invalid")
            else:
                print("Value for Deceleration is Valid")

        elif to_check == 'jerk':
            value_for_jerk = value
            if (value_for_jerk > 1000000) or (value_for_jerk < 100):
                raise ValueError(f"The Value {value_for_jerk} for Jerk is Invalid")
            else:
                print("Value for Jerk is Valid")

        elif to_check == 'abort_deceleration':
            value_for_abort_deceleration = value
            if (value_for_abort_deceleration > 1000000) or (value_for_abort_deceleration < 10):
                raise ValueError(f"The Value {value_for_abort_deceleration} for Abort-Deceleration is Invalid")
            else:
                print("Value for Abort-Deceleration is Valid")

        elif to_check == 'fast_velocity':
            value_for_fast_velocity = value
            if (value_for_fast_velocity > 40000) or (value_for_fast_velocity < 0.1):
                raise ValueError(f"The Value {value_for_fast_velocity} for Fast-Velocity is Invalid")
            else:
                print("Value for Fast-Velocity is Valid")

        elif to_check == 'slow_velocity':
            value_for_slow_velocity = value
            if (value_for_slow_velocity > 40000) or (value_for_slow_velocity < 0.1):
                raise ValueError(f"The Value {value_for_slow_velocity} for Slow-Velocity is Invalid")
            else:
                print("Value for Slow-Velocity is Valid")

        elif to_check == 'accel_decel':
            value_for_accel_decel = value
            if (value_for_accel_decel > 100000) or (value_for_accel_decel < 10):
                raise ValueError(f"The Value {value_for_accel_decel} for Accel-Decel is Invalid")
            else:
                print("Value for Accel-Decel is Valid")

        elif to_check == 'home_offset':
            value_for_home_offset = value
            if (value_for_home_offset > 150000) or (value_for_home_offset < -150000):
                raise ValueError(f"The Value {value_for_home_offset} for Home-Offset is Invalid")
            else:
                print("Value for Home-Offset is Valid")

        else:
            raise ValueError(f"The chosen Variable {to_check} does not exist!")

    # Allowed to check all Axes for their current position
    def current_position(self, axis=None):
        axes = self.all_axes_check(axis)
        positions = {}
        for each_axis in axes:
            if each_axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
                value_str = self.get_command(self.current_position_register, axis=each_axis)
                print(f'Current position: {value_str}')

                # Convert the status value from dec to integer directly since "v" is already stripped
                value = int(value_str)
                positions[each_axis] = value
                # if value == 0:
                # set_current_position_as_home(each_axis)
                # elif value < 0:
                # homing_with_home_switch(each_axis, 'positive')
                # elif value > 0:
                # homing_with_home_switch(each_axis, 'negative')
            else:
                raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

        if len(axes) == 1:
            # If only one axis was checked, return its position directly
            return positions.get(axes[0], None)
        else:
            # If multiple axes were checked, return a dictionary of their positions
            return positions

    # Enable any Axes
    def enable_axis(self, axis=None):
        """Enable a specific axis."""
        axes = self.all_axes_check(axis)
        for each_axis in axes:
            # Check if the axis is correctly specified
            if each_axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
                self.set_command(f'{self.axis_register} 1', axis=each_axis)
                # Update the 'motor_enabled' status for the specified axis in the check_axis dictionary
                self.check_axis[each_axis]['motor_enabled'] = True
                self.check_homing[each_axis]['motor_enabled'] = True
                print(f"Axis {each_axis} enabled.")
                self.update_events(each_axis)
            else:
                raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Disable any Axes
    def disable_axis(self, axis=None):
        """Disable a specific axis."""
        axes = self.all_axes_check(axis)
        for each_axis in axes:
            # Check if the axis is correctly specified
            if each_axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
                self.set_command(f'{self.axis_register} 0', axis=each_axis)
                # Update the 'motor_enabled' status for the specified axis in the check_axis dictionary
                self.check_axis[each_axis]['motor_enabled'] = False
                self.check_homing[each_axis]['motor_enabled'] = False
                print(f"Axis {each_axis} disabled.")
                self.update_events(each_axis)
            else:
                raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Set the mode for the motor to use Servo or Stepper
    def set_mode(self, mode='servo', axis=None):
        """Set the drive mode to Servo or Stepper."""
        axes = self.all_axes_check(axis)
        for each_axis in axes:
            if each_axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
                if mode == 'servo':
                    mode_value = 21
                    self.set_command(f'{self.mode_register} {mode_value}', axis=each_axis)
                    # Update the 'mode_set' status for the specified axis in the check_axis dictionary
                    self.check_axis[each_axis]['mode_set'] = True
                    print(f"Axis {each_axis} uses a {mode}-motor.")
                elif mode == 'stepper':
                    mode_value = 31
                    self.set_command(f'{self.mode_register} {mode_value}', axis=each_axis)
                    # Update the 'mode_set' status for the specified axis in the check_axis dictionary
                    self.check_axis[each_axis]['mode_set'] = True
                    print(f"Axis {each_axis} uses a {mode}-motor.")
                else:
                    raise ValueError("Invalid mode for motor. Please choose 'servo' or 'stepper'.")
            else:
                raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Position
    def set_position(self, position, axis=None):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # If the axis is correctly specified, proceed with sending the command
            self.check_limit_for_values(to_check='position', value=position)
            position = int(position)
            self.set_command(f'{self.position_register} {position}', axis=axis)  # Position or distance\
            self.check_axis[axis]['position_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Velocity
    def set_velocity(self, velocity, axis=None):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # If the axis is correctly specified, proceed with sending the command
            self.check_limit_for_values(to_check='velocity', value=velocity)
            velocity_unit = int(velocity * 10)
            self.set_command(f'{self.velocity_register} {velocity_unit}', axis=axis)  # Velocity
            self.check_axis[axis]['velocity_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Acceleration
    def set_acceleration(self, acceleration, axis=None):

        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # If the axis is correctly specified, proceed with sending the command
            self.check_limit_for_values(to_check='acceleration', value=acceleration)
            acceleration_unit = int(acceleration * 0.1)
            self.set_command(f'{self.acceleration_register} {acceleration_unit}', axis=axis)  # Acceleration
            self.check_axis[axis]['acceleration_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Deceleration
    def set_deceleration(self, deceleration, axis=None):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # If the axis is correctly specified, proceed with sending the command
            self.check_limit_for_values(to_check='deceleration', value=deceleration)
            deceleration_unit = int(deceleration * 0.1)
            self.set_command(f'{self.deceleration_register} {deceleration_unit}', axis=axis)  # Deceleration
            self.check_axis[axis]['deceleration_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Jerk
    def set_jerk(self, jerk, axis=None):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # If the axis is correctly specified, proceed with sending the command
            self.check_limit_for_values(to_check='jerk', value=jerk)
            jerk_unit = int(jerk * 0.01)
            self.set_command(f'{self.jerk_register} {jerk_unit}', axis=axis)  # Jerk
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Abort_deceleration_rate
    def set_abort_deceleration(self, abort_deceleration, axis=None):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # If the axis is correctly specified, proceed with sending the command
            self.check_limit_for_values(to_check='abort_deceleration', value=abort_deceleration)
            abort_deceleration_unit = int(abort_deceleration * 0.1)
            self.set_command(f'{self.abort_deceleration_register} {abort_deceleration_unit}', axis=axis)  # Abort deceleration rate
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Allows to change mode
    def configure_motion_profile(self, mode='absolute', shape='trapezoidal', axis=None):
        """Configure the movement profile by specifying mode and profile shape."""
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # Define profile type values based on mode and profile shape combinations
            profile_values = {
                ('absolute', 'trapezoidal'): 0,
                ('absolute', 's_curve'): 1,
                ('relative', 'trapezoidal'): 256,
                ('relative', 's_curve'): 257,
                ('velocity', None): 2  # Assuming 'velocity' mode doesn't combine with profile shapes
            }
            # Construct the command with the specified mode and profile shape
            motion_type = profile_values.get((mode, shape))
            if motion_type is not None:
                self.set_command(f'{self.motion_profile_register} {motion_type}', axis=axis)
                self.check_axis[axis]['motion_profile_set'] = True
                # Complete the print statement to include the mode and shape
                print(f"Motion profile for axis {axis} set to mode '{mode}' with shape '{shape}'.")
            else:
                print(f"Invalid mode/profile_shape combination: {mode}/{shape}")
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # rework to only use X and Z or all, since we check multiple axis
    def check_motion_parameters(self, checklist, axes_to_check):
        # Ensure axes_to_check is a list to simplify processing
        if isinstance(axes_to_check, str):
            axes_to_check = self.all_axes_check(axes_to_check)
        results = {}
        for each_axis in axes_to_check:
            if each_axis is not None:
                each_axis = self.normalize_axis(each_axis)  # Ensure axis is in the correct format
            self.update_events(each_axis)
            # Check if the axis is present in the check_axis dictionary
            if each_axis in self.check_axis:
                # Check if all parameters for the axis are True
                if all(checklist[each_axis].values()):
                    results[each_axis] = True
                    print(f"All parameters set for axis {each_axis}.")
                else:
                    results[each_axis] = False
                    print(f'Some parameters are not set for axis {each_axis}.')
                    raise ValueError("Axis was not ready")
            else:
                results[each_axis] = None
                print(f"Axis {each_axis} is not recognized.")
        # This function can be used with print to print the status of each parameter
        # for the specified axes and returns a dictionary with the results for each axis.
        return results
    
    def wait_for_motion_completion(self, axis=None):
        """Wait until the motion on the specified axis is completed."""
        # Give the drives time to start moving
        time.sleep(1)
        while True:
            # Construct the command to read the Trajectory Status Register
            status_value_str = self.get_command(self.trajectory_register, axis)
    
            # If get_command returns None, log an error and continue with the next iteration
            if status_value_str is None:
                print("Error: Received None from get_command. This might indicate a communication error or an unexpected state. Continuing...")
                time.sleep(0.1)  # Wait a bit before retrying
                continue  # Continue with the next iteration of the loop
    
            try:
                # Convert the status value from dec to integer directly since "v" is already stripped
                status_value = int(status_value_str)
    
                # Check if the motion completion bit is not set
                if not status_value & (1 << self.trajectory_register_in_motion_bit):
                    print("Motion completed.")
                    break
                else:
                    print("Motion in progress...")
                    time.sleep(0.5)  # Wait a bit before retrying
            except ValueError:
                # Log the ValueError and continue with the next iteration
                print("Error: ValueError encountered while converting status_value_str to int. This might indicate an invalid response. Continuing...")
                time.sleep(0.5)  # Wait a bit before retrying

    """       
    def wait_for_motion_completion(self, axis=None):
        
        # Give the drives time to start moving
        time.sleep(1)
        while True:
            try:
                # Construct the command to read the Trajectory Status Register
                status_value_str = self.get_command(self.trajectory_register, axis)

                # Convert the status value from dec to integer directly since "v" is already stripped
                status_value = int(status_value_str)

                # Check if the motion completion bit is not set
                if not status_value & (1 << self.trajectory_register_in_motion_bit):
                    print("Motion completed.")
                    break
                else:
                    print("Motion in progress...")
                    # current_position('X')
                    time.sleep(0.5)  # Wait a bit before retrying
            except ValueError as e:
                print(f"Failed to read Trajectory Status Register or invalid response. Trying again...Error: {e}")
    """
    
    
    # Start a movement, no Initialization
    def initiate_movement(self, axis):
        """Initiate movement for a specific axis."""
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            result = self.check_motion_parameters(self.check_axis, axis)
            if result[axis]:
                print(f'Axis {axis} is fully configured and movement started.')
                self.trajectory_generator_command(axis=axis, trajectory_mode='move')
            else:
                print(f'Axis {axis} is not fully configured.')
            self.wait_for_motion_completion(axis)
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Set all motion parameters as one easy function
    def set_motion_parameters(self, axis=None, velocity=None, acceleration=None, deceleration=None, jerk=None, abort_deceleration=None):
        """Set velocity, acceleration, deceleration and adjust motion dynamics parameters for a specific axis."""
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            # Only run those that need to be updated
            if velocity is not None:
                self.set_velocity(velocity, axis)
            if acceleration is not None:
                self.set_acceleration(acceleration, axis)
            if deceleration is not None:
                self.set_deceleration(deceleration, axis)
            if jerk is not None:
                self.set_jerk(jerk, axis)
            if abort_deceleration is not None:
                self.set_abort_deceleration(abort_deceleration, axis)
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Set Position or Distance and Mode for Motion and then Move
    def movement(self, axis=None, position=None, mode=None, shape=None):
        """Set the position and mode (relative or absolute, velocity and also trapezoidal or s_curve)
        for a specific axis and then move."""
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            if mode and shape is not None:
                self.configure_motion_profile(mode, shape, axis)
            if position is None:
                raise ValueError("No position or Distance specified.")
            self.set_position(position, axis)
            self.initiate_movement(axis)
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    def wait_until_home_referenced(self, axis):
        """Wait until the motor axis is referenced after homing."""
        # Give the drives time to start moving
        time.sleep(1)
        while True:
            status_value_str = self.get_command(self.trajectory_register, axis)
            if status_value_str is not None:
                # Convert the status value from dec to integer directly since "v" is already stripped
                status_value = int(status_value_str)

                is_homing = (status_value & (1 << self.trajectory_register_homing_bit)) != 0
                is_referenced = (status_value & (1 << self.trajectory_register_referenced_bit)) != 0
                homing_error = (status_value & (1 << self.trajectory_register_homing_error_bit)) != 0
                if homing_error:
                    time.sleep(0.1)
                    if is_homing:
                        print("Homing in progress...")
                    else:
                        print("Homing didn't work due to an error.")
                        break
                elif is_homing:
                    print("Homing in progress...")
                elif is_referenced:
                    print("Axis is successfully referenced.")
                    break
                else:
                    print("No Error, no movement and no Reference...")
            else:
                print("Error reading status, trying again...")

            time.sleep(0.25)  # Wait before retrying

    # Fast Velocity
    def set_fast_velocity(self, fast_velocity, axis):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            self.check_limit_for_values(to_check='fast_velocity', value=fast_velocity)
            fast_velocity_unit = int(fast_velocity * 10)
            self.set_command(f'{self.homing_fast_velocity_register} {fast_velocity_unit}', axis=axis)
            self.check_homing[axis]['fast_velocity_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Slow Velocity
    def set_slow_velocity(self, slow_velocity, axis):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            self.check_limit_for_values(to_check='slow_velocity', value=slow_velocity)
            slow_velocity_unit = int(slow_velocity * 10)
            self.set_command(f'{self.homing_slow_velocity_register} {slow_velocity_unit}', axis=axis)
            self.check_homing[axis]['slow_velocity_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Acceleration / Deceleration
    def set_accel_decel(self, accel_decel, axis):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            self.check_limit_for_values(to_check='accel_decel', value=accel_decel)
            accel_decel_unit = int(accel_decel)
            self.set_command(f'{self.homing_accel_decel_register} {accel_decel_unit}', axis=axis)
            self.check_homing[axis]['accel_decel_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # Home Offset
    def set_home_offset(self, home_offset, axis):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            self.check_limit_for_values(to_check='home_offset', value=home_offset)
            home_offset = int(home_offset)
            self.set_command(f'{self.homing_offset_register} {home_offset}', axis=axis)
            self.check_homing[axis]['home_offset_set'] = True
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    # All Parameter for Homing collected -> all Axes possible
    def homing_parameter(self, fast_velocity, slow_velocity, accel_decel, home_offset, axis):
        # Check if 'all' is specified to run for both 'X' and 'Z'
        axes = self.all_axes_check(axis)
        for each_axis in axes:
            self.set_slow_velocity(slow_velocity, each_axis)
            self.set_fast_velocity(fast_velocity, each_axis)
            self.set_accel_decel(accel_decel, each_axis)
            self.set_home_offset(home_offset, each_axis)

    # Initialize Homing Parameter
    def initialize_homing_parameter(self, axis):
        init_fast_velocity = 20000  # because Units: 0.1 counts/s -> 2000 counts/s
        init_slow_velocity = 10000  # because Units: 0.1 counts/s -> 1000 counts/s
        init_accel_decel = 100000  # because Units = 10 counts/s² -> 1_000_000 counts/s²
        init_home_offset = 0  # Units = 1 counts -> 0 counts
        # Also set general Homing parameter to ??? Maybe current position as home
        self.homing_parameter(init_fast_velocity, init_slow_velocity, init_accel_decel, init_home_offset, axis)

    # go to whatever is set Home with, based on the saved Homing method
    def go_home(self, axis):
        if axis.lower() in [axis_name.lower() for axis_name in self.available_axes]:
            if axis is not None:
                axis = self.normalize_axis(axis)  # Ensure axis is in the correct format
            result = self.check_motion_parameters(self.check_homing, axis)
            if result[axis]:
                print(f'Axis {axis} is fully configured and movement started.')
                self.trajectory_generator_command(axis=axis, trajectory_mode='home')
            else:
                print(f'Axis {axis} is not fully configured.')
            self.wait_until_home_referenced(axis)
        else:
            raise ValueError("Invalid axis specified. Please choose 'X' for X or 'Z' for Z.")

    def set_current_position_as_home(self, axis):
        """Sets the current position as home."""
        self.set_command(f'{self.homing_method_register} 512', axis)
        self.check_homing[axis]['homing_method_chosen'] = True
        self.go_home(axis)

    def set_homing_with_limit_switch(self, axis, direction='negative'):
        """Initiates homing to the limit switch."""
        if direction == 'positive':
            self.set_command(f'{self.homing_method_register} 513', axis)
            self.check_homing[axis]['homing_method_chosen'] = True
        elif direction == 'negative':
            self.set_command(f'{self.homing_method_register} 529', axis)
            self.check_homing[axis]['homing_method_chosen'] = True
        else:
            raise ValueError("Invalid direction specified. Choose 'positive' or 'negative'.")

    def go_home_with_limit_switch(self, axis, direction='negative'):
        self.set_homing_with_limit_switch(axis=axis, direction=direction)
        self.go_home(axis=axis)

    def set_homing_with_home_switch(self, axis, direction='negative'):
        """Initiates homing to the home switch."""
        if direction == 'positive':
            self.set_command(f'{self.homing_method_register} 514', axis)
            self.check_homing[axis]['homing_method_chosen'] = True
        elif direction == 'negative':
            self.set_command(f'{self.homing_method_register} 530', axis)
            self.check_homing[axis]['homing_method_chosen'] = True
        else:
            raise ValueError("Invalid direction specified. Choose 'positive' or 'negative'.")

    def go_home_with_home_switch(self, axis, direction='negative'):
        self.set_homing_with_home_switch(axis=axis, direction=direction)
        self.go_home(axis)

    # Go to 0:0
    def go_to_zero_home(self):
        self.movement('X', 0, 'absolute', 'trapezoidal')
        self.movement('Z', 0, 'absolute', 'trapezoidal')

    # Starting from here come functions which are needed for NewMotor directly

    def move_to_zero(self, mode='servo', velocity=2000, acceleration=10000, deceleration=10000, jerk=100000, abort_deceleration=70000):
        self.enable_axis('all')
        self.set_mode(mode=mode, axis='all')
        self.set_motion_parameters(axis='X', velocity=velocity, acceleration=acceleration, deceleration=deceleration, jerk=jerk, abort_deceleration=abort_deceleration)
        self.set_motion_parameters(axis='Z', velocity=velocity, acceleration=acceleration, deceleration=deceleration, jerk=jerk, abort_deceleration=abort_deceleration)
        self.go_to_zero_home()
        self.disable_axis('all')

    def recenter_sequence(self, callback=None):
        self.reset_command()
        self.enable_axis('X')
        self.enable_axis('Z')
        self.set_mode(mode='servo', axis='X')
        self.set_mode(mode='servo', axis='Z')
        self.set_motion_parameters('X', 10000, 10000, 10000)
        self.set_motion_parameters('Z', 10000, 10000, 10000)
        self.initialize_homing_parameter('X')
        self.initialize_homing_parameter('Z')
        self.go_home_with_limit_switch('X', 'negative')
        self.go_home_with_limit_switch('Z', 'negative')
        self.movement('X', 136000, 'absolute', 'trapezoidal')
        self.movement('Z', 194500, 'absolute', 'trapezoidal')
        self.set_current_position_as_home('X')
        self.set_current_position_as_home('Z')
        self.disable_axis('X')
        self.disable_axis('Z')
        # At the end of the method, call the callback if provided
        if callback:
            callback()

    def initialize_everything(self, callback=None):
        if self.initialized == 0:
            _, baud_rate_comm = self.attempt_communication(self.initial_baudrate)
            self.serial_motor.baudrate = baud_rate_comm
            self.reset_command()
            self.set_motion_parameters(axis='X', abort_deceleration=70000)
            self.set_motion_parameters(axis='Z', abort_deceleration=70000)
            self.initialize_homing_parameter('all')
            self.enable_axis('all')
            self.set_current_position_as_home('X')
            self.set_current_position_as_home('Z')
            self.disable_axis('all')
            self.set_homing_with_home_switch('X')
            self.set_homing_with_home_switch('Z')

            self.initialized = 1
            self.current_index = 0
            self.start = 0
            self.focus_init = 0

            self.rows = 0
            self.columns = 0
            self.max_exp_time = 0

            self.height_grading = 0
            self.width_grading = 0

            self.absolute_position_X = []
            self.absolute_position_Z = []

            self.start_pos_X = 0
            self.start_pos_Z = 0
            
            self.OutOfBoundaries = False
            
            
        if callback:
            callback()

    def finish_focus(self, callback=None):
        # no need for check_init_focus since all variables in move_to_zero set!
        self.move_to_zero()
        self.focus_init = 0
        if callback:
            callback()

    # checks if everything initialized for focus-movement
    def check_init_focus(self):
        if self.focus_init == 0:
            self.set_mode(mode='servo', axis='all')
            self.set_motion_parameters(axis='X', velocity=2000, acceleration=250, deceleration=250)
            self.set_motion_parameters(axis='Z', velocity=2000, acceleration=250, deceleration=250)
            self.enable_axis('all')

            self.go_to_zero_home()

            self.focus_init = 1

    # moves to top on film
    def focus_top(self, callback=None):
        self.check_init_focus()
        # Move to center before going to any edges
        self.go_to_zero_home()
        self.movement(axis='Z', position=30000, mode='absolute', shape='trapezoidal')
        if callback:
            callback()

    # moves to bottom on film
    def focus_bottom(self, callback=None):
        self.check_init_focus()
        # Move to center before going to any edges
        self.go_to_zero_home()
        self.movement(axis='Z', position=-30000, mode='absolute', shape='trapezoidal')
        if callback:
            callback()

    # moves to left on film
    def focus_left(self, callback=None):
        self.check_init_focus()
        # Move to center before going to any edges
        self.go_to_zero_home()
        self.movement(axis='X', position=-30000, mode='absolute', shape='trapezoidal')
        if callback:
            callback()

    # moves to right on film
    def focus_right(self, callback=None):
        self.check_init_focus()
        # Move to center before going to any edges
        self.go_to_zero_home()
        self.movement(axis='X', position=30000, mode='absolute', shape='trapezoidal')
        if callback:
            callback()

    # Use after clicking end to early!!!!!
    def reset_after_interrupted(self):
        # self.enable_axis(axis='all')
        # self.set_mode(mode='servo', axis='all')
        self.set_motion_parameters(axis='X', velocity=10000, acceleration=50000, deceleration=50000)
        self.set_motion_parameters(axis='Z', velocity=10000, acceleration=50000, deceleration=50000)
        self.go_to_zero_home()
        self.disable_axis(axis='all')
        self.reset_command()

        self.current_index = 0
        self.initialized = 0
        self.start = 0
        self.focus_init = 0

        self.rows = 0
        self.columns = 0
        self.max_exp_time = 0

        self.height_grading = 0
        self.width_grading = 0

        self.absolute_position_X = []
        self.absolute_position_Z = []

        self.start_pos_X = 0
        self.start_pos_Z = 0

    def calculate_size_grading(self, mode):
        self.height_grading = 0
        self.width_grading = 0
        if mode == 'stitching':
            self.width_grading = (self.columns * self.SLM_stitching_pixel_X)
            width_grading_print = (self.width_grading / 2)
            print(f'Width in µm: {width_grading_print}')
            width_grading_print = (width_grading_print / 1000)
            print(f'Width in mm: {width_grading_print}')
            self.height_grading = (self.rows * self.SLM_stitching_pixel_Z)
            height_grading_print = (self.height_grading / 2)
            print(f'Height in µm: {height_grading_print}')
            height_grading_print = (height_grading_print / 1000)
            print(f'Height in mm: {height_grading_print}')
        elif mode == 'printing':
            self.width_grading = (self.columns * self.SLM_printing_pixel)
            width_grading_print = (self.width_grading / 2)
            print(f'Width in µm: {width_grading_print}')
            width_grading_print = (width_grading_print / 1000)
            print(f'Width in mm: {width_grading_print}')
            self.height_grading = (self.rows * self.SLM_printing_pixel)
            height_grading_print = (self.height_grading / 2)
            print(f'Height in µm: {height_grading_print}')
            height_grading_print = (height_grading_print / 1000)
            print(f'Height in mm: {height_grading_print}')
        else:
            raise ValueError("Wrong Mode for calculating the size")

    def calculate_time_grading(self, mode):
        if mode == 'stitching':
            max_time = ((self.max_exp_time + self.time_movement) * self.columns * self.rows)
            print(f'Max Time for Stitch: {max_time}')
        elif mode == 'printing':
            self.length_movement = 0
            self.length_movement = ((self.rows - 1) * self.SLM_printing_pixel + self.SLM_printing_height_difference + self.SLM_printing_offset)
            max_time_column = (self.length_movement / self.speed_printing)
            max_time = (max_time_column * self.columns)

            print("Times without the reset for the next line!")
            print(f'Max Time for a single column in s: {max_time_column}')
            max_time_column = (max_time_column / 60)
            print(f'Max Time for a single column in min: {max_time_column}')
            max_time_column = (max_time_column / 60)
            print(f'Max Time for a single column in h: {max_time_column}')

            print(f'Max Time for a all columns in s: {max_time}')
            max_time = (max_time / 60)
            print(f'Max Time for a all columns in min: {max_time}')
            max_time = (max_time / 60)
            print(f'Max Time for a all columns in h: {max_time}')
        else:
            raise ValueError(f'No Calculation of Time possible, because {mode} is not a available mode!')

    def check_borders(self, mode, start_x, start_z, offset_x, offset_z):
        if mode == 'stitching':
            max_x = start_x + offset_x
            min_x = (start_x + offset_x) - ((self.columns * self.SLM_stitching_pixel_X) - self.SLM_stitching_pixel_X)
            min_z = start_z + offset_z
            max_z = (start_z + offset_z) + ((self.rows * self.SLM_stitching_pixel_Z) - self.SLM_stitching_pixel_Z)
        elif mode == 'printing':
            max_x = start_x + offset_x
            min_x = (start_x + offset_x) - ((self.columns * self.SLM_printing_pixel) - self.SLM_printing_pixel + self.SLM_printing_offset)
            min_z = start_z + offset_z
            max_z = (start_z + offset_z) + ((self.rows * self.SLM_printing_pixel) + self.SLM_printing_offset - self.SLM_printing_pixel + self.SLM_printing_height_difference)
        else:
            raise ValueError(f'Mode defined wrong for border-check: {mode}')

        if max_x > self.max_limit or max_z > self.max_limit or min_x < self.min_limit or min_z < self.min_limit:
            # raise ValueError("Out of set boundaries! Lens would hit the corners!")
            return True  # Indicate boundary violation
        else:
            return False  # Indicate within boundaries

    def init_operation(self, columns, rows, time_or_speed, x_value, z_value, start_offset_x=0, start_offset_z=0, mode=None, stitch=None):
        if self.start == 0:
            self.start = 1
            self.columns = columns
            self.rows = rows

            if mode == 'stitching':
                self.current_index = 0
                self.max_exp_time = time_or_speed

                if stitch == 'absolute':
                    self.absolute_position_X = x_value[:]
                    self.absolute_position_Z = z_value[:]
                    self.OutOfBoundaries = self.check_borders(mode=mode, start_x=self.absolute_position_X[0], start_z=self.absolute_position_Z[0], offset_x=start_offset_x, offset_z=start_offset_z)
                elif stitch == 'relative':
                    if x_value is None or z_value is None:
                        # Calculate new Start so fully in middle
                        self.start_pos_X = ((self.SLM_stitching_half_pixel * self.columns) - self.SLM_stitching_pixel_X + self.SLM_stitching_half_pixel)
                        self.start_pos_Z = (-1 * ((self.SLM_stitching_half_pixel * self.rows) - self.SLM_stitching_pixel_Z + self.SLM_stitching_half_pixel))
                    else:
                        # int not needed since set later anyway
                        self.start_pos_X = int(x_value)
                        self.start_pos_Z = int(z_value)
                    self.OutOfBoundaries = self.check_borders(mode=mode, start_x=self.start_pos_X, start_z=self.start_pos_Z, offset_x=start_offset_x, offset_z=start_offset_z)
                else:
                    raise ValueError("Error while initializing for Stitching, no Mode for Stitching chosen!")

                self.calculate_size_grading(mode='stitching')
                self.calculate_time_grading(mode='stitching')
                print("Preparation before Stitching are DONE, moving to center!")

            elif mode == 'printing':
                self.current_line = 0
                self.speed_printing = time_or_speed

                if x_value is None or z_value is None:
                    # if none we want the print to be in the middle
                    self.start_pos_X = ((self.SLM_printing_half_pixel * self.columns) - self.SLM_printing_half_pixel)
                    self.start_pos_Z = (-1 * ((self.SLM_printing_half_pixel * self.rows) - self.SLM_printing_pixel + self.SLM_printing_half_height + self.SLM_printing_height_difference))
                else:
                    self.start_pos_X = int(x_value)
                    self.start_pos_Z = int(z_value)
                
                self.OutOfBoundaries = self.check_borders(mode='printing', start_x=self.start_pos_X, start_z=self.start_pos_Z, offset_x=start_offset_x, offset_z=start_offset_z)
                self.calculate_size_grading(mode='printing')
                self.calculate_time_grading(mode='printing')
                print("Preparation before Printing are DONE, moving to center!")
            else:
                raise ValueError("Error while initializing!")

            self.enable_axis(axis='all')
            self.set_mode(mode='servo', axis='all')
            self.set_motion_parameters(axis='X', velocity=1000, acceleration=1000, deceleration=1000)
            self.set_motion_parameters(axis='Z', velocity=1000, acceleration=1000, deceleration=1000)
            self.go_to_zero_home()

    def end_operation(self, mode):
        if mode == 'printing' and self.current_line == self.columns + 1:
            self.go_to_zero_home()
            self.disable_axis(axis='all')
            self.reset_command()

            self.current_line = 0
            self.initialized = 0
            self.start = 0
            self.focus_init = 0

            self.rows = 0
            self.columns = 0
            self.speed_printing = 0
            self.length_movement = 0

            self.height_grading = 0
            self.width_grading = 0

            self.start_pos_X = 0
            self.start_pos_Z = 0
            
            self.OutOfBoundaries = False

            print("Clean up after Stitching!")

        elif mode == 'stitching' and self.current_index == (self.columns * self.rows):
            self.go_to_zero_home()
            self.disable_axis(axis='all')
            self.reset_command()

            self.current_index = 0
            self.initialized = 0
            self.start = 0
            self.focus_init = 0

            self.rows = 0
            self.columns = 0
            self.max_exp_time = 0

            self.height_grading = 0
            self.width_grading = 0

            self.absolute_position_X = []
            self.absolute_position_Z = []

            self.start_pos_X = 0
            self.start_pos_Z = 0
            
            self.OutOfBoundaries = False

            print("Clean up after Stitching!")

        elif self.current_line == (self.columns + 1) or self.current_index == (self.columns * self.rows):
            raise ValueError(f'End reached, but {mode} has been chosen wrong and doesnt align with expectations!')

    def stitching_absolute(self, columns, rows, max_exp, absolute_x, absolute_z, start_offset_x=0, start_offset_z=0, callback=None, boundary_exit_function=None):
        """
            Move the motor to absolute positions defined in 2 list.
            Args:
                columns: Columns of the current Stitch
                rows: Rows of the current Stitch
                max_exp: Maximum Exposure Time that has been set
                absolute_x: List containing absolute values for X
                absolute_z: List containing absolute values for Z
                start_offset_x (int/float): Offset for X coordinates.
                start_offset_z (int/float): Offset Y coordinates.
                callback: A function that we call back after
        """
        # self.init_stitching(columns=columns, rows=rows, max_exp=max_exp, x_value=absolute_x, z_value=absolute_z, stitch='absolute')
        # self.init_operation(columns=columns, rows=rows, time_or_speed=max_exp, x_value=absolute_x, z_value=absolute_z, mode='stitching', stitch='absolute')
        self.init_operation(columns=columns, rows=rows, time_or_speed=max_exp, x_value=absolute_x, z_value=absolute_z, start_offset_x=start_offset_x, start_offset_z=start_offset_z, mode='stitching', stitch='absolute')
        # self.check_borders(mode='absolute', start_x=self.absolute_position_X[0], start_z=self.absolute_position_Z[0], offset_x=start_offset_x, offset_z=start_offset_z)
        
        if not self.OutOfBoundaries:
            if self.current_index >= self.columns * self.rows:
                # Complete the stitching process
                print("Stitching complete.")
            else:
                # int not needed since set later anyway
                current_x = int(self.absolute_position_X[self.current_index] + start_offset_x)
                current_z = int(self.absolute_position_Z[self.current_index] + start_offset_z)
    
                self.movement(axis='X', position=current_x, mode='absolute', shape='trapezoidal')
                self.movement(axis='Z', position=current_z, mode='absolute', shape='trapezoidal')
    
            self.end_operation(mode='stitching')
            self.current_index += 1
            
            # Once movement completes
            if callback:
                callback()
        else:
            print("No Movement due to boundary violation.")
            self.current_index = (self.columns * self.rows)
            self.end_operation(mode='stitching')
            if boundary_exit_function:
                boundary_exit_function()
        
    
    def stitching_relative(self, columns, rows, max_exp, start_x=None, start_z=None, callback=None, boundary_exit_function=None):
        """
            Move the motor with the help of relatives through a reverse snake-patter.
            Args:
                columns: Columns of the current Stitch
                rows: Rows of the current Stitch
                max_exp: Maximum Exposure Time that has been set
                start_x: Value for the current starting location X
                start_z: Value for the current starting location Z
                callback: A function that we call back after
        """
        # self.init_stitching(columns=columns, rows=rows, max_exp=max_exp, x_value=start_x, z_value=start_z, stitch='relative')
        # self.init_operation(columns=columns, rows=rows, time_or_speed=max_exp, x_value=start_x, z_value=start_z, mode='stitching', stitch='relative')
        self.init_operation(columns=columns, rows=rows, time_or_speed=max_exp, x_value=start_x, z_value=start_z, start_offset_x=0, start_offset_z=0, mode='stitching', stitch='relative')
        # self.check_borders(mode='relative', start_x=self.start_pos_X, start_z=self.start_pos_Z, offset_x=0, offset_z=0)
        
        if not self.OutOfBoundaries:
            # Logic for relative movement
            if self.current_index >= self.columns * self.rows:
                # Complete the stitching process
                print("Stitching complete.")
                
            elif self.start == 1:
                self.movement(axis='X', position=self.start_pos_X, mode='absolute', shape='trapezoidal')
                self.movement(axis='Z', position=self.start_pos_Z, mode='absolute', shape='trapezoidal')
                self.start = 2
                
            elif self.start == 2:
                current_row = self.current_index // self.columns
                row_before = (self.current_index - 1) // self.columns
                if current_row < self.rows:
                    if current_row != row_before:
                        # move up on film into positive Z-direction
                        self.movement(axis='Z', position=self.SLM_stitching_pixel_Z, mode='relative', shape='trapezoidal')
                    elif current_row % 2 == 1:
                        # odd rows, move right on film into positive X-direction
                        self.movement(axis='X', position=self.SLM_stitching_pixel_X, mode='relative', shape='trapezoidal')
                    elif current_row % 2 == 0:
                        # even rows, move left on film into negative X-direction
                        self.movement(axis='X', position=(-1 * self.SLM_stitching_pixel_X), mode='relative', shape='trapezoidal')
                    else:
                        raise ValueError("No movement with logic, Error!")
                else:
                    print("End reached, no more rows to go through!")
            else:
                raise ValueError("Error inside Logic for relative Stitching!")
    
            self.end_operation(mode='stitching')
            self.current_index += 1
            # Once movement completes
            if callback:
                callback()
        else:
            print("No Movement due to boundary violation.")
            self.current_index = (self.columns * self.rows)
            self.end_operation(mode='stitching')
            if boundary_exit_function:
                boundary_exit_function()

    def printing(self, columns, rows, speed, start_x=None, start_z=None, callback=None, boundary_exit_function=None):
        """
            Allows for printing lines.
            Args:
                columns: Columns of the current Printing, so the amount of lines
                rows: Rows of the current Printing, so the Length of the lines
                speed: Maximum speed to print along the lines
                start_x: Value for the current starting location X
                start_z: Value for the current starting location Z
                callback: A function that we call back after
        """
        # self.init_printing(columns=columns, rows=rows, speed=speed, start_x=start_x, start_z=start_z)
        # self.init_operation(columns=columns, rows=rows, time_or_speed=speed, x_value=start_x, z_value=start_z, mode='printing')
        self.init_operation(columns=columns, rows=rows, time_or_speed=speed, x_value=start_x, z_value=start_z, start_offset_x=0, start_offset_z=0, mode='printing')
        # self.check_borders(mode='printing', start_x=self.start_pos_X, start_z=self.start_pos_Z, offset_x=0, offset_z=0)

        if not self.OutOfBoundaries:
            if self.current_line > self.columns:
                # Complete the stitching process
                print("Stitching complete.")            
            elif self.start == 1:
                # Move to starting location
                self.movement(axis='X', position=self.start_pos_X, mode='absolute', shape='trapezoidal')
                self.movement(axis='Z', position=self.start_pos_Z, mode='absolute', shape='trapezoidal')
                self.start = 2
            elif self.start == 2:
                # Printing of the Line:
                self.set_motion_parameters(axis='Z', velocity=self.speed_printing)
                self.movement(axis='Z', position=self.length_movement, mode='relative', shape='trapezoidal')
                # Moving over to the next line
                self.movement(axis='X', position=(-1 * self.SLM_printing_pixel), mode='relative', shape='trapezoidal')
                self.set_motion_parameters(axis='Z', velocity=2000)
                self.movement(axis='Z', position=(-1 * self.length_movement), mode='relative', shape='trapezoidal')
            else:
                raise ValueError("Error inside Logic for Printing!")
    
            # self.end_printing()
            self.end_operation(mode='printing')
            self.current_line += 1

            if callback:
                callback()
        else:
            print("No Movement due to boundary violation.")
            self.current_line = (self.columns + 1)
            self.end_operation(mode='printing')
            if boundary_exit_function:
                boundary_exit_function()

    def exit_stop_movement(self, callback=None, abort_attempts=2):
        # Make sure nothing at all will be moving
        for _ in range(abort_attempts):
            self.trajectory_generator_command(axis='X', trajectory_mode='abort')
            time.sleep(1)
            self.trajectory_generator_command(axis='Z', trajectory_mode='abort')
            time.sleep(1)
        
        self.move_to_zero()

        if callback:
            callback()


if __name__ == "__main__":
    motor_controller = MotorController()
    # motor_controller.attempt_communication(9600)
    # motor_controller.recenter_sequence()
    motor_controller.close_connection()
