import os
import json
import nibabel as nib
from nilearn import plotting
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from sklearn.metrics import mean_squared_error
import t1_mapping

# Change plot style
plt.style.use('Solarize_Light2')

# Load dataset paths
subject = '334264'
scan = '401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
scan_num = '401'
scan_times = ['1010', '3310', '5610']
dataset_path = '/nfs/masi/saundam1/outputs/mp2rage_converted_v2023/'
subject_path = os.path.join(dataset_path, subject, scan)

# Load NIFTI files
inv1_real = nib.load(os.path.join(subject_path, f'{scan_num}_real_t{scan_times[0]}.nii'))
inv1_imag = nib.load(os.path.join(subject_path, f'{scan_num}_imaginary_t{scan_times[0]}.nii'))
inv2_real = nib.load(os.path.join(subject_path, f'{scan_num}_real_t{scan_times[1]}.nii'))
inv2_imag = nib.load(os.path.join(subject_path, f'{scan_num}_imaginary_t{scan_times[1]}.nii'))
inv3_real = nib.load(os.path.join(subject_path, f'{scan_num}_real_t{scan_times[2]}.nii'))
inv3_imag = nib.load(os.path.join(subject_path, f'{scan_num}_imaginary_t{scan_times[2]}.nii'))

# Load JSON
inv1_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.json')
inv2_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.json')
inv3_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[2]}.json')
with open(inv1_json_path, 'r') as f1, open(inv2_json_path, 'r') as f2, open(inv3_json_path, 'r') as f3:
    inv1_json = json.load(f1)
    inv2_json = json.load(f2)
    inv3_json = json.load(f3)

# Load data from NIFTI
inv1_real_data = inv1_real.get_fdata()
inv1_imag_data = inv1_imag.get_fdata()
inv2_real_data = inv2_real.get_fdata()
inv2_imag_data = inv2_imag.get_fdata()
inv3_real_data = inv3_real.get_fdata()
inv3_imag_data = inv3_imag.get_fdata()

# Create combined complex data
inv1_data = inv1_real_data + 1j*inv1_imag_data
inv2_data = inv2_real_data + 1j*inv2_imag_data
inv3_data = inv3_real_data + 1j*inv3_imag_data

# Create NIFTIs
inv1 = nib.nifti1.Nifti1Image(inv1_data, inv1_real.affine)
inv2 = nib.nifti1.Nifti1Image(inv2_data, inv2_real.affine)
inv3 = nib.nifti1.Nifti1Image(inv3_data, inv3_real.affine)

# Load acquisition parameters
params : t1_mapping.utils.MP2RAGEParameters = {
    "MP2RAGE_TR": 8.25,
    "TR": inv1_json["RepetitionTime"],
    "flip_angles": [inv1_json['FlipAngle'], inv2_json['FlipAngle'], inv3_json['FlipAngle']],
    "inversion_times": [inv1_json['TriggerDelayTime']/1000, inv2_json['TriggerDelayTime']/1000, inv3_json['TriggerDelayTime']/1000],
    "n": [225],
    "eff": 0.84,
}

# Calculate MP2RAGE image
t1w1 = t1_mapping.utils.mp2rage_t1w(inv1_data, inv2_data)
t1w1_nifti = nib.nifti1.Nifti1Image(t1w1, inv1_real.affine)

t1w2 = t1_mapping.utils.mp2rage_t1w(inv1_data, inv3_data)
t1w2_nifti = nib.nifti1.Nifti1Image(t1w1, inv1_real.affine)

# Plot T1w image
fig, ax = plt.subplots()
plotting.plot_img(t1w1_nifti, cut_coords=(15, 5, 30), cmap='gray', axes=ax, colorbar=True)
ax.set_title('T1-Weighted Image')

fig, ax = plt.subplots()
plotting.plot_img(t1w2_nifti, cut_coords=(15, 5, 30), cmap='gray', axes=ax, colorbar=True)
ax.set_title('T1-Weighted Image')
plt.show()

# Range of values for T1
t1_estimate = np.arange(0.05, 5.01, 0.05)
num_points = len(t1_estimate)

# Get equation parameters
eqn_params = t1_mapping.utils.acq_to_eqn_params(params)

# Calculate what values would be produced using these parameters
GRE = t1_mapping.utils.gre_signal(T1=t1_estimate, **eqn_params)

# Calculate what MP2RAGE image would have been
mp2rage1 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
mp2rage2 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[2,:])

# Plot GRE
fig, ax = plt.subplots()
ax.plot(t1_estimate, GRE[0,:], label="GRE1")
ax.plot(t1_estimate, GRE[1,:], label="GRE2")
ax.plot(t1_estimate, GRE[2,:], label="GRE3")
ax.set_title('GRE Estimates')
ax.set_xlabel("T1 (s)")
ax.set_ylabel("GRE Value")
fig.legend()
plt.show()

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Plot curve of known values
ax.plot(mp2rage1, mp2rage2, t1_estimate, label='Calculated values')
ax.set_xlabel('MP2RAGE_1*')
ax.set_ylabel('MP2RAGE_2*')
ax.set_zlabel('T1 (s)')
ax.set(xlim=(-0.5, 0.5), ylim=(-0.5, 0.5), zlim=(0,5))

# Plot values we want to calculate
indx = np.arange(0, len(t1w1.flatten()), 50000)
ax.scatter(t1w1.flatten()[indx], t1w2.flatten()[indx], zs=0, zdir='z', color=[0,1,0,0.2], label='Unknown values')

# Plot projections
ax.plot(mp2rage1, mp2rage2, zs=0, zdir='z', color=[1,0,0,0.2])
ax.plot(mp2rage1, t1_estimate, zs=-0.5, zdir='x', color=[1,0,0,0.2])
ax.plot(mp2rage2, t1_estimate, zs=0.5, zdir='y', color=[1,0,0,0.2])

ax.legend()
plt.show()

print('Calculating distances')

# Calculate closest point
mp2rage = np.array((mp2rage1, mp2rage2), dtype=np.float16).T
t1w = np.array((t1w1.flatten(), t1w2.flatten()), dtype=np.float16).T

# closest_indices = []
# for pt in t1w:
#     distances = np.linalg.norm(mp2rage - pt, axis=1)
#     closest_index = np.argmin(distances)
#     closest_indices.append(closest_index)
abs_dist = mp2rage[:,np.newaxis,:] - t1w
distances = np.sum((abs_dist)** 2, axis=2)
closest_indices = np.argmin(distances, axis=0)
