# Summarize tissue-level analysis in CSV format
import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from adam_utils.nifti import load_slice
import seaborn as sns

# Load labels
lut_path = '/home/local/VANDERBILT/saundam1/Documents/slant/slant.lut'
label_df = pd.read_table(lut_path, delimiter='\s+', engine='python', names=['Label', 'R', 'G', 'B', 'Name'])

# Create RMSE dataframe
df = pd.DataFrame(columns=['Subject', 'Tissue Label', 'Label Name', 'Number of Voxels', 'Method', 'RMSE'])

# Loop through subjects and get error in WM, GM and other
for subject in os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25_mask')):
    print(subject) 

    # Load SLANT segmentation
    slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25_mask', subject, 't1w_seg.nii.gz'))

    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    map_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_0.005_mask', subject, f't1_map.nii.gz'))
    map_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_3_0.005_mask', subject, f't1_map.nii.gz'))
    map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_all_0.005_mask', subject, f't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_lut_mask', subject, f't1_map.nii.gz'))

    # Loop through labels and find error
    for label in np.unique(slant.get_fdata()):
        label_mask = slant.get_fdata() == label

        # Get number of voxels in label
        num_voxels = np.count_nonzero(label_mask)

        # Get error in label for each
        map_s1_2_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_s1_2.get_fdata()[label_mask])**2))
        map_s1_3_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_s1_3.get_fdata()[label_mask])**2))
        map_both_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - map_both.get_fdata()[label_mask])**2))
        lut_rmse = np.sqrt(np.mean((truth.get_fdata()[label_mask] - lut.get_fdata()[label_mask])**2))

        # Add to dataframe
        label_name = label_df[label_df['Label'] == label]['Name'].values[0]
        df.loc[len(df)] = [subject, int(label), label_name, num_voxels, 's1_2', map_s1_2_rmse]
        df.loc[len(df)] = [subject, int(label), label_name, num_voxels, 's1_3', map_s1_3_rmse]
        df.loc[len(df)] = [subject, int(label), label_name, num_voxels, 'both', map_both_rmse]
        df.loc[len(df)] = [subject, int(label), label_name, num_voxels, 'lut', lut_rmse]
        
print(df)

# Save as CSV file
df.to_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_results.csv')