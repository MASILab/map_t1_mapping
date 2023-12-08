# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import plot_nifti, load_slice

fig, axes = plt.subplots(3,4, figsize=(6.5, 3))
for i, subject in enumerate(['334264']):
    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_lut_mask', subject, f't1_map.nii.gz'))
    map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_all_mask', subject, f't1_map.nii.gz'))
    map1 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', subject, f't1_map.nii.gz'))
    map2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_3_mask', subject, f't1_map.nii.gz'))
    
    # Error NIFTIs
    lut_error = nib.Nifti1Image(truth.get_fdata() - lut.get_fdata(), truth.affine)
    map_both_error = nib.Nifti1Image(truth.get_fdata() - map_both.get_fdata(), truth.affine)
    map1_error = nib.Nifti1Image(truth.get_fdata() - map1.get_fdata(), truth.affine)
    map2_error = nib.Nifti1Image(truth.get_fdata() - map2.get_fdata(), truth.affine)

    # Load slices
    lut_slice = load_slice(lut_error, view=2)
    map_both_slice = load_slice(map_both_error, view=2)
    map1_slice = load_slice(map1_error, view=2)
    map2_slice = load_slice(map2_error, view=2)

    # Plot slices
    t = axes[i,0].imshow(lut_slice, 'RdBu', vmin=-3, vmax=3)
    axes[i,1].imshow(map_both_slice, 'RdBu', vmin=-3, vmax=3)
    axes[i,2].imshow(map1_slice, 'RdBu', vmin=-3, vmax=3)
    axes[i,3].imshow(map2_slice, 'RdBu', vmin=-3, vmax=3)

    axes[i,0].set_axis_off()
    axes[i,1].set_axis_off()
    axes[i,2].set_axis_off()
    axes[i,3].set_axis_off()

# Add colorbars
cbar1 = fig.colorbar(t, ax=axes)
cbar1.ax.set_xlabel('s')
cbar1.ax.set_ylabel('Error compared to ground truth')

plt.show()

fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/errors.png', dpi=600)