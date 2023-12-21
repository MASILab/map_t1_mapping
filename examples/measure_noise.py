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

# Measurements from ROI
roi_mean = [31789, 89513, 89813]
roi_range = [(21590, 40847), (77878, 97875), (79730, 103060)]
all_range = [(-125053, 156384), (-150234, 206007), (158011, 181566)]
roi_std = [3156, 3664, 4123]
roi_snr = [m/s for m,s in zip(roi_mean, roi_std)]

# Calculate GRE
GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **subj.eqn_params
)

# Print ranges
# GRE_mean = np.mean(GRE, axis=1)
GRE_range = [(np.min(GRE[i,:]), np.max(GRE[i,:])) for i in range(3)]
mean_scaled = [0,0,0]
for i in range(3):
    mean_scaled[i] = (roi_mean[i] - roi_range[i][0])/(roi_range[i][1] - roi_range[i][0]) * (GRE_range[i][1] - GRE_range[i][0]) + GRE_range[i][0]
# GRE_std = np.std(GRE, axis=1)

desired_std = [m/snr for m,snr in zip(mean_scaled, roi_snr)]
print(desired_std)