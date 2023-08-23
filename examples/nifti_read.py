# Read NIFTI

import os
import glob
import json
import nibabel as nib
from nibabel.testing import data_path

# Load folder
subject = '334264'
scan = '401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
scan_num = '401'
dataset_path = '/nfs/masi/saundam1/outputs/mp2rage_converted_v2023/'
subject_path = os.path.join(dataset_path, subject, scan)

# Load NIFTI 
nifti_path = os.path.join(subject_path, '401_ph_t3310.nii')
img = nib.load(nifti_path)

# Load JSON
json_path = os.path.join(subject_path, '401_ph_t3310.json')
with open(json_path, 'r') as f:
    json = json.load(f)

# Set slope and intercept
scl_slope = 1/json["PhilipsScaleSlope"]
scl_inter = json["PhilipsRescaleIntercept"]/(json["PhilipsScaleSlope"]*json["PhilipsRescaleSlope"])
print(f'Setting slope to {scl_slope} and intercept to {scl_inter}')
img.header.set_slope_inter(scl_slope, scl_inter)

# Save file
output_path = os.path.join('outputs', f'{subject}_{scan_num}_nifti_scaled.nii.gz')
print(os.listdir())
with open(output_path, 'w') as f:
    nib.save(img, output_path)