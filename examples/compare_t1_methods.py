# Create different T1 maps
import os
import t1_mapping
import nibabel as nib
import numpy as np

# Load subject
subj_12 = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2.npy'), 
    all_inv_combos=False,
)

subj_13 = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_3.npy'), 
    all_inv_combos=False,
)

subj_123 = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'), 
    all_inv_combos=False,
)

output_file = os.path.join(t1_mapping.definitions.OUTPUTS, 'test', 't1_map')

# Save T1 maps
# nib.save(subj_12.t1_map('likelihood'), output_file + '_s1_2.nii.gz')
# nib.save(subj_13.t1_map('likelihood'), output_file + '_s1_3.nii.gz')
# nib.save(subj_123.t1_map('likelihood'), output_file + '_s1_2_3.nii.gz')
# nib.save(subj_12.t1_map('linear'), output_file + '_s1_2_lut.nii.gz')
nib.save(subj_12.t1_map('map'), output_file + '_s1_2_map.nii.gz')
