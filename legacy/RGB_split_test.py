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

img=im.open("C:/Users/mcgeelab/Desktop/watermelon.png")
#image= img.resize((10,10))
imgsplit=im.Image.split(img)
redarray=np.asarray(imgsplit[0])
greenarray=np.asarray(imgsplit[1])
bluearray=np.asarray(imgsplit[2])



#newimage.show()
#newimage.save("C:/Users/mcgeelab/Desktop/Logo_scaled.PNG")
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

    while i<regionblue+regiongreen-1:
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
#R=32,G=178,B=170-->LightSeaGreen
#R=int(redscale[0][9])
#G=int(greenscale[0][9])
#B=int(bluescale[0][9])

exp_list=[]
count=len(redarray)**2
SLM_pattern=0
line=0
lines=len(redarray)-1
while SLM_pattern<count:
    
    k=0
    l=500
    while k<len(redarray) and SLM_pattern<count:
        R=redarray[lines-line][lines-k]#lenght of array - position
        G=greenarray[lines-line][lines-k]
        B=bluearray[lines-line][lines-k]
        if line <10:
            if k<10:
                name=str(0)+str(line)+str(0)+str(k)
            if k>=10:
                name=str(0)+str(line)+str(k)
        if line >=10:
            if k<10:
                name=str(line)+str(0)+str(k)
            if k>=10:
                name=str(line)+str(k)
        k=k+1
        total=int(R)+int(G)+int(B)
        exp_list.append(total)
        blue=B/total
        green=G/total
        red=R/total
        SLM=make_SLM_pattern(red,green,blue)
        SLM_pattern=SLM_pattern+1
        SLM.save("C:/Users/mcgeelab/Desktop/watermelon_SLM/"+name+".png")
        l=0
    line=line+1
    while l<len(redarray) and SLM_pattern<count:
        R=redarray[lines-line][l]
        G=greenarray[lines-line][l]
        B=bluearray[lines-line][l]
        if line <10:
            if l<10:
                name=str(0)+str(line)+str(0)+str(l)
            if l>=10:
                name=str(0)+str(line)+str(l)
        if line >=10:
            if l<10:
                name=str(line)+str(0)+str(l)
            if l>=10:
                name=str(line)+str(l)
        l=l+1
        total=int(R)+int(G)+int(B)
        exp_list.append(total)
        blue=B/total
        green=G/total
        red=R/total
        SLM=make_SLM_pattern(red,green,blue)
        SLM_pattern=SLM_pattern+1
        k=0
        SLM.save("C:/Users/mcgeelab/Desktop/watermelon_SLM/"+name+".png")
    line=line+1

print(len(exp_list))
np.savetxt("C:/Users/mcgeelab/Desktop/watermelon_SLM/exp_times.csv",exp_list,delimiter=",",fmt="%s",)

    
