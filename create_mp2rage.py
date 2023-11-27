# Create MP2RAGE data
import os
import t1_mapping
import nibabel as nib
import numpy as np
import pandas as pd
from tqdm import tqdm
import re

# Load groups
groups = pd.read_excel(os.path.join(t1_mapping.definitions.GROUND_TRUTH_MAT, 'scanID_groups.xlsx'))
control_subj = groups['Health Control Scans'].dropna().astype(np.int64)
ms_subj = groups['MS Patient Scans'].dropna().astype(np.int64)

# Loop through subjects
for subject in tqdm(os.listdir(t1_mapping.definitions.DATA)):
    subj_id = int(subject)
    subj_path = os.path.join(t1_mapping.definitions.OUTPUTS, 'mp2rage_t1w', subject)
    if subj_id in ms_subj.to_numpy():
        group = 'ms'
    elif subj_id in control_subj.to_numpy():
        group = 'control'
    else:
        print(f'Skipping {subj_id}')
        group = 'n/a'
        continue

    if os.path.exists(subj_path) and 't1w.nii' in os.listdir(subj_path):
        print(f'Already did {subj_id}')
        continue

    # Get list of scans
    scan = os.listdir(os.path.join(t1_mapping.definitions.DATA, subject))

    # Get scan IDs
    scan_id = [s.split('-')[0] for s in scan]
    primary_scan_ids = [int(s) for s in scan_id if s.endswith('1')]
    primary_scan_ids = sorted(primary_scan_ids)
    highest_primary_scan_id = primary_scan_ids[-1]

    # Get scan that starts with highest primary scan ID
    chosen_scan = [s for s in scan if s.startswith(str(highest_primary_scan_id))][0]

    # Find scan times
    data_files = os.listdir(os.path.join(t1_mapping.definitions.DATA, subject, chosen_scan))

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
    save_folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'mp2rage_t1w', str(subj_id))

    os.makedirs(save_folder, exist_ok=True)
    t1w = subj.mp2rage[0]
    t1w.to_filename(os.path.join(save_folder, 't1w.nii'))
