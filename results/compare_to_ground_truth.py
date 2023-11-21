# Compare MI of MP2RAGE images
import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import wilcoxon
import seaborn as sns
from statannotations.Annotator import Annotator

def calculate_rmse(subject_id):
    # Load subject
    likelihood = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_all_mask', subject_id, 't1_map.nii.gz'))
    likelihood_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_mask', subject_id, 't1_map.nii.gz'))
    likelihood_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_3_mask', subject_id, 't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'old', 't1_maps_lut_mask', subject_id, 't1_map.nii.gz'))
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject_id, 't1_map.nii.gz'))

    # Get data
    likelihood_data = likelihood.get_fdata()
    likelihood_s1_2_data = likelihood_s1_2.get_fdata()
    likelihood_s1_3_data = likelihood_s1_3.get_fdata()
    lut_data = lut.get_fdata()
    truth_data = truth.get_fdata()
    #truth_data[np.isinf(truth_data)] = 0

    # Mask data
    #mask = truth_data > 0
    #likelihood_data = likelihood_data[mask]
    #likelihood_s1_2_data = likelihood_s1_2_data[mask]
    #likelihood_s1_3_data = likelihood_s1_3_data[mask]
    #truth_data = truth_data[mask]

    # Calculate RMSE
    rmse = np.sqrt(np.mean((likelihood_data - truth_data)**2))
    rmse_s1_2 = np.sqrt(np.mean((likelihood_s1_2_data - truth_data)**2))
    rmse_s1_3 = np.sqrt(np.mean((likelihood_s1_3_data - truth_data)**2))
    rmse_lut = np.sqrt(np.mean((lut_data - truth_data)**2))

    return rmse, rmse_s1_2, rmse_s1_3, rmse_lut

# Get a list of all folders under t1_mapping.definitions.GROUND_TRUTH_DATA
subject_ids = os.listdir(t1_mapping.definitions.GROUND_TRUTH_DATA)
folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'mp2rage_converted_v2019', '336547', '1101-x-MP2RAGE_0p8mm_1sTI_autoshim-x-MP2RAGE_0p8mm_1sTI_autoshim')
# Perform Wilcoxon signed-rank test
zero_method = 'pratt'
stat, p1 = wilcoxon(rmse_array, rmse_s1_2_array, zero_method=zero_method)
print(f'Wilcoxon signed-rank test between both and S1_2 alone: {p1=}')

stat, p2 = wilcoxon(rmse_array, rmse_s1_3_array, zero_method=zero_method)
print(f'Wilcoxon signed-rank test between both and S1_3 alone: {p2=}')

stat, p3 = wilcoxon(rmse_s1_2_array, rmse_lut_array, zero_method=zero_method)
print(f'Wilcoxon signed-rank test between S1_2 alone and LUT: {p3=}')

data = [rmse_s1_2_array, rmse_array, rmse_s1_3_array, rmse_lut_array]
fig, ax = plt.subplots(figsize=(6,8))
ax = sns.violinplot(data=data, inner='quartile', cut=0)

# Add p-values and data points
ax = sns.stripplot(data=data, color='black', jitter=0, size=5)
annotator = Annotator(ax, pairs=[(0, 1), (1, 2), (0, 3)], data=data)
annotator.configure(text_format='simple')
annotator.set_pvalues([p1, p2, p3]).annotate()

ax.set_xticks(range(4), labels=['$S_{1,2}$ only', '$S_{1,2}$ and $S_{1,3}$', '$S_{1,3}$ only', 'Original MP2RAGE method'])
ax.set_ylabel('RMSE compared to ground truth (s)')

for i in range(len(rmse_array)):
    ax.plot([0, 1], [rmse_s1_2_array[i], rmse_array[i]], color=[0.25, 0.25, 0.25, 0.75], linestyle='--')
    ax.plot([1, 2], [rmse_array[i], rmse_s1_3_array[i]], color=[0.25, 0.25, 0.25, 0.75], linestyle='--')

paired_df = pd.DataFrame({
    'subject': subjects,
    'diff_s1_2': rmse_array - rmse_s1_2_array,
    'diff_s1_3': rmse_s1_3_array - rmse_array,
    'diff_lut': rmse_s1_2_array - rmse_lut_array
})

print(paired_df)

# Find subject IDs where diff is 0
print('S1_2: ', paired_df['subject'][paired_df['diff_s1_2'] == 0])
print('S1_3: ', paired_df['subject'][paired_df['diff_s1_3'] == 0])

plt.show()
