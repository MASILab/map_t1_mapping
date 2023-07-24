# Getting started with NiBabel
# Based on https://nipy.org/nibabel/gettingstarted.html

import os
import numpy as np
import nibabel as nib
from nibabel.testing import data_path

# Load example file from NiBabel
#example_file = os.path.join(data_path, 'example4d.nii.gz')
example_file = '/home/saundam1/Datasets/ds003642/sub-025/ses-003/anat/sub-025_ses-003_INV2.nii.gz'
img = nib.load(example_file)

# Print some information about the data
print(f'Shape: {img.shape}')
print(f'Data type: {img.get_data_dtype()}')
print(f'Affine transformation: \n{img.affine}')

# Load header
hdr = img.header
print(hdr)
print(f'Units: {hdr.get_xyzt_units()}')
