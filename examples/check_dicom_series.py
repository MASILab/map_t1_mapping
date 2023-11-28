# Check that DICOMs all have same # of series
import os
import t1_mapping
import nibabel as nib
import numpy as np
import pandas as pd
from tqdm import tqdm
import re
import pydicom

# Load groups
groups = pd.read_excel(os.path.join(t1_mapping.definitions.GROUND_TRUTH_MAT, 'scanID_groups.xlsx'))
control_subj = groups['Health Control Scans'].dropna().astype(np.int64)
ms_subj = groups['MS Patient Scans'].dropna().astype(np.int64)

# Loop through subjects
for subject in sorted(os.listdir(t1_mapping.definitions.DATA)):
    subj_id = int(subject)
    if subj_id in ms_subj.to_numpy():
        group = 'ms'
    elif subj_id in control_subj.to_numpy():
        group = 'control'
    else:
        #print(f'Skipping {subj_id}')
        group = 'n/a'
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

    path = os.path.join('/nfs/masi/saundam1/datasets/MP2RAGE', subject, subject, chosen_scan, 'DICOM')
    data_files = os.listdir(path)

    dcm = data_files[0]

    #info = os.popen(f'dcminfo {path}/{dcm}').read()
    #print(info)

    #num_series = len([line for line in info.split('\n') if 'image type' in line])
    #print(f'There are {num_series} series in {subj_id}')

    ds = pydicom.dcmread(f'{path}/{dcm}', stop_before_pixels=True)
    print(f"{subj_id}: echo time {ds.PerFrameFunctionalGroupsSequence[0][0x2005,0x140f][0][0x0018,0x0081]}")
