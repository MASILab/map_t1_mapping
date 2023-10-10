# Compare LUT T1 map with ground truth
import t1_mapping
import os
import nibabel as nib
import nibabel.processing
import numpy as np
import matplotlib.pyplot as plt
from nilearn.plotting import plot_anat

# Load data
subj_id = 334264
t1_lut = nib.load(os.path.join(t1_mapping.definitions.T1_MAPS_LUT, str(subj_id), 't1_map.nii'))
t1_truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_reg', 'Warped.nii.gz'))

# Plot T1 map and ground truth
# fig, ax = plt.subplots()
# display = plot_anat(t1_lut, cut_coords=(5, 0, 2), radiological=True, 
#     axes=ax, colorbar=True, vmin=0, vmax=5)
# display.add_overlay(t1_truth, threshold=0.5, cmap='gray', cbar_vmin=0, cbar_vmax=5)
# ax.set_title('T1 Map and Ground Truth')
# plt.show()

# Mask LUT by zero values of ground truth
t1_lut_data = t1_lut.get_fdata()
t1_truth_data = t1_truth.get_fdata()
mask = t1_truth_data > 0
t1_lut_data_masked = t1_lut_data * mask
t1_lut_masked = nib.Nifti1Image(t1_lut_data_masked, t1_lut.affine)

# Take difference
t1_diff = np.abs(t1_lut_data_masked - t1_truth_data)
t1_diff_nifti = nib.Nifti1Image(t1_diff, t1_lut.affine)

# Show masked data
fig, ax = plt.subplots()
display = plot_anat(t1_diff_nifti, cut_coords=(5, 0, 2), radiological=True, 
    axes=ax, colorbar=True)
plt.show()