# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 10:54:26 2023

@author: Oktay Senel 

this code adds sawteeth. we are not sure this code will work. 


"""
import numpy as np 
from scipy import signal 
from PIL import Image as im
#import matplotlib

t= np.linspace(0,1920,1920)

f1=1/30
f2=1/15
f3=1/9

st1= (1+signal.sawtooth(2*np.pi*f1*t))*64
st2= (1+signal.sawtooth(2*np.pi*f2*t))*10
st3= (1+signal.sawtooth(2*np.pi*f3*t))*4

#st=(st1+(1/3)*st2+(1/5)*st3)
st=st1
array= np.zeros((1152,1920))
i=0

j=0
while i<1920 :
    array[0][i]=(st[i])
    i=i+1
    
while j<1152:
    array[j]=array[0]
    j=j+1
    
    
data=im.fromarray(array)
data.show()
image=data.convert("RGB")
#image.save("sqw3microns4.png")
#matplotlib.pyplot.imshow(array, cmap="gray",vmax="128")