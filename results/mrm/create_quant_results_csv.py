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
    likelihood = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_all_0.005_mask', subject_id, 't1_map.nii.gz'))
    likelihood_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_0.005_mask', subject_id, 't1_map.nii.gz'))
    likelihood_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_3_0.005_mask', subject_id, 't1_map.nii.gz'))
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

rmse_list = []
subjects = []
methods = []
for subject in df['Subject'].values:
    subject_id = str(subject)
    print(subject_id)
    rmse_both, rmse_s1_2, rmse_s1_3, rmse_lut = calculate_rmse(subject_id)
    rmse_list.append(rmse_both)
    rmse_list.append(rmse_s1_2)
    rmse_list.append(rmse_s1_3)
    rmse_list.append(rmse_lut)
    subjects.extend([subject_id]*4)
    methods.extend(['both', 's1_2', 's1_3', 'lut'])

quant_results = {
    'Subject': subjects,
    'Method': methods,
    'RMSE': rmse_list
}
quant_results_df = pd.DataFrame(quant_results)

print(quant_results_df)
quant_results_df.to_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/quant_results.csv', index=False)