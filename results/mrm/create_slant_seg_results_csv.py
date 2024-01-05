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
df = pd.DataFrame(columns=['Subject', 'Tissue Label', 'Method', 'Tissue Type', 'RMSE'])

# Loop through subjects and get error in WM, GM and other
for subject in os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25_mask')):
    print(subject) 
    
    # Load SLANT segmentation
    slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25_mask', subject, 't1w_seg.nii.gz'))

    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    map_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_custom_mask', subject, f't1_map.nii.gz'))
    map_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_3_custom_mask', subject, f't1_map.nii.gz'))
    map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_all_custom_mask', subject, f't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_lut_mask', subject, f't1_map.nii.gz'))

    # Loop through labels and find error
    for label in np.unique(slant.get_fdata()):
        label_mask = slant.get_fdata() == label

        # Decide if label is WM, GM or other
        if label >= 40 and label <= 45:
            tissue_label = 'WM'
        elif label == 208 or label == 209 or label == 0 or label == 51 or label == 52:
            tissue_label = 'Other'
        else:
            tissue_label = 'GM'

        # Get error in label for each
        map_s1_2_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_s1_2.get_fdata()[label_mask])**2))
        map_s1_3_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_s1_3.get_fdata()[label_mask])**2))
        map_both_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_both.get_fdata()[label_mask])**2))
        lut_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - lut.get_fdata()[label_mask])**2))

        # Add to dataframe
        df.loc[len(df)] = [subject, label, 's1_2', tissue_label, map_s1_2_rmse]
        df.loc[len(df)] = [subject, label, 's1_3', tissue_label, map_s1_3_rmse]
        df.loc[len(df)] = [subject, label, 'both', tissue_label, map_both_rmse]
        df.loc[len(df)] = [subject, label, 'lut', tissue_label, lut_rmse]

print(df)
df.to_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_seg_results.csv', index=False)