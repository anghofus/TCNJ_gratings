from PIL import Image
import numpy as np
from scipy import signal 
import os

'''
Created Jun 10 2025 

Creates images for use with the modified printing code (chirped_printer.py) 
Takes a starting and ending period in pixel values and chirps it over a specified number of columns

To Do: add GUI to collect user inputs 

@author: Phill Nezamis
'''

'''User Inputs''' 
xmax_i = 20	    #starting period in pixels
xmax_f = 80    	#final period in pixels

num_cols = 5    	#number of desired columns in final print run 
				#program outputs 1 image for each column 

ymin = 0		    #minium greyscale value           
ymax = 128		#maximum greyscale value 

'''Folder and File name'''
#folder where images will be saved, leave blank to save in same directory as script 
save_to = 'C:/Users/mcgeelab/Desktop/SLMImages'
#name scheme for saved mages, a number corresponding to the image's column is appended 
basic_name = 'chirp_test1_20to80.png' 

'''Generate the chirped sawtooth waveform'''
SLM_width = 1920    	#parameters of SLM screen
SLM_height = 1152 

chirp_width = SLM_width*num_cols    #calculate total pixel width of final chirped grating 
y_pp = ymax - ymin 					#peak to peak greyscale value 

xmax_array = np.linspace(xmax_i, xmax_f, chirp_width) #calculate the instaneous xmax value over the whole width 

phase = 2*np.pi*np.cumsum(1/xmax_array) #nonlinear array that produces a linear chirp when fed to sawtooth function
										#essentially the integral of the instaneous xmax value 

waveform = ymin + y_pp*(1 + signal.sawtooth(phase) / 2) 	#generate a chirped sawtooth that oscillates from ymin to ymax


'''Create image object and save''' 
image_array = np.zeros((SLM_height, SLM_width), dtype = np.uint8)	#empty array to build image in 

for n in np.arange(num_cols):						#loop for each column in print
	
	for x in np.arange(SLM_width):					#in each column build the SLM image from waveform
		ii = x + n*SLM_width						    #index for the chirp waveform to be correct for each column
		image_array[:,x] = waveform[ii]				#fill the image array 
		
	colname = str(num_cols - n)								#images are created from left to right, but printed right to left 
	image = Image.fromarray(image_array)		#turn the array into an image object and save 
	image.save(os.path.join(save_to, colname + basic_name)) 	#image names are preceded by the column number
  
'''
#just for testing/debugging
wholeimage_array = np.zeros((SLM_height, chirp_width), dtype=np.uint8)
for xx in np.arange(chirp_width):
    wholeimage_array[:,xx] = waveform[xx]

wholeimage = Image.fromarray(wholeimage_array)
wholeimage.save(os.path.join(save_to, 'whole.png'))
'''