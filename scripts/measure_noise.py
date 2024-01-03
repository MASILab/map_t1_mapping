# Create noise estimates in ROI from SLANT segmentation
import numpy as np
import matplotlib.pyplot as plt
import t1_mapping
import nibabel as nib
import os
import pandas as pd
from adam_utils.nifti import plot_nifti
from skimage.draw import polygon2mask

subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    all_inv_combos=False
)

points = [
    [170, 251],
    [186, 260],
    [191, 236], 
    [188, 230],
    [172, 238]
]
points = np.array(points)
roi = np.zeros(subj.mp2rage[0].shape)
roi2d = polygon2mask(roi.shape[1:], points)
roi[102, :, :] = roi2d
roi_nifti = nib.nifti1.Nifti1Image(roi, subj.mp2rage[0].affine)
roi_nifti.to_filename(os.path.join(t1_mapping.definitions.OUTPUTS, 'robust_t1w_0.25', '334264', 'cc_mask.nii.gz'))

# Load ROI
roi = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'robust_t1w_0.25', '334264', 'cc_mask.nii.gz')).get_fdata()
fig, ax = plot_nifti(subj.mp2rage[0], slice=[102, 256, 256], mask=roi, mask_alpha=0.5)

# Get data from NIFTI
roi_mean_real = []
roi_range_real = []
roi_std_real = []
all_range_real = []
roi_mean_imag = []
roi_range_imag = []
roi_std_imag = []
all_range_imag = []
for i, inv in enumerate(subj.inv):
    inv_data_real = np.real(inv.get_fdata(dtype=np.complex64))
    roi_data_real = inv_data_real[roi.astype(bool)]

    roi_mean_real.append(np.mean(roi_data_real))
    roi_range_real.append((np.min(roi_data_real), np.max(roi_data_real)))
    roi_std_real.append(np.std(roi_data_real))
    all_range_real.append((np.min(inv_data_real), np.max(inv_data_real)))

    # Repeat for imaginary
    inv_data_imag = np.imag(inv.get_fdata(dtype=np.complex64))
    roi_data_imag = inv_data_imag[roi.astype(bool)]

    roi_mean_imag.append(np.mean(roi_data_imag))
    roi_range_imag.append((np.min(roi_data_imag), np.max(roi_data_imag)))
    roi_std_imag.append(np.std(roi_data_imag))
    all_range_imag.append((np.min(inv_data_imag), np.max(inv_data_imag)))

    
# Calculate SNR
roi_cnr_real = [(r[1]-r[0])/s for r,s in zip(all_range_real, roi_std_real)]
roi_cnr_imag = [(r[1]-r[0])/s for r,s in zip(all_range_imag, roi_std_imag)]

# Measurements from ROI
# roi_mean = [31789, 89513, 89813]
# roi_range = [(21590, 40847), (77878, 97875), (79730, 103060)]
# all_range = [(-125053, 156384), (-150234, 206007), (158011, 181566)]
# roi_std = [3156, 3664, 4123]
# roi_snr = [m/s for m,s in zip(roi_mean, roi_std)]

# Calculate GRE
GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **subj.eqn_params
)

# Print ranges
# GRE_mean = np.mean(GRE, axis=1)
GRE_range = [(np.min(GRE[i,:]), np.max(GRE[i,:])) for i in range(3)]
# mean_scaled = [0,0,0]
# for i in range(3):
    # mean_scaled[i] = (roi_mean[i] - roi_range[i][0])/(roi_range[i][1] - roi_range[i][0]) * (GRE_range[i][1] - GRE_range[i][0]) + GRE_range[i][0]

desired_std_real = [(r[1]-r[0])/cnr for r,cnr in zip(GRE_range, roi_cnr_real)]
desired_std_imag = [(r[1]-r[0])/cnr for r,cnr in zip(GRE_range, roi_cnr_imag)]
print(f'Real: {desired_std_real}')
print(f'Imag: {desired_std_imag}')

plt.show()