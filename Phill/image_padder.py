import os
from PIL import Image
import numpy as np

'''
Adds a pad of black (zeros) around an image to make it SLM sized
'''

filepath = os.getcwd()		#fielpath to folder where original image is and where edited image is saved
image_path = 'odd_pad_test.jpg'				#filepath to original image
SLM_image_path = 'pad_test.png'			#filepath to edited image 

image = Image.open(os.path.join(filepath, image_path))
image_arr = np.array(image)
image_size = np.shape(image_arr)

SLM_height, SLM_width = 1152, 1920

if image_size[0] < SLM_height:
	height_diff = SLM_height - image_size[0]
	height_pad = int(height_diff/2)
	
	if height_diff % 2 == 0:
		top_bottom = (height_pad, height_pad) 
	else:
		top_bottom = (height_pad, height_pad + 1) 
else:
	top_bottom = (0, 0)
	
if image_size[1] < SLM_width:
	width_diff = SLM_width - image_size[1]
	width_pad = int(width_diff/2)
	
	if width_diff % 2 == 0:
		left_right = (width_pad, width_pad)
	else:
		left_right = (width_pad, width_pad + 1) 
else:
	left_right = (0,0)
	
image_arr = np.pad(image_arr, (top_bottom, left_right, (0,0)), 'constant', constant_values = ((0,0),(0,0), (0,0))) 
			
final_image = Image.fromarray(image_arr) 
final_image.save(os.path.join(filepath, SLM_image_path)) 