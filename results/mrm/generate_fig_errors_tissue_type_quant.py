# Generate figure 4: quantitative results (group)
import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from adam_utils.nifti import load_slice
import seaborn as sns
import ast

# Dictionary to hold labels, label names, and list of subjects with that label
label_df = pd.read_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_results.csv')
label_df['Subjects'] = label_df['Subjects'].apply(ast.literal_eval)

# Plot example slice of each in an 8 x 12 grid
fig, axes = plt.subplots(8, 12, figsize=(12, 8))
for i, label in enumerate(label_df['Label'].values):

    # Get current axes
    ax = axes[i//12, i%12]

    # Load example subject
    example_subject = label_df['Subjects'].iloc[i][0]
    subject = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', example_subject, 't1_map.nii.gz'))
    slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask', example_subject, 't1w_seg.nii.gz'))
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', example_subject, 't1_map.nii.gz'))

    # Choose axial slice number as one where label has most pixel values
    slant_data = slant.get_fdata()
    num_per_slice = [np.sum(slant_data[:,:,i] == label, axis=(0,1)) for i in range(slant_data.shape[2])]
    slice_num = np.argmax(num_per_slice)

    # Calculate error
    error = nib.Nifti1Image(truth.get_fdata() - subject.get_fdata(), slant.affine)
    error_slice = load_slice(error, view=2, slice=slice_num)
    slant_slice = load_slice(slant, view=2, slice=slice_num)

    # Mask error_slice by label
    error_slice[slant_slice != label] = 0

    # Split label name at hyphens
    label_name = label_df['Name'].iloc[i]
    label_name_split = label_name.split('-')
    label_name_split = [split for split in label_name_split if split != '']

    
    # Set label as splits separated by newlines every other word
    label_name = ''
    for j, split in enumerate(label_name_split):
        if (j + 1) % 2 == 0:
            label_name += split + '\n'
        else:
            label_name += split + ' '


    vmin = -3
    vmax = 3
    norm = matplotlib.colors.SymLogNorm(
        linthresh=0.1,
        linscale=0.2,
        vmin=vmin,
        vmax=vmax,
    )

    t = ax.imshow(error_slice, cmap='RdBu', norm=norm, interpolation='nearest')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(label_name, fontsize=8)

# Add colorbar to bottom
cbar = fig.colorbar(t, ax=axes[:, -1])
cbar.ax.set_xlabel('s')
cbar.ax.set_ylabel('Error (ground truth - experimental value,\nsymmetric log scale)')

# Adjust colorbar to be farther right
cbar.ax.set_position([0.92, 0.15, 0.05, 0.7])

# Adjust so titles don't overlap
fig.subplots_adjust(hspace=1.2, wspace=0.5)

fig, ax = plt.subplots(figsize=(14,8))
# ax = sns.pointplot(x='Name', y='Mean Error S1_2', data=label_df, color='blue', label='MAP using $S_{1,2}$', markers='o', error='Standard Error S1_2')
# ax = sns.pointplot(x='Name', y='Mean Error S1_3', data=label_df, color='green', label='MAP using $S_{1,3}$', markers='o', error='Standard Error S1_3')
# ax = sns.pointplot(x='Name', y='Mean Error All', data=label_df, color='orange', label='MAP using both $S_{1,2}$ and $S_{1,3}$', markers='o', error='Standard Error All')
# ax = sns.pointplot(x='Name', y='Mean Error Orig', data=label_df, color='red', label='Original point estimate', markers='o', error='Standard Error Orig')
for i, (mean, error, color, label) in enumerate(zip(['Mean Error S1_2', 'Mean Error S1_3', 'Mean Error All', 'Mean Error Orig'],
                                                    ['Standard Error S1_2', 'Standard Error S1_3', 'Standard Error All', 'Standard Error Orig'],
                                                    ['blue', 'green', 'orange', 'red'],
                                                    ['MAP using $S_{1,2}$', 'MAP using $S_{1,3}$', 'MAP using both $S_{1,2}$ and $S_{1,3}$', 'Original point estimate'])):
    ax = sns.scatterplot(x=label_df['Name'], y=label_df[mean], color=color, label=label)
    plt.errorbar(x=label_df['Name'], y=label_df[mean], yerr=label_df[error], fmt='o', color=color, capsize=3)


ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_xlabel('Tissue Type')
ax.set_ylabel('RMSE compared to ground truth (s)')

plt.tight_layout()
plt.show()

# fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/quantitative_results.png', dpi=600)