# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:30:48 2023

@author:Oktay Senel 

this code is made to create color in a collectivly shared first diffraction order. The angle is chosen with blue = 2 microns but can be changed 
by changing f1,f2 and f3. The denominator represents Xmax from the sawtooth_slider; code 15 is 1 micron on the film  
"""

import numpy as np 
from scipy import signal 
from PIL import Image as im
#import cv2
#redscale = cv2.imread("test_red1.png",0)
#bluescale= cv2.imread("test_blue2.png",0)
#greenscale = cv2.imread("test_green2.png",0)

#newimage= img.resize((20,20))
#newimage.save("blackCanvas20x20.png")
t= np.linspace(0,1920,1920)

f1=1/30#blue
f2=1/32.7#green
f3=1/38.91#red

st= (1+signal.sawtooth(2*np.pi*f1*t))*64
st1= (1+signal.sawtooth(2*np.pi*f2*t))*64
st2= (1+signal.sawtooth(2*np.pi*f3*t))*64

def make_SLM_pattern(red,green,blue):
    array= np.zeros((1152,1920))
    i=0
    j=0
    regionblue=1920*blue
    regiongreen=1920*green
    regionred=1920*red
    while i<regionblue:
        array[0][i]=(st[i])
        i=i+1

    while i<regionblue+regiongreen:
        array[0][i]=(st1[i])
        i=i+1

    while i<1920:
        array[0][i]=(st2[i])
        i=i+1

    while j<1152:
        array[j]=array[0]
        j=j+1
    
    
    data=im.fromarray(array)
    image=data.convert("RGB")
    return image
R=255
G=105
B=180
total=int(R)+int(G)+int(B)
blue=B/total
green=G/total
red=R/total
SLM=make_SLM_pattern(red,green,blue)
SLM.show()
#SLM.save("C:/Users/mcgeelab/Desktop/"+"deeppink.png")



    
    
    
