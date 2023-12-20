import nibabel as nib
from adam_utils.nifti import plot_nifti
import matplotlib.pyplot as plt
import numpy as np
import os

# # Load GREs
# scan_folder = '/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_converted_v2023/334264/401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
# gre1_real = nib.load(os.path.join(scan_folder, '401_real_t1010.nii'))
# gre1_imag = nib.load(os.path.join(scan_folder, '401_imaginary_t1010.nii'))
# gre2_real = nib.load(os.path.join(scan_folder, '401_real_t3310.nii'))
# gre2_imag = nib.load(os.path.join(scan_folder, '401_imaginary_t3310.nii'))

# gre1 = gre1_real.get_fdata() + 1j*gre1_imag.get_fdata()
# gre2 = gre2_real.get_fdata() + 1j*gre2_imag.get_fdata()

# # Create robust T1-weighted image
# t1w = np.real(np.conj(gre1)*gre2)/(np.abs(gre1)**2 + np.abs(gre2)**2)
# mask = nib.load('/nfs/masi/saundam1/outputs/t1_mapping/t1w_strip/334264/mask.nii')
# denom_masked = (np.abs(gre1)**2 + np.abs(gre2)**2) * mask.get_fdata()
# beta = np.mean(denom_masked)
# robust_t1w = (np.real(np.conj(gre1)*gre2) - beta)/(np.abs(gre1)**2 + np.abs(gre2)**2 + 2*beta)
# robust_t1w += 0.5

# t1w_nifti = nib.Nifti1Image(t1w, affine=gre1_real.affine)
# robust_t1w_nifti = nib.Nifti1Image(robust_t1w, affine=gre1_real.affine)

# # Save to NIFTI
# robust_t1w_nifti.to_filename('/nfs/masi/saundam1/outputs/t1_mapping/test/robust_t1w.nii.gz')

# Create MP2RAGE data
import os
import t1_mapping
import nibabel as nib
import numpy as np
import pandas as pd
from tqdm import tqdm
import re

# Load groups
# groups = pd.read_excel(os.path.join(t1_mapping.definitions.GROUND_TRUTH_MAT, 'scanID_groups.xlsx'))
# control_subj = groups['Health Control Scans'].dropna().astype(np.int64)
# ms_subj = groups['MS Patient Scans'].dropna().astype(np.int64)
# ground_truth = pd.read_csv(os.path.join(t1_mapping.definitions.GROUND_TRUTH, 'ground_truth_subjects.csv'))
groups = pd.read_csv(os.path.join(t1_mapping.definitions.OUTPUTS, 'ground_truth_subjects.csv'))


# Loop through subjects
for subject in tqdm(os.listdir(t1_mapping.definitions.DATA)):
    subj_id = int(subject)
    if subj_id not in groups['Subject'].to_numpy():
        continue
    subj_path = os.path.join(t1_mapping.definitions.OUTPUTS, 'robust_t1w', subject)
    data_dir = os.path.join(t1_mapping.definitions.OUTPUTS, 'mp2rage_converted_v2023', subject)
    # if subj_id in ms_subj.to_numpy():
    #     group = 'ms'
    # elif subj_id in control_subj.to_numpy():
    #     group = 'control'
    # else:
    #     print(f'Skipping {subj_id}')
    #     group = 'n/a'
    #     continue

    # if os.path.exists(subj_path) and 't1w.nii.gz' in os.listdir(subj_path):
    #     print(f'Already did {subj_id}')
    #     continue

    # if subj_id not in ground_truth['Subject'].values:
    #     print(f'{subj_id} not in ground truth')
    #     continue

    # Get list of scans
    scan = os.listdir(os.path.join(t1_mapping.definitions.DATA, subject))

    # Get scan IDs
    scan_id = [s.split('-')[0] for s in scan]
    primary_scan_ids = [int(s) for s in scan_id if s.endswith('1')]
    primary_scan_ids = sorted(primary_scan_ids)
    highest_primary_scan_id = primary_scan_ids[-1]

    # Get scan that starts with highest primary scan ID
    chosen_scan = [s for s in scan if s.startswith(str(highest_primary_scan_id))][0]
    print(f'{chosen_scan=}')

    # Find scan times
    data_files = os.listdir(os.path.join(data_dir, chosen_scan))
    print(f'{data_files=}')

    # Get scan times from files
    times = [re.findall(r'\d{4}(?=\.)', s)[0] for s in data_files]

    # Get unique items and sort
    times = list(set(times))
    times = sorted(t for t in times)
    times = [times[0], times[1]]
    print(f'{subj_id}: {times}')

    # Create MP2RAGE subject
    subj = t1_mapping.mp2rage.MP2RAGESubject(
        subject_id=subject,
        scan=chosen_scan,
        scan_times=times
    )

    # Calculate T1 map and save
    os.makedirs(subj_path, exist_ok=True)

    # Make robust T1-weighted image
    gre1 = subj.inv[0].get_fdata(dtype=np.complex64)
    gre2 = subj.inv[1].get_fdata(dtype=np.complex64)
    # t1w = np.real(np.conj(gre1)*gre2)/(np.abs(gre1)**2 + np.abs(gre2)**2)

    # Get beta value by mean value of denominator in brain
    # mask = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1w_strip', subject, 'mask.nii'))
    denom = np.abs(gre1)**2 + np.abs(gre2)**2
    # denom_masked = denom * mask.get_fdata()
    beta = 0.25*np.mean(denom)
    robust_t1w = (np.real(np.conj(gre1)*gre2) - beta)/(np.abs(gre1)**2 + np.abs(gre2)**2 + 2*beta)
    robust_t1w += 0.5
    robust_t1w_nifti = nib.Nifti1Image(robust_t1w, affine=subj.affine)

    # Save to NIFTI
    save_folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'robust_t1w_0.25', subject)
    os.makedirs(save_folder, exist_ok=True)
    robust_t1w_nifti.to_filename(os.path.join(save_folder, 'robust_t1w.nii.gz'))