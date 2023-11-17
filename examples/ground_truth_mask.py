# Fix ground truth mask
import t1_mapping
import os
import nibabel as nib 
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import plot_nifti
from skimage import morphology, measure
from tqdm import tqdm
import pandas as pd

def process_subject(subject_id):
    # Load subject 
    subj = nib.load(os.path.join(t1_mapping.definitions.GROUND_TRUTH_DATA, subject_id, 'filtered_t1_map.nii'))
    subj_data = subj.get_fdata()
    # Replace inf with 0
    subj_data[np.isinf(subj_data)] = 0

    subj = nib.nifti1.Nifti1Image(subj_data, subj.affine)

    # Apply opening
    opened_subj_mask = morphology.isotropic_opening(subj_data, 50)
    subj_data[opened_subj_mask == 0] = 0
    opened_subj = nib.nifti1.Nifti1Image(subj_data, subj.affine)

    return opened_subj 

# Example
# opened_subj = process_subject('336672')
# subj = nib.load(os.path.join(t1_mapping.definitions.GROUND_TRUTH_DATA, '336954', 'filtered_t1_map.nii'))
# fig, ax = plot_nifti(opened_subj, vmin=0, vmax=5)
# fig, ax = plot_nifti(subj, vmin=0, vmax=5)

# plt.show()

# Get list of all subject IDs
subject_ids = os.listdir(t1_mapping.definitions.GROUND_TRUTH_DATA)

# Process each subject
ground_truth_df = pd.read_csv('/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv', dtype={'Subject': str})
for subject_id in tqdm(subject_ids):
    if subject_id not in ground_truth_df['Subject'].values:
        continue
    output_dir = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_opening', subject_id)
    opened_subj = process_subject(subject_id)
    os.makedirs(output_dir, exist_ok=True)
    nib.save(opened_subj, os.path.join(output_dir, f't1_map.nii'))

