# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 10:48:55 2023

@author: Oktay for LED-Project  
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
    degree=-degree
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



def getspecs(n,line):
    distancetocenterg=n*0.000130#center of line
    center=0.0033+line*0.000080
    distancetoorigin=((distancetocenterg**2)+(center**2))**0.5
    angle=np.arcsin(distancetocenterg/distancetoorigin)*180/np.pi
    period=6.0613513513513515+((1.43-5)/(0.0144-0.0033))*distancetoorigin
    Xmax=period*15
    return Xmax,angle

Xmax,angle=getspecs(69,0)
print(Xmax,angle)

#print(angle)
"""
number_of_lines=29
offset=((number_of_lines-1)/2)+1

n=number_of_lines*number_of_lines
exp_list=[]
row=0
col=0
i=0
SLM_pattern=0
line=0
lines=number_of_lines-1


while SLM_pattern<n:
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
        Xmax,angle=getspecs((offset-k),line)
        SLM=make_SLM_pattern(Xmax,angle)
        #print(str(Xmax)+";"+str(angle))
        SLM_pattern=SLM_pattern+1
        SLM.save("C:/Users/mcgeelab/Desktop/Oktay-Photonics-Lab/New folder5/"+name+".png")
        l=0
    line=line+1
    
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
        Xmax,angle=getspecs((l-offset),line)
        SLM=make_SLM_pattern(Xmax,angle)
        #print(str(Xmax)+":"+str(angle))
        SLM_pattern=SLM_pattern+1
        k=0
        SLM.save("C:/Users/mcgeelab/Desktop/Oktay-Photonics-Lab/New folder5/"+name+".png")
    line=line+1    

print("done")
np.savetxt("C:/Users/mcgeelab/Desktop/Oktay-Photonics-Lab/New folder5/exp_times.csv",exp_list,delimiter=",",fmt="%s",)

"""
