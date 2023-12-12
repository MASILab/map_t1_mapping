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
df = pd.DataFrame(columns=['Subject', 'Region', 'Method', 'RMSE', 'SE'])

# Loop through subjects and get error in WM, GM and other
for subject in os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask')):

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
        wm_error = np.abs(truth.get_fdata()[wm_mask] - map.get_fdata()[wm_mask])
        gm_error = np.abs(truth.get_fdata()[gm_mask] - map.get_fdata()[gm_mask])
        other_error = np.abs(truth.get_fdata()[other_mask] - map.get_fdata()[other_mask])

        # Add to dataframe
        df = df.append({'Subject': subject, 'Region': 'WM', 'Method': method, 'RMSE': np.sqrt(np.mean(wm_error**2)), 'SE': np.std(wm_error)/np.sqrt(wm_error.shape[0])}, ignore_index=True)
        df = df.append({'Subject': subject, 'Region': 'GM', 'Method': method, 'RMSE': np.sqrt(np.mean(gm_error**2)), 'SE': np.std(gm_error)/np.sqrt(gm_error.shape[0])}, ignore_index=True)
        df = df.append({'Subject': subject, 'Region': 'Other', 'Method': method, 'RMSE': np.sqrt(np.mean(other_error**2)), 'SE': np.std(other_error)/np.sqrt(other_error.shape[0])}, ignore_index=True)
    
print(df)