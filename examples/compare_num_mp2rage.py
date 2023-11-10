# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import plot_nifti, load_slice

# Load subject
subj_like = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing_full.npy'), 
    all_inv_combos=True,
)
t1_like = subj_like.t1_map
t1_like_slice = load_slice(t1_like, view=2)

t1_ev = subj_like.t1_ev
t1_ev_slice = load_slice(t1_ev, view=2)

t1_var = subj_like.t1_var
t1_std = nib.Nifti1Image(np.sqrt(t1_var.dataobj), subj_like.affine)
t1_std_slice = load_slice(t1_std, view=2)

# Load subject
subj_like2 = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'), 
    all_inv_combos=False,
)
t1_like2 = subj_like.t1_map
t1_like_slice2 = load_slice(t1_like, view=2)

t1_ev2 = subj_like.t1_ev
t1_ev_slice2 = load_slice(t1_ev, view=2)

t1_var2 = subj_like.t1_var
t1_std2 = nib.Nifti1Image(np.sqrt(t1_var.dataobj), subj_like.affine)
t1_std_slice2 = load_slice(t1_std, view=2)

fig, axes = plt.subplots(1, 3)

im = axes[0].imshow(t1_like_slice - t1_like_slice2, 'gray')
axes[0].set_title('Difference in MAP Estimate of $T_1$')
axes[0].set_axis_off()
cax = axes[0].inset_axes([-0.1, 0, 0.05, 1])
cbar = fig.colorbar(im, ax=axes[0], cax=cax, location='left')
cbar.ax.set_xlabel('s')

im = axes[1].imshow(t1_ev_slice - t1_ev_slice2, 'gray')
axes[1].set_title('Difference in Expected Value of $T_1$')
axes[1].set_axis_off()
cax = axes[1].inset_axes([-0.1, 0, 0.05, 1])
cbar = fig.colorbar(im, ax=axes[1], cax=cax, location='left')
cbar.ax.set_xlabel('s')

im = axes[2].imshow(t1_std_slice - t1_std_slice, cmap='viridis')
axes[2].set_title('Difference in Standard Deviation of $T_1$')
axes[2].set_axis_off()
cax = axes[2].inset_axes([-0.1, 0, 0.05, 1])
cbar = fig.colorbar(im, ax=axes[2], cax=cax, location='left')
cbar.ax.set_xlabel('s')

plt.tight_layout()
# fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/ISMRM_figures/Figure_2.png', dpi=600)

map_nifti = nib.Nifti1Image(t1_like.dataobj - t1_like2.dataobj, subj_like.affine)
ev_nifti = nib.Nifti1Image(t1_ev.dataobj - t1_ev2.dataobj, subj_like.affine)
var_nifti = nib.Nifti1Image(t1_var.dataobj - t1_var.dataobj, subj_like.affine)
nib.save(map_nifti, '/nfs/masi/saundam1/outputs/t1_mapping/test/map_diff.nii.gz')
nib.save(ev_nifti, '/nfs/masi/saundam1/outputs/t1_mapping/test/ev_diff.nii.gz')
nib.save(var_nifti, '/nfs/masi/saundam1/outputs/t1_mapping/test/var_diff.nii.gz')

plt.show()
