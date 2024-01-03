import numpy as np
import nibabel as nib
import os
from tqdm import tqdm

input_dir = '/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_sir_qmt'
output_dir = '/nfs/masi/saundam1/outputs/t1_mapping/t1_truth_inf_to_zero'

# Loop through folders in input_dir, and replace infinity values in t1_map.nii in each folder with zeros
for folder in tqdm(os.listdir(input_dir)):
    # Skip if t1_map doesn't exist
    if not os.path.exists(os.path.join(input_dir, folder, 'filtered_t1_map.nii')):
        print(f'Skipping {folder}')
        continue
    os.makedirs(os.path.join(output_dir, folder), exist_ok=True)
    t1_map = nib.load(os.path.join(input_dir, folder, 'filtered_t1_map.nii'))
    t1_map_data = t1_map.get_fdata()
    t1_map_data[np.isinf(t1_map_data)] = 0
    nib.save(nib.Nifti1Image(t1_map_data, t1_map.affine), os.path.join(output_dir, folder, 't1_map.nii'))