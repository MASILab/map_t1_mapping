# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import load_slice

noise_levels = [0.001, 0.005, 0.01, 0.015, 0.02, 0.025, 0.05]
fig, axes = plt.subplots(3,len(noise_levels), figsize=(9, 3))
fig2, axes2 = plt.subplots(3, len(noise_levels), figsize=(9, 3))
for i, subject in enumerate(['334264', '335749', '336954']):
    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    noisy_maps = [nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', f't1_maps_s1_2_{noise_level}_mask', subject, 't1_map.nii.gz')) for noise_level in noise_levels]

    # Calculate error NIFTIs
    error_maps = [nib.Nifti1Image(truth.get_fdata() - n.get_fdata(), truth.affine) for n in noisy_maps]

    # Load slices
    truth_slice = load_slice(truth, view=2)
    error_slices = [load_slice(e, view=2) for e in error_maps]
    noise_slice = [load_slice(n, view=2) for n in noisy_maps]

    # Plot slices
    for j, error_slice in enumerate(error_slices):
        t = axes[i,j].imshow(error_slice, 'RdBu', vmin=-3, vmax=3)
        t2 = axes2[i,j].imshow(noise_slice[j], 'gray', vmin=0, vmax=5)

    for k, noise_level in enumerate(noise_levels):
        axes[0, k].set_title(f'$\sigma = {noise_level}$')
        axes2[0, k].set_title(f'$\sigma = {noise_level}$')

    _ = [a.set_axis_off() for a in axes[i,:]]
    _ = [a.set_axis_off() for a in axes2[i,:]]

# Add colorbars
cbar1 = fig.colorbar(t, ax=axes)
cbar1.ax.set_xlabel('s')
cbar1.ax.set_ylabel('Error compared to ground truth')

cbar2 = fig2.colorbar(t2, ax=axes2)
cbar2.ax.set_xlabel('s')
cbar2.ax.set_ylabel('$T_1$')

plt.show()

fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/sensitivity_qualitative.png', dpi=600)
fig2.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/sensitivity_errors.png', dpi=600)