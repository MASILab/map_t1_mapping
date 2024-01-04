# Generate figure 4: quantitative results (group)
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
    likelihood = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_all_custom_mask', subject_id, 't1_map.nii.gz'))
    likelihood_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_custom_mask', subject_id, 't1_map.nii.gz'))
    likelihood_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_3_custom_mask', subject_id, 't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_lut_mask', subject_id, 't1_map.nii.gz'))
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject_id, 't1_map.nii.gz'))

    # Get data
    likelihood_data = likelihood.get_fdata()
    likelihood_s1_2_data = likelihood_s1_2.get_fdata()
    likelihood_s1_3_data = likelihood_s1_3.get_fdata()
    lut_data = lut.get_fdata()
    truth_data = truth.get_fdata()

    # Calculate RMSE
    rmse_both = np.sqrt(np.mean((likelihood_data - truth_data)**2))
    rmse_s1_2 = np.sqrt(np.mean((likelihood_s1_2_data - truth_data)**2))
    rmse_s1_3 = np.sqrt(np.mean((likelihood_s1_3_data - truth_data)**2))
    rmse_lut = np.sqrt(np.mean((lut_data - truth_data)**2))

    return rmse_both, rmse_s1_2, rmse_s1_3, rmse_lut

# Get a list of all folders under t1_mapping.definitions.GROUND_TRUTH_DATA
# subject_ids = os.listdir(t1_mapping.definitions.GROUND_TRUTH_DATA)

# Run calculate_rmse() for each folder
# ground_truth_df = pd.read_csv('/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv', dtype={'Subject': str})
df = pd.read_csv('/nfs/masi/saundam1/outputs/t1_mapping/ground_truth_subjects.csv')

rmse_both_list = []
rmse_s1_2_list = []
rmse_s1_3_list = []
rmse_lut_list = []
subjects = []
for subject in df['Subject'].values:
    subject_id = str(subject)
    rmse_both, rmse_s1_2, rmse_s1_3, rmse_lut = calculate_rmse(subject_id)
    rmse_both_list.append(rmse_both)
    rmse_s1_2_list.append(rmse_s1_2)
    rmse_s1_3_list.append(rmse_s1_3)
    rmse_lut_list.append(rmse_lut)
    subjects.append(subject_id)

rmse_both_array = np.array(rmse_both_list)
rmse_s1_2_array = np.array(rmse_s1_2_list)
rmse_s1_3_array = np.array(rmse_s1_3_list)
rmse_lut_array = np.array(rmse_lut_list)

print(f'RMSE (S1_2 and S1_3): {np.mean(rmse_both_array):.4f} +/- {np.std(rmse_both_array):.4f}')
print(f'RMSE S1_2: {np.mean(rmse_s1_2_array):.4f} +/- {np.std(rmse_s1_2_array):.4f}')
print(f'RMSE S1_3: {np.mean(rmse_s1_3_array):.4f} +/- {np.std(rmse_s1_3_array):.4f}')
print(f'RMSE LUT: {np.mean(rmse_lut_array):.4f} +/- {np.std(rmse_lut_array):.4f}')

# Perform Wilcoxon signed-rank test
zero_method = 'zsplit'
stat, p1 = wilcoxon(rmse_both_array, rmse_lut_array, zero_method=zero_method)
print(f'Wilcoxon signed-rank test between both and LUT: {p1=}')

stat, p2 = wilcoxon(rmse_s1_2_array, rmse_lut_array, zero_method=zero_method)
print(f'Wilcoxon signed-rank test between S1_2 alone and LUT: {p2=}')

stat, p3 = wilcoxon(rmse_s1_3_array, rmse_lut_array, zero_method=zero_method)
print(f'Wilcoxon signed-rank test between S1_3 alone and LUT: {p3=}')

data = [rmse_lut_array, rmse_both_array, rmse_s1_2_array, rmse_s1_2_array]
fig, ax = plt.subplots(figsize=(7,6))
ax = sns.violinplot(data=data, inner='quartile', cut=0)

# Add p-values and data points
ax = sns.stripplot(data=data, color='black', jitter=0, size=5)
annotator = Annotator(ax, pairs=[(0, 1), (0, 2), (0, 3)], data=data)
annotator.configure(text_format='simple')
annotator.set_pvalues([p1, p2, p3]).annotate()

ax.set_xticks(range(4), labels=['Original point\nestimate $T_1$', 'MAP $T_1$ using\n$S_{1,2}$ and $S_{1,3}$', 'MAP $T_1$ using\n$S_{1,2}$ only', 'MAP $T_1$ using\n$S_{1,3}$ only'])
ax.set_ylabel('RMSE compared to ground truth $T_1$ (s)')

plt.show()

fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/quantitative_results.png', dpi=600)