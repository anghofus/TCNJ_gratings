import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
from scipy.interpolate import RectBivariateSpline 

def get_file_path():
	"""
	Opens a file dialog to select a single image file.
	Returns the file path as a string.
	"""
	root = tk.Tk()
	root.withdraw()

	while True:
		file_path = filedialog.askopenfilenames(title="Select exactly 1 image")
		if file_path == ():
			raise KeyboardInterrupt  # User canceled
		elif len(file_path) != 1:
			messagebox.showerror("Error", "Select exactly 1 image")
		else:
			return file_path[0]


def gs(img, max_iter):
	"""
	Performs the Gerchberg-Saxton algorithm. 
	Also does some padding/interpolating shennanginans. (Don't ask)  
	Args:
	img: 2D numpy array (grayscale image as amplitude constraint)
	max_iter: number of iterations
	Returns:
	2D complex numpy array representing the final near-field result
	"""
	target_amplitude = img / 255
	source_amplitude = np.ones_like(target_amplitude)
	
	x,y = np.shape(img) 
	fun = RectBivariateSpline(np.linspace(0,1,x), np.linspace(0,1,y), target_amplitude) #interpolation function 
	
	target_amplitude = np.fft.ifftshift(fun(np.linspace(0, 1, 2*x), np.linspace(0, 1, 2*y))) #interpolate target amplitude to be larger and inverse fftshift for numpy 
	source_amplitude = np.pad(source_amplitude, ((x//2, x//2), (y//2, y//2)), 'constant') #pad zeros around source amplitude to make same size as target 
		  
	near_field = np.fft.ifft2(target_amplitude) #inverse fft shift to start 

	#GS algo loop 
	for i in range(max_iter):
		near_field = source_amplitude * np.exp(1j*np.angle(near_field))
		far_field = np.fft.fft2(near_field)
		far_field = target_amplitude * np.exp(1j*np.angle(far_field)) 
		near_field = np.fft.ifft2(far_field) 

		print(f"Iteration {i+1}")
	
	phase_map = np.fft.fftshift(np.angle(near_field)) #pull out phase and fftshift it 

	return phase_map[x//2:-x//2, y//2:-y//2] #remove padding and return 


# --- Main Execution ---

# Load grayscale image
image = Image.open(get_file_path()).convert("L")
image_array = np.asarray(image)

while True:
	max_iters = input('How many iterations?:')
	try: 
		max_iters = int(max_iters) 
	except:
		print('ERROR: Enter an integer')
	else:
		break
		
# Run Gerchberg-Saxton algorithm
phase = gs(image_array, max_iters)

# Extract and normalize the phase to 0–255 for visualization
#direct mapping
#phase = np.angle(complex_near_field_array)
phase_normalized_scaled = (((phase + np.pi) / (2 * np.pi)) * 128).astype(np.uint8) #trying mapping directly to 128

# Save and display the phase map
phase_map = Image.fromarray(phase_normalized_scaled)

#get user input for filename and save phase map 
while True:
	phase_filename = input('Filename for phase map (include extension):')
	try: 
		phase_map.save(phase_filename)
	except:
		print('ERROR: Enter a valid filename')
	else:
		break

phase_map.show()

# Reconstruct far-field intensity for verification
reconstructed_field = np.exp(1j * phase)  # reconstruct complex field from phase
far_field = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(reconstructed_field)))  # proper FFT with shifts
intensity = np.abs(far_field) ** 2
normalized_intensity = (intensity / np.max(intensity) * 255).astype(np.uint8)
Image.fromarray(normalized_intensity).show()