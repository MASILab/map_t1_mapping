# Double check T1 maps
import numpy as np
import matplotlib.pyplot as plt
import t1_mapping
import nibabel as nib
import os
from adam_utils.nifti import plot_nifti

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'], #5610
    all_inv_combos=False,
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2_0.0006.npy')
)

# Load T1 maps
t1_map = subj.t1_map('map')

# Plot
fig, ax = plot_nifti(t1_map)

plt.show()