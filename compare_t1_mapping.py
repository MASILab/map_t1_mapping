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
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310']
)
# t1_lut = subj.t1_map
# t1_truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_affine', str(subj_id), 'Warped.nii.gz'))

# # Mask LUT by zero values of ground truth
# t1_lut_data = t1_lut.get_fdata()
# t1_truth_data = t1_truth.get_fdata()
# mask = t1_truth_data > 0
# t1_lut_data_masked = t1_lut_data * mask
# t1_lut_masked = nib.Nifti1Image(t1_lut_data_masked, t1_lut.affine)

# # Generate Bland-Altman plot
# fig, ax = plt.subplots()
# mean_diff_plot(t1_lut_data_masked.flatten()[::50], t1_truth_data.flatten()[::50], ax=ax)
# plt.show()

t1_linear = subj.get_t1_map(method='linear')
t1_cubic = subj.get_t1_map(method='cubic')

# Plot both
fig, ax = plt.subplots()
plot_anat(t1_linear, cut_coords=(15, 5, 30), radiological=True, 
    axes=ax, colorbar=True)
ax.set_title('T1 Linear')

fig, ax = plt.subplots()
plot_anat(t1_cubic, cut_coords=(15, 5, 30), radiological=True, 
    axes=ax, colorbar=True)
ax.set_title('T1 Cubic')

# Plot difference
diff = nib.Nifti1Image(t1_linear.get_fdata() - t1_cubic.get_fdata(), t1_linear.affine)
fig, ax = plt.subplots()
plot_anat(diff, cut_coords=(15, 5, 30), radiological=True, 
    axes=ax, colorbar=True)
ax.set_title('Difference')

# Generate Bland-Altman plot
fig, ax = plt.subplots()
mean_diff_plot(t1_linear.get_fdata().flatten()[::50], t1_cubic.get_fdata().flatten()[::50], ax=ax)
plt.show()