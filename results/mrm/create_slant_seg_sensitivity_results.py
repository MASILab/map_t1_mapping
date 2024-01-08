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
df = pd.DataFrame(columns=['Subject', 'Method', 'Tissue Type', 'Noise Level', 'RMSE'])

# Loop through subjects and get error in WM, GM and other
for subject in os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25_mask')):
    print(subject) 
    
    # Load SLANT segmentation
    slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25_mask', subject, 't1w_seg.nii.gz'))

    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject, f't1_map.nii.gz'))

    # Get masks
    slant_data = slant.get_fdata()
    all_mask = slant_data > 0
    wm_mask = (slant_data >= 40) & (slant_data <= 45)
    other_mask = (slant_data == 208) | (slant_data == 209) | (slant_data == 51) | (slant_data == 52)
    gm_mask = np.logical_and(all_mask, np.logical_not(wm_mask | other_mask))

    num_all = np.sum(all_mask)
    num_wm = np.sum(wm_mask)
    num_gm = np.sum(gm_mask)
    num_other = np.sum(other_mask)

    # Loop through noise levels
    for noise_level in [0.0005, 0.001, 0.005, 0.01, 0.015, 0.02]:
        map_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'sensitivity', f't1_maps_likelihood_s1_2_{noise_level}_mask', subject, f't1_map.nii.gz'))
        map_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'sensitivity', f't1_maps_likelihood_s1_3_{noise_level}_mask', subject, f't1_map.nii.gz'))
        map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'sensitivity', f't1_maps_likelihood_all_{noise_level}_mask', subject, f't1_map.nii.gz'))
        map_lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', f't1_maps_lut_mask', subject, f't1_map.nii.gz'))

        # for label in np.unique(slant.get_fdata()):
        #     label_mask = slant.get_fdata() == label

        #     # Decide if label is WM, GM or other
        #     if label >= 40 and label <= 45:
        #         tissue_label = 'WM'
        #     elif label == 208 or label == 209 or label == 0 or label == 51 or label == 52:
        #         tissue_label = 'Other'
        #     else:
        #         tissue_label = 'GM'

        # Loop through labels and find error
        for label_mask, tissue_label, num_voxel in zip([wm_mask, gm_mask, other_mask, all_mask], ['WM', 'GM', 'Other', 'All'], [num_wm, num_gm, num_other, num_all]):
            # Get error in label for each
            map_s1_2_rmse = np.sqrt(np.sum((truth.get_fdata()[label_mask] - map_s1_2.get_fdata()[label_mask])**2)/num_voxel)
            map_s1_3_rmse = np.sqrt(np.sum((truth.get_fdata()[label_mask] - map_s1_3.get_fdata()[label_mask])**2)/num_voxel)
            map_both_rmse = np.sqrt(np.sum((truth.get_fdata()[label_mask] - map_both.get_fdata()[label_mask])**2)/num_voxel)
            map_lut_rmse = np.sqrt(np.sum((truth.get_fdata()[label_mask] - map_lut.get_fdata()[label_mask])**2)/num_voxel)

            # Add to dataframe
            df.loc[len(df)] = [subject, 's1_2', tissue_label, noise_level, map_s1_2_rmse]
            df.loc[len(df)] = [subject, 's1_3', tissue_label, noise_level, map_s1_3_rmse]
            df.loc[len(df)] = [subject, 'both', tissue_label, noise_level, map_both_rmse]
            # df.loc[len(df)] = [subject, 'lut', tissue_label, noise_level, map_lut_rmse]

print(df)
df.to_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_seg_sensitivity_results.csv', index=False)