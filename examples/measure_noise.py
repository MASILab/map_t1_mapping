# Create noise estimates in ROI from SLANT segmentation
import numpy as np
import matplotlib.pyplot as plt
import t1_mapping
import nibabel as nib
import os
import pandas as pd
from adam_utils.nifti import plot_nifti

subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    all_inv_combos=False
)

# Calculate GRE
GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **subj.eqn_params
)

# Print ranges
GRE_ranges = [np.max(GRE[i,:]) - np.min(GRE[i,:]) for i in range(3)]
print(f'GRE 1 range: {GRE_ranges[0]}')
print(f'GRE 2 range: {GRE_ranges[1]}')
print(f'GRE 3 range: {GRE_ranges[2]}')

# Print what STD you need to get same CNR
CNR = [9.49, 24.6, 22.35]
for i in range(3):
    print(f'GRE {i+1} STD: {GRE_ranges[i]/CNR[i]}')
