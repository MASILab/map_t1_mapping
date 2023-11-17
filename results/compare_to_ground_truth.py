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
    likelihood = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_rigid_open', subject_id, 'reg_t1_map.nii.gz'))
    likelihood_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_2_rigid_open', subject_id, 'reg_t1_map.nii.gz'))
    likelihood_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_s1_3_rigid_open', subject_id, 'reg_t1_map.nii.gz'))
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_opening', subject_id, 't1_map.nii'))

    # Get data
    likelihood_data = likelihood.get_fdata()
    likelihood_s1_2_data = likelihood_s1_2.get_fdata()
    likelihood_s1_3_data = likelihood_s1_3.get_fdata()
    truth_data = truth.get_fdata()
    truth_data[np.isinf(truth_data)] = 0

    # Mask data
    mask = truth_data > 0
    likelihood_data = likelihood_data[mask]
    likelihood_s1_2_data = likelihood_s1_2_data[mask]
    likelihood_s1_3_data = likelihood_s1_3_data[mask]
    truth_data = truth_data[mask]

    # Calculate RMSE
    rmse = np.sqrt(np.mean((likelihood_data - truth_data)**2))
    rmse_s1_2 = np.sqrt(np.mean((likelihood_s1_2_data - truth_data)**2))
    rmse_s1_3 = np.sqrt(np.mean((likelihood_s1_3_data - truth_data)**2))

    return rmse, rmse_s1_2, rmse_s1_3

# Get a list of all folders under t1_mapping.definitions.GROUND_TRUTH_DATA
subject_ids = os.listdir(t1_mapping.definitions.GROUND_TRUTH_DATA)

# Run calculate_rmse() for each folder
ground_truth_df = pd.read_csv('/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv', dtype={'Subject': str})

rmse_list = []
rmse_s1_2_list = []
rmse_s1_3_list = []
subjects = []
for subject_id in subject_ids:
    if subject_id not in ground_truth_df['Subject'].values:
        continue
    rmse, rmse_s1_2, rmse_s1_3 = calculate_rmse(subject_id)
    rmse_list.append(rmse)
    rmse_s1_2_list.append(rmse_s1_2)
    rmse_s1_3_list.append(rmse_s1_3)
    subjects.append(subject_id)

rmse_array = np.array(rmse_list)
rmse_s1_2_array = np.array(rmse_s1_2_list)
rmse_s1_3_array = np.array(rmse_s1_3_list)

print(f'RMSE: {np.mean(rmse_array):.4f} +/- {np.std(rmse_array):.4f}')
print(f'RMSE S1_2: {np.mean(rmse_s1_2_array):.4f} +/- {np.std(rmse_s1_2_array):.4f}')
print(f'RMSE S1_3: {np.mean(rmse_s1_3_array):.4f} +/- {np.std(rmse_s1_3_array):.4f}')

# Perform Wilcoxon signed-rank test
stat, p1 = wilcoxon(rmse_array, rmse_s1_2_array)
print(f'Wilcoxon signed-rank test between both and S1_2 alone: {p1=}')

stat, p2 = wilcoxon(rmse_array, rmse_s1_3_array)
print(f'Wilcoxon signed-rank test between both and S1_3 alone: {p2=}')

data = [rmse_s1_2_array, rmse_array, rmse_s1_3_array]
fig, ax = plt.subplots(figsize=(6,8))
ax = sns.violinplot(data=data, inner='quartile', cut=0)

# Add p-values and data points
ax = sns.stripplot(data=data, color='black', jitter=0, size=5)
annotator = Annotator(ax, pairs=[(0, 1), (1, 2)], data=data)
annotator.configure(text_format='simple')
annotator.set_pvalues([p1, p2]).annotate()

ax.set_xticks(range(3), labels=['$S_{1,2}$ only', '$S_{1,2}$ and $S_{1,3}$', '$S_{1,3}$ only'])
ax.set_ylabel('RMSE')

for i in range(len(rmse_array)):
    ax.plot([0, 1], [rmse_s1_2_array[i], rmse_array[i]], color=[0.25, 0.25, 0.25, 0.75], linestyle='--')
    ax.plot([1, 2], [rmse_array[i], rmse_s1_3_array[i]], color=[0.25, 0.25, 0.25, 0.75], linestyle='--')

paired_df = pd.DataFrame({
    'subject': subjects,
    'diff_s1_2': rmse_array - rmse_s1_2_array,
    'diff_s1_3': rmse_s1_3_array - rmse_array,
})

# Find subject IDs where diff is negative
print('S1_2: ', paired_df['subject'][paired_df['diff_s1_2'] < 0])
print('S1_3: ', paired_df['subject'][paired_df['diff_s1_3'] < 0])

plt.show()