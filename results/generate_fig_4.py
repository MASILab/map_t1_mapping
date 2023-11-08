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

t1_diff = nib.Nifti1Image(t1_like.dataobj - t1_lut.dataobj, subj_like.affine)

fig, axes = plot_nifti(t1_diff, cmap='RdBu', vmin=-3, vmax=3, slice_labels=False, cbar_label='s', title='Difference\nMAP $T_1$ Map - Original MP2RAGE $T_1$ Map')

plt.tight_layout()
fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/ISMRM_figures/Figure_4.png', dpi=600)
plt.show()
