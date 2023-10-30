# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
from nilearn import plotting 
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import plot_nifti

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_1M_spacing_full.npy'), 
    all_inv_combos=True,
)

# Get T1 map and plot
t1_map = subj.t1_map
fig, ax = plot_nifti(t1_map, title='T1 Map')
plt.show()

# Save
t1_map.to_filename(os.path.join(t1_mapping.definitions.T1_MAPS_LIKELIHOOD, subj.subject_id, 't1_map.nii'))