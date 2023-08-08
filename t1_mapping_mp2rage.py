# Calculates a quantitative T1 mapping from MP2RAGE data
import os
import json
import matplotlib.pyplot as plt
import pymp2rage
import nibabel as nib
from nilearn import plotting

# Load dataset paths
subject = '334236'
scan = '601-x-WIPMP2RAGE_1mm_1sTI_TFEprepulsecardiacSENSE-x-WIPMP2RAGE_1mm_1sTI_TFEprepulsecardiacSENSE'
scan_num = '601'
scan_times = ['1010', '3310']
dataset_path = '/nfs/masi/saundam1/Outputs/MP2RAGE_converted/'
subject_path = os.path.join(dataset_path, subject, scan)


# Load JSON
inv1_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.json')
inv2_json_path = os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.json')
with open(inv1_json_path, 'r') as f1, open(inv2_json_path, 'r') as f2:
    inv1_json = json.load(f1)
    inv2_json = json.load(f2)

# Load NIFTI files
inv1 = nib.load(os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.nii'))
inv1_ph = nib.load(os.path.join(subject_path, f'{scan_num}_ph_t{scan_times[0]}.nii'))
inv2 = nib.load(os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.nii'))
inv2_ph = nib.load(os.path.join(subject_path, f'{scan_num}_ph_t{scan_times[1]}.nii'))

# Load acquisition parameters
MPRAGE_tr = 6
nZslices = 34
FLASH_tr = [inv1_json['RepetitionTime'], inv2_json['RepetitionTime']]
invtimesAB = [inv1_json['TriggerDelayTime']/1000, inv2_json['TriggerDelayTime']/1000]
flipangleABdegree =[inv1_json['FlipAngle'], inv2_json['FlipAngle']]
sequence = 'normal'
inversion_efficiency = 0.96 # estimate
B0 = inv1_json['MagneticFieldStrength']

# Create MP2RAGE fitter
fitter = pymp2rage.MP2RAGE(MPRAGE_tr = MPRAGE_tr,
                           invtimesAB = invtimesAB,
                           flipangleABdegree = flipangleABdegree,
                           nZslices = nZslices,
                           FLASH_tr = FLASH_tr,
                           sequence = sequence,
                           inversion_efficiency = inversion_efficiency,
                           B0 = B0,
                           inv1 = inv1,
                           inv1ph = inv1_ph,
                           inv2 = inv2,
                           inv2ph = inv2_ph)

# Plot T1 map
t1map = fitter.t1map
fig = plt.figure(figsize=(24,6))
plotting.plot_anat(t1map, figure=fig, cut_coords=(0,0,0), colorbar=True)
plotting.show()

# Save
output_path = os.path.join('outputs', f'{subject}_{scan_num}_t1map.nii.gz')
nib.save(t1map, output_path)