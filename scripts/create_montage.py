# Loop through subjects and create montage image
import t1_mapping
from adam_utils.nifti import montage_to_png
import os
import nibabel as nib
import pandas as pd
from tqdm import tqdm
import matplotlib

# Load SLANT lookup table
lut_path = '/home/local/VANDERBILT/saundam1/Documents/slant/slant.lut'
df = pd.read_table(lut_path, delimiter='\s+', engine='python')


max_val = 209
# Loop through values in first column of df
colors_list = []
for i in range(max_val):
    
    # If i is in the first column of df, get the corresponding color
    if i in df.iloc[:,0].values:
        row_with_i = df[df.iloc[:, 0] == i]

        R = row_with_i.iloc[0, 1]  # Second column
        G = row_with_i.iloc[0, 2]   # Third column
        B = row_with_i.iloc[0, 3]  # Fourth column

        colors_list.append((R, G, B, 1.))
    else:
        colors_list.append((0, 0, 0, 1.))

# Create colormap
slant_cmap = matplotlib.colors.ListedColormap(colors_list, name='slant')

# Get a list of all folders under t1_mapping.definitions.GROUND_TRUTH_DATA
# subject_ids = os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask'))
subject_ids_truth = os.listdir('/home/saundam1/temp_data/t1_maps_truth')
subject_ids_t1w = os.listdir('/home/saundam1/temp_data/mp2rage_t1w_strip_rigid')

subject_ids = list(set(subject_ids_truth) & set(subject_ids_t1w))

# Run calculate_rmse() for each folder
# ground_truth_df = pd.read_csv('/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv', dtype={'Subject': str})

print(subject_ids)
for subject_id in tqdm(subject_ids):
    # if subject_id not in ground_truth_df['Subject'].values:
    #     continue
    # t1 = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', subject_id, 't1_map.nii.gz')
    # slant = os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_mask', subject_id, 't1w_seg.nii.gz')

    t1 = os.path.join('/home/saundam1/temp_data/t1_maps_truth', subject_id, 'filtered_t1_map.nii.gz')
    t1w = os.path.join('/home/saundam1/temp_data/mp2rage_t1w_strip_rigid', subject_id, 't1w.nii.gz')

    # output_folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'montage')
    # output = os.path.join(t1_mapping.definitions.OUTPUTS, 'montage', subject_id)
    output_folder = os.path.join('/home/saundam1/temp_data/montage')
    output = os.path.join(output_folder, subject_id)

    # Create montage
    os.makedirs(output_folder, exist_ok=True)
    montage_to_png(t1, output, overlay=t1w, num_slices=3, vmin=0, vmax=5, overlay_alpha=0.5)

