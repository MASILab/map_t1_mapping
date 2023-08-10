# Create MP2RAGE image
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
from mp2rage.utils import MP2RAGE

# Load dataset paths
subject = '334264'
scan = '401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
scan_num = '401'
scan_times = ['1010', '3310']
dataset_path = '/nfs/masi/saundam1/Outputs/MP2RAGE_converted/'
subject_path = os.path.join(dataset_path, subject, scan)

# Load NIFTI files
inv1 = nib.load(os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.nii'))
inv1_ph = nib.load(os.path.join(subject_path, f'{scan_num}_ph_t{scan_times[0]}.nii'))
inv2 = nib.load(os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.nii'))
inv2_ph = nib.load(os.path.join(subject_path, f'{scan_num}_ph_t{scan_times[1]}.nii'))

# Load data from NIFTI
inv1_mag = inv1.get_fdata()
inv1_ph = inv1_ph.get_fdata()
inv2_mag = inv2.get_fdata()
inv2_ph = inv2_ph.get_fdata()

# Print maxes and mins for sanity
print(nib.volumeutils.finite_range(inv1_mag))
print(nib.volumeutils.finite_range(inv1_ph))
print(nib.volumeutils.finite_range(inv2_mag))
print(nib.volumeutils.finite_range(inv2_ph))

# Create combined complex data
inv1_data = inv1_mag*np.exp(1j*inv1_ph)
inv2_data = inv2_mag*np.exp(1j*inv2_ph)

# Calculate MP2RAGE image (scale to same as pymp2rage)
mp2rage = MP2RAGE(inv1_data, inv2_data)
mp2rage_nifti = nib.nifti1.Nifti1Image(mp2rage, inv1.affine)

# Save to file
output_path = os.path.join('outputs', f'{subject}_{scan_num}_mp2rage.nii.gz')
nib.save(mp2rage_nifti, output_path)