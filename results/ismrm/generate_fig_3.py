# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import plot_nifti, load_slice

# Load subject
subj_lut = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
)
t1_lut = subj_lut.t1_map

subj_like = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'), 
    all_inv_combos=False,
)
t1_like = subj_like.t1_map

# Mask by zero values of ground truth
t1_lut_data = t1_lut.get_fdata()
t1_like_data = t1_like.get_fdata()
mask = (t1_lut_data > 0) & (t1_like_data > 0)
t1_lut_data_masked = t1_lut_data[mask > 0]
t1_like_data_masked = t1_like_data[mask > 0]

# Get difference and average arrays
difference = t1_like_data_masked - t1_lut_data_masked
average = (t1_like_data_masked + t1_lut_data_masked)/2

# Plot histogram
nbins = 50
fig, ax = plt.subplots()
counts, xbins, ybins, hist = ax.hist2d(average, difference, bins=[nbins, nbins], norm='log', cmap='viridis') #norm='log'
ax.set_xlabel('Mean (s)')
ax.set_ylabel('Difference (s)\nMAP $T_1$ Map - Original MP2RAGE $T_1$ Map')

# Add colorbar
cbar = fig.colorbar(hist, ax=ax)
cbar.set_label('Count (log scale)')
ax.set_title('Bland-Altman Density Plot')

fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/ISMRM_figures/Figure_3.png', dpi=600)
plt.show()
