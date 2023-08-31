import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import os
import t1_mapping
from nilearn import plotting
import json

# Load dataset paths
subject = '334264'
scan = '401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
scan_num = '401'
scan_times = ['1010', '3310']
dataset_path = '/nfs/masi/saundam1/outputs/mp2rage_converted_v2023/'
subject_path = os.path.join(dataset_path, subject, scan)

# Load NIFTI files
inv1_real = nib.load(os.path.join(subject_path, f'{scan_num}_real_t{scan_times[0]}.nii'))
inv1_imag = nib.load(os.path.join(subject_path, f'{scan_num}_imaginary_t{scan_times[0]}.nii'))
inv2_real = nib.load(os.path.join(subject_path, f'{scan_num}_real_t{scan_times[1]}.nii'))
inv2_imag = nib.load(os.path.join(subject_path, f'{scan_num}_imaginary_t{scan_times[1]}.nii'))

# Load JSON
inv1_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.json')
inv2_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.json')
with open(inv1_json_path, 'r') as f1, open(inv2_json_path, 'r') as f2:
    inv1_json = json.load(f1)
    inv2_json = json.load(f2)
# Load data from NIFTI
inv1_real_data = inv1_real.get_fdata()
inv1_imag_data = inv1_imag.get_fdata()
inv2_real_data = inv2_real.get_fdata()
inv2_imag_data = inv2_imag.get_fdata()

# Create combined complex data
inv1_data = inv1_real_data + 1j*inv1_imag_data
inv2_data = inv2_real_data + 1j*inv2_imag_data

# # Create NIFTIs
# inv1 = nib.nifti2.Nifti2Image(inv1_data, inv1_real.affine)
# inv2 = nib.nifti2.Nifti2Image(inv2_data, inv2_real.affine)

# Calculate MP2RAGE image
t1w = t1_mapping.utils.mp2rage_t1w(inv1_data, inv2_data)
t1w_nifti = nib.nifti2.Nifti2Image(t1w, inv1_real.affine)

# # Plot T1w image
# fig, ax = plt.subplots()
# plotting.plot_img(t1w_nifti, cut_coords=(15, 5, 30), cmap='gray', axes=ax, colorbar=True)
# ax.set_title('T1-Weighted Image')

# Plot T1w image
# fig = t1_mapping.utils.plot_ortho(t1w, cut_coords=(15, 5, 30), affine=t1w_nifti.affine)
# fig.suptitle('T1-weighted image (mine)')
# plt.show()
fig, axes = plt.subplots(1, 3)
viewer = nib.viewers.OrthoSlicer3D(t1w, axes=axes, affine=t1w_nifti.affine, title='My T1W')
plt.colorbar()
plt.show()