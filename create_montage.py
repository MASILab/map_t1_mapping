# Loop through subjects and create montage image
import t1_mapping
from adam_utils.nifti import montage_to_png
import os
import nibabel as nib
import pandas as pd
from tqdm import tqdm

# Get a list of all folders under t1_mapping.definitions.GROUND_TRUTH_DATA
subject_ids = os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_inf_to_zero'))

# Run calculate_rmse() for each folder
ground_truth_df = pd.read_csv('/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv', dtype={'Subject': str})

for subject_id in tqdm(subject_ids):
    if subject_id not in ground_truth_df['Subject'].values:
        continue
    try:
    
        t1_likelihood = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_strip_rigid', subject_id, 'reg_t1_map.nii.gz')
        t1_mask = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_strip_mask', subject_id, 'mask.nii')
        t1_truth = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_inf_to_zero', subject_id, 't1_map.nii')

        output = os.path.join(t1_mapping.definitions.OUTPUTS, 'montage', subject_id)

        # Create montage
        montage_to_png(t1_truth, output, overlay=t1_mask, num_slices=3, vmin=0, vmax=5)

    except FileNotFoundError:
        print(f'File not found for {subject_id}')
        continue
    
