# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 12:04:57 2023

@author: Oktay based on move.py by?
"""

import serial
import time
import math

from exceptions import EquipmentError
from exceptions import MotorError
from exceptions import ShutterError

class Motor():
    def __init__(self, port,speed):
        self.ser = serial.Serial()

        self.ser.port = port
        self.ser.baudrate = float(19200)
        self.ser.timeout = float(.1)
        self.ser.stopbits = float(1)
        self.ser.bytesize = float(8)
        self.ser.parity = 'N'
        self.command_pause = .1

        for axis in (1,2):
            self.write_command(str(axis)+'MO')      # Turns Motor on
            self.write_command(str(axis)+'VA'+speed)  # Sets velocity 
            self.write_command(str(axis)+'AC'+'4')  # Sets acceleration to 4
            self.write_command(str(axis)+'AG'+'4')  # Sets deceleration to 4


    def write_command(self, command:str):
        if not self.ser.is_open:
            self.ser.open()

        if command.find('\r') == -1:
            command += '\r'

        try:
            self.ser.write(command.encode())
        except Exception as e:
            message = ('Could not write this command to serial device:\n\t' + command)
            raise EquipmentError(message, e)
        time.sleep(self.command_pause)

    def wait_motion_done(self, axis:int):
        WAIT = .25
        while True:
            self.write_command(str(axis)+'MD?')
            byte_info = self.ser.read(4)
            try:
                str_info = str(byte_info.decode())
                if '1' in str_info:
                    return
                else:
                    time.sleep(WAIT)
            except Exception:
                pass

    def move_absolute(self, axis:int, go_to_position:float):
        """
        Move any axis to an absolute position.
        """

        self.write_command(str(axis)+'PA'+str(go_to_position))
        self.wait_motion_done(axis)

    def move_home(self, axis:int):
        """
        Move the motor to the home position.
        """

        self.write_command(str(axis)+'OR0')
        self.wait_motion_done(axis)

    def move_rel(self, axis:int, increment:float):
        """
        Move the axis to a relative position
        """

        self.write_command(str(axis)+'PR'+str(increment))
        self.wait_motion_done(axis)
        
    def close(self):
        self.ser.close()
        

class Shutter:
    '''
    ser: serial port (serial object)
    '''
    
    ser = serial.Serial()
    
    def __init__(self, port, baudrate=9600, timeout=.1, stopbits=1, bytesize=8):
        '''
        Construct an object and configure the serial port.
        #flow control = 1?
        '''
        
        
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.ser.stopbits = stopbits
        self.ser.bytesize = bytesize
        
    def writeCommand(self, command, closeAfter=False):
        '''
        Send any command to a serial port.
        (arg1) self 
        (arg2) command: the command to send to the motor (string)
        (arg3) closeAfter: close port after command, if true (boolean)
        '''
        
        cmd = command
        if cmd.find('\r') == -1:
            cmd = cmd + '\r'
        if self.ser.is_open == False:
            self.ser.open()
        self.ser.write(cmd.encode())
        if closeAfter == True:
            self.ser.close()
            
    def toggle_pause(self, pause):
        '''
        Opens the shutter. Pauses for a certain amount of time. Closes
            the shutter.
        (arg1) pause : number of seconds to pause (float)
        '''
        self.writeCommand('ens')
        time.sleep(pause)
        self.writeCommand('ens')

    def toggle(self):
        self.writeCommand('ens')

    def startup(self):
        response = self.writeCommand('ens?')
        if response == "0":
            self.writeCommand('ens')
    def close(self):
        self.ser.close()
        




def print1(distance,speed):
    motor = Motor('COM5', speed)
    shutter=Shutter("COM6")
    shutter.toggle()
    motor.move_rel(1,distance)
    shutter.toggle()
    motor.close()
    shutter.close()

def newline(distance):
    motor = Motor('COM5', "1")
    motor.move_rel(1,-0.12)
    motor.move_rel(2,distance*-1)
    #motor.close()
    

def print2lines():
    distance=-5#up=negative
    print1(distance,"0.002")
    newline(distance)
    print1(distance,"0.002")
    newline(distance)
    
    
    
def print10lines():
    print2lines()
    print2lines()
    print2lines()
    print2lines()
    print2lines()

    
def start(): 
    print10lines()
    print10lines()
    print10lines()
    print10lines()
    print2lines()
    
radius=1
distance=radius*2*math.pi
print(distance)
speed=0.02
Time=2*(distance/speed)
print("this will take "+str(Time/60)+" minutes")
rotspeed=360/Time

shutter=Shutter("COM6")
motor = Motor('COM5',str(rotspeed))
shutter.toggle()
motor.move_rel(2,180)
shutter.toggle()
motor.move_rel(1, 0.07)
shutter.toggle()
motor.move_rel(2,-180)
shutter.toggle()
motor.move_rel(1, 0.07)

motor.close()
shutter.close()
    
    


