# Create MP2RAGE image
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting
import nibabel as nib
from mp2rage.utils import MP2RAGE

# # Load dataset paths
# subject = '334264'
# scan = '401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
# scan_num = '401'
# scan_times = ['1010', '3310']
# dataset_path = '/nfs/masi/saundam1/outputs/MP2RAGE_converted/'
# subject_path = os.path.join(dataset_path, subject, scan)

# # Load NIFTI files
# inv1 = nib.load(os.path.join(subject_path, f'{scan_num}_t{scan_times[0]}.nii'))
# inv1_ph = nib.load(os.path.join(subject_path, f'{scan_num}_ph_t{scan_times[0]}.nii'))
# inv2 = nib.load(os.path.join(subject_path, f'{scan_num}_t{scan_times[1]}.nii'))
# inv2_ph = nib.load(os.path.join(subject_path, f'{scan_num}_ph_t{scan_times[1]}.nii'))

# # Load data from NIFTI
# inv1_mag = inv1.get_fdata()
# inv1_ph = inv1_ph.get_fdata()
# inv2_mag = inv2.get_fdata()
# inv2_ph = inv2_ph.get_fdata()

# Load example files from original MP2RAGE repo
folder = '/nfs/masi/saundam1/datasets/MPI-LEMON/'
subject = 'sub-032501'
session = 'ses-01'
scan_folder = os.path.join(folder, subject, session, 'anat')
inv1_file = os.path.join(scan_folder, subject + '_' + session + '_inv-1_mp2rage.nii.gz')
inv2_file = os.path.join(scan_folder, subject + '_' + session + '_inv-2_mp2rage.nii.gz')
mp2rage_file = os.path.join(scan_folder, subject + '_' + session + '_acq-mp2rage_T1w.nii.gz')
inv1 = nib.load(inv1_file)
inv2 = nib.load(inv2_file)

inv1_data = inv1.get_fdata()
inv2_data = inv2.get_fdata()


# # Print maxes and mins for sanity
# print(nib.volumeutils.finite_range(inv1_mag))
# print(nib.volumeutils.finite_range(inv1_ph))
# print(nib.volumeutils.finite_range(inv2_mag))
# print(nib.volumeutils.finite_range(inv2_ph))

# # Plot for sanity check
# fig = plt.figure(figsize=(24, 8))
# plotting.plot_anat(inv1_ph, cut_coords=(70, 158, 179), colorbar=True, figure=fig)
# plotting.show()

# # Create combined complex data
# inv1_data = inv1_mag*np.exp(1j*inv1_ph)
# inv2_data = inv2_mag*np.exp(1j*inv2_ph)

# Calculate MP2RAGE image (scale to same as pymp2rage)
mp2rage = MP2RAGE(inv1_data, inv2_data)
mp2rage_nifti = nib.nifti2.Nifti2Image(mp2rage, inv1.affine)

# Save to file
output_file = os.path.join('outputs', f'example_mp2rage.nii.gz')
nib.save(mp2rage_nifti, output_file)

# Display all results
# os.system('fsleyes ' + inv1_file + ' ' + inv2_file + ' ' + output_file + ' ' + mp2rage_file + ' &')