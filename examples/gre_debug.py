import os
import json
import nibabel as nib
from nilearn import plotting
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import t1_mapping

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

# Load data from NIFTI
inv1_real_data = inv1_real.get_fdata()
inv1_imag_data = inv1_imag.get_fdata()
inv2_real_data = inv2_real.get_fdata()
inv2_imag_data = inv2_imag.get_fdata()

# Create combined complex data
inv1_data = inv1_real_data + 1j*inv1_imag_data
inv2_data = inv2_real_data + 1j*inv2_imag_data

# Load JSON
inv1_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.json')
inv2_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.json')
with open(inv1_json_path, 'r') as f1, open(inv2_json_path, 'r') as f2:
    inv1_json = json.load(f1)
    inv2_json = json.load(f2)

# Load acquisition parameters
params : t1_mapping.mp2rage.MP2RAGEParameters = {
    "MP2RAGE_TR": 8.25,
    "TR": inv1_json["RepetitionTime"],
    "flip_angles": [inv1_json['FlipAngle'], inv2_json['FlipAngle']],
    "inversion_times": [inv1_json['TriggerDelayTime']/1000, inv2_json['TriggerDelayTime']/1000],
    "n": 225,
    "eff": 0.84,
}

# Calculate MP2RAGE image
t1w = t1_mapping.utils.mp2rage_t1w(inv1_data, inv2_data)

# Range of values for T1
t1_estimate = np.arange(0.05, 5.01, 0.05)
num_points = len(t1_estimate)
t1_estimate = t1_estimate.reshape(num_points,1)

# Calculate TA, TB, TC
TA = params["inversion_times"][0] - params["n"]/2*params["TR"]
TB = params["inversion_times"][1] - params["inversion_times"][0] - params["n"]*params["TR"]
TC = params["MP2RAGE_TR"] - params["inversion_times"][1] - params["n"]/2*params["TR"]

# Calculate what values would be produced with the range for T1
[GRE1, GRE2] = t1_mapping.utils.gre_signal(
    T1=t1_estimate,
    TA=TA,
    TB=TB,
    TC=TC,
    TR=params["TR"],
    alpha_1=params["flip_angles"][0],
    alpha_2=params["flip_angles"][1],
    n=params["n"],
    MP2RAGE_TR=params["MP2RAGE_TR"],
    eff=params["eff"]
)

# Create estimated T1-weighted image
MP2RAGE = t1_mapping.utils.mp2rage_t1w(GRE1, GRE2)

# Sort arrays
sorted_idx = np.argsort(MP2RAGE)
MP2RAGE = MP2RAGE[sorted_idx]
t1_estimate = t1_estimate[sorted_idx]

# Calculate for desired values
t1_calc = np.interp(t1w.flatten(), MP2RAGE, t1_estimate)