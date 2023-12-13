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

# Dictionary to hold labels, label names, and list of subjects with that label
lut_path = '/home/local/VANDERBILT/saundam1/Documents/slant/slant.lut'
df = pd.read_table(lut_path, delimiter='\s+', engine='python', names=['Label', 'R', 'G', 'B', 'Name'])
label_df = pd.DataFrame({
    'Label': df['Label'].values,
    'Name': df['Name'].values,
    'Subjects': [[] for _ in range(len(df))],
    'Mean Error S1_2': np.zeros(len(df)),
    'Standard Error S1_2': np.zeros(len(df)),
    'Mean Error S1_3': np.zeros(len(df)),
    'Standard Error S1_3': np.zeros(len(df)),
    'Mean Error All': np.zeros(len(df)),
    'Standard Error All': np.zeros(len(df)),
})

# Loop through subjects 
for subject in os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask')):

    # Load SLANT segmentation
    slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask', subject, 't1w_seg.nii.gz'))
    slant_data = slant.get_fdata()

    # Loop through labels
    for label in np.unique(slant_data):
        # Calculate mean error and standard error for each labelwith that label
        label_df.loc[label_df['Label'] == label, 'Subjects'].iloc[0].append(subject)


# Create df containing only values with at least 1 subject
label_df = label_df[label_df['Subjects'].map(len) > 0]


# Now calculate mean error and standard error for each label
for i, label in enumerate(label_df['Label'].values):
    print(label)
    # Loop through subjects that have this label
    errors_s1_2 = []
    errors_s1_3 = []
    errors_all = []
    errors_orig = []
    for subject in label_df['Subjects'].iloc[i]:
        s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', subject, 't1_map.nii.gz'))
        s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_3_mask', subject, 't1_map.nii.gz'))
        all = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_all_mask', subject, 't1_map.nii.gz'))
        orig = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_lut_mask', subject, 't1_map.nii.gz'))
        truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject, 't1_map.nii.gz'))
        slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask', subject, 't1w_seg.nii.gz'))

        # Calculate error
        rmse_s1_2 = np.sqrt(np.mean((truth.get_fdata() - s1_2.get_fdata())**2))
        rmse_s1_3 = np.sqrt(np.mean((truth.get_fdata() - s1_3.get_fdata())**2))
        rmse_all = np.sqrt(np.mean((truth.get_fdata() - all.get_fdata())**2))
        rmse_orig = np.sqrt(np.mean((truth.get_fdata() - orig.get_fdata())**2))

        # Append
        errors_s1_2.append(rmse_s1_2)
        errors_s1_3.append(rmse_s1_3)
        errors_all.append(rmse_all)
        errors_orig.append(rmse_orig)
    
    # Calculate mean error and standard error
    errors = [errors_s1_2, errors_s1_3, errors_all, errors_orig]
    error_col = ['Mean Error S1_2', 'Mean Error S1_3', 'Mean Error All', 'Mean Error Orig']
    std_err_col = ['Standard Error S1_2', 'Standard Error S1_3', 'Standard Error All', 'Standard Error Orig']
    for err, err_col, std_err_col in zip(errors, error_col, std_err_col):
        mean_error = np.mean(err)
        standard_error = np.std(err) / np.sqrt(len(err))

        # Add to df
        label_df.loc[label_df['Label'] == label, err_col] = mean_error
        label_df.loc[label_df['Label'] == label, std_err_col] = standard_error

print(label_df)

# Save as CSV file
label_df.to_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_results.csv')