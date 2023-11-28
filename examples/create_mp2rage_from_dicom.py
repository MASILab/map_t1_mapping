# Create MP2RAGE data directly from DICOM
import os
import t1_mapping
import numpy as np
import pydicom 
from collections import defaultdict
import matplotlib.pyplot as plt

dcm_path = '/nfs/masi/saundam1/datasets/MP2RAGE/336547/336547/1101-x-MP2RAGE_0p8mm_1sTI_autoshim-x-MP2RAGE_0p8mm_1sTI_autoshim/DICOM/1.3.46.670589.11.9904.5.0.9528.2019021314591912000-1101-1-9s5np1.dcm'
dcm = pydicom.dcmread(dcm_path)
array = dcm.pixel_array

print(dcm.NumberOfFrames)

# 3 images - imaginary, magnitude, real
imag_array = array[::3,:,:]
mag_array = array[1::3,:,:]
real_array = array[2::3,:,:]

# Show first few frames from each 
fig, axs = plt.subplots(3, 4, figsize=(12, 9))

arrays = [imag_array, mag_array, real_array]

for i, array in enumerate(arrays):
    for j in range(4):
        axs[i, j].imshow(array[j,:,:], cmap='gray')
        axs[i, j].axis('off')  # Optional: remove axes for a cleaner look

plt.tight_layout()  # Optional: improve spacing between subplots
plt.show()
