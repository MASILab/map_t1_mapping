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

# Load SLANT lookup table
lut_path = '/home/local/VANDERBILT/saundam1/Documents/slant/slant.lut'
df = pd.read_table(lut_path, delimiter='\s+', engine='python')


max_val = 209
# Loop through values in first column of df
colors_list = []
for i in range(max_val):
    
    # If i is in the first column of df, get the corresponding color
    if i in df.iloc[:,0].values:
        row_with_i = df[df.iloc[:, 0] == i]

        R = row_with_i.iloc[0, 1]  # Second column
        G = row_with_i.iloc[0, 2]   # Third column
        B = row_with_i.iloc[0, 3]  # Fourth column

        colors_list.append((R, G, B, 1.))
    else:
        colors_list.append((0, 0, 0, 1.))

# Create colormap
slant_cmap = matplotlib.colors.ListedColormap(colors_list, name='slant')


# Load SLANT segmentation
slant = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_test_mp2rage_nss_xnat_mask', '334264', 'mp2rage_seg.nii.gz'))
slant_slice = load_slice(slant, view=2)

# Create SLANT contour
unique_labels = np.unique(slant_slice)
contours = np.full_like(slant_slice, fill_value=np.nan)

for label in unique_labels:
    contour_mask = np.where(slant_slice == label, 1, 0)
    label_countours = find_contours(contour_mask, 0.5)
    for contour in label_countours:
        for point in contour:
            contours[int(point[0]), int(point[1])] = label


fig, axes = plt.subplots(2,2, figsize=(6.5, 3))
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
    t = axes[0,0].imshow(lut_slice, 'RdBu', vmin=-3, vmax=3)
    axes[0,1].imshow(map_both_slice, 'RdBu', vmin=-3, vmax=3)
    axes[1,0].imshow(map1_slice, 'RdBu', vmin=-3, vmax=3) 
    axes[1,1].imshow(map2_slice, 'RdBu', vmin=-3, vmax=3)


    axes[0,0].imshow(contours, cmap=slant_cmap, vmin=0, vmax=max_val, interpolation='none')
    axes[0,1].imshow(contours, cmap=slant_cmap, vmin=0, vmax=max_val, interpolation='none')
    axes[1,0].imshow(contours, cmap=slant_cmap, vmin=0, vmax=max_val, interpolation='none')
    axes[1,1].imshow(contours, cmap=slant_cmap, vmin=0, vmax=max_val, interpolation='none')


    axes[0,0].set_axis_off()
    axes[0,1].set_axis_off()
    axes[1,0].set_axis_off()
    axes[1,1].set_axis_off()

    axes[0,0].set_title('Original point\nestimate T1')
    axes[0,1].set_title('MAP T1 with both\n$S_{1,2}$ and $S_{1,3}$')
    axes[1,0].set_title('MAP T1 with $S_{1,2}$ alone')
    axes[1,1].set_title('MAP T1 with $S_{1,3}$ alone')

# Add colorbars
cbar1 = fig.colorbar(t, ax=axes)
cbar1.ax.set_xlabel('s')
cbar1.ax.set_ylabel('Error compared to ground truth')

plt.show()

# fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/errors.png', dpi=600)