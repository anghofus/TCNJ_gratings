# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 09:11:38 2023

@author: Oktay Senel

this is a shell code to put any folder of images on the SLM. It does not create any images.

This is (till now 4/2023) not an automatic code. This code will nee you to know what you want to do on the film.

If you do not know how to code or understand code this will not be easy to make it suitable to your task.

"""

### Python libraries ###
# Monitor packages
from screeninfo import get_monitors # Screen Information (screeninfo) is a package to fetch location and size of physical screens.
# Window packages 
import tkinter as tk
from tkinter import Toplevel, Tk, Label, filedialog # Graphical User Interface (GUI) package
import PIL.Image, PIL.ImageTk # Python Imaging Librarier (PIL) package
# Processing packages

import numpy as np # Scientific computing package (NumPy)
from PIL import Image as im #package for images 
import glob #package to read a whole folder 
import serial #package to be able to comunicate via serial
import os# needed for filepaths 
import time

from exceptions import EquipmentError
from exceptions import MotorError


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
            self.write_command(str(axis)+'VA'+ speed)  # Sets velocity: this will be important for printing a grating 
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
        
      


class SLM_window():

    def __init__(self, master, grating = None):
        ### Monitor controlling 
        # Finds the resolution of all monitors that are connected.
        active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"
        

        # Assign the separated x and y start values to variables
        begin_monitor_horizontal = active_monitors[0].x
        begin_monitor_vertical = active_monitors[0].y
        begin_slm_horizontal = active_monitors[1].x
        begin_slm_vertical = active_monitors[1].y

        #print(begin_slm_horizontal, begin_slm_vertical)
        width = 1920
        height = 1152

        if grating is None:
            array = np.zeros((height, width), dtype = np.uint16)
            image = PIL.Image.fromarray(array)
            image = image.convert('L')
            grating = PIL.ImageTk.PhotoImage(image)

        # self.image_window = Tk()
        self.image_window = master
        

        # Create a window on the screen of the SLM monitor
        self.window_slm = Toplevel(self.image_window)
        self.window_slm_geometry = str("{:}".format(width) + 'x' + "{:}".format(height) + '+' + "{:}".format(begin_slm_horizontal) + '+' + "{:}".format(begin_slm_vertical))
        
        #print(self.window_slm_geometry)
        self.window_slm.geometry(self.window_slm_geometry)
        self.window_slm.overrideredirect(1)
        
        

        # Load the opened image into the window of the SLM monitor
        
        self.window_slm_label = Label(self.window_slm,image=grating)
        self.window_slm_label.image = grating
        self.window_slm_label.pack()
        
        # Termination command for the code
        self.window_slm.bind("<Escape>", lambda e: self.window_slm.destroy())
       
    
    def display(self,grating):
        self.window_slm_label.config(image=grating)
        self.window_slm_label.image = grating
        
    def display_text(self,msg):
        self.window_slm_label.config(text=msg)

    def close_window(self):
        self.window_slm.destroy()
        self.window_slm.update()
    
    
def next_image():
    global i
    global slm
    global image_list
    slm.close_window()
    slm = SLM_window(root)
    slm.display(image_list[i])
    print("you are showing image "+ str(names[i]))
    i=i+1

def prev_image():
    global i
    global slm
    global image_list
    slm.close_window()
    slm = SLM_window(root)
    slm.display(image_list[i-2])
    print("you are showing image "+ str(names[i-2]))
    i=i-1
    

def new_matrix():
    motor = Motor('COM25', "1")
    print("movement started")
    motor.move_rel(1,-1)
    motor.move_rel(2,-1)
    motor.close()
    print("movement done next matrix can be printed")
    
    
def open_images():
    global image_list
    global names
    global slm
    global speeds
    filepath=filedialog.askdirectory()
    image_list=[]
    names=[]
    for filename in glob.glob(filepath + "/*.png"):
        image=im.open(filename)
        image=PIL.ImageTk.PhotoImage(image)
        names.append(os.path.basename(filename))
        image_list.append(image)
        
    speed=np.genfromtxt(filepath + "/speeds.csv")
    speeds=[]
    m=len(speed)
    p=0
    while p<m:
        time=str(speed[p])#put your max speed here. 0.002-0.015
        speeds.append(time) 
        p=p+1
    print(str(m)+" images and speeds loaded: you are showing " +str(names[0])+ " please make sure that the images are read in the order you want them to be")
    slm=SLM_window(root)
    slm.display(image_list[0])
    
#define your movement here; most changes will be made here (do not forget to set your velocity)
#while the movement is beeing done you can not change the image on the SLM so far (4/2023)
    

def movement1(print_velo):
    motor = Motor('COM25', print_velo)
    shutter = Shutter("COM24")
    shutter.toggle()
    motor.move_rel(2,-0.5)
    shutter.toggle()
    motor.close()
    motor=Motor('COM25', "1")
    motor.move_rel(1,-0.2)
    motor.move_rel(2,0.5)
    shutter.close()
    
    
def movement2(print_velo):
    motor = Motor('COM25', print_velo)
    shutter = Shutter("COM24")
    shutter.toggle()
    motor.move_rel(2,-1)
    shutter.toggle()
    motor.move_rel(1,-0.13)
    motor.close()
    shutter.close()


def print_folder():
    prints=len(speeds)
    print("printing started")
    p=0
    while p<prints  :
        if p % 2==0 and p<prints:
            print(speeds[p]+" mm per second for line "+ str(p+1))
            movement1(speeds[p])
            next_image()
            root.update()
            p=p+1
        if p % 2 ==1 and p<prints:
            print(speeds[p]+" mm per second for line "+ str(p+1))
            movement1(speeds[p])
            next_image()
            root.update()
            p=p+1
            
def color_palette():
    k=0
    j=0
    count= len (speeds)
    while k<count: 
        if j<9 and j%2==0 and  k<count: 
            movement1(speeds[k])
            next_image()
            root.update()
            k=k+1
            j=j+1     
        if  j<9 and j%2==1 and  k<count:
            movement1(speeds[k])
            next_image()
            root.update()
            k=k+1
            j=j+1
        if j==9 and k<count :
            new_matrix()
            j=0
   
 





root = tk.Tk()
global i
i=1
btn0=tk.Button(root,text="read",bd="5", command=open_images)
btn0.pack(side="left")
btn2=tk.Button(root,text="next", bd="5", command=next_image)
btn2.pack(side="left")
btn7=tk.Button(root,text="prev",bd="5", command=prev_image)
btn7.pack(side="left")
btn3=tk.Button(root,text="single lines", bd="5", command= print_folder)
btn3.pack(side="left")
btn5=tk.Button(root,text="3_stripes_color", bd="5", command= color_palette)
btn5.pack(side="left")
btn4=tk.Button(root,text="end",bd="5",command=root.destroy)
btn4.pack(side="left")
root.mainloop()