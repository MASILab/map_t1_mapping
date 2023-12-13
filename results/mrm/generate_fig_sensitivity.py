# Generate figure 4: quantitative results (group)
import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import wilcoxon
import seaborn as sns
#from statannotations.Annotator import Annotator

def calculate_rmse(subject_id):
    # Load subject
    std1 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.0001_mask', subject_id, 't1_map.nii.gz'))
    std2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.0005_mask', subject_id, 't1_map.nii.gz'))
    std3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.001_mask', subject_id, 't1_map.nii.gz'))
    std4 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.005_mask', subject_id, 't1_map.nii.gz'))
    std5 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.01_mask', subject_id, 't1_map.nii.gz'))
    std6 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.015_mask', subject_id, 't1_map.nii.gz'))
    std7 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.02_mask', subject_id, 't1_map.nii.gz'))
    std8 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.025_mask', subject_id, 't1_map.nii.gz'))
    std9 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'sensitivity', 't1_maps_s1_2_0.05_mask', subject_id, 't1_map.nii.gz'))
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_mask', subject_id, 't1_map.nii.gz'))

    # Get data
    std1_data = std1.get_fdata()
    std2_data = std2.get_fdata()
    std3_data = std3.get_fdata()
    std4_data = std4.get_fdata()
    std5_data = std5.get_fdata()
    std6_data = std6.get_fdata()
    std7_data = std7.get_fdata()
    std8_data = std8.get_fdata()
    std9_data = std9.get_fdata()
    truth_data = truth.get_fdata()

    # Calculate RMSE
    rmse1 = np.sqrt(np.mean(std1_data - truth_data)**2)
    rmse2 = np.sqrt(np.mean(std2_data - truth_data)**2)
    rmse3 = np.sqrt(np.mean(std3_data - truth_data)**2)
    rmse4 = np.sqrt(np.mean(std4_data - truth_data)**2)
    rmse5 = np.sqrt(np.mean(std5_data - truth_data)**2)
    rmse6 = np.sqrt(np.mean(std6_data - truth_data)**2)
    rmse7 = np.sqrt(np.mean(std7_data - truth_data)**2)
    rmse8 = np.sqrt(np.mean(std8_data - truth_data)**2)
    rmse9 = np.sqrt(np.mean(std9_data - truth_data)**2)
    return rmse1, rmse2, rmse3, rmse4, rmse5, rmse6, rmse7, rmse8, rmse9

# Get a list of all folders under t1_mapping.definitions.GROUND_TRUTH_DATA
subject_ids = os.listdir(t1_mapping.definitions.GROUND_TRUTH_DATA)

# Run calculate_rmse() for each folder
ground_truth_df = pd.read_csv('/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv', dtype={'Subject': str})

rmse1_list = []
rmse2_list = []
rmse3_list = []
rmse4_list = []
rmse5_list = []
rmse6_list = []
rmse7_list = []
rmse8_list = []
rmse9_list = []
subjects = []
for subject_id in subject_ids:
    if subject_id not in ground_truth_df['Subject'].values:
        continue
    elif subject_id in ['336547', '336530', '336699', '336388']:
        continue
    rmse1, rmse2, rmse3, rmse4, rmse5, rmse6, rmse7, rmse8, rmse9 = calculate_rmse(subject_id)
    rmse1_list.append(rmse1)
    rmse2_list.append(rmse2)
    rmse3_list.append(rmse3)
    rmse4_list.append(rmse4)
    rmse5_list.append(rmse5)
    rmse6_list.append(rmse6)
    rmse7_list.append(rmse7)
    rmse8_list.append(rmse8)
    rmse9_list.append(rmse9)
    subjects.append(subject_id)

rmse1_array = np.array(rmse1_list)
rmse2_array = np.array(rmse2_list)
rmse3_array = np.array(rmse3_list)
rmse4_array = np.array(rmse4_list)
rmse5_array = np.array(rmse5_list)
rmse6_array = np.array(rmse6_list)
rmse7_array = np.array(rmse7_list)
rmse8_array = np.array(rmse8_list)
rmse9_array = np.array(rmse9_list)

data = [rmse1_array, rmse2_array, rmse3_array, rmse4_array, rmse5_array, rmse6_array, rmse7_array, rmse8_array, rmse9_array]
mean = [np.mean(d) for d in data]
std = [np.std(d) for d in data]
x = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.015, 0.02, 0.025, 0.05]

fig, ax = plt.subplots()
ax.plot(x,mean, 'b.-')
ax.errorbar(x,mean,yerr=std, capsize=5)
ax.set_xlabel('Standard deviation of noise')
ax.set_ylabel('RMSE of MAP T1 estimate compared to ground truth (s)')
#sns.lineplot(y = [np.mean(d) for d in data], x = [0.0005, 0.001, 0.005, 0.01, 0.05, 0.1])
plt.show()

#print(f'RMSE (S1_2 and S1_3): {np.mean(rmse_both_array):.4f} +/- {np.std(rmse_both_array):.4f}')
#print(f'RMSE S1_2: {np.mean(rmse_s1_2_array):.4f} +/- {np.std(rmse_s1_2_array):.4f}')
#print(f'RMSE S1_3: {np.mean(rmse_s1_3_array):.4f} +/- {np.std(rmse_s1_3_array):.4f}')
#print(f'RMSE LUT: {np.mean(rmse_lut_array):.4f} +/- {np.std(rmse_lut_array):.4f}')
#
## Perform Wilcoxon signed-rank test
#zero_method = 'pratt'
#stat, p1 = wilcoxon(rmse_both_array, rmse_lut_array, zero_method=zero_method)
#print(f'Wilcoxon signed-rank test between both and LUT: {p1=}')
#
#stat, p2 = wilcoxon(rmse_s1_2_array, rmse_lut_array, zero_method=zero_method)
#print(f'Wilcoxon signed-rank test between S1_2 alone and LUT: {p2=}')
#
#stat, p3 = wilcoxon(rmse_s1_3_array, rmse_lut_array, zero_method=zero_method)
#print(f'Wilcoxon signed-rank test between S1_3 alone and LUT: {p3=}')
#
#data = [rmse_lut_array, rmse_both_array, rmse_s1_2_array, rmse_s1_2_array]
#fig, ax = plt.subplots(figsize=(7,6))
#ax = sns.violinplot(data=data, inner='quartile', cut=0)
#
## Add p-values and data points
#ax = sns.stripplot(data=data, color='black', jitter=0, size=5)
#annotator = Annotator(ax, pairs=[(0, 1), (0, 2), (0, 3)], data=data)
#annotator.configure(text_format='simple')
#annotator.set_pvalues([p1, p2, p3]).annotate()
#
#ax.set_xticks(range(4), labels=['Original point\nestimate $T_1$', 'MAP $T_1$ using\n$S_{1,2}$ and $S_{1,3}$', 'MAP $T_1$ using\n$S_{1,2}$ only', 'MAP $T_1$ using\n$S_{1,3}$ only'])
#ax.set_ylabel('RMSE compared to ground truth $T_1$ (s)')
#
#plt.show()
#
#fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/quantitative_results.png', dpi=600)
