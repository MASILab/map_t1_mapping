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
t1_lut_slice = load_slice(t1_lut, view=2)

subj_like = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'), 
    all_inv_combos=False,
)
t1_like = subj_like.t1_map
t1_like_slice = load_slice(t1_like, view=2)

t1_ev = subj_like.t1_ev
t1_ev_slice = load_slice(t1_ev, view=2)

t1_var = subj_like.t1_var
t1_var_slice = load_slice(t1_var, view=2)

fig, axes = plt.subplots(2, 2, figsize=(6.5, 6.5))
im = axes[0,0].imshow(t1_lut_slice, 'gray', vmin=0, vmax=5)
axes[0,0].set_title('Original MP2RAGE $T_1$ Map')
axes[0,0].set_axis_off()
cax = axes[0,0].inset_axes([-0.1, 0, 0.05, 1])
fig.colorbar(im, ax=axes[0,0], cax=cax, location='left')

axes[0,1].imshow(t1_like_slice, 'gray', vmin=0, vmax=5)
axes[0,1].set_title('MAP Estimate of $T_1$')
axes[0,1].set_axis_off()
cax = axes[0,1].inset_axes([-0.1, 0, 0.05, 1])
fig.colorbar(im, ax=axes[0,1], cax=cax, location='left')

axes[1,0].imshow(t1_ev_slice, 'gray', vmin=0, vmax=5)
axes[1,0].set_title('Expected Value of $T_1$')
axes[1,0].set_axis_off()
cax = axes[1,0].inset_axes([-0.1, 0, 0.05, 1])
fig.colorbar(im, ax=axes[1,0], cax=cax, location='left')

im = axes[1,1].imshow(t1_var_slice, cmap='viridis', vmin=0, vmax=1)
axes[1,1].set_title('Variance of $T_1$')
axes[1,1].set_axis_off()
cax = axes[1,1].inset_axes([-0.1, 0, 0.05, 1])
fig.colorbar(im, ax=axes[1,1], cax=cax, location='left')

plt.tight_layout()
fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/ISMRM_figures/Figure_2.tiff', dpi=600)
plt.show()
