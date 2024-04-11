# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:34:49 2023

@author: Oktay Senel 
"""


import numpy as np 
from scipy import signal 
from PIL import Image as im
#import cv2


width = 1920
height = 1152
array_width = 3000
array_height = array_width

def center_crop(image, array_width, array_height, width, height):
            x_margin = (array_width - width) //2
            y_margin = (array_height - height) // 2
            return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))


def make_SLM_pattern(Xmax,degree):
    t= np.linspace(0,3000,3000)
    f1=1/Xmax
    st= (1+signal.sawtooth(2*np.pi*f1*t))*64
    array= np.zeros((3000,3000))
    i=0
    j=0

    while i<3000:
        array[0][i]=(st[i])
        i=i+1

    while j<3000:
        array[j]=array[0]
        j=j+1
    
    
    data=im.fromarray(array)
    image=data.convert("RGB")
    img=image.rotate(90)
    img = img.rotate(degree)
    
    img = center_crop(img, array_width, array_height ,width, height)
    return img


number_of_lines=29
distance=0.05
step=(number_of_lines-1)/2
print(step)
angle=np.arctan((distance-(step*0.00008))/(distance))
angle2=np.arctan((distance+(step*0.00008))/(distance))
print(angle*180/np.pi)
xmax1=(15*633*10**(-3))/(np.sin(angle))
xmin1=(15*633*10**(-3))/(np.sin(angle2))
print(xmax1/15)
print(xmin1/15)
print(xmax1/15-xmin1/15)

rot=np.arctan((step*0.000130)/(distance*1.41421356237))*180/np.pi
print(rot)
rotpergrating=rot*2/(number_of_lines-1)
addpergrating=(xmax1-xmin1)/(number_of_lines-1)
print(rotpergrating)
print(addpergrating)
"""
n=number_of_lines*number_of_lines
exp_list=[]
row=0
col=0
i=0
SLM_pattern=0
line=0
lines=number_of_lines-1
xmax=xmax1

while SLM_pattern<n:
    degree=-rot
    k=0
    l=500
    while k<lines+1 and SLM_pattern<n:
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
        total=768
        exp_list.append(total)
        SLM=make_SLM_pattern(xmax,degree)
        print(str(xmax)+";"+str(degree))
        degree=degree+rotpergrating
        SLM_pattern=SLM_pattern+1
        SLM.save("C:/Users/mcgeelab/Desktop/Oktay-Photonics-Lab/New folder4/"+name+".png")
        l=0
    line=line+1
    xmax=xmax-addpergrating
    degree=+rot
    
    while l<lines+1 and SLM_pattern<n:
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
        total=768
        exp_list.append(total)
        SLM=make_SLM_pattern(xmax,degree)
        print(str(xmax)+":"+str(degree))
        degree=degree-rotpergrating
        SLM_pattern=SLM_pattern+1
        k=0
        SLM.save("C:/Users/mcgeelab/Desktop/Oktay-Photonics-Lab/New folder4/"+name+".png")
    line=line+1
    xmax=xmax-addpergrating

print(len(exp_list))
np.savetxt("C:/Users/mcgeelab/Desktop/Oktay-Photonics-Lab/New folder4/exp_times.csv",exp_list,delimiter=",",fmt="%s",)
"""
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    