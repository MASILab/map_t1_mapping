# Use package to create MP2RAGE T1w image and T1 map
import os
import json
import matplotlib.pyplot as plt
import t1_mapping
import nibabel as nib
from nilearn import plotting
import numpy as np

# Load dataset paths
# Load dataset paths
subject = '334264'
scan = '401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
scan_num = '401'
scan_times = ['1010', '3310']
dataset_path = '/nfs/masi/saundam1/outputs/mp2rage_converted_v2023/'
subject_path = os.path.join(dataset_path, subject, scan)

# Load NIFTI files
inv1_real = nib.load(os.path.join(subject_path, f'{scan_num}_real_t{scan_times[0]}.nii'))
inv1_imag = nib.load(os.path.join(subject_path, f'{scan_num}_imaginary_t{scan_times[0]}.nii'))
inv2_real = nib.load(os.path.join(subject_path, f'{scan_num}_real_t{scan_times[1]}.nii'))
inv2_imag = nib.load(os.path.join(subject_path, f'{scan_num}_imaginary_t{scan_times[1]}.nii'))

# Load JSON
inv1_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.json')
inv2_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.json')
with open(inv1_json_path, 'r') as f1, open(inv2_json_path, 'r') as f2:
    inv1_json = json.load(f1)
    inv2_json = json.load(f2)

# Load data from NIFTI
inv1_real_data = inv1_real.get_fdata()
inv1_imag_data = inv1_imag.get_fdata()
inv2_real_data = inv2_real.get_fdata()
inv2_imag_data = inv2_imag.get_fdata()

# Create combined complex data
inv1_data = inv1_real_data + 1j*inv1_imag_data
inv2_data = inv2_real_data + 1j*inv2_imag_data

# Create NIFTI
inv1 = nib.nifti2.Nifti2Image(inv1_data, inv1_real.affine)
inv2 = nib.nifti2.Nifti2Image(inv2_data, inv2_real.affine)

# Create parameter dict
params = {
    "TR": inv1_json["RepetitionTime"],
    "MP2RAGE_TR": 8.25,
    "flip_angles": [inv1_json['FlipAngle'], inv2_json['FlipAngle']],
    "inversion_times": [inv1_json['TriggerDelayTime']/1000, inv2_json['TriggerDelayTime']/1000],
    "n": 225,
    "eff": 0.84,
}

print(t1_mapping.utils.acq_to_eqn_params(params))

# Create MP2RAGE object
fitter = t1_mapping.mp2rage.MP2RAGEFitter([inv1, inv2], params)

# Plot T1-weighted image
fig, ax = plt.subplots()
plotting.plot_img(fitter.t1w, cut_coords=(15, 5, 30), cmap='gray', axes=ax, colorbar=True)
ax.set_title('T1-weighted image')
plt.show()

# Plot T1 map
fig, ax = plt.subplots()
plotting.plot_img(fitter.t1_map, cut_coords=(15, 5, 30), cmap='gray', axes=ax, colorbar=True, vmin=0, vmax=5)
ax.set_title('T1 map')
plt.show()

# Save to NIFTI
nib.save(fitter.t1_map, os.path.join('examples', 'outputs', '334264_t1_map.nii.gz'))