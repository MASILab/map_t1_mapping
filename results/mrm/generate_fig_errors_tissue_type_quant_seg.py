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

# Create RMSE dataframe
df = pd.DataFrame(columns=['Subject', 'Region', 'Method', 'RMSE'])

# Loop through subjects and get error in WM, GM and other
for subject in os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask')):
    # print(subject) 

    # # Load SLANT segmentation
    # slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask', subject, 't1w_seg.nii.gz'))

    # # Load niftis
    # truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    # map_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', subject, f't1_map.nii.gz'))
    # map_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_3_mask', subject, f't1_map.nii.gz'))
    # map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_all_mask', subject, f't1_map.nii.gz'))
    # lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_lut_mask', subject, f't1_map.nii.gz'))

    # # Loop through labels and find error
    # for label in np.unique(slant.get_fdata()):
    #     label_mask = slant.get_fdata() == label

    #     # Decide if label is WM, GM or other
    #     if label >= 40 and label <= 45:
    #         tissue_label = 'WM'
    #     elif label == 208 or label == 209 or label == 0 or label == 51 or label == 52:
    #         tissue_label = 'Other'
    #     else:
    #         tissue_label = 'GM'

    #     # Get error in label for each
    #     map_s1_2_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_s1_2.get_fdata()[label_mask])**2))
    #     map_s1_3_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_s1_3.get_fdata()[label_mask])**2))
    #     map_both_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_both.get_fdata()[label_mask])**2))
    #     lut_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - lut.get_fdata()[label_mask])**2))

    #     # Add to dataframe
    #     df.loc[len(df)] = [subject, label, 's1_2', tissue_label, map_s1_2_rmse]
    #     df.loc[len(df)] = [subject, label, 's1_3', tissue_label, map_s1_3_rmse]
    #     df.loc[len(df)] = [subject, label, 'both', tissue_label, map_both_rmse]
    #     df.loc[len(df)] = [subject, label, 'lut', tissue_label, lut_rmse]


    # Load SLANT segmentation
    slant_wm = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_mask', subject, 't1w_seg_wm.nii.gz'))
    slant_gm = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_mask', subject, 't1w_seg_gm.nii.gz'))
    slant_other = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_mask', subject, 't1w_seg_other.nii.gz'))

    wm_mask = slant_wm.get_fdata() > 0
    gm_mask = slant_gm.get_fdata() > 0
    other_mask = slant_other.get_fdata() > 0

    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    map_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', subject, f't1_map.nii.gz'))
    map_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_3_mask', subject, f't1_map.nii.gz'))
    map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_all_mask', subject, f't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_lut_mask', subject, f't1_map.nii.gz'))

    for method, map in zip(['s1_2', 's1_3', 'both', 'lut'], [map_s1_2, map_s1_3, map_both, lut]):
        # Get error in WM, GM and other
        wm_error = truth.get_fdata()[wm_mask] - map.get_fdata()[wm_mask]
        gm_error = truth.get_fdata()[gm_mask] - map.get_fdata()[gm_mask]
        other_error = truth.get_fdata()[other_mask] - map.get_fdata()[other_mask]

        # Add to dataframe
        df.loc[len(df)] = [subject, 'WM', method, np.sqrt(np.mean(wm_error**2))]
        df.loc[len(df)] = [subject, 'GM', method, np.sqrt(np.mean(gm_error**2))]
        df.loc[len(df)] = [subject, 'Other', method, np.sqrt(np.mean(other_error**2))]
        
print(df)

# Plot RMSE and standard error using seaborn
fig, ax = plt.subplots(figsize=(6.5, 3))
sns.barplot(
    data=df,
    x='Region',
    y='RMSE',
    hue='Method',
    errorbar=None,
    ax=ax,
)

# Calculate standard error
for i, bar in enumerate(ax.patches):
    region = df['Region'].unique()[i // len(df['Method'].unique())]
    method = df['Method'].unique()[i % len(df['Method'].unique())]
    
    # Calculate standard error
    rmse_values = df[(df['Region'] == region) & (df['Method'] == method)]['RMSE']

    # Calculate number of subjects with this label
    num_subjects = df[(df['Region'] == region) & (df['Method'] == method)]['Subject'].unique().shape[0]

    se_val = np.std(rmse_values)/np.sqrt(num_subjects)

    print(f'{region} {method} {num_subjects}')

    ax.errorbar(
        x=bar.get_x() + bar.get_width() / 2,
        y=bar.get_height(),
        yerr=se_val,
        fmt='none',
        ecolor='black',
        capsize=5
    )

ax.set_ylabel('Mean RMSE across subjects (s)')

# Change legend labels
ax.legend(labels=['MAP T1 using $S_{1,2}$', 'MAP T1 using $S_{1,3}$', 'MAP T1 using both $S_{1,2}$ and $S_{1,3}$', 'Original point estimate T1'], loc='upper left')
plt.tight_layout()
plt.show()