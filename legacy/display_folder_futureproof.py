"""
Created on Mon Apr 17 09:11:38 2023

@author: Oktay Senel

this is a shell code to put any folder of images on the SLM. It does not create any images.

This is (till now 7/2023) not an automatic code. I fixed a Problem regarding RAM usage that display_folder_test had.

This code will nee you to know what you want to do on the film.

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
    
    image=im.open(names[i])
    image=PIL.ImageTk.PhotoImage(image)
    slm.close_window()
    slm = SLM_window(root)
    slm.display(image)
    print("you are showing image "+ str(os.path.basename(names[i])))
    i=i+1

def prev_image():
    global i
    global slm
    
    image=im.open(names[i-2])
    image=PIL.ImageTk.PhotoImage(image)
    slm.close_window()
    slm = SLM_window(root)
    slm.display(image)
    print("you are showing image "+ str(os.path.basename(names[i-2])))
    i=i-1
    

    
def open_images():
    
    global names
    global slm
    global exp_times
    filepath=filedialog.askdirectory()
    
    names=[]
    for filename in glob.glob(filepath + "/*.png"):
        #image=im.open(filename)
        #image=PIL.ImageTk.PhotoImage(image)
        names.append(filename)
        #image_list.append(image)
        
    exp_time=np.genfromtxt(filepath + "/exp_times.csv")
    exp_times=[]
    m=len(exp_time)
    p=0
    while p<m:
        time=(exp_time[p]/768)*20#put your max exposure time here in seconds.
        #print(time)
        exp_times.append(time) 
        p=p+1
    
    print(str(m)+" images and exposure times loaded: you are showing " +str(names[0])+ " please make sure that the images are read in the order you want them to be")
    image=im.open(names[0])
    image=PIL.ImageTk.PhotoImage(image)
    slm=SLM_window(root)
    slm.display(image)
    
#define your movement here; most changes will be made here (do not forget to set your velocity)
#while the movement is beeing done you can not change the image on the SLM so far (4/2023)
    
print_velo="0.01"
def movement1():
    motor = Motor('COM25', print_velo)
    shutter = Shutter("COM24")
    print("movement started")
    shutter.toggle()
    motor.move_rel(2,1)
    shutter.toggle()
    motor.move_rel(1,-0.13)
    motor.close()
    shutter.close()
    print("movement done next move should be -")
    
    
def movement2():
    motor = Motor('COM25', print_velo)
    shutter = Shutter("COM24")
    print("movement started")
    shutter.toggle()
    motor.move_rel(2,-1)
    shutter.toggle()
    motor.move_rel(1,-0.13)
    motor.close()
    print("movement done next move should be +")
    shutter.close()
    
    
def new_matrix():
    motor = Motor('COM25', "0.5")
    print("movement started")
    motor.move_rel(1,-0.5)
    motor.close()
    print("movement done nextmatrix can be printed")
    
def stichright(exp_time):
    if exp_time==0:
        motor = Motor('COM25',"1")
        motor.move_rel(1,0.13)
        motor.wait_motion_done(2)
        motor.close()
    else:
        motor = Motor('COM25',"1")
        shutter = Shutter("COM24")
        motor.move_rel(1,0.13)
        motor.wait_motion_done(2)
        shutter.toggle()
        time.sleep(exp_time)
        shutter.toggle()
        motor.close()
        shutter.close()
    
def stichleft(exp_time):
    if exp_time==0:
        motor = Motor('COM25',"1")
        motor.move_rel(1,-0.13)
        motor.wait_motion_done(2)
        motor.close()
        
    else:
        motor = Motor('COM25',"1")
        shutter = Shutter("COM24")
        motor.move_rel(1,-0.13)
        motor.wait_motion_done(2)
        shutter.toggle()
        time.sleep(exp_time)
        shutter.toggle()
        motor.close()
        shutter.close()
    
def newline(exp_time):
    if exp_time==0:
        motor = Motor('COM25',"1")
        motor.move_rel(2,0.08)
        motor.wait_motion_done(1)
        motor.close()
    else:    
        motor = Motor('COM25',"1")
        shutter = Shutter("COM24")
        motor.move_rel(2,0.08)
        motor.wait_motion_done(1)
        shutter.toggle()
        time.sleep(exp_time)
        shutter.toggle()
        shutter.close()
        motor.close()
    
def put_that_on_there():
    global names
    global exp_times
    n=int(len(names)**0.5)
    print(n)
    print("stitching started a "+str(n) +"x"+str(n)+" grating")
    j=0
    k=500
    start=0
    nn=len(names)
    o=0
    while j<nn :
        if start==0 and j<nn:
             shutter = Shutter("COM24")
             shutter.toggle()
             time.sleep(exp_times[j])
             shutter.toggle()
             shutter.close()
             start=1
             j=j+1
        if o<n-1 and j<nn:
            next_image()
            root.update()
            stichleft(exp_times[j])
            o=o+1
            j=j+1        
        if o==n-1 and j<nn:
            k=0
            o=500
            next_image()
            root.update()
            newline(exp_times[j])
            j=j+1
        if k<n-1 and j<nn :
            next_image()
            root.update()
            stichright(exp_times[j])
            k=k+1
            j=j+1
        if k==n-1 and j<nn :
            k=500
            o=0
            next_image()
            root.update()
            newline(exp_times[j])
            j=j+1
    print("stitching done")
    
    
    
def exposuresinaline():
    global names
    global exp_times
    
    motor = Motor('COM25',"1")
    shutter = Shutter("COM24")
    q=0
    while q<6:
        shutter.toggle()
        time.sleep(exp_times[q])
        shutter.toggle()
        motor.move_rel(1,0.3)
        next_image()
        root.update()
        q=q+1
    motor.close()
    shutter.close()
    
root = tk.Tk()
global i
i=1
btn0=tk.Button(root,text="read",bd="5", command=open_images)
btn0.pack(side="left")
btn2=tk.Button(root,text="next", bd="5", command=next_image)
btn2.pack(side="left")
btn7=tk.Button(root,text="prev",bd="5", command=prev_image)
btn7.pack(side="left")
btn3=tk.Button(root,text="line", bd="5", command=exposuresinaline)
btn3.pack(side="left")
btn5=tk.Button(root,text="stich",bd="5", command=put_that_on_there)
btn5.pack(side="left")
btn4=tk.Button(root,text="end",bd="5",command=root.destroy)
btn4.pack(side="left")
root.mainloop()