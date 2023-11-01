# Create T1 map using MP2RAGE data (only 2 GREs)
import os
import t1_mapping
import nibabel as nib
from tqdm import tqdm
import pandas as pd
import numpy as np
from adam_utils.nifti import plot_nifti
import matplotlib.pyplot as plt
import re

# Load groups
# groups = pd.read_excel(os.path.join(t1_mapping.definitions.GROUND_TRUTH_MAT, 'scanID_groups.xlsx'))
# control_subj = groups['Health Control Scans'].dropna().astype(np.int64)
# ms_subj = groups['MS Patient Scans'].dropna().astype(np.int64)

# # Loop through subjects2
#         group = 'control'
#     else:
#         group = 'n/a'

#     # Get list of scans
#     scan = os.listdir(os.path.join(t1_mapping.definitions.DATA, subject))

#     # Get scan IDs
#     scan_id = [s.split('-')[0] for s in scan]
#     primary_scan_ids = [int(s) for s in scan_id if s.endswith('1')]
#     primary_scan_ids = sorted(primary_scan_ids)
#     highest_primary_scan_id = primary_scan_ids[-1]
2
#         subject_id=subject,
#         scan=chosen_scan,
#         scan_times=times[0:2]
#     )

#     # Calculate T1 map and save
#     save_folder = os.path.join(t1_mapping.definitions.T1_MAPS_LUT, str(subj_id))
#     # os.mkdir(save_folder)
#     # subj.t1_map.to_filename(os.path.join(save_folder, 't1_map.nii'))
#     subj.t1_map.to_filename('test_eff96.nii')

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'), 
    all_inv_combos=False,
)

# Get T1 map and plot
t1_map = subj.t1_map
fig, ax = plot_nifti(t1_map, title='T1 Map')
plt.show()
