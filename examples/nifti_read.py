# Getting started with NiBabel
# Based on https://nipy.org/nibabel/gettingstarted.html

import os
import numpy as np
import nibabel as nib
from nibabel.testing import data_path

# Load example file from NiBabel
example_file = '/nfs/masi/saundam1/Datasets/MP2RAGE/336195/336195/MP2RAGE-x-336195-x-336195-x-mp2rage_v2_1-x-a0d72a85-bda8-490d-a558-129ae2a86c83/MP2RAGE/mp2rage.nii.gz'
img = nib.load(example_file)

# Print some information about the data
print(f'Shape: {img.shape}')
print(f'Data type: {img.get_data_dtype()}')
print(f'Affine transformation: \n{img.affine}')

# Load header
hdr = img.header
print(hdr)
print(f'Units: {hdr.get_xyzt_units()}')
