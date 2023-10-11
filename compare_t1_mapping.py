# Compare LUT T1 map with ground truth
import t1_mapping
import os
import nibabel as nib
import nibabel.processing
import numpy as np
from statsmodels.graphics.agreement import mean_diff_plot
import matplotlib.pyplot as plt
from nilearn.plotting import plot_anat

# Load data
subj_id = 334264
t1_lut = nib.load(os.path.join(t1_mapping.definitions.T1_MAPS_LUT, str(subj_id), 't1_map.nii'))
t1_truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_affine', str(subj_id), 'Warped.nii.gz'))

# Mask LUT by zero values of ground truth
t1_lut_data = t1_lut.get_fdata()
t1_truth_data = t1_truth.get_fdata()
mask = t1_truth_data > 0
t1_lut_data_masked = t1_lut_data * mask
t1_lut_masked = nib.Nifti1Image(t1_lut_data_masked, t1_lut.affine)

# Generate Bland-Altman plot
fig, ax = plt.subplots()
mean_diff_plot(t1_lut_data_masked.flatten()[::50], t1_truth_data.flatten()[::50], ax=ax, sd_limit=50)
plt.show()