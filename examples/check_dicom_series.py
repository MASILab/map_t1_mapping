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

    # path = os.path.join('/nfs/masi/saundam1/datasets/MP2RAGE', subject, subject, chosen_scan, 'DICOM')
    # data_files = os.listdir(path)

    # dcm = data_files[0]


    # info = os.popen(f'dcminfo {path}/{dcm}').read()
    #print(info)

    # num_series = len([line for line in info.split('\n') if 'image type' in line])
    # print(f'There are {num_series} series in {subj_id}')

    # ds = pydicom.dcmread(f'{path}/{dcm}', stop_before_pixels=True)
    # print(f"{subj_id}: scanner {ds.StationName}")

    path = os.path.join(t1_mapping.definitions.OUTPUTS, 'mp2rage_converted_v2023', subject, chosen_scan)

    range_r1 = os.popen(f'fslstats {path}/{highest_primary_scan_id}_real_t{1010}.nii -R').read()
    range_i1 = os.popen(f'fslstats {path}/{highest_primary_scan_id}_imaginary_t{1010}.nii -R').read()
    range_r2 = os.popen(f'fslstats {path}/{highest_primary_scan_id}_real_t{3310}.nii -R').read()
    range_i2 = os.popen(f'fslstats {path}/{highest_primary_scan_id}_imaginary_t{3310}.nii -R').read()
    range_r3 = os.popen(f'fslstats {path}/{highest_primary_scan_id}_real_t{5610}.nii -R').read()
    range_i3 = os.popen(f'fslstats {path}/{highest_primary_scan_id}_imaginary_t{5610}.nii -R').read()

    print(
        f'{subj_id}: \
        \nGRE 1\treal {range_r1}\timag {range_i1} \
        \nGRE 2\treal {range_r2}\timag {range_i2}\
        \nGRE 3\treal {range_r3}\timag {range_i3}'
    )