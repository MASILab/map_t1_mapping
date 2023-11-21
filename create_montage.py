# Loop through subjects and create montage image
import t1_mapping
from adam_utils.nifti import montage_to_png
import os
import nibabel as nib
import pandas as pd
from tqdm import tqdm

# Get a list of all folders under t1_mapping.definitions.GROUND_TRUTH_DATA
subject_ids = os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask'))

# Run calculate_rmse() for each folder
ground_truth_df = pd.read_csv('/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv', dtype={'Subject': str})

print(subject_ids)
for subject_id in tqdm(subject_ids):
    if subject_id not in ground_truth_df['Subject'].values:
        continue
    try:
    
        t1 = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_lut', subject_id, 't1_map.nii')
        # t1_truth = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject_id, 't1_map.nii.gz')

        output_folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'montage')
        output = os.path.join(t1_mapping.definitions.OUTPUTS, 'montage', subject_id)

        # Create montage
        os.makedirs(output_folder, exist_ok=True)
        montage_to_png(t1, output, num_slices=3, vmin=0, vmax=5)

    except FileNotFoundError:
        print(f'File not found for {subject_id}')
        continue
    
