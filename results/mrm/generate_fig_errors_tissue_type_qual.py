# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import plot_nifti, load_slice
import pandas as pd
import matplotlib
from skimage.measure import find_contours
import copy

# Plot errors with segmentations
fig, axes = plt.subplots(3,4, figsize=(6.5, 3))
for i, subject in enumerate(['334264', '335749', '336954']):

    # Load SLANT segmentation
    slant = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_mask', subject, 't1w_seg.nii.gz'))
    slant_slice = load_slice(slant, view=2)

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
    vmin = -3
    vmax = 3
    norm = matplotlib.colors.SymLogNorm(
        linthresh=0.1,
        linscale=0.2,
        vmin=vmin,
        vmax=vmax,
    )
    t = axes[i,0].imshow(lut_slice, 'RdBu', norm=norm)
    axes[i,1].imshow(map_both_slice, 'RdBu', norm=norm)
    axes[i,2].imshow(map1_slice, 'RdBu', norm=norm) 
    axes[i,3].imshow(map2_slice, 'RdBu', norm=norm)


    axes[i,0].set_axis_off()
    axes[i,1].set_axis_off()
    axes[i,2].set_axis_off()
    axes[i,3].set_axis_off()

axes[0,0].set_title('Original point\nestimate T1')
axes[0,1].set_title('MAP T1 with both\n$S_{1,2}$ and $S_{1,3}$')
axes[0,2].set_title('MAP T1 with $S_{1,2}$ alone')
axes[0,3].set_title('MAP T1 with $S_{1,3}$ alone')

# Add colorbars
cbar1 = fig.colorbar(t, ax=axes)
cbar1.ax.set_xlabel('s')
cbar1.ax.set_ylabel('Error (ground truth - experimental value,\nsymmetric log scale)')

# Plot WM, GM, other for example subjects
fig2, axes2 = plt.subplots(3,4, figsize=(6.5, 3))
for i, subject in enumerate(['334264', '335749', '336954']):

    # Load SLANT segmentation
    slant_wm = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_mask', subject, 't1w_seg_wm.nii.gz'))
    slant_gm = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_mask', subject, 't1w_seg_gm.nii.gz'))
    slant_other = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_mask', subject, 't1w_seg_other.nii.gz'))
    slant_wm_slice = load_slice(slant_wm, view=2, slice=2)
    slant_gm_slice = load_slice(slant_gm, view=2, slice=2)
    slant_other_slice = load_slice(slant_other, view=2, slice=2)

    wm_mask = slant_wm_slice > 0
    gm_mask = slant_gm_slice > 0
    other_mask = slant_other_slice > 0

    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    map = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', subject, f't1_map.nii.gz'))
    
    # Error NIFTIs
    map_error = nib.Nifti1Image(truth.get_fdata() - map.get_fdata(), truth.affine)

    # Load slices
    map_slice = load_slice(map_error, view=2, slice=2)
    map_slice_wm = copy.deepcopy(map_slice)
    map_slice_gm = copy.deepcopy(map_slice)
    map_slice_other = copy.deepcopy(map_slice)

    map_slice_wm[~wm_mask] = 0
    map_slice_gm[~gm_mask] = 0
    map_slice_other[~other_mask] = 0

    # Plot slices
    t = axes2[i,0].imshow(map_slice_wm, 'RdBu', norm=norm)
    axes2[i,1].imshow(map_slice_gm, 'RdBu', norm=norm)
    axes2[i,2].imshow(map_slice_other, 'RdBu', norm=norm)
    axes2[i,3].imshow(map_slice, 'RdBu', norm=norm)

    axes2[i,0].set_xticks([])
    axes2[i,0].set_yticks([])
    axes2[i,1].set_xticks([])
    axes2[i,1].set_yticks([])
    axes2[i,2].set_xticks([])
    axes2[i,2].set_yticks([])
    axes2[i,3].set_xticks([])
    axes2[i,3].set_yticks([])

axes2[0,0].set_title('WM')
axes2[0,1].set_title('GM')
axes2[0,2].set_title('Other')
axes2[0,3].set_title('All')

# Add colorbars
cbar2 = fig2.colorbar(t, ax=axes2)
cbar2.ax.set_xlabel('s')
cbar2.ax.set_ylabel('Error (ground truth - experimental value,\nsymmetric log scale)')

plt.show()

# fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/errors.png', dpi=600)